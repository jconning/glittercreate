import subprocess

#imageMagickPath = "C:/Program Files/ImageMagick-6.5.6-Q16/"
imageMagickPath = "/opt/local/bin/"

def getImageMagickPath():
    return imageMagickPath

def readImageAttributes(fileName):
    # Invoke the imagemagick command 'identify' to quickly read the image width, height, and format.
    # The identify command will read the image information from the image header, so that it doesn't
    # need to read in the entire image.
    imOutput = subprocess.Popen([
        imageMagickPath + "identify",
        "-format",
        '%w %h %m,',  # output the width, height, and image format.  Include delimeter to assist with animated gif output.
        fileName
        ], stdout=subprocess.PIPE).communicate()[0]

    imOutput = imOutput.split(',')[0].rstrip() # grab only the first frame of an animated gif, and chop off the trailing line feed
    print "imOutput: " + imOutput

    (width, height, imageFormat) = imOutput.split(' ')

    width = int(width)
    height = int(height)
    
    print "width:%s height:%s format:%s" % (width, height, imageFormat)

    # Calculate the content type and image file type from the ImageMagick image format (JPEG, etc)
    if imageFormat == 'JPEG':
        contentType = 'image/jpeg'
        imageFileType = 'jpg'
    else:
        contentType = 'unknown'
        imageFileType = 'unknown'

    return (width, height, imageFileType, contentType)

def resize(srcFileName, destFileName, width, height):
    # Invoke the imagemagick command 'convert' to resize the file such that both
    # the width and height will be equal to or less than the passed in parameters,
    # and aspect ratio will be preserved.
    imOutput = subprocess.Popen([
        imageMagickPath + "convert",
        srcFileName,
        "-resize",
        "%dx%d" % (width, height),
        destFileName
        ], stdout=subprocess.PIPE).communicate()[0]
    print "imOutput: " + imOutput
    return

    
