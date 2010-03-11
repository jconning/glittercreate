import datetime

class AssetActor:
    def __init__(self, asset=None):
        self.asset = asset
        self.assetId = None
        self.user = None
        self.backgroundColor = None
        if asset:
            self.unmarshal()
            self.assetId = asset.id
        return
    def setAsset(self, asset):
        self.asset = asset
        self.unmarshal()  # this method to be implemented in subclass
        return
    def setUser(self, user):
        self.user = user
        return
    def setBackgroundColor(self, backgroundColor):
        self.backgroundColor = backgroundColor
        return
    def registerAddedToRepository(self):
        self.asset.last_added_to_repo_date = datetime.datetime.now()  # We track when the asset was added to the repository so the application can prevent the user from added the same asset over and over again.
        self.asset.save()
    def getLastAddedToRepoDate(self):
        return self.asset.last_added_to_repo_date
    def getAsset(self):
        return self.asset
    def getAssetId(self):
        return self.asset.id
    def getAssetType(self):  # override in subclass
        return None
    def getUser(self):
        return self.user
    def getElementValue(self, document, tagName):  # called by subclass (utility method for use by subclass)
        try:
            element = document.getElementsByTagName(tagName)[0]
            return element.childNodes[0].data
        except IndexError:
            return ''
    def addTextElement(self, document, elementName, elementText): # called by subclass (utility method for use by subclass)
        if elementText and elementText != '0':
            element = document.createElement(elementName)
            element.appendChild(document.createTextNode(elementText))
            document.documentElement.appendChild(element)
    def save(self):
        self.marshal()   # this method to be implemented in subclass
        self.asset.save()
        self.assetId = self.asset.id
        return
    def render(self, assetPlacement, innerContent, isEdit):

        prefix = \
            '<div id="div' + str(self.asset.id) + '" ' + \
            'style="position:absolute;top:' + str(assetPlacement.top) + 'px;' + \
            'left:' + str(assetPlacement.left) + 'px;' + \
            'width:' + str(assetPlacement.width) + 'px;' + \
            'height:' + str(assetPlacement.height) + 'px;'

        if self.backgroundColor:
            prefix += 'background-color:' + self.backgroundColor + ';'

        if isEdit:
            prefix += 'border:1px dashed gray;'

        prefix += '">'

        suffix = '</div>\n'

        return prefix + innerContent + suffix
