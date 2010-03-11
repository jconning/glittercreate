from django.conf.urls.defaults import *

from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',
    (r'^glitter/', include('glitterproj.glitter.urls')),

#    (r'^site_media/(?P<path>.*)$', 'django.views.static.serve', {'document_root': 'C:/daDjangoProject/siteMedia/'}),
    (r'^site_media/(?P<path>.*)$', 'django.views.static.serve', {'document_root': '/Users/jimconning/daDjangoProject/siteMedia/'}),

    # Uncomment the admin/doc line below and add 'django.contrib.admindocs' 
    # to INSTALLED_APPS to enable admin documentation:
    # (r'^admin/doc/', include('django.contrib.admindocs.urls')),

    (r'^admin/', include(admin.site.urls)),

    (r'', 'glitter.views.viewGlitterRepoAssets'),
)
