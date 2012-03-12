from django.http import HttpResponse

def site_root(request):
	return HttpResponse("This is site root")
