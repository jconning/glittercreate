from django.conf.urls.defaults import *

urlpatterns = patterns('glitterproj.glitter.views',
    (r'^signup/$', 'signup'),
    (r'^login/$', 'login'),
    (r'^logout/$', 'logout'),
    (r'^viewpage/(?P<page_id>\d+)/$', 'viewPage'),
    (r'^editor/$', 'pageEditor'),
    (r'^edittext/$', 'editText'),
    (r'^uploadphoto/$', 'uploadPhoto'),
    (r'^editglitter/', 'editGlitter'),
    (r'^repopublish/$', 'assetRepositoryPublish'),
    (r'^myglitter/$', 'viewGlitterAssets'),
    (r'^myglitterdetail/$', 'viewGlitterAssetDetail'),
    (r'^myglitterdetail/(?P<assetId>\d+)/$', 'viewGlitterAssetDetail'),
    (r'^choose/$', 'viewGlitterRepoAssets'),
    (r'^myrglitter/$', 'viewUserGlitterRepoAssets'),
)
