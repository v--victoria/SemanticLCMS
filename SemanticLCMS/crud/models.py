#! /bin/python
# -*- coding: utf-8 -*-

from django.db.models import *
from django.db.models.query import QuerySet
from SemanticObjects import *

# Create your models here.

class SemanticQuerySet (QuerySet):

	def __init__(self, model, uri):

		super(SemanticQuerySet, self).__init__(model)

		self.s = SemanticObjects ("http://fourstore.avalon.ru:80")
		#self.s.add_namespace ("wines", "http://www.w3.org/TR/2003/PR-owl-guide-20031209/wine#")
		self.uri = uri

		# получаем все экземпляры класса
		self.resources = self.s.get_resources (self.uri)

	def __repr__ (self):

		return str (self.resources)

	def __iter__ (self):

		return iter (self.resources)

	def __getitem__ (self, k):

		if -1 < k < len (self.resources): return self.resources[k]
		else: raise Exception ("Object doesn't have item with key '" + str(key)+"'")

	def __len__ (self):

		return len (self.resources)

	def filter (self, **kwargs):

		res = list (self.resources)

		for attr in kwargs:

			tmp = []

			for obj in res:

				if hasattr (obj, attr) and obj[attr] == kwargs[attr]: tmp.append (obj)				

			res = list(tmp)

		return res

	def get (self, **kwargs):

		t = self.filter (**kwargs)

		if len (t) > 1: raise Exception ("Too many records retrieved for ", kwargs)

		return t

	available_properties = property (lambda self: self.s.get_available_properties (self.uri))

#	def get_properties (self):
#	
#		return self.s.get_properties (self.uri)
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

	def __init__(self, uri):

		super(SemanticManager, self).__init__()
		self.uri = uri	

	def get_query_set (self):

		return SemanticQuerySet (self.model, self.uri)

# описываем модель, по которой будем получать данные из онтологии
class Factory (object):

#	uri = "http://www.w3.org/2002/07/owl#Class"
#	uri = "http://www.w3.org/TR/2003/PR-owl-guide-20031209/wine#Chardonnay"#"Zinfandel" # вызывает фейл: "DryRedWine"
#	namespace = "http://www.w3.org/TR/2003/PR-owl-guide-20031209/wine#" #"http://www.w3.org/2002/07/owl#"#
#	ns = "wines"

	def __new__ (cls, uri):

		t = uri.rsplit ("#")
		name = t[1] if len (t) > 1 else uri.rsplit (":")[1]

		return type (name, (object,), {"uri": uri, "objects": SemanticManager (uri)})

	def __init__ (self, uri):

		pass
#		self.objects = SemanticManager (uri)
