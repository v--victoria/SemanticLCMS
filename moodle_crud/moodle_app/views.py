from django.http import HttpResponse
from moodle_app.models import *
from django.utils.html import escape
from django.shortcuts import render_to_response
import json
import re

# id of all classes : TODO
def show_classes(request):
    pass

#show all objects of class
#reprmode - representation mode (i.e table, list, json)
def show_objects(request, classname, reprmode):
    objs = Region.objects.all() #objs is a QuerySet
    n = len(objs)
    if reprmode == None: reprmode = ''
    reprmode = reprmode[1:]
    
    if reprmode == 'table': 
        return render_to_response('objects_table.html', {'classname': classname, 'objs': objs, 'count': n})
    elif reprmode == 'list': 
        return render_to_response('objects_list.html',  {'classname': classname, 'objs': objs, 'count': n})
    elif reprmode == 'json':
        objsstr = []
        for obj in objs:
            objsstr.append(str(obj))	
        jsondata = json.dumps({classname: {'objects' : objsstr}})
        #json.dumps(list(obj_list.__iter__())) #wines:BeaujolaisRegion is not JSON serializable
        return render_to_response('json_repr.html', {'jsondata': jsondata})
    else: 
        return render_to_response('objects_no_repr.html', {'classname': classname, 'objs': objs.__repr__(), 'count': n, 'reprmode': reprmode})

#show k object of class
#reprmode - representation mode (i.e table, list, json)
def show_object_by_num(request, classname, k, reprmode):
    objs = Region.objects.all()
    k = int(k)
    k = k - 1
    if k >= len(objs): 
        return render_to_response('object_error.html', {'classname': classname})
    if reprmode == None: reprmode = ''
    reprmode = reprmode[1:]

    obj = objs.__getitem__(int(k))
    props = []
    
    try:
        props.append(('adjacentRegion', obj.adjacentRegion))
    except AttributeError:
        props.append(('adjacentRegion', None))
    try:
        props.append(('locatedIn', obj.locatedIn))
    except AttributeError:
        props.append(('locatedIn', None))
    k = k + 1
    if reprmode == 'table':
        return render_to_response('object_table.html', {'classname': classname, 'obj': obj, 'k': k, 'props': props})
    elif reprmode == 'list':
        return render_to_response('object_list.html',  {'classname': classname, 'obj': obj, 'k': k, 'props': props})
    elif reprmode == 'json':
        jsondata = json.dumps({str(obj): {'props': props}})
        return render_to_response('json_repr.html', {'jsondata': jsondata})
    else:
	return render_to_response('object_no_repr.html', {'classname': classname, 'obj': obj, 'k': k, 'props': props, 'reprmode': reprmode})


def show_object_by_name(request, classname, objectname, reprmode): #TODO get(name='')
    objs = Region.objects.all()
    n = len(objs)
    patt = re.compile(':\w+')
    for i in range(n):
        if patt.search(str(objs.__getitem__(i))).group(0)[1:] == objectname:
            return show_object_by_num(request, classname, i + 1, reprmode)
    return render_to_response('object_error.html', {'classname': classname})
