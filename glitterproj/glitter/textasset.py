from glitter.assetactor import AssetActor
from glitter.models import Asset
from glitter.models import AssetType
from xml.dom.minidom import getDOMImplementation
from xml.dom.minidom import parseString

class TextAsset(AssetActor):
    def setTextContent(self, textContent):
        self.textContent = textContent
        return
    def getAssetType(self):
        return AssetType.objects.get(asset_type_name='text')
    def getTextContent(self):
        return self.textContent
    def getBackgroundColor(self):
        return self.backgroundColor
    def marshal(self):
        if not self.asset:
            self.asset = Asset(
                user=self.user,
                asset_type=self.getAssetType()
                )

        domImpl = getDOMImplementation()
        doc = domImpl.createDocument(None, "textAsset", None)

        self.addTextElement(doc, 'text', self.textContent)
        self.addTextElement(doc, 'bgColor', self.backgroundColor)

        self.asset.state = doc.toxml()

        return
    def unmarshal(self):
        doc = parseString(self.asset.state)

        self.textContent = self.getElementValue(doc, 'text')
        self.backgroundColor = self.getElementValue(doc, 'bgColor')

        return
    def render(self, assetPlacement, isEdit=False):

        innerContent = self.textContent

        innerContent += \
            '\n<br><a href="/glitter/edittext/?assetid=%d">edit text</a>' % (self.asset.id)
            
        return AssetActor.render(self, assetPlacement, innerContent, isEdit)
