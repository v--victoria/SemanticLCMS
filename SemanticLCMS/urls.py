from django.conf.urls.defaults import patterns, include, url
from SemanticLCMS.views import site_root
from SemanticLCMS.crud.views import show_classes, show_objects, show_object

# Uncomment the next two lines to enable the admin:
# from django.contrib import admin
# admin.autodiscover()

urlpatterns = patterns('',
    # Examples:
    # url(r'^$', 'moodle_crud.views.home', name='home'),
    # url(r'^moodle_crud/', include('moodle_crud.foo.urls')),

    # Uncomment the admin/doc line below to enable admin documentation:
    # url(r'^admin/doc/', include('django.contrib.admindocs.urls')),

    # Uncomment the next line to enable the admin:
    # url(r'^admin/', include(admin.site.urls)),
    (r'^$', show_classes),
    (r'^(\w+)/$', show_objects),
    (r'^(\w+)/(\w+)/$', show_object),
)
