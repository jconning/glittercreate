from glitterproj.glitter import s3helper

def getImageUrl(imageFileName):
    if (s3helper.getBucketName() == 'tribble'):
        return "http://%s.s3.amazonaws.com/%s" % (s3helper.getBucketName(), imageFileName)
    return "http://images.glittercreate.com/%s" % (imageFileName)
