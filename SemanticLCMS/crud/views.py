from django.http import HttpResponse
from django.shortcuts import render_to_response
from django.utils.html import escape
from SemanticLCMS.crud.models import *
import json
import re

def get_acc_types(request):
    return [a.split(';')[0] for a in request.META['HTTP_ACCEPT'].split(',')]

def get_short(full):
    patt = re.compile('[#:]\w+')
    return patt.search(full).group(0)[1:]

def show_classes(request):
    qs = Factory('http://www.w3.org/2002/07/owl#Class').objects.all()
    uris = map(str, qs)
    ids  = map(get_short, uris)
    classes = map(lambda a, b: (a, b), uris, ids)
    n = len(qs)
    
    accepts = get_acc_types(request)
#    accepts.append('text/json')
#    accepts = []

    if 'text/json' in accepts:
        return HttpResponse(json.dumps(uris), content_type = 'text/json')
    elif 'text/html' in accepts:
        return render_to_response('classes_table.html',   {'classes': classes, 'count': n})
    else:
        return render_to_response('classes_no_repr.html', {'classes': classes, 'count': n})



def show_objects(request, classid):
    ns = 'http://www.w3.org/TR/2003/PR-owl-guide-20031209/wine#'

    accepts = get_acc_types(request)
#    accepts.append('text/json')
#    accepts = []

    # if such class doesn't exist
    qs = Factory('http://www.w3.org/2002/07/owl#Class').objects.all()
    if len(qs.get(uri = ns + classid)) == 0:
        if 'text/json' in accepts:	
            return HttpResponse(json.dumps({}), content_type = 'text/json')
        else:
	    return render_to_response('error.html', {'msg': 'No class ' + classid})

    qs = Factory(ns + str(classid)).objects.all()
    uris = map(str, qs)
    ids  = map(get_short, uris)
    objs = map(lambda a, b: (a, b), uris, ids)
    n = len(objs)

    if 'text/json' in accepts:	
        return HttpResponse(json.dumps({ns + classid: uris}), content_type = 'text/json')
    elif 'text/html' in accepts:
        return render_to_response('objects_table.html',   {'classid': classid, 'objs': objs, 'count': n})
    else:
        return render_to_response('objects_no_repr.html', {'classid': classid, 'objs': objs, 'count': n})


def show_object(request, classid, objectid):
    ns = 'http://www.w3.org/TR/2003/PR-owl-guide-20031209/wine#'

    accepts = get_acc_types(request)
#    accepts.append('text/json')
    accepts = []

    # if such class doesn't exist
    qs = Factory('http://www.w3.org/2002/07/owl#Class').objects.all()
    if len(qs.get(uri = ns + classid)) == 0:
        if 'text/json' in accepts:	
            return HttpResponse(json.dumps({}), content_type = 'text/json')
        else:
	    return render_to_response('error.html', {'msg': 'No class ' + classid})

    qs = Factory(ns + str(classid)).objects.all()
    obj = qs.get(uri = ns + objectid)

    # if such object doesn't exist
    if len(obj) == 0:
        if 'text/json' in accepts:	
            return HttpResponse(json.dumps({ns + classid: None}), content_type = 'text/json')
        else:
	    return render_to_response('error.html', {'msg': 'No object ' + objectid + ' of class ' + classid})

    obj = obj[0]
    ps = qs.available_properties
    props = {}
    for p in ps:
        if hasattr(obj, p):
            if type(obj[p]) == list: #for future, no implementation yet
                props[p] = list((val, str(type(val))) for val in obj[p])
            else:
                props[p] = list({obj[p]: str(type(obj[p]))}.iteritems())
        else:
            props[p] = None
                
    if 'text/json' in accepts:	
        return HttpResponse(json.dumps({ns + classid: {ns + objectid: props}}), content_type = 'text/json')
    else:
        p = []
        for k, v in props.iteritems():
	    if v == None: p.append([k, get_short(k), None, None, None])
	    else: p.append([k, get_short(k), v[0][0], get_short(v[0][0]), v[0][1]])
        return render_to_response('object_table.html',   {'classid': classid, 'objectid': objectid, 'props': p})

