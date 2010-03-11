import datetime
from glitterproj.glitter.models import RepoAsset
from glitterproj.glitter.models import AssetType
from glitterproj.glitter.models import Asset
from glitterproj.glitter.models import RepoAssetDailyConsume
from glitterproj.glitter.textasset import TextAsset
from glitterproj.glitter.imageasset import UserUploadedImageAsset
from glitterproj.glitter.derivedimageasset import DerivedUserUploadedImageAsset
from glitterproj.glitter.glitterasset import GlitterAsset

# OPTIMIZATION: cache these statically, there are a limited number and they don't change.  Just keep a static dictionary and populate it when an entry is not found.
def getAssetType(assetTypeName):
    return AssetType.objects.get(asset_type_name=assetTypeName)

def getAssetActor(asset):

    # Construct the proper type of AssetActor for this asset type
    assetActor = None
    if asset.asset_type == getAssetType('text'):
        assetActor = TextAsset()
    elif asset.asset_type == getAssetType('userUploadedImage'):
        assetActor = UserUploadedImageAsset()
    elif asset.asset_type == getAssetType('derivedUserUploadedImage'):
        assetActor = DerivedUserUploadedImageAsset()
    elif asset.asset_type == getAssetType('glitter'):
        assetActor = GlitterAsset()
    else:
        print "assethelper.getAssetActor(): Invalid asset type"
        return None

    assetActor.setAsset(asset)

    return assetActor

def getAssetActorFromRepo(repoAssetId, assetType, user=None):

    repoAsset = RepoAsset.objects.get(id=repoAssetId)

    if repoAsset.getAssetTypeName() != assetType.asset_type_name:
        raise

    asset = Asset()
    if user:
        asset.user = user
    asset.asset_type = assetType
    asset.state = repoAsset.getState()

    registerRepoAssetConsumeCopy(repoAsset)  # register the fact that we have just copied this repo asset for a consumption, so it can be counted
    
    return getAssetActor(asset), repoAsset.getImageUrl(), repoAsset.getImageWidth(), repoAsset.getImageHeight()

def registerRepoAssetConsumeCopy(repoAsset):

    repoAsset.incrementConsumeCopyCount()
    repoAsset.save()

    repoAssetDailyConsumeQuerySet = RepoAssetDailyConsume.objects.filter(repo_asset = repoAsset, consume_date = datetime.date.today())

    # I don't know how to get the first element in the query set so I do it the hard way
    repoAssetDailyConsume = None
    for radc in repoAssetDailyConsumeQuerySet:
        repoAssetDailyConsume = radc

    if not repoAssetDailyConsume:
        repoAssetDailyConsume = RepoAssetDailyConsume()
        repoAssetDailyConsume.repo_asset = repoAsset
        repoAssetDailyConsume.consume_date = datetime.date.today()

    repoAssetDailyConsume.incrementConsumeCopyCount()
    repoAssetDailyConsume.save()
