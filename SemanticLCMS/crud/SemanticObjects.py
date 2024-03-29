#! /bin/python
# -*- coding: utf-8 -*-

import SPARQLWrapper as wrap
from DBBackends import SparqlBackend

class Thing (object):

	def __repr__ (self): 

		return self.uri

	def __str__ (self):
 	
 		return self.uri
 	
	def __unicode__ (self):
 	
		return self.uri

	def __getattr__ (self, key):		

		return self.get_property (s.uri, key)

	def __setattr__ (self, key, val):

		self.__dict__[key] = val
 			
	__getitem__ = __getattr__
	__setitem__ = __setattr__

# Класс, отображающий RDF-триплеты в объекты Python
class SemanticObjects ():

	def __init__ (self, addr):

		# запоминаем SPARQL-endpoint
		#self.sparql = SPARQLWrapper(addr)
		self.db = SparqlBackend (addr)

		# строка, содержащая в итоге все нужные запросам 
		# префиксы для более короткого написания URI ресурсов
		self.prefixes = ""

		# пространства имен 
		self.namespaces = {}
		# сокращение для self.namespaces
		self.ns = self.namespaces

		# список базовых классов, понадобится при запросах классов и ресурсов из хранилища
		# также играет роль кэша классов
		self.classes = {}
		self.superclasses = {}

		# заранее добавляем пространства, которые точно понадобятся
		self.ns["owl"] = "http://www.w3.org/2002/07/owl#"
		self.ns["rdfs"] = "http://www.w3.org/2000/01/rdf-schema#"
		self.ns["rdf"] = "http://www.w3.org/1999/02/22-rdf-syntax-ns#"

		# формируем сразу шапку запросов из префиксов
		for ns in self.ns: self.prefixes += "PREFIX %s: <%s>\n" % (ns, self.ns[ns])

	def get_query (self, query):

		return self.db.query (self.prefixes + query)

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

	# конвертация результатов от get_query в более удобный вид (description is obsoleted)
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
	def convert (self, properties, schemas, split = False, create = False):

		c = {}

		for schema in schemas:

			if len (schema) == 1:

				i, = schema

				for prop in properties["results"]["bindings"]:

					p = prop[i]

					if p["type"] != "bnode":

#						if p["type"] == "uri": p = self.get_resource (p["value"])
#						else: p = p["value"]
						p = p["value"]

						c[i] = p

			else:

				name,val = schema

				if type(val) == str:

					i,j = name,val

					for prop in properties["results"]["bindings"]:

						p = prop[i]
						v = prop[j]

						if p["type"] != "bnode" and v["type"] != "bnode":

							p = p["value"]

#							if v["type"] == "uri": v = self.get_resource (v["value"])
#							else: v = v["value"]
							v = v["value"]

							c[p] = v

				elif type(val) == list:

					c[name] = []

					for p in properties["results"]["bindings"]:

						for n in val:

							if p[n]["type"] != "bnode": 

#								if p[n]["type"] == "uri": v = self.get_resource (p[n]["value"])
#								else: v = p[n]["value"]
								v = p[n]["value"]

								c[name].append (v)

		return c

	def get_class_properties (self, uri):

		# запрос на определение свойств класса в нем же непосредственно определенных
		# (не из иерархии классов)
		q = """
				select ?val
				where 
				{
					{ 
						<%s> a owl:Class ; 
						?rel ?sub . 
						?sub owl:onProperty	?prop ;
					 		 owl:hasValue ?val
					}
					union
					{					
						<%s> a owl:Class ;
						?prop ?val .
						?prop a rdf:Property
					}
					union
					{					
						<%s> a owl:Class ;
						owl:intersectionOf (?f [ owl:onProperty ?prop; owl:hasValue ?val])
					}		
					union
					{					
						<%s> a owl:Class ;
						owl:intersectionOf ( ?class [ owl:onProperty ?prop; owl:hasValue ?val] ?b ) .
						?class a owl:Class
					}
				}
				""" % ((uri,)*4)

		# добавляем найденные свойства в словарь, понадобится при создании класса
		props = self.convert (self.get_query (q), [("prop", "val",)])

		return props

	def get_resource_properties (self, uri):

		# запрашиваем свойства ресурса из онтологии
		q = """
				select *
				where
				{
					<%s> ?prop ?val .
					FILTER (?prop != rdf:type)
				}
			""" % uri

		props = self.convert (self.get_query (q), [("prop", "val", )])

		return props

	def get_available_properties (self, class_uri):

		q_all = "select distinct ?prop where { ?prop rdf:type owl:ObjectProperty . }"
		q_inverse = "select distinct ?prop where { ?prop rdf:type owl:ObjectProperty ; owl:inverseOf ?p }"
		q_domain = "select distinct ?prop where { ?prop rdf:type owl:ObjectProperty ; rdfs:domain ?d }"

		s_all = set (self.convert (self.get_query (q_all), [("props", ["prop"],)])["props"])
		s_inverse = set (self.convert (self.get_query (q_inverse), [("props", ["prop"],)])["props"])
		s_domain = set (self.convert (self.get_query (q_domain), [("props", ["prop"],)])["props"])

		obj = self.classes[class_uri]

		walk = []

		q = "select distinct ?prop where {"

		for cls in obj.__mro__:

			if hasattr (cls, "uri"):

				q += """
					{
					?prop rdf:type owl:ObjectProperty .
					?prop rdfs:domain <%s>
					}
					union
					""" % cls.uri

		q = q[:-16] + "}"

		props = self.convert (self.get_query (q), [("props", ["prop"],)])["props"] + \
				list (s_all-s_domain-s_inverse)

		return props


	# если несколько разных значений одного атрибута, то возьмется последнее
	def get_property (self, uri, name):

		obj = self.classes[uri]

		if name not in obj.__dict__: 

			t = self.__get_property (obj.uri, name)
			if t is not None: return t

		else: return obj.__dict__[name]		

		for base in obj.__class__.__mro__:

			print "base:", base

			if hasattr (base, name):

				return getattr (base, name)

			else:

				t = self.__get_property (base.uri, name)
				if t is not None: return t

		raise AttributeError ("Key '" + name + "' not in '" + uri + "'")

	def __get_property (self, uri, name):

		c = {}

		q = """
				select ?val
				where 
				{
					{ 
						<%s> a owl:Class ; 
						?rel ?sub . 
						?sub owl:onProperty	<%s> ;
					 		 owl:hasValue ?val
					}
					union
					{					
						<%s> a owl:Class ;
						owl:intersectionOf (?f [ owl:onProperty <%s>; owl:hasValue ?val])
					}		
					union
					{					
						<%s> a owl:Class ;
						owl:intersectionOf ( ?class [ owl:onProperty <%s>; owl:hasValue ?val] ?b ) .
						?class a owl:Class
					}
					union
					{
						<%s> rdfs:subClassOf [ 	rdf:type owl:Restriction ;
												owl:onProperty <%s>;
												owl:hasValue ?val ]
					}
					union
					{					
						<%s> a owl:Class ;
						<%s> ?val .
						<%s> a rdf:Property
					}
				}
				""" % ((uri, name, )*5 + (name,))

		# добавляем найденные свойства в словарь, понадобится при создании класса

		val = self.convert (self.get_query (q), [("val",)])

		if "val" in val: 

			setattr (self.classes[uri], name, val["val"])
			return val["val"]

		return None

	def get_class_superclasses (self, uri):

		bases = []

		# запрос на определение родительских классов
		q = """
				select ?class 
				where 
				{ 
					{
						<%s> a owl:Class ; 
						rdfs:subClassOf ?class .
						?class a owl:Class
					}
					union
					{					
						<%s> a owl:Class ;
						owl:intersectionOf ( ?class ?a ) .
						?class a owl:Class
					}
					union
					{					
						<%s> a owl:Class ;
						owl:intersectionOf ( ?class ?a ?b ) .
						?class a owl:Class
					}
					union
					{
						<%s> a owl:Class ;
						owl:intersectionOf ( ?class ?x ) .
						?class a owl:Class .
						?x a owl:Class
					}												
					union
					{
						<%s> a owl:Class ;
						owl:intersectionOf ( ?x ?class ) .
						?class a owl:Class .
						?x a owl:Class
					}
				}""" % ((uri,)*5)

		a = self.convert (self.get_query (q), [("classes", ["class"], )])["classes"]

		# сразу заполняем кэш классов, если класс еще не встречался
		for i in a: 

			if i not in self.classes: 

				self.classes[i] = self.get_class (i)

			bases.append (self.classes[i])

		return bases

	# функция создания классов по URI
	def get_class (self, uri):

		if uri in self.classes: return self.classes[uri]

		t = uri.rsplit ("#")
		name = t[1] if len (t) > 1 else uri.rsplit (":")[1]

		props = {} #self.get_class_properties (uri)
		bases = self.get_class_superclasses (uri)

		# создаем новый тип, который потом и вернем
		r = type (str(name), tuple (bases), props)
		r.uri = uri

		r.__repr__ = lambda self: u"" + self.uri
		r.__str__ = lambda self: u"" + self.uri

		def get_attr (s, key):

			return self.get_property (s.uri, key)

		def set_attr (s, key, val):

			s.__dict__[key] = val

		r.__getitem__ = get_attr
		r.__getattr__ = get_attr
		r.__setitem__ = set_attr
		r.available_properties = property (lambda x: self.get_available_properties (r.uri))
		# r.__getattribute__ = get

 		self.classes[uri] = r
 		
		return r

	# функция получения экземпляров 
	# class_uri - идентификатор класса экземпляров
	def get_resources (self, class_uri):

		#t = self.get_class (class_uri)

		q = """
				select ?inst
				where
				{
					?inst a <%s>
				}
			""" % class_uri

		# список названий всех экземпляров из онтологии

		instances = self.convert (self.get_query (q), [("inst", ["inst"], )])["inst"]

		res = []

		for inst in instances:

			res.append (self.get_resource (inst, class_uri))

		return res

	# функция получения конкретного ресурса 
	# uri - идентификатор ресурса
	def get_resource (self, uri, type_name = None):

		t = None

		if type_name is None:

			q = """
					select ?type
					where
					{
						<%s> a ?type
					}
				""" % uri

			t = self.convert (self.get_query (q), [("type",)])

		else:

			t = self.get_class (type_name)

		r = t()
		r.uri = uri

		self.classes[uri] = r

		# добавляем в созданный экземпляр найденные свойства

#		props = self.get_resource_properties (uri)
#		
#		for i in props: r.__dict__[i] = props[i]		

		return r

	def insert (self, query):

		print self.db.insert (query)

	def delete (self, query):

		print self.db.delete (query)

	def test (self):

#		self.insert ("insert {<http://www.w3.org/TR/2003/PR-owl-guide-20031209/wine#test> <http://www.w3.org/1999/02/22-rdf-syntax-ns#type> <http://www.w3.org/2002/07/owl#Class>}")

		#self.delete ("delete where {<http://www.w3.org/TR/2003/PR-owl-guide-20031209/wine#test> <http://www.w3.org/1999/02/22-rdf-syntax-ns#type> <http://www.w3.org/2002/07/owl#Class>}")

		self.get_class ("http://www.w3.org/TR/2003/PR-owl-guide-20031209/wine#Chardonnay")

		print self.get_properties ("http://www.w3.org/TR/2003/PR-owl-guide-20031209/wine#Chardonnay")

		pass
