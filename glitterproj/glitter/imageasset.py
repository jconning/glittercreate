from glitter.assetactor import AssetActor
from glitter.models import Asset
from glitter.models import AssetType
from xml.dom.minidom import getDOMImplementation
from xml.dom.minidom import parseString

class UserUploadedImageAsset(AssetActor):
    def setUrl(self, url):
        self.url = url
        return
    def setImageFileType(self, imageFileType):
        self.imageFileType = imageFileType
        return
    def setSize(self, size):
        self.size = size;
        return
    def setWidth(self,width):
        self.width = width;
        return
    def setHeight(self,height):
        self.height = height;
        return
    def setOriginalFileName(self,originalFileName):
        self.originalFileName = originalFileName;
        return
    def getAssetType(self):
        return AssetType.objects.get(asset_type_name='userUploadedImage')
    def getWidth(self):
        return self.width
    def getHeight(self):
        return self.height
    def getUrl(self):
        return self.url
    def marshal(self):
        if not self.asset:
            self.asset = Asset(
                user=self.user,
                asset_type=self.getAssetType()
                )

        domImpl = getDOMImplementation()
        doc = domImpl.createDocument(None, "userUploadedImageAsset", None)

        self.addTextElement(doc, 'url', self.url)
        self.addTextElement(doc, 'imageFileType', self.imageFileType)
        self.addTextElement(doc, 'size', str(self.size))
        self.addTextElement(doc, 'width', str(self.width))
        self.addTextElement(doc, 'height', str(self.height))
        self.addTextElement(doc, 'originalFileName', str(self.originalFileName))

        self.asset.state = doc.toxml()

        return
    def unmarshal(self):
        doc = parseString(self.asset.state)

        self.url = self.getElementValue(doc, 'url')
        self.imageFileType = self.getElementValue(doc, 'imageFileType')
        self.size = self.getElementValue(doc, 'size')
        self.width = self.getElementValue(doc, 'width')
        self.height = self.getElementValue(doc, 'height')
        self.originalFileName = self.getElementValue(doc, 'originalFileName')

        return
    def render(self, assetPlacement, isEdit=False):

        innerContent = '<img border=0 src="%s">' % (self.url)

        return AssetActor.render(self, assetPlacement, innerContent, isEdit)
    
