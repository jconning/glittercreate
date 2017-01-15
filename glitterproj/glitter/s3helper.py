import httplib
import time
from glitterproj import S3

bucketName = "tribble" # development
#bucketName = "images.glittercreate.com" # production
awsAccessKey = "TODO"
awsSecretAccessKey = "TODO"

def getBucketName():
    return bucketName

def putImageToS3(contentType, fileSize, localFilePathName, remoteFileName):

    if not localFilePathName:
        raise ValueError, 'localFilePathName: ' + localFilePathName
    if not remoteFileName:
        raise ValueError, 'remoteFileName: ' + remoteFileName
    if not fileSize:
        raise ValueError, 'fileSize: ' + str(fileSize)
    if not contentType:
        raise ValueError, 'contentType: ' + contentType

    headers = {
        'Content-Type': contentType,
        'Content-Length': str(fileSize),
        'Date': time.strftime("%a, %d %b %Y %X GMT", time.gmtime()),
        'x-amz-acl': 'public-read'
        }

    canonicalString = S3.canonical_string(
        method="PUT",
        bucket=bucketName,
        key=remoteFileName,
        query_args={},
        headers=headers
        )

    headers['Authorization'] = \
        "AWS %s:%s" % (awsAccessKey, S3.encode(awsSecretAccessKey, canonicalString))

    print headers

    s3Conn = httplib.HTTPConnection(bucketName + ".s3.amazonaws.com:80")

    print "opening local file for reading: " + localFilePathName

    # Open the local image file for reading
    imageFile = open(localFilePathName, 'rb')

    print "calling request..."
    s3Conn.request("PUT", "/" + remoteFileName, imageFile, headers)

    print "getting response..."
    response = s3Conn.getresponse()

    print response.status, response.reason, response.getheaders(), response.read()

    s3Conn.close()
    
    imageFile.close()

    return

def copyObjectWithinS3(srcFileName, destFileName):

    headers = {
        'x-amz-copy-source': "/" + getBucketName() + "/" + srcFileName,
        'Date': time.strftime("%a, %d %b %Y %X GMT", time.gmtime()),
        'x-amz-acl': 'public-read'
        }

    canonicalString = S3.canonical_string(
        method="PUT",
        bucket=bucketName,
        key=destFileName,
        query_args={},
        headers=headers
        )

    headers['Authorization'] = \
        "AWS %s:%s" % (awsAccessKey, S3.encode(awsSecretAccessKey, canonicalString))

    print headers

    s3Conn = httplib.HTTPConnection(bucketName + ".s3.amazonaws.com:80")

    print "calling request..."
    s3Conn.request("PUT", "/" + destFileName, None, headers)

    print "getting response..."
    response = s3Conn.getresponse()

    print response.status, response.reason, response.getheaders(), response.read()

    s3Conn.close()

    return
