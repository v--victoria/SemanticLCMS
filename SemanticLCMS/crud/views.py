from crud.models import *
from django.http import HttpResponse
from django.shortcuts import render_to_response
from django.utils.html import escape
import json
import re

class HttpJsonResponse(HttpResponse):
    def __init__(self, data):
        super(HttpJsonResponse, self).__init__(data)
        self['Content-Type'] = 'text/json'



def get_short_name(full_name):
    patt = re.compile('[#:]\w+')
    return patt.search(full_name).group(0)[1:]



def show_classes(request, reprmode): #TODO get reprmode from request
    t = Factory('http://www.w3.org/2002/07/owl#Class')
    fullnames = map(str, t.objects.all())
    shortnames = map(get_short_name, fullnames)
    classes = map(lambda a, b: (a, b), fullnames, shortnames)

    n = len(classes)

    if reprmode == None: reprmode = ''
    reprmode = reprmode[1:]

    if reprmode == 'table':
        return render_to_response('classes_table.html',  {'classes': classes, 'count': n})
    elif reprmode == 'json':
        return HttpJsonResponse(json.dumps(fullnames))
    else:
        return render_to_response('classes_no repr.html', {'classes': classes, 'count': n, 'reprmode': reprmode})



#show all objects of class
#reprmode - representation mode (i.e table, list, json)
def show_objects(request, classname, reprmode): #TODO get reprmode from request
    ns = 'http://www.w3.org/TR/2003/PR-owl-guide-20031209/wine#'
    t = Factory(ns + str(classname))
    fullnames = map(str, t.objects.all())
    shortnames = map(get_short_name, fullnames)
    objs = map(lambda a, b: (a, b), fullnames, shortnames)

    n = len(objs)

    if reprmode == None: reprmode = ''
    reprmode = reprmode[1:]
    
    if reprmode == 'table': 
        return render_to_response('objects_table.html', {'classname': classname, 'objs': objs, 'count': n})
    elif reprmode == 'json':	
        return HttpJsonResponse(json.dumps({classname: fullnames}))
    else: 
        return render_to_response('objects_no_repr.html', {'classname': classname, 'objs': objs, 'count': n, 'reprmode': reprmode})



def show_object(request, classname, objectname, reprmode):
    ns = 'http://www.w3.org/TR/2003/PR-owl-guide-20031209/wine#'
    t = Factory(ns + str(classname))
    obj = t.objects.all().get(uri = ns + objectname)[0]
    
    if reprmode == None: reprmode = ''
    reprmode = reprmode[1:]

    #TODO props
    props = []

    shortprop = 'locatedIn'
    fullprop = ns + shortprop
    try:
        fullvalue = obj[fullprop]
        props.append((shortprop, fullvalue, get_short_name(fullvalue)))
    except AttributeError:
        props.append((shortprop, None, None))

    shortprop = 'adjacentRegion'
    fullprop = ns + shortprop
    try:
        fullvalue = obj[fullprop]
        props.append((shortprop, fullvalue, get_short_name(fullvalue)))
    except AttributeError:
        props.append((shortprop, None, None))
    

    if reprmode == 'table':
        return render_to_response('object_table.html', {'classname': classname, 'obj': get_short_name(str(obj)), 'props': props})
    elif reprmode == 'json':
        return HttpJsonResponse(json.dumps({ns + classname: {str(obj): props}}))
    else:
	return render_to_response('object_no_repr.html', {'classname': classname, 'obj': get_short_name(str(obj)), 'props': props, 'reprmode': reprmode})
