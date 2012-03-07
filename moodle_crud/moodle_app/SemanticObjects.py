#! /bin/python
# -*- coding: utf-8 -*-

#view https://github.com/tsouvarev
#

import SPARQLWrapper as wrap
from SPARQLWrapper import SPARQLWrapper, JSON

# Класс, отображающий RDF-тройки в объекты Python
class SemanticObjects ():

	def __init__ (self, addr):

		# запоминаем SPARQL-endpoint
		self.sparql = SPARQLWrapper(addr)

		# строка, содержащая в итоге все нужные запросам 
		# префиксы для более короткого написания URI ресурсов
		self.prefixes = ""

		# пространства имен 
		self.namespaces = {}
		# сокращение для self.namespaces
		self.ns = self.namespaces

		# список базовых классов, понадобится при запросах классов и ресурсов из хранилища
		# также играет роль кэша классов
		self.bases = {}

		# заранее добавляем пространства, которые точно понадобятся
		self.ns["owl"] = "http://www.w3.org/2002/07/owl#"
		self.ns["rdfs"] = "http://www.w3.org/2000/01/rdf-schema#"
		self.ns["rdf"] = "http://www.w3.org/1999/02/22-rdf-syntax-ns#"

		# формируем сразу шапку запросов из префиксов
		for ns in self.ns: self.prefixes += "PREFIX %s: <%s>\n" % (ns, self.ns[ns])

	# выполняет запрос, возвращает результат в виде почти прямого 
	# переноса XML/RDF на списки и объекты в Python
	def get_query (self, query):

		self.sparql.setQuery(self.prefixes + query)

		self.sparql.setReturnFormat(JSON)
		results = self.sparql.query().convert()

		return results

	# красивая печать результатов
	def print_results (self, results):

		print results

		for result in results["results"]["bindings"]:

			for i in results["head"]["vars"]: print "%s: %s" % (i, result[i]["value"])
			print

	# добавление пространства имен
	def add_namespace (self, name, namespace):

		self.namespaces[name] = namespace

		# сразу обновляем шапку запросов
		self.prefixes += "PREFIX %s: <%s>\n" % (name, namespace)

	# конвертация результатов от get_query в более удобный вид
	# properties - результаты от get_query
	# schema - схема преобразования
	#
	# schema состоит из кортежей соответствия нового названия, которое хотим дать, и свойств из properties
	#
	# каждый кортеж преобразовывается в атрибут итогового объекта
	#
	# первый параметр в кортеже есть название для атрибута в итоговом объекте
	# если в кортеже второй параметр строка, то атрибут будет строковым
	# если в кортеже второй параметр список, то множество значений из properties
	# попадут в один и тот же список. в списке может быть произвольное число элементов, из них и будет 
	# формироваться атрибут в итоговом объекте
	# 
	# например, кортеж ("a", "b") означает взять из properties свойство "b" и 
	# записать его в итоговый объект как атрибут "a"
	# кортеж ("a", ["b","c"]) означает взять из properties все свойства под названиями "b" и "c" и
	# записать их в один список под названием "a"
	def convert (self, properties, schema):

		c = {}

		for name,val in schema:

			if type(val) == str:

				i,j = name,val

				for prop in properties["results"]["bindings"]:

					p = prop[i]
					v = prop[j]

					if p["type"] != "bnode" and v["type"] != "bnode":

						p = p["value"].rsplit ("#")[1]
						v = v["value"].rsplit ("#")[1]
						c[p] = v

			elif type(val) == list:

				c[name] = []

				for p in properties["results"]["bindings"]:

					for n in val:

						if p[n]["type"] != "bnode": c[name].append (p[n]["value"].rsplit("#")[1])

		return c

	# функция создания классов по URI
	def get_class (self, uri):

		# выделяем название класса из URI
		# может быть в виде smth#name или smth:name
		# первое есть традиционная форма записи, вторая принята в SPARQL-запросах
		t = uri.rsplit ("#")
		name = t[1] if len (t) > 1 else uri.rsplit (":")[1]

		props = {}

		# запрос на определение свойств класса в нем же непосредственно определенных
		# (не из иерархии классов)
		queries = ["""
					select ?prop ?val
					where 
					{
						{ 
							%s a owl:Class ; 
							?rel ?sub . 
							?sub owl:onProperty	?prop ;
						 		 owl:hasValue ?val
						}
						union
						{					
							%s a owl:Class ;
							?prop ?val .
							?prop a rdf:Property
						}
						union
						{					
							%s a owl:Class ;
							owl:intersectionOf (?f [ owl:onProperty ?prop; owl:hasValue ?val])
						}		
						union
						{					
							%s a owl:Class ;
							owl:intersectionOf ( ?class [ owl:onProperty ?prop; owl:hasValue ?val] ?b ) .
							?class a owl:Class
						}
					}
					""" % ((uri,)*4)
					]

		# добавляем найденные свойства в словарь, понадобится при создании класса
		for q in queries: 
			props.update (self.convert (self.get_query (q), [("prop", "val",)]))

		# запрос на определение родительских классов
		q = """
				select ?class 
				where 
				{ 
					{
						%s a owl:Class ; 
						rdfs:subClassOf ?class .
						?class a owl:Class
					}
					union
					{					
						%s a owl:Class ;
						owl:intersectionOf ( ?class ?a ) .
						?class a owl:Class
					}
					union
					{					
						%s a owl:Class ;
						owl:intersectionOf ( ?class ?a ?b ) .
						?class a owl:Class
					}
					union
					{
						%s a owl:Class ;
						owl:intersectionOf ( ?class ?x ) .
						?class a owl:Class .
						?x a owl:Class
					}												
					union
					{
						%s a owl:Class ;
						owl:intersectionOf ( ?x ?class ) .
						?class a owl:Class .
						?x a owl:Class
					}
				}""" % ((uri,)*5)

		# сразу заполняем кэш классов, если класс еще не встречался
		# TODO: если кэш не сбрасывается между запросами, 
		# то почему в иерархии наследования для конкретного класса нет лишних классов?
		for i in self.convert (self.get_query (q), [("classes", ["class"], )])["classes"]: 

			if i not in self.bases:

				self.bases[i] = self.get_class ("wines:" + i)

		# создаем новый тип, который потом и вернем
		r = type (str(name), tuple (self.bases.values()), props)
		r.uri = uri

 		r.__repr__ = lambda self: u"" + self.uri
 		r.__str__ = lambda self: u"" + self.uri
 		

 		def get (self, key):

			# обход всего дерева наследования в поиске атрибута 			
 			for cls in [self] + list (self.__class__.__mro__):
 			
 				if hasattr (cls,key): return cls.__dict__[key] 					
 			
 			return None
 			
 		r.__getitem__ = get
 		
		return r

	# функция получения экземпляров 
	# class_uri - идентификатор класса экземпляров
	def get_resources (self, class_uri):

		#t = self.get_class (class_uri)

		q = """
				select ?inst
				where
				{
					?inst a %s
				}
			""" % ((class_uri,)*1)

		# список названий всех экземпляров из онтологии
		instances = self.convert (self.get_query (q), [("inst", ["inst"], )])["inst"]

		res = []

		for inst in instances:

			res.append (self.get_resource ("wines:" + inst)) # TODO: hardcoded ns!!!

		return res

	# функция получения конкретного ресурса 
	#  uri - идентификатор ресурса
	def get_resource (self, uri):

		q = """
				select ?type
				where
				{
					%s a ?type
				}
			""" % uri

		type_name = self.convert (self.get_query (q), [("type", ["type"])])["type"][0]

		t = self.get_class ("wines:" + str(type_name))

		# запрашиваем свойства ресурса из онтологии
		q = """
				select *
				where
				{
					%s ?p ?o .
					FILTER (?p != rdf:type)
				}
			""" % uri

		r = t()

		r.uri = uri
		query = self.convert (self.get_query (q), [("p", "o", )])

		# добавляем в созданный экземпляр найденные свойства
		for i in query: r.__dict__[i] = query[i]		

		return r
