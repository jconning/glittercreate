from django.contrib import admin
from glitterproj.glitter.models import User
from glitterproj.glitter.models import Page
from glitterproj.glitter.models import AssetType
from glitterproj.glitter.models import Asset
from glitterproj.glitter.models import AssetPlacement
from glitterproj.glitter.models import RepoAsset

admin.site.register(User)
admin.site.register(Page)
admin.site.register(AssetType)
admin.site.register(Asset)
admin.site.register(AssetPlacement)
admin.site.register(RepoAsset)
