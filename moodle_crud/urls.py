from django.conf.urls.defaults import patterns, include, url
from moodle_crud.views import site_root
from moodle_crud.moodle_app.views import show_objects, show_object_by_num, show_object_by_name

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
    (r'^(\w+)/(\*[a-zA-Z]*)?$', show_objects), # i.e Region, Region/?, Region/?list, Region/?json
    (r'^(\w+)/(\d{1,2})/(\*[a-zA-Z]*)?$', show_object_by_num),
    (r'^(\w+)/(\w+)/(\*[a-zA-Z]*)?$', show_object_by_name),
    ('^$', site_root),
)
