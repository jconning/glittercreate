import datetime
from glitter.models import User
from glitter.models import Page
from glitter.models import Asset
from glitter.models import AssetType
from glitter.models import AssetPlacement
from glitter.textasset import TextAsset

def postSignupActions(user):
    createNewSite(user)
    return

def createNewSite(user):

    print 'createNewSite'

    # Create a new page
    page = Page(
        user = user,
        page_name = 'My first page',
        url_name = 'myfirstpage'
    )
    page.save()

    textAsset = TextAsset()
    textAsset.setUser(user)
    textAsset.setTextContent("This is my first text asset!")
    textAsset.save()
    placement = AssetPlacement(asset=textAsset.getAsset(), page=page, top=100, left=100, width=300, height=100)
    placement.save()

    textAsset = TextAsset()
    textAsset.setUser(user)
    textAsset.setTextContent("This is my second text asset!")
    textAsset.setBackgroundColor("FFFF00")
    textAsset.save()
    placement = AssetPlacement(asset=textAsset.getAsset(), page=page, top=200, left=200, width=300, height=100)
    placement.save()

    return

def setLoginCookies(request, user):
    request.session.flush()
    request.session['loggedInUserId'] = str(user.id)
    request.session['lastLoginTime'] = datetime.datetime.now()
    request.session['lastUpdateTime'] = datetime.datetime.now()
    return

def checkLoggedIn(request):
    loggedInUserId = request.session.get('loggedInUserId', '')
    if not loggedInUserId:
        return None
    user = User.objects.get(pk=loggedInUserId)
    return user

