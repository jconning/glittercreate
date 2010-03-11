import datetime
import time
import random
import os.path
from django.http import HttpResponse
from django.template import Context, loader
from django.db import IntegrityError
from django.http import HttpResponseRedirect
from django.core.urlresolvers import reverse
from django.contrib.sessions.backends.db import SessionStore
from django.contrib.sessions.models import Session
from django.shortcuts import get_object_or_404, render_to_response
from django import forms
from django.core.files.uploadhandler import TemporaryFileUploadHandler
from glitterproj.glitter.models import User
from glitterproj.glitter.models import Page
from glitterproj.glitter.models import Asset
from glitterproj.glitter.models import AssetPlacement
from glitterproj.glitter.models import AssetType
from glitterproj.glitter.models import RepoAsset
from glitterproj.glitter import userhelper
from glitterproj.glitter import imagehelper
from glitterproj.glitter import imhelper
from glitterproj.glitter import glitterhelper
from glitterproj.glitter import s3helper
from glitterproj.glitter import assethelper
from glitterproj.glitter.textasset import TextAsset
from glitterproj.glitter.imageasset import UserUploadedImageAsset
from glitterproj.glitter.derivedimageasset import DerivedUserUploadedImageAsset
from glitterproj.glitter.glitterasset import GlitterAsset

repoGlitterAssetsPerPage = 20

def index(request):
    return HttpResponse("This is the index.")

def signup(request):
    username = request.POST.get('username', '')
    password = request.POST.get('password', '')
    password2 = request.POST.get('password2', '')
    email = request.POST.get('email', '')
    postLoginAction = request.REQUEST.get('postlogin', '')
    validateStr = request.POST.get('val', '')

    validate = True if validateStr == "y" else False

    username = username.strip()
    password = password.strip()

    error_message = ''
    if not validate:
        error_message = ''
    elif username == '':
        error_message = 'Please enter a username'
    elif password == '':
        error_message = 'Please enter a password'
    elif password2 == '':
        error_message = 'Please confirm the password'
    elif email == '':
        error_message = 'Please enter an email address'
    elif password != password2:
        error_message = 'The two passwords do not match'

    user = User(
        username = username,
        password = password,
        email_address = email,
        signup_date = datetime.datetime.now()
    )
    try:
        if not error_message and validate:  # save to db only if no validation error found
            user.save()

            # Grab the glitterAsset from the session before setting the login cookies, because that will create a new session
            if postLoginAction == 'finalizeglitter':
                glitterAsset = request.session['glitterAsset']

            userhelper.setLoginCookies(request, user)  # log the user in
            userhelper.postSignupActions(user)
            if postLoginAction == 'finalizeglitter':
                return finalizeGlitterAsset(request, glitterAsset)            
            return HttpResponseRedirect('/')
    except IntegrityError:
        error_message = 'That username is already taken.'

    return render_to_response('glitter/signup.html', {
        'username': username,
        'password': password,
        'password2': password2,
        'email': email,
        'error_message': error_message,
        'postLoginAction': postLoginAction,
        'user': user,
        })

def login(request):
    username = request.POST.get('username', '')
    password = request.POST.get('password', '')
    postLoginAction = request.REQUEST.get('postlogin', '')
    validateStr = request.POST.get('val', '')

    validate = True if validateStr == "y" else False

    if not username and not validate:
        return render_to_response("glitter/login.html", {
            'postLoginAction': postLoginAction
            })

    username = username.strip()
    password = password.strip()

    errorCode = ""
    if username == '':
        errorCode = 'Please enter a username'
    elif password == '':
        errorCode = 'Please enter a password'

    if validate and not errorCode:
        try:
            user = User.objects.get(username=username)

            if user.password == password:
                # Grab the glitterAsset from the session before setting the login cookies, because that will create a new session
                if postLoginAction == 'finalizeglitter':
                    glitterAsset = request.session['glitterAsset']

                userhelper.setLoginCookies(request, user)

                if postLoginAction == 'finalizeglitter':
                    return finalizeGlitterAsset(request, glitterAsset)
            
                # Always return an HttpResponseRedirect after successfully dealing
                # with POST data. This prevents data from being posted twice if a
                # user hits the Back button.
                # Forward to the choose glitter landing page.
                return HttpResponseRedirect('/')
            else:
                errorCode = "invalidPassword"
        except User.DoesNotExist:
            errorCode = "noSuchUser"

    return render_to_response('glitter/login.html', {
        'username': username,
        'password': password,
        'errorCode': errorCode,
        'postLoginAction': postLoginAction
        })

def logout(request):
    request.session.flush()
    return HttpResponseRedirect('/glitter/glitter')

def pageEditor(request):

    user = userhelper.checkLoggedIn(request)
    if not user:
        return HttpResponse("session has timed out")

    page = Page.objects.get(user=user)

    # Query all asset placements on the given page and retrieve into the
    # queryset cache all related asset objects.
    assetPlacements = AssetPlacement.objects.select_related().filter(page=page)

    pageOutput = ""

    for placement in assetPlacements:
        asset = placement.asset
        assetActor = assethelper.getAssetActor(asset)
        print "assetActor: "
        print assetActor
        pageOutput += assetActor.render(placement, isEdit=True)

    pageOutput += '<form action="/glitter/edittext/" method="post">\n'
    pageOutput += '<input type=hidden name=pageid value=%d>\n' % (page.id)
    pageOutput += '<input type=hidden name=isnew value=y>\n'
    pageOutput += '<input type=submit value="Add Text">\n'
    pageOutput += '</form>\n'

    pageOutput += '<form enctype="multipart/form-data" action="/glitter/uploadphoto/" method="post">\n'
    pageOutput += '<input type=hidden name=pageid value=%d>\n' % (page.id)
    pageOutput += '<input type=file name=file1 size=40>\n'
    pageOutput += '<input type=submit value="Upload">\n'
    pageOutput += '</form>\n'

    pageOutput += '<form action="/glitter/editglitter/" method="post">\n'
    pageOutput += '<input type=hidden name=pageid value=%d>\n' % (page.id)
    pageOutput += '<input type=submit value="Add Glitter">\n'
    pageOutput += '</form>\n'

    pageOutput += '<a href="/glitter/myglitter/">My Glitter</a>\n';

    pageOutput += '<br><a href="/glitter/logout/">Logout</a>\n';

    return HttpResponse(pageOutput)

def viewPage(request, page_id):

    page = Page.objects.get(id=page_id)

    # Query all asset placements on the given page and retrieve into the
    # queryset cache all related asset objects.
    assetPlacements = AssetPlacement.objects.select_related().filter(page=page)

    pageOutput = ""

    for placement in assetPlacements:
        print placement  #debug
        asset = placement.asset
        print asset      #debug
        assetActor = assethelper.getAssetActor(asset)
        pageOutput += assetActor.render(placement)

    return HttpResponse(pageOutput)

def editText(request):
    user = userhelper.checkLoggedIn(request)
    if not user:
        return HttpResponse("session has timed out")

    validateStr = request.POST.get('val', '')
    isNewStr = request.POST.get('isnew', '')
    text = request.POST.get('text', '')
    assetId = request.REQUEST.get('assetid', '0')  # passed in for existing assets (isNew is False)
    pageId = request.REQUEST.get('pageid', '0')    # passed in for new assets (isNew is True)
    backgroundColor = request.POST.get('bgcolor', '')

    isNew = True if isNewStr == "y" else False
    validate = True if validateStr == "y" else False

    # Get the existing asset, if any
    asset = None
    if not isNew:
        asset = TextAsset(Asset.objects.get(pk=int(assetId)))

    if validate:
        if isNew:
            print "pageId: " + str(pageId)
            page = Page.objects.get(pk=int(pageId))
            
            # Create and place the asset
            asset = TextAsset()
            asset.setUser(user)
            asset.setTextContent(text)
            asset.setBackgroundColor(backgroundColor)
            asset.save()
            placement = AssetPlacement(asset=asset.getAsset(), page=page, top=400, left=100, width=300, height=100)
            placement.save()
            return HttpResponseRedirect('/glitter/editor/')
        else:
            asset.setTextContent(text)
            asset.setBackgroundColor(backgroundColor)
            asset.save()
            return HttpResponseRedirect('/glitter/editor/')
    else:
        if not isNew:
            # Populate return parameters with contents of existing asset
            text = asset.getTextContent()
            backgroundColor = asset.getBackgroundColor()
            if backgroundColor == None:
                backgroundColor = ''

    return render_to_response('glitter/editText.html', {
        'isNew': isNew,
        'pageId': pageId,
        'text': text,
        'bgColor': backgroundColor,
        'assetId': assetId,
        })

class UploadFileForm(forms.Form):
#    title = forms.CharField(max_length=50)
    file  = forms.FileField()

def uploadPhoto(request):
    user = userhelper.checkLoggedIn(request)
    if not user:
        return HttpResponse("session has timed out")

    # Modify the default upload handlers.  Force photos to always be written to temporary files, which
    # we want to do so that the image processing servers can reach them (the Python code will not be
    # reading in the contents of photos.)  Setting this here means the setting FILE_UPLOAD_HANDLERS
    # in settings.py will be ignored, as will the setting FILE_UPLOAD_MAX_MEMORY_SIZE.
    request.upload_handlers = [TemporaryFileUploadHandler()]

    pageId = request.POST.get('pageid', 0)

    page = Page.objects.get(id=pageId)

    try:
        form = UploadFileForm(request.POST, request.FILES)
    except Exception, extraInfo:
        print "have caught exception, extraInfo: "
        print extraInfo

    for fileKey in request.FILES:
        uploadedFile = request.FILES[fileKey]

        imageFileType = "unknown"
        if uploadedFile.content_type == "image/jpeg":
            imageFileType = "jpg"

        uploadWorkPath = "C:/uploadwork/"

        # Construct a working file name that is composed of the userId, time, a random number, and the file type suffix
        workingFilePrefix = str(user.id) + "." + str(time.time()) + "." + str(random.randint(1, 99999))
        rawUploadedFileName = uploadWorkPath + workingFilePrefix + "." + imageFileType

        # Keep track of the current latest and greatest image file, because some steps are optional
        # and we want to know which version to use when it comes time to transfer the file to s3.
        currentWorkingFileName = rawUploadedFileName

        # The first thing we do is copy the freshly uploaded file to the working file.  We do this
        # because django deletes its temporary file as soon as it is no longer referenced, and
        # we don't want to deal with that.
        print "filename: " + rawUploadedFileName
        destination = open(rawUploadedFileName, 'wb+')
        for chunk in uploadedFile.chunks():
            destination.write(chunk)
        destination.close()

        # Invoke imagemagick to read the image's attributes
        (width, height, imageFileType, contentType) = imhelper.readImageAttributes(rawUploadedFileName)
        print "contentType:%s imageFileType:%s" % (contentType, imageFileType)

        # If the image is greater than 1280 pixels on either side then resize it down to 1280 pixels.
        # Invoke ImageMagick command line.
        maxWidthHeight = 1280
        if int(width) > maxWidthHeight or int(height) > maxWidthHeight:
            initialResizedFileName = uploadWorkPath + workingFilePrefix + ".initialResized." + imageFileType
            # Resize the file so that the longer side is maxWidthHeight pixels and aspect ratio is preserved
            imhelper.resize(
                srcFileName=currentWorkingFileName,
                destFileName=initialResizedFileName,
                width=maxWidthHeight,
                height=maxWidthHeight)
            currentWorkingFileName = initialResizedFileName  # now we have a new current working file
            (width, height, imageFileType, contentType) = imhelper.readImageAttributes(initialResizedFileName)  # get the width and height after resize

        asset = UserUploadedImageAsset()
        asset.setUser(user)
        asset.setUrl("unknown")  # To be set after we have the assetId
        asset.setImageFileType(imageFileType)
        asset.setSize(uploadedFile.size)
        asset.setWidth(width)
        asset.setHeight(height)
        asset.setOriginalFileName(uploadedFile.name)

        # Saving the asset will generate an auto-increment primary key, which we can then use to name the file
        asset.save()

        # Name the file with the assetId
        remoteFileName = str(asset.getAssetId()) + "." + imageFileType
        asset.setUrl(imagehelper.getImageUrl(remoteFileName))
        asset.save()

        fileSize = os.path.getsize(currentWorkingFileName)

        # Put the file to s3.  This is the UserUploadedImageAsset (NOT the DerivedUserUploadedImageAsset).
        s3helper.putImageToS3(
            contentType=contentType,
            fileSize=fileSize,
            localFilePathName=currentWorkingFileName,
            remoteFileName=remoteFileName)

        # If the image is a JPEG and either its width or its height is greater than 640 pixels,
        # then resize the image down to 640 pixels and create a DerivedUserUploadedImageAsset.
        # We don't want to resize down PNGs because users sometimes make very sharp looking
        # "blends" and resizing them screws them up, and resizing can also screw up animated GIFs.
        maxDerivedWidthHeight = 640
        print "imageTypeType:%s width:%d height:%d" % (imageFileType, width, height)
        if imageFileType == 'jpg' and (width > maxDerivedWidthHeight or height > maxDerivedWidthHeight):
            print "and here I am inside the if"
            derivedResizedFileName = uploadWorkPath + workingFilePrefix + ".derivedResized." + imageFileType
            # Resize the file so that the longer side is maxDerivedWidthHeight pixels and aspect ratio is preserved
            imhelper.resize(
                srcFileName=currentWorkingFileName,
                destFileName=derivedResizedFileName,
                width=maxDerivedWidthHeight,
                height=maxDerivedWidthHeight)
            currentWorkingFileName = derivedResizedFileName  # now we have a new current working file
            (width, height, imageFileType, contentType) = imhelper.readImageAttributes(derivedResizedFileName)  # get the width and height after resize
            fileSize = os.path.getsize(derivedResizedFileName)

            #  Create the DerivedUserUploadedImageAsset
            derivedAsset = DerivedUserUploadedImageAsset()
            derivedAsset.setUser(user)
            derivedAsset.setUrl("unknown")  # To be set after we have the assetId
            derivedAsset.setImageFileType(imageFileType)
            derivedAsset.setSize(fileSize)
            derivedAsset.setWidth(width)
            derivedAsset.setHeight(height)
            derivedAsset.setSourceUserUploadedImageAssetId(asset.getAssetId())
            derivedAsset.setSourceUserUploadedImageUrl(asset.getUrl())
            derivedAsset.save()

            # Name the file with the assetId
            remoteFileName = str(derivedAsset.getAssetId()) + "." + imageFileType
            derivedAsset.setUrl(imagehelper.getImageUrl(remoteFileName))
            derivedAsset.save()

            # Put the file to s3.  This is the DerivedUserUploadedImageAsset.
            s3helper.putImageToS3(
                contentType=contentType,
                fileSize=fileSize,
                localFilePathName=derivedResizedFileName,
                remoteFileName=remoteFileName)

            # Place the DerivedUserUploadedImage onto the page
            placement = AssetPlacement(asset=derivedAsset.getAsset(), page=page, top=350, left=350,
                width=derivedAsset.getWidth(),
                height=derivedAsset.getHeight()
                )
            placement.save()
        else:
            # Place the UserUploadedImage onto the page
            placement = AssetPlacement(asset=asset.getAsset(), page=page, top=350, left=350,
                width=asset.getWidth(),
                height=asset.getHeight()
                )
            placement.save()

        # THIS IS CODE TO DO THE UPLOAD USING THE DOCUMENTED METHODS IN THE AWS PYTHON CODE, WHICH
        # DEPENDS ON LOADING THE CONTENTS OF THE FILE INTO MEMORY.  BUT THE CODE DOESN'T WORK, IT
        # TIMES OUT AFTER 20 SECONDS.  SO INSTEAD ABOVE I USE A COUPLE FUNCTIONS FROM THE AWS PYTHON
        # CODE, AND USE PYTHON'S HTTPLIB DIRECTLY TO MAKE THE REQUEST.  I AM LEAVING THIS CODE HERE
        # COMMENTED OUT IN CASE I WANT TO COME BACK TO IT.
        #
        #s3Conn = S3.AWSAuthConnection(
        #    aws_access_key_id="AKIAJBDVX3G6AFAX54KQ",
        #    aws_secret_access_key="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")
        #imageData = uploadedFile.read()  # read the entire file contents into memory
        #print "putting file on s3..., size: " + str(uploadedFile.size)
        #s3Response = s3Conn.put(
        #    bucket="tribble",
        #    key=imageFileName,
        #    object=S3.S3Object(data=imageData, metadata={}),
        #    headers={
        #        "Content-Type": "image/jpeg",
        #        "Content-Length": uploadedFile.size
        #        }
        #    )
        #print "s3Response HTTP response:%s Message:%s" % (s3Response.http_response.status, s3Response.message)

    return HttpResponseRedirect('/glitter/editor/')

def editGlitter(request):
    assetId = int(request.REQUEST.get('assetid', '0'))  # passed in for existing assets
    repoAssetId = int(request.REQUEST.get('repoassetid', '0'))  # passed in to start with the settings from a glitter in the asset repository
    clonedAssetId = int(request.REQUEST.get('clonedassetid', '0'))  # passed in to clone an existing asset to create a new asset
    text = request.POST.get('text', '')
    fontName = request.POST.get('fontname', '')
    try:
        pointSize = int(request.POST.get('pointsize', '0'))
    except:
	    pointSize = 0
    backgroundType = request.POST.get('bgtype', '')
    topBackgroundColor = request.POST.get('topbgcolor', '')
    bottomBackgroundColor = request.POST.get('bottombgcolor', '')
    gradientType = request.POST.get('gradienttype', '')
    fillType = request.POST.get('filltype', '')
    fillColor = request.POST.get('fillcolor', '')
    fillTile = request.POST.get('filltile', '')
    strokeColor = request.POST.get('strokecolor', '')
    try:
        strokeWidth = int(request.POST.get('strokewidth', ''))
    except:
        strokeWidth = 0
    numBlankLinesAboveText = int(request.POST.get('numBlankLinesAboveText', '0'))
    numBlankLinesBelowText = int(request.POST.get('numBlankLinesBelowText', '0'))
    editStage = request.POST.get('editstage', '')
    glitterImageUrl = request.POST.get('glitterimageurl', '')
    glitterFileName = request.POST.get('glitterfilename', '')
    fileSize = int(request.POST.get('filesize', '0'))
    width = int(request.POST.get('width', '0'))
    height = int(request.POST.get('height', '0'))
    pageId = int(request.REQUEST.get('pageid', '0'))    # passed in for adding new glitter to a page
    destination = request.REQUEST.get('dest', '')
    cancelUrl = request.REQUEST.get('cancelurl', '')
    try:
        pageIndex = int(request.REQUEST.get('pi', '0'))
    except:
        pageIndex = 0

    user = userhelper.checkLoggedIn(request)
    
    startingPointSizeForEditingCopiedRepoGlitterAsset = 70

    # Remove leading and trailing carriage returns and line feeds.  The problem with allowing the user to include
    # carriage returns is that it makes it hard for the consumer to replicate the look of the graphic they selected,
    # because they are unaware of the fact that the author included those.  So to prevent this usability issue, we
    # prevent authors from including leading and trailing carriage returns.  Note that we do not strip leading and
    # trailing spaces, because it is ok for the author to include those because it gives an effect of filling out
    # the background to widen the graphic, and its easy enough for the consumer to figure out what's going on.
    if (text):
        text = text.strip("\n\r")

    repoSampleImageUrl = ''
    repoSampleImageWidth = 0
    repoSampleImageHeight = 0

    # Get the existing asset, if any.  Also record if we are starting the edit glitter flow with a repo asset.
    isExistingAsset = False
    isRepoAsset = False
    isClonedAsset = False
    asset = None
    if assetId:
        asset = GlitterAsset(Asset.objects.get(pk=int(assetId)))
        isExistingAsset = True
    elif clonedAssetId:
        asset = GlitterAsset(Asset.objects.get(pk=int(clonedAssetId)))
        isClonedAsset = True
    elif repoAssetId:
        isRepoAsset = True

    # editStage may have one of the following values:
    #   -- empty string: user is viewing the Edit Glitter page in order to create a new glitter image
    #   -- 'validate': user has made an editing change and is submitting it to have the image re-rendered
    #   -- 'confirm': user has viewed the resulting image and has confirmed he or she is really done editing
    #   -- 'reedit': user has viewed the confirmation page and has decided to continue editing some more

    if (isExistingAsset or isClonedAsset) and not editStage:
        glitterImageUrl = asset.getUrl()
        glitterFileName = asset.getFileName()
        fileSize = asset.getFileSize()
        width = asset.getWidth()
        height = asset.getHeight()
        text = asset.getText()
        fontName = asset.getFontName()
        pointSize = asset.getPointSize()
        topBackgroundColor = asset.getTopBackgroundColor()
        bottomBackgroundColor = asset.getBottomBackgroundColor()
        gradientType = asset.getGradientType()
        fillColor = asset.getFillColor()
        fillTile = asset.getFillTile()
        strokeColor = asset.getStrokeColor()
        strokeWidth = asset.getStrokeWidth()
        numBlankLinesAboveText = asset.getNumBlankLinesAboveText()
        numBlankLinesBelowText = asset.getNumBlankLinesBelowText()
    elif isRepoAsset:
        # Get a new unsaved glitter asset that has been unmarshalled with the glitter settings from the asset repository.
        # We are not going to save this glitter asset to the database, instead we are just going to grab its settings and discard it.
        # The repo sample image is used to display to the user when starting the process, but we definitely don't want to
        # save the URL of the repo sample image in the asset.
        (glitterAssetFromRepo, repoSampleImageUrl, repoSampleImageWidth, repoSampleImageHeight) = assethelper.getAssetActorFromRepo(
            repoAssetId=repoAssetId,
            assetType=AssetType.objects.get(asset_type_name='glitter'))

        # Set the local variables to the values from the asset repository
        fontName = glitterAssetFromRepo.getFontName()
        pointSize = glitterAssetFromRepo.getPointSize()
        topBackgroundColor = glitterAssetFromRepo.getTopBackgroundColor()
        bottomBackgroundColor = glitterAssetFromRepo.getBottomBackgroundColor()
        gradientType = glitterAssetFromRepo.getGradientType()
        fillColor = glitterAssetFromRepo.getFillColor()
        fillTile = glitterAssetFromRepo.getFillTile()
        strokeColor = glitterAssetFromRepo.getStrokeColor()
        strokeWidth = glitterAssetFromRepo.getStrokeWidth()
        numBlankLinesAboveText = glitterAssetFromRepo.getNumBlankLinesAboveText()
        numBlankLinesBelowText = glitterAssetFromRepo.getNumBlankLinesBelowText()

        # The text may come in on the query string at the same time that repoAssetId does, so if text is already populated then don't override with the value from the repo.
        print "text: " + text
        if not text:
            text = glitterAssetFromRepo.getText()
            
        # Don't use the repo's numBlankLines settings.  We always start with no blank lines.
        numBlankLinesAboveText = 0
        numBlankLinesBelowText = 0
        
        # Don't use the repo's point size.  We always start with a standard point size.
        pointSize = startingPointSizeForEditingCopiedRepoGlitterAsset
    elif not editStage: # editStage is empty string, which means the user is starting to edit an existing glitter or creating a new glitter image from scratch
        # Set defaults
        fontName = "candice"
        pointSize = 40
        topBackgroundColor = "FFFFFF"
        bottomBackgroundColor = "FFFFFF"
        gradientType = "vertical"
        fillColor = "0000FF"
        fillTile = ""
        strokeColor = "000080"
        strokeWidth = 2
        numBlankLinesAboveText = 0
        numBlankLinesBelowText = 0

    # If not already set, calculate the background type
    if not backgroundType:
        backgroundType = glitterhelper.deriveBackgroundType(topBackgroundColor, bottomBackgroundColor)

    # If not already set, calculate the fill type
    if not fillType:
        fillType = glitterhelper.deriveFillType(fillColor)

    # Once the user confirms the resulting glitter image, then we can create an asset and copy it to S3.
    # We want to reduce needless copies to S3, because they cost money.  So we make the user go through this
    # extra step to confirm that he or she is indeed really done editing.
    if editStage == 'confirm':
        return prepareAndFinalizeGlitterAsset(
            request=request,
            asset=asset,
            isExistingAsset=isExistingAsset,
            pageId=pageId,
            text=text,
            fontName=fontName,
            pointSize=pointSize,
            backgroundType=backgroundType,
            topBackgroundColor=topBackgroundColor,
            bottomBackgroundColor=bottomBackgroundColor,
            gradientType=gradientType,
            fillType=fillType,
            fillColor=fillColor,
            fillTile=fillTile,
            strokeColor=strokeColor,
            strokeWidth=strokeWidth,
            glitterFileName=glitterFileName,
            fileSize=fileSize,
            width=width,
            height=height,
            numBlankLinesAboveText=numBlankLinesAboveText,
            numBlankLinesBelowText=numBlankLinesBelowText,
            )

    errorStr = ""
    if editStage == 'validate':
        if pointSize > 200:
            errorStr = "The Point Size cannot be greater than 200"
        if pointSize < 10:
            errorStr = "The Point Size cannot be less than 10"	
        if pointSize == 0: # pointSize 0 could mean blank point size, see exception handling above
            errorStr = "Please enter a Point Size"
        if strokeWidth > 50:
            errorStr = "The Stroke Width cannot be greater than 50"
        if strokeWidth < 0:
            errorStr = "The Stroke Width cannot be less than 0"
        if text == '':
            errorStr = "Please enter some text"
	
    hasRendered = False   # Indicates whether imagemagick as rendered an image prior to this display of the Edit Glitter page, which is needed because 'confirm' depends on the image already being rendered.

    # Render the glitter if the user has submitted changes (editStage == 'validate') or if the user has
    # selected a repoAssetId for which to base the rendering of their text on.  However, if the user is
    # currently viewing a rendered glitter on the choose glitter page and wants to switch to the
    # advanced editor (dest == 'switchtoadvancededitor') then don't render because it is unnecessary.
    # Likewise if the user is paginating between repo assets (dest == 'paginate') then don't render because
    # it is unnecessary.
    if (editStage == 'validate' and errorStr == "") or (repoAssetId and destination != "switchtoadvancededitor" and destination != "paginate"):
        (glitterFileName, fileSize, width, height) = glitterhelper.renderGlitter(
            text=text,
            fontName=fontName,
            pointSize=pointSize,
            backgroundType=backgroundType,
            topBackgroundColor=topBackgroundColor,
            bottomBackgroundColor=bottomBackgroundColor,
            gradientType=gradientType,
            fillType=fillType,
            fillColor=fillColor,
            fillTile=fillTile,
            strokeColor=strokeColor,
            strokeWidth=strokeWidth,
            numBlankLinesAboveText=numBlankLinesAboveText,
            numBlankLinesBelowText=numBlankLinesBelowText,
            showWatermark=True,
            )
        hasRendered = True
        glitterImageUrl = '/site_media/work/' + glitterFileName

    # If fillType is glitter, then set fillColor to a default color before forwarding to the response page,
    # because that works a little better with the color picker.
    if fillType == 'glitter' and not fillColor:
        fillColor = '8080C0'

    # If we are choosing glitter from the repository, query the repository assets.
    # THIS WILL HAVE TO BE REPLACED WITH A REST CALL TO THE AR TIER ONCE AR IS MOVED TO A DIFFERENT APP.
    repoAssetQuerySet = queryRepoAssets(pageIndex)
    repoAssets = []
    for repoAsset in repoAssetQuerySet:
        repoAssets.append(repoAsset)

    nextIndex = pageIndex + 1
    previousIndex = pageIndex - 1

    # This will suppress the next link on the final page when the final page has fewer than a complete set of items.  If
    # we are unlucky enough to have a full set of items on the last page then unfortunately when the user clicks next then
    # the final page will be empty and will only contain a previous link.
    if repoAssetQuerySet.count() < repoGlitterAssetsPerPage:
	    nextIndex = -1

    if destination == 'chooseglitter':
        responseTemplate = 'glitter/chooseGlitter.html'
    elif destination == 'paginate':
        responseTemplate = 'glitter/chooseGlitter.html'
    else:
        responseTemplate = 'glitter/editGlitter.html'

    return render_to_response (responseTemplate, {
        'assetId': assetId,
        'pageId': pageId,
        'glitterImageUrl': glitterImageUrl,
        'glitterFileName': glitterFileName,
        'fileSize': fileSize,
        'width': width,
        'height': height,
        'repoSampleImageUrl': repoSampleImageUrl,
        'repoSampleImageWidth': repoSampleImageWidth,
        'repoSampleImageHeight': repoSampleImageHeight,
        'repoAssets': repoAssets,
        'repoAssetId': repoAssetId,
        'hasRendered': hasRendered,
        'cancelUrl': cancelUrl,
        'glitterFontList': glitterhelper.glitterFonts,
        'glitterFillList': glitterhelper.glitterFills,
        'text': text,
        'fontName': fontName,
        'pointSize': pointSize,
        'backgroundType': backgroundType,
        'topBackgroundColor': topBackgroundColor,
        'bottomBackgroundColor': bottomBackgroundColor,
        'gradientType': gradientType,
        'fillType': fillType,
        'fillColor': fillColor,
        'fillTile': fillTile,
        'strokeColor': strokeColor,
        'strokeWidth': strokeWidth,
        'numBlankLinesAboveText': numBlankLinesAboveText,
        'numBlankLinesBelowText': numBlankLinesBelowText,
        'user': user,
        'nextIndex': nextIndex,
        'previousIndex': previousIndex,
        'pageIndex': pageIndex,
        'errorStr': errorStr,
        })
	
def prepareAndFinalizeGlitterAsset(request, asset, isExistingAsset, pageId, text, fontName, pointSize,
    backgroundType, topBackgroundColor, bottomBackgroundColor, gradientType, fillType, fillColor, fillTile,
    strokeColor, strokeWidth, glitterFileName, fileSize, width, height,
    numBlankLinesAboveText, numBlankLinesBelowText                            
    ):
    
    # We don't store fillType, so persist only the fillColor or fillTile, but not both.  Otherwise
    # we won't be able to properly derive the fillType upon depersisting the asset.
    if fillType == 'solid':
        fillTile = ''
    elif fillType == 'glitter':
        fillColor = ''

    # We don't store backgroundType, so persist the background colors properly so we can derive it when we depersist.
    if backgroundType == 'solid':
        bottomBackgroundColor = ''
    elif backgroundType == 'transparent':
        topBackgroundColor = ''
        bottomBackgroundColor = ''

    imageFileType = 'gif'

    # Create a new asset, if the user is creating a new asset rather than editing an existing one
    if not isExistingAsset:
        asset = GlitterAsset()

    asset.setUrl(glitterFileName)   # save the glitter file name as the URL, finalizeGlitterAsset() will need it
    asset.setImageFileType(imageFileType)
    asset.setFileSize(fileSize)
    asset.setWidth(width)
    asset.setHeight(height)
    asset.setText(text)
    asset.setFontName(fontName)
    asset.setPointSize(pointSize)
    # We do not store backgroundType, it is derived from the top and bottom background colors
    asset.setTopBackgroundColor(topBackgroundColor)
    asset.setBottomBackgroundColor(bottomBackgroundColor)
    asset.setGradientType(gradientType)
    # We do not store fillType, it is derived from the fill color and tile
    asset.setFillColor(fillColor)
    asset.setFillTile(fillTile)
    asset.setStrokeColor(strokeColor)
    asset.setStrokeWidth(strokeWidth)
    asset.setNumBlankLinesAboveText(numBlankLinesAboveText)
    asset.setNumBlankLinesBelowText(numBlankLinesBelowText)

    result = finalizeGlitterAsset(request, asset)

    print "returning: " + str(result)

    return result

def finalizeGlitterAsset(request, asset, pageId=None):

    user = userhelper.checkLoggedIn(request)
    if not user:
        request.session['glitterAsset'] = asset  # save the glitter asset to the session, we will pick it up after the user logs in.
        return HttpResponseRedirect("/glitter/login/?postlogin=finalizeglitter")

    # If the asset doesn't yet have a user, that means it's a new asset, so set the user.
    if not asset.getUser():
        asset.setUser(user)

    asset.generateAccessKey()  # generate a new access key since we have re-rendered the asset

    # Save the asset
    asset.save()

    existingUrl = asset.getUrl()
    existingFileName = asset.getFileName()  # capture the file name before calling setUrl(), because that will change it

    remoteFileName = str(asset.getAssetId()) + "_" + str(asset.getAccessKey()) + "." + asset.getImageFileType()

    asset.setUrl(imagehelper.getImageUrl(remoteFileName))

    # Save the asset only if its URL has changed (as it would if it is a new asset that has just been saved, because the asset URL includes the asset ID that gets set on the first save)
    if asset.getUrl() != existingUrl:
        # Save the asset again
        asset.save()

    print "putting glitter file on s3, local file name: " + existingFileName

    # Put the file to s3.  This is the UserUploadedImageAsset (NOT the DerivedUserUploadedImageAsset).
    s3helper.putImageToS3(
        contentType=asset.getContentType(),
        fileSize=asset.getFileSize(),
        localFilePathName=glitterhelper.getImageWorkPath() + existingFileName,
        remoteFileName=remoteFileName)

    # Place the glitter on the page, but only if the user provided a pageId.
    # If the user did not provide a pageId, that means the user wants to add the asset to their collection of
    # assets but not place it on a page at this time.
    if pageId:
        page = Page.objects.get(id=pageId)
        placement = AssetPlacement(asset=asset.getAsset(), page=page, top=375, left=325, width=asset.getWidth(), height=asset.getHeight())
        placement.save()
        return HttpResponseRedirect('/glitter/editor/')  # Asset was placed on a page so go to the page editor

    # Asset was not placed on a page, so forward to the glitter detail page rather than the page editor
    return HttpResponseRedirect('/glitter/myglitterdetail/%d/?glittersaved=y' % (asset.getAssetId()))

def assetRepositoryPublish(request):
    assetId = request.REQUEST.get('assetid', '0')
    cancelUrl = request.REQUEST.get('cancelurl', '')
    validateStr = request.POST.get('val', '')

    validate = True if validateStr == "y" else False

    user = userhelper.checkLoggedIn(request)
    if not user:
        return HttpResponse("session has timed out")

    standardRepositoryGlitterText = "Glitter"
    standardRepositoryGlitterPointSize = 60

    asset = Asset.objects.get(id=assetId)

    assetActor = assethelper.getAssetActor(asset)

    if validate:
        if not verifyAssetNotAlreadyInRepository(asset):
            return HttpResponse("That asset already exists in the repository.")
		
        backgroundType = glitterhelper.deriveBackgroundType(assetActor.getTopBackgroundColor(), assetActor.getBottomBackgroundColor())
        fillType = glitterhelper.deriveFillType(assetActor.getFillColor())

        # Render the image for AR.  We render a different image for AR because we want a standard text label rather
        # than the user generated text, and a standard font size.  We also suppress the watermark in the AR image.
        (localFileName, fileSize, width, height) = glitterhelper.renderGlitter(
            text=standardRepositoryGlitterText,
            fontName=assetActor.getFontName(),
            pointSize=standardRepositoryGlitterPointSize,
            backgroundType=backgroundType,
            topBackgroundColor=assetActor.getTopBackgroundColor(),
            bottomBackgroundColor=assetActor.getBottomBackgroundColor(),
            gradientType=assetActor.getGradientType(),
            fillType=fillType,
            fillColor=assetActor.getFillColor(),
            fillTile=assetActor.getFillTile(),
            strokeColor=assetActor.getStrokeColor(),
            strokeWidth=assetActor.getStrokeWidth(),
            numBlankLinesAboveText=0, # Always skip the above and below lines when rendering for AR
            numBlankLinesBelowText=0,
            showWatermark=False,
            )

        imageUrl = ''
        imageFileType = assetActor.getImageFileType()

        repoAsset = RepoAsset()
        repoAsset.setAssetId(asset.id)
        repoAsset.setContributorId(asset.user_id)
        repoAsset.setAssetTypeName(assetActor.getAssetType().asset_type_name)
        repoAsset.setState(asset.state)
        repoAsset.setImageWidth(width)
        repoAsset.setImageHeight(height)
        repoAsset.initializeConsumeCopyCount()  # need to initialize it to zero due to mysql non-null constraint
        repoAsset.save()
        
        # Name the file with the assetId
        remoteFileName = "ar" + str(repoAsset.id) + "." + imageFileType
        #repoAsset.setImageUrl("http://%s.s3.amazonaws.com/%s" % (s3helper.getBucketName(), remoteFileName))
        repoAsset.setImageUrl(imagehelper.getImageUrl(remoteFileName))

        # Copy the rendered image to S3
        s3helper.putImageToS3(
            contentType="image/gif", # I should get this from the asset, but it wasn't working and I took a shortcut.  Here is the old line: asset.getContentType(),
            fileSize=fileSize,
            localFilePathName=glitterhelper.getImageWorkPath() + localFileName,
            remoteFileName=remoteFileName)
	
        # After the file was successfully copied to S3, then save the repo asset.
        repoAsset.save()

        # We used to copy the asset file to be the repo asset file.  But the logic was changed to instead
        # re-render the image file with a standard text label ("Glitter") so that the various fonts have
        # similar sizes and so that we don't have to deal with offensive user-generated content in the
        # images features in the asset repository.
        #
        #print "copying file " + assetActor.getFileName() + " on s3 to file " + remoteFileName + " on s3"
        #s3helper.copyObjectWithinS3(assetActor.getFileName(), remoteFileName)

        # Inform the asset actor that the asset has been added to the repository.  The asset tracks this for informational purposes.
        assetActor.registerAddedToRepository()

        return HttpResponseRedirect('/glitter/myrglitter/?wasadded=y')

    # Some assets (such as glitter) will have an image that we can use to display the asset.  If such
    # an image exists for this asset, then pass it to the view.
    imageUrl = ''
    width = 0
    height = 0
    if isinstance(assetActor, GlitterAsset):
        imageUrl = assetActor.getUrl()
        width = assetActor.getWidth()
        height = assetActor.getHeight()
        
    return render_to_response ('glitter/repositoryPublish.html', {
        'assetId': assetId,
        'cancelUrl': cancelUrl,
        'imageUrl': imageUrl,
        'width': width,
        'height': height
        })

def verifyAssetNotAlreadyInRepository(asset):

    # Get all repo assets that were added from this assetId.  The assetId may have been added multiple times,
    # because if an asset is added to the repository then subsequently edited in the user's asset collection,
    # then it can be added to the repository again.
    repoAssetQuerySet = RepoAsset.objects.filter(asset_id=asset.id)

    # Iterate through all matching repository assets and see if the asset state is an exact match.
    # If there is an exact match, that means the asset would be a duplicate in the repository, which we
    # don't want, so we fail the verification.
    for repoAsset in repoAssetQuerySet:
        if repoAsset.state == asset.state:
            return False
    
    return True  # true means the verification passed, the asset does not already exist in the repository

def viewGlitterAssets(request):
    user = userhelper.checkLoggedIn(request)
    if not user:
        return HttpResponse("session has timed out")

    glitterAssets = []

    assetQuerySet = Asset.objects.filter(user=user, asset_type=assethelper.getAssetType('glitter')).order_by('-creation_date')

    for asset in assetQuerySet:
        glitterAssets.append(GlitterAsset(asset))

    return render_to_response("glitter/viewGlitterAssets.html", {
        'glitterAssets': glitterAssets,
        'user': user
        })

def viewGlitterAssetDetail(request, assetId=None):
    wasGlitterSavedStr = request.REQUEST.get('glittersaved', '')

    user = userhelper.checkLoggedIn(request)
    if not user:
        return HttpResponse("session has timed out")

    wasGlitterSaved = True if wasGlitterSavedStr == "y" else False

    if not assetId:  # read the query string only if assetId not passed in as a parameter
        assetId = request.REQUEST.get('assetid', '0')

    glitterAsset = GlitterAsset(Asset.objects.get(id=assetId))

    return render_to_response("glitter/viewGlitterAssetDetail.html", {
        'glitterAsset': glitterAsset,
        'wasGlitterSaved': wasGlitterSaved
        })

def queryRepoAssets(pageIndex):
    return RepoAsset.objects.filter(asset_type_name='glitter').order_by('-consume_copy_count')[pageIndex * repoGlitterAssetsPerPage:pageIndex * repoGlitterAssetsPerPage + repoGlitterAssetsPerPage] # the leading hyphen means order by DESCENDING
	
def viewGlitterRepoAssets(request):
    pageIndex = int(request.REQUEST.get('pi', '0'))
    text = request.REQUEST.get('text', '')

    user = userhelper.checkLoggedIn(request)

    repoAssetQuerySet = queryRepoAssets(pageIndex)

    repoAssets = []

    for repoAsset in repoAssetQuerySet:
        repoAssets.append(repoAsset)

    nextIndex = pageIndex + 1
    previousIndex = pageIndex - 1

    # This will suppress the next link on the final page when the final page has fewer than a complete set of items.  If
    # we are unlucky enough to have a full set of items on the last page then unfortunately when the user clicks next then
    # the final page will be empty and will only contain a previous link.
    if repoAssetQuerySet.count() < repoGlitterAssetsPerPage:
	    nextIndex = -1

    return render_to_response("glitter/chooseGlitterLanding.html", {
        'repoAssets': repoAssets,
        'user': user,
        'nextIndex': nextIndex,
        'previousIndex': previousIndex,
        'text': text,
        })

def viewUserGlitterRepoAssets(request):
    wasAssetAddedStr = request.REQUEST.get('wasadded', '')

    user = userhelper.checkLoggedIn(request)

    wasAssetAdded = True if wasAssetAddedStr == "y" else False

    repoAssetQuerySet = RepoAsset.objects.filter(asset_type_name='glitter', contributor_id=user.id).order_by('-creation_date')  # the leading hyphen means order by DESCENDING

    repoAssets = []

    for repoAsset in repoAssetQuerySet:
        repoAssets.append(repoAsset)
        
    return render_to_response("glitter/viewUserGlitterRepoAssets.html", {
        'repoAssets': repoAssets,
        'wasAssetAdded': wasAssetAdded
        })

