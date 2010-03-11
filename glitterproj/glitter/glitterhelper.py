import subprocess
import os.path
import os
import time
import random
from glitterproj.glitter import imhelper

#fontPath = "C:/piczofontsandfills/fonts/"
#fillPath = "C:/piczofontsandfills/fills/"
#imageWorkPath = "C:/daDjangoProject/siteMedia/work/"
fontPath = "/Users/jimconning/daDjangoProject/fonts/"
fillPath = "/Users/jimconning/daDjangoProject/siteMedia/fills/"
imageWorkPath = "/Users/jimconning/daDjangoProject/siteMedia/work/"

glitterFonts = [
    'rm/AdvertRegular',
    'rm/BlackCastleMF',
    'rm/BodieMFFlag',
    'rm/CasualMarkerMF',
    'rm/ClubMF',
    'rm/EarthquakeMF',
    'rm/Flames',
    'rm/HayStackMFWide',
    'rm/Kompakt',
    'rm/MamaRegular',
    'rm/PaintPeelInitials',
    'rm/Sixties',
    'rm/StarshineMF',
    'rm/TamboScript',
    'rm/Titania',
    'rm/TuscanMFNarrow',
    'rm/Vassar',
    '11d/08Underground',
    '11d/5cent',
    '11d/bboy',
    '11d/cancontrol',
    '11d/cigar',
    '11d/homeboy',
    '11d/konfekt',
    #'11d/subway', COMMENTED OUT BECAUSE TOO MUCH SPACE WASTED BELOW THE LETTERS
    '11d/vinterstad',
    '11d/whoa',
    #'11d/writers2', COMMENTED OUT BECAUSE TOO MUCH SPACE WASTED BELOW THE LETTERS
    '11d/writers3',
    '11d/writers_original',  # I'm on the verge of yanking this one for too much space below the letters, but it is a really good font and complement to the other graffiti fonts so for now I am leaving it in.
    ]
    
lowerCaseOnlyFonts = { # This is a subset of glitterFonts.  Some fonts support lower case only.  For these, we need to convert the text to all lower case before rendering.
    '11d/08Underground': True,
    '11d/5cent': True,
    '11d/bboy': True,
    '11d/cancontrol': True,
    '11d/homeboy': True,
    '11d/konfekt': True,
    '11d/subway': True,
    '11d/vinterstad': True,
    '11d/whoa': True,
    '11d/writers2': True,
    '11d/writers3': True,
    '11d/writers_original': True,
    }

glitterFills = [
    'dd/gf_12.gif',
    'dd/gf_13.gif',
    'dd/gf_14.gif',
    'dd/gf_15.gif',
    'dd/gf_16.gif',
    'dd/gf_2.gif',
    'dd/gf_21.gif',
    'dd/gf_22.gif',
    'dd/gf_24.gif',
    'dd/gf_26.gif',
    'dd/gf_27.gif',
    'dd/gf_29.gif',
    'dd/gf_3.gif',
    'dd/gf_31.gif',
    'dd/gf_32.gif',
    'dd/gf_35.gif',
    'dd/gf_38.gif',
    'dd/gf_39.gif',
    'dd/gf_40.gif',
    'dd/gf_41.gif',
    'dd/gf_42.gif',
    'dd/gf_46.gif',
    'dd/gf_47.gif',
    'dd/gf_52.gif',
    'dd/gf_56.gif',
    'dd/gf_58.gif',
    'dd/gf_66.gif',
    'dd/gf_69.gif',
    'dd/gf_71.gif',
    'dd/gf_72.gif',
    'dd/gf_73.gif',
    'dd/gf_74.gif',
    'dd/gf_99.gif',
    ]

def getImageWorkPath():
    return imageWorkPath

def deriveBackgroundType(topBackgroundColor, bottomBackgroundColor):
    if not topBackgroundColor and not bottomBackgroundColor:
        backgroundType = 'transparent'
    elif not bottomBackgroundColor:
        backgroundType = 'solid'
    elif topBackgroundColor != bottomBackgroundColor:
        backgroundType = 'gradient'
    else:
        backgroundType = 'solid'
    return backgroundType

def deriveFillType(fillColor):
    if fillColor:
        fillType = 'solid'
    else:
        fillType = 'glitter'
    return fillType

def renderGlitter(text, fontName, pointSize, backgroundType, topBackgroundColor, bottomBackgroundColor, gradientType,
    fillType, fillColor, fillTile, strokeColor, strokeWidth, numBlankLinesAboveText, numBlankLinesBelowText,
    showWatermark):

    for line in range(numBlankLinesAboveText):
        text = "\n" + text
    for line in range(numBlankLinesBelowText):
        text += "\n"
        
    # If the chosen font is one that does not support upper case letters, then convert the text to lower case.
    print "value: "
    print lowerCaseOnlyFonts.get(fontName)
    if lowerCaseOnlyFonts.get(fontName):
        text = text.lower()

    # The structure of the operations is different for solid color fills, so we go to a specific method to handle those.
    if fillType == 'solid':
        return renderGlitterSolidFill(text, fontName, pointSize, backgroundType, topBackgroundColor,
            bottomBackgroundColor, gradientType, fillColor, strokeColor, strokeWidth, showWatermark)

    # Construct a working file name that is composed of the time and a random number
    workingFileName = str(time.time()) + "_" + str(random.randint(1, 99999))

    textMaskFile = imageWorkPath + "textmask" + workingFileName + ".gif"
    glitterMaskedFile = imageWorkPath + "glittermask" + workingFileName + ".gif"
    glitterDoneFile = "TEMPORARY_URL_" + workingFileName + ".gif"  # name it TEMPORARY_URL to disuade the user from hot linking to this temporarily hosted image
    glitterDonePathFile = imageWorkPath + glitterDoneFile

    if gradientType == 'radial':
        gradientKeyword = 'radial-gradient'
    else:
        gradientKeyword = 'gradient'

    # Render the text to an image that we will subsequently use to mask the glitter.
    # EXAMPLE: convert -background black -fill white -font fonts\candice.ttf -pointsize 80 -gravity center label:"Jim\nwas\nhere" glitter_mask.gif
    args = [imhelper.getImageMagickPath() + "convert"]
    args += ["-background", "black"]
    args += ["-fill", "white"]
    args += ["-font", fontPath + fontName + ".ttf"]
    args += ["-pointsize", str(pointSize)]
    if strokeWidth > 0:
        args += ["-stroke", "white"]
        args += ["-strokewidth", str(strokeWidth)]
    args += ["label:" + text]
    args += [textMaskFile]

    print args

    # Invoike imagemagick command line
    imOutput = subprocess.Popen(args, stdout=subprocess.PIPE).communicate()[0]

    # Get the width and height of the rendered image
    (width, height, imageFileType, contentType) = imhelper.readImageAttributes(textMaskFile)

    # Mask the glitter animation.   
    # EXAMPLE: convert ( fills\gold_glitter.gif -virtual-pixel tile -set option:distort:viewport 149x259 -distort SRT 0 ) -coalesce null: glitter_mask.gif +matte -compose CopyOpacity -layers composite glitter_masked.gif
    args = [imhelper.getImageMagickPath() + "convert"]
    args += ["(", fillPath + fillTile]
    args += ["-virtual-pixel", "tile"]
    args += ["-set", "option:distort:viewport", "%dx%d" % (width, height)]  # tile the animation to cover the area that the text is rendered to
    args += ["-distort", "SRT", "0", ")"]
    args += ["-coalesce"]  # de-optimize the glitter animation, otherwise it will look bad
    args += ["null:", textMaskFile]
    args += ["+matte", "-compose", "CopyOpacity"]
    args += ["-layers", "composite"]  # this is the main operation: layers composite
    args += [glitterMaskedFile]  # output file

    print args

    # Invoke imagemagick command line
    imOutput = subprocess.Popen(args, stdout=subprocess.PIPE).communicate()[0]

    # Layer the background under the masked text and the stroke over it.
    # EXAMPLE: convert glitter_masked.gif -size 149x259 null: gradient:gold1-gold4 -compose DstOver -layers composite null: ( -fill none -background none -stroke white -strokewidth 2 -font fonts\candice.ttf -gravity center -pointsize 80 label:"Jim\nwas\nhere" ) -compose over -layers composite glittered_letter.gif
    args = [imhelper.getImageMagickPath() + "convert"]
    args += [glitterMaskedFile]
    args += ["-size", "%dx%d" % (width, height)]
    args += ["null:"]
    if backgroundType == "solid":
        args += ["%s:#%s-#%s" % (gradientKeyword, topBackgroundColor, topBackgroundColor)]  # should be replaced with a "-background color" tag or likewise (can't figure out how to do it right now)
    elif backgroundType == "gradient":
        args += ["%s:#%s-#%s" % (gradientKeyword, topBackgroundColor, bottomBackgroundColor)]
    if backgroundType != "transparent":  # skip this layer for transparent backgrounds (the source image already has a transparent background)
        args += ["-compose", "DstOver"]
        args += ["-layers", "composite"]
        args += ["null:"]
    args += ["("]
    args += ["-fill", "none"]
    args += ["-background", "none"]
    if strokeWidth > 0:
        args += ["-stroke", "#" + strokeColor]
        args += ["-strokewidth", str(strokeWidth)]
    args += ["-font", fontPath + fontName + ".ttf"]
    args += ["-pointsize", str(pointSize)]
    args += ["label:" + text]
    args += [")"]
    args += ["-compose", "over"]
    args += ["-layers", "composite"]

    # Render the watermark
    if showWatermark:
        # I was going to set it up so that larger fonts get the watermark inside the image, and smaller fonts get
        # it appended below.  But I didn't resolve how to choose which watermark text color to use when the glitter
        # background is a solid color.  So, for now the watermark-inside logic is disabled.
        if False:
            if backgroundType == "transparent":
                watermarkColor = "#808080"
            elif backgroundType == "gradient":
                watermarkColor = "#" + topBackgroundColor
            else:
                watermarkColor = "#808080"  
            args += ["null:"]
            args += ["("]
            args += ["-fill", watermarkColor]
            args += ["-pointsize", "12"]
            args += ["-stroke", "none"]
            args += ["-font", "/Library/Fonts/Arial.ttf"]
            args += ["-gravity", "SouthEast"]
            args += ["label:GlitterCreate.com"]
            args += [")"]
            args += ["-compose", "over"]
            args += ["-layers", "composite"]
        else:
            args += ["null:"]
            args += ["("]
            args += ["-clone", "0"]
            args += ["-coalesce"]
            args += ["-gravity", "SouthEast"]
            args += ["-splice", "0x13"]
            args += ["-pointsize", "11"]
            args += ["-stroke", "none"]
            if pointSize < 30:
                args += ["-font", "/Library/Fonts/Arial Narrow.ttf"]
            else:
                args += ["-font", "/Library/Fonts/Arial.ttf"]
            args += ["-fill", "#404040"]
            args += ["-annotate", "+0+0", "GlitterCreate.com"]
            args += [")"]
            args += ["-swap", "-1,0"]
            args += ["+delete"]

    args += [glitterDonePathFile]  # output file

    print args

    # Invoke imagemagick command line
    imOutput = subprocess.Popen(args, stdout=subprocess.PIPE).communicate()[0]

    # Get the width and height of the rendered image
    (width, height, imageFileType, contentType) = imhelper.readImageAttributes(glitterDonePathFile)
    fileSize = os.path.getsize(glitterDonePathFile)

    # Clean up temporary files
    os.remove(textMaskFile)
    os.remove(glitterMaskedFile)

    return glitterDoneFile, fileSize, width, height

def renderGlitterSolidFill(text, fontName, pointSize, backgroundType, topBackgroundColor,
    bottomBackgroundColor, gradientType, fillColor, strokeColor, strokeWidth, showWatermark):
    
    wasTextSizeFileCreated = False
    wasWatermarkFileCreated = False

    # Construct a working file name that is composed of the time and a random number
    workingFileName = str(time.time()) + "_" + str(random.randint(1, 99999))

    textSizeFile = imageWorkPath + "textsize" + workingFileName + ".gif"
    preWatermarkFile = imageWorkPath + "prewater" + workingFileName + ".gif"
    glitterFile = "TEMPORARY_URL_" + workingFileName + ".gif"  # name it TEMPORARY_URL to disuade the user from hot linking to this temporarily hosted image
    glitterPathFile = imageWorkPath + glitterFile

    if gradientType == 'radial':
        gradientKeyword = 'radial-gradient'
    else:
        gradientKeyword = 'gradient'

    # If a gradient is being used, we need to render the text first to determine its size, because gradient has to know the size up front.
    if backgroundType == 'gradient':
        args = [imhelper.getImageMagickPath() + "convert"]
        args += ["-font", fontPath + fontName + ".ttf"]
        args += ["-pointsize", str(pointSize)]
        if strokeWidth > 0:
            args += ["-stroke", "#" + strokeColor]
            args += ["-strokewidth", str(strokeWidth)]
        args += ["label:" + text]
        args += [textSizeFile]  # output file

        # Invoike imagemagick command line
        imOutput = subprocess.Popen(args, stdout=subprocess.PIPE).communicate()[0]
        wasTextSizeFileCreated = True

        # Get the width and height of the rendered image
        (width, height, imageFileType, contentType) = imhelper.readImageAttributes(textSizeFile)

    # Render the text from scratch, passing in the size if this is a gradient.
    args = [imhelper.getImageMagickPath() + "convert"]
    if backgroundType == 'solid':
        args += ["-background", "#" + topBackgroundColor]
    elif backgroundType == 'gradient':
        args += ["-size", "%dx%d" % (width, height)]
        args += ["%s:#%s-#%s" % (gradientKeyword, topBackgroundColor, bottomBackgroundColor)]
        args += ["-background", "none"]
    else:
        args += ["-background", "none"]
    args += ["-fill", "#" + fillColor]
    args += ["-font", fontPath + fontName + ".ttf"]
    args += ["-pointsize", str(pointSize)]
    if strokeWidth > 0:
        args += ["-stroke", "#" + strokeColor]
        args += ["-strokewidth", str(strokeWidth)]
    args += ["label:" + text]
    if backgroundType == 'gradient':
        args += ["-composite"]

    # name of output file
    if showWatermark:
        args += [preWatermarkFile]
        wasWatermarkFileCreated = True
    else:
        args += [glitterPathFile]

    # Invoike imagemagick command line
    imOutput = subprocess.Popen(args, stdout=subprocess.PIPE).communicate()[0]

    if showWatermark:
        # Render the watermark below the image
        args = [imhelper.getImageMagickPath() + "convert"]
        args += [preWatermarkFile]
        args += ["-background", "none"]
        args += ["-gravity", "SouthEast"]
        args += ["-pointsize", "11"]
        if pointSize < 30:
            args += ["-font", "/Library/Fonts/Arial Narrow.ttf"]
        else:
            args += ["-font", "/Library/Fonts/Arial.ttf"]
        args += ["-fill", "#404040"]
        args += ["label:GlitterCreate.com"]
        args += ["-append"]
        args += [glitterPathFile]

        imOutput = subprocess.Popen(args, stdout=subprocess.PIPE).communicate()[0]

    # Get the width and height of the rendered image
    (width, height, imageFileType, contentType) = imhelper.readImageAttributes(glitterPathFile)
    fileSize = os.path.getsize(glitterPathFile)

    # Clean up temporary files
    if wasTextSizeFileCreated:
        os.remove(textSizeFile)
    if wasWatermarkFileCreated:
        os.remove(preWatermarkFile)

    return glitterFile, fileSize, width, height

