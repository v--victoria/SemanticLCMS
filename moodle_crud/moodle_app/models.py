#! /bin/python
# -*- coding: utf-8 -*-
#view https://github.com/tsouvarev
#

from django.db.models import *
from django.db.models.query import QuerySet
from SemanticObjects import *

# Create your models here.

class SemanticQuerySet (QuerySet):

	def __init__(self, model, uri, ns, namespace):

		super(SemanticQuerySet, self).__init__(model)

		self.s = SemanticObjects ("http://fourstore.avalon.ru/sparql/")
#		self.s = SemanticObjects ("http://192.168.19.12:8080/sparql/")
#		self.s = SemanticObjects ("http://fourstore.avalon.ru:8080/sparql/")
		self.s.add_namespace (ns, namespace)

		self.ns = ns
		self.uri = uri

		# получаем все экземпляры класса
		self.resources = self.s.get_resources (self.ns + ":" + self.uri)

	def __repr__ (self):

		return str (self.resources)

	def __iter__ (self):

		return iter (self.resources)

	def __getitem__ (self, k):

		if -1 < k < len (self.resources): return self.resources[k]
		else: return None

	def __len__ (self):

		return len (self.resources)

	def filter (self, **kwargs):

		print kwargs

		res = list (self.resources)

		for attr in kwargs:

			tmp = []

			for obj in res:

				if hasattr (obj, attr) and obj[attr] == kwargs[attr]: tmp.append (obj)

			res = tmp			

		return res

	def get (self, **kwargs):

		t = self.filter (**kwargs)

		print "t: " % t

		return t[0] if len(t)>0 else []
#		
#	def exclude (self, **kwargs):
#	
#		return None
#		
#	def annotate (self, *args, **kwargs):
#	
#		return None
#		
#	def order_by (self, *fields):
#	
#		return None
#		
#	def reverse (self):
#	
#		return None
#		
#	def distinct (self, *fields):
#	
#		return None

# менеджер семантического репозитария
class SemanticManager (Manager):

	def __init__(self, namespace, ns, uri):

		super(SemanticManager, self).__init__()

		self.namespace = namespace
		self.ns = ns
		self.uri = uri	

	def get_query_set (self):

		return SemanticQuerySet (self.model, self.uri, self.ns, self.namespace)
	
# описываем модель, по которой будем получать данные из онтологии
class Winery (Model):
	uri = "Winery"
	namespace = "http://www.w3.org/TR/2003/PR-owl-guide-20031209/wine#"
	ns = "wines"
	objects = SemanticManager(namespace, ns, uri)

class Region (Model):
	uri = "Region"
	namespace = "http://www.w3.org/TR/2003/PR-owl-guide-20031209/wine#"
	adjacentRegion = CharField (max_length = 20)
	locatedIn = CharField (max_length = 20)
	ns = "wines"
	objects = SemanticManager(namespace, ns, uri)

class VintageYear (Model):
	uri = "VintageYear"
	namespace = "http://www.w3.org/TR/2003/PR-owl-guide-20031209/wine#"
	ns = "wines"
	objects = SemanticManager(namespace, ns, uri)
	yearValue = IntegerField()
	def __unicode__(self):
		return self.yearValue
	
