import random
from glitter.assetactor import AssetActor
from glitter.models import Asset
from glitter.models import AssetType
from xml.dom.minidom import getDOMImplementation
from xml.dom.minidom import parseString

class GlitterAsset(AssetActor):
    def setUrl(self, url):
        self.url = url
        return
    def setImageFileType(self, imageFileType):
        self.imageFileType = imageFileType
        return
    def setAccessKey(self, accessKey):
        self.accessKey = accessKey
        return
    def generateAccessKey(self):
        self.accessKey = random.randint(1, 99999)
        return
    def setFileSize(self, fileSize):
        self.fileSize = fileSize
        return
    def setWidth(self, width):
        self.width = width
        return
    def setHeight(self, height):
        self.height = height
        return
    def setText(self, text):
        self.text = text
        return
    def setFontName(self, fontName):
        self.fontName = fontName
        return
    def setPointSize(self, pointSize):
        self.pointSize = pointSize
        return
    def setTopBackgroundColor(self, topBackgroundColor):
        self.topBackgroundColor = topBackgroundColor
        return
    def setBottomBackgroundColor(self, bottomBackgroundColor):
        self.bottomBackgroundColor = bottomBackgroundColor
        return
    def setGradientType(self, gradientType):
        self.gradientType = gradientType
        return
    def setFillColor(self, fillColor):
        self.fillColor = fillColor
        return
    def setFillTile(self, fillTile):
        self.fillTile = fillTile
        return
    def setStrokeColor(self, strokeColor):
        self.strokeColor = strokeColor
        return
    def setStrokeWidth(self, strokeWidth):
        self.strokeWidth = strokeWidth
        return
    def setNumBlankLinesAboveText(self, numBlankLinesAboveText):
        self.numBlankLinesAboveText = numBlankLinesAboveText
        return
    def setNumBlankLinesBelowText(self, numBlankLinesBelowText):
        self.numBlankLinesBelowText = numBlankLinesBelowText
        return
    def getAssetType(self):
        return AssetType.objects.get(asset_type_name='glitter')
    def getWidth(self):
        return int(self.width)
    def getHeight(self):
        return int(self.height)
    def getUrl(self):
        return self.url
    def getFileName(self):
        return self.url.split('/')[-1]
    def getFileSize(self):
        return int(self.fileSize)
    def getAccessKey(self):
        if not self.accessKey:
            return 0
        return int(self.accessKey)
    def getImageFileType(self):
        return self.imageFileType
    def getContentType(self):
        if self.imageFileType == 'gif':
            return "image/gif"
        else:
            return "unknown"
    def getText(self):
        return self.text
    def getFontName(self):
        return self.fontName
    def getPointSize(self):
        return int(self.pointSize)
    def getTopBackgroundColor(self):
        return self.topBackgroundColor
    def getBottomBackgroundColor(self):
        return self.bottomBackgroundColor
    def getGradientType(self):
        return self.gradientType
    def getFillColor(self):
        return self.fillColor
    def getFillTile(self):
        return self.fillTile
    def getStrokeColor(self):
        return self.strokeColor
    def getStrokeWidth(self):
        if not (self.strokeWidth):
            return 0
        return int(self.strokeWidth)
    def getNumBlankLinesAboveText(self):
        if not (self.numBlankLinesAboveText):
            return 0
        return int(self.numBlankLinesAboveText)
    def getNumBlankLinesBelowText(self):
        if not (self.numBlankLinesBelowText):
            return 0
        return int(self.numBlankLinesBelowText)
    def marshal(self):
        if not self.asset:
            self.asset = Asset(
                user=self.user,
                asset_type=self.getAssetType()
                )

        domImpl = getDOMImplementation()
        doc = domImpl.createDocument(None, "glitterAsset", None)

        self.addTextElement(doc, 'url', self.url)
        self.addTextElement(doc, 'imageFileType', self.imageFileType)
        self.addTextElement(doc, 'accessKey', str(self.accessKey))
        self.addTextElement(doc, 'fileSize', str(self.fileSize))
        self.addTextElement(doc, 'width', str(self.width))
        self.addTextElement(doc, 'height', str(self.height))
        self.addTextElement(doc, 'text', self.text)
        self.addTextElement(doc, 'fontName', self.fontName)
        self.addTextElement(doc, 'pointSize', str(self.pointSize))
        self.addTextElement(doc, 'topBgColor', str(self.topBackgroundColor))
        self.addTextElement(doc, 'bottomBgColor', str(self.bottomBackgroundColor))
        self.addTextElement(doc, 'gradientType', str(self.gradientType))
        self.addTextElement(doc, 'fillColor', str(self.fillColor))
        self.addTextElement(doc, 'fillTile', str(self.fillTile))
        self.addTextElement(doc, 'strokeColor', str(self.strokeColor))
        self.addTextElement(doc, 'strokeWidth', str(self.strokeWidth))
        self.addTextElement(doc, 'numBlankLinesAboveText', str(self.numBlankLinesAboveText))
        self.addTextElement(doc, 'numBlankLinesBelowText', str(self.numBlankLinesBelowText))

        self.asset.state = doc.toxml()

        return
    def unmarshal(self):
        doc = parseString(self.asset.state)

        self.url = self.getElementValue(doc, 'url')
        self.imageFileType = self.getElementValue(doc, 'imageFileType')
        self.accessKey = self.getElementValue(doc, 'accessKey')
        self.fileSize = self.getElementValue(doc, 'fileSize')
        self.width = self.getElementValue(doc, 'width')
        self.height = self.getElementValue(doc, 'height')
        self.text = self.getElementValue(doc, 'text')
        self.fontName = self.getElementValue(doc, 'fontName')
        self.pointSize = self.getElementValue(doc, 'pointSize')
        self.topBackgroundColor = self.getElementValue(doc, 'topBgColor')
        self.bottomBackgroundColor = self.getElementValue(doc, 'bottomBgColor')
        self.gradientType = self.getElementValue(doc, 'gradientType')
        self.fillColor = self.getElementValue(doc, 'fillColor')
        self.fillTile = self.getElementValue(doc, 'fillTile')
        self.strokeColor = self.getElementValue(doc, 'strokeColor')
        self.strokeWidth = self.getElementValue(doc, 'strokeWidth')
        self.numBlankLinesAboveText = self.getElementValue(doc, 'numBlankLinesAboveText')
        self.numBlankLinesBelowText = self.getElementValue(doc, 'numBlankLinesBelowText')

        return
    def render(self, assetPlacement, isEdit=False):

        innerContent = '<img border=0 src="%s">' % (self.url)

        innerContent += \
            '\n<br><a href="/glitter/editglitter/?assetid=%d">edit glitter</a>' % (self.asset.id)

        innerContent += \
            '\n<a href="/glitter/repopublish/?assetid=%d">publish</a>' % (self.asset.id)

        return AssetActor.render(self, assetPlacement, innerContent, isEdit)
    

