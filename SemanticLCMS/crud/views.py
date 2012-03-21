from django.http import HttpResponse
from django.shortcuts import render_to_response
from django.utils.html import escape
from SemanticLCMS.crud.models import *
import json
import re

def get_acc_types(request):
    return [a.split(';')[0] for a in request.META['HTTP_ACCEPT'].split(',')]

def get_short(full_name):
    patt = re.compile('[#:]\w+')
    return patt.search(full_name).group(0)[1:]

#show all classes
def show_classes(request): #TODO it is only for get method
    t = Factory('http://www.w3.org/2002/07/owl#Class')
    fullnames = map(str, t.objects.all())
    shortnames = map(get_short, fullnames)
    classes = map(lambda a, b: (a, b), fullnames, shortnames)
    n = len(classes)
    
    accepts = get_acc_types(request)
#   accepts.append('text/json')
#   accepts = []

    if 'text/json' in accepts:
        return HttpResponse(json.dumps(fullnames), content_type = 'text/json')
    elif 'text/html' in accepts:
        return render_to_response('classes_table.html',  {'classes': classes, 'count': n})
    else:
        return render_to_response('classes_no repr.html', {'classes': classes, 'count': n})



#show all objects of class
def show_objects(request, classname):
    ns = 'http://www.w3.org/TR/2003/PR-owl-guide-20031209/wine#'
    t = Factory(ns + str(classname))
    fullnames = map(str, t.objects.all())
    shortnames = map(get_short, fullnames)
    objs = map(lambda a, b: (a, b), fullnames, shortnames)
    n = len(objs)


    accepts = get_acc_types(request)
#   accepts.append('text/json')
#   accepts = []
    if 'text/json' in accepts:	
        return HttpResponse(json.dumps({ns + classname: fullnames}), content_type = 'text/json')
    elif 'text/html' in accepts:
        return render_to_response('objects_table.html', {'classname': classname, 'objs': objs, 'count': n})
    else:
        return render_to_response('objects_no_repr.html', {'classname': classname, 'objs': objs, 'count': n})


def show_object(request, classname, objectname):
    ns = 'http://www.w3.org/TR/2003/PR-owl-guide-20031209/wine#'
    t = Factory(ns + str(classname))
    obj = t.objects.all().get(uri = ns + objectname)
    obj = obj[0]
    accepts = get_acc_types(request)
#   accepts.append('text/json')
#   accepts = []

    #TODO props
    props = []

    shortprop = 'locatedIn'
    fullprop = ns + shortprop
    try:
        fullvalue = obj[fullprop]
        props.append((fullprop, shortprop, fullvalue, get_short(fullvalue)))
    except AttributeError:
        props.append((fullprop, shortprop, None, None))

    shortprop = 'adjacentRegion'
    fullprop = ns + shortprop
    try:
        fullvalue = obj[fullprop]
        props.append((fullprop, shortprop, fullvalue, get_short(fullvalue)))
    except AttributeError:
        props.append((fullprop, shortprop, None, None))
    
    if 'text/json' in accepts:	
        return HttpResponse(json.dumps({ns + classname: {str(obj): [[p[0], p[2]] for p in props]}}), content_type = 'text/json')
    elif 'text/html' in accepts:
        return render_to_response('object_table.html', {'classname': classname, 'obj': get_short(str(obj)), 'props': props})
    else:
	return render_to_response('object_no_repr.html', {'classname': classname, 'obj': get_short(str(obj)), 'props': props})

