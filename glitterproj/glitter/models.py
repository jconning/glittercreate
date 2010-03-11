from django.db import models

ACCOUNT_STATUS_CHOICES = (
    ('A', 'Active'),
    ('C', 'Closed by user'),
)

EMAIL_VERIFICATION_STATUS_CHOICES = (
    ('V', 'Verified'),
    ('U', 'Unverified'),
)

EMAIL_BOUNCE_STATUS_CHOICES = (
    ('B', 'Bounced'),
    ('N', 'Not Bounced'),
)

EMAIL_MARKETING_STATUS_CHOICES = (
    ('Y', 'Yes, send me marketing emails'),
    ('N', 'No, don\'t send me marketing emails'),
)

class User(models.Model):
    username = models.CharField(max_length=50, unique=True)
    password = models.CharField(max_length=50)
    email_address = models.CharField('email address', max_length=75)
    first_name = models.CharField('first name', max_length=30)
    last_name = models.CharField('last name', max_length=30)
    date_of_birth = models.DateTimeField('date of birth', null=True, blank=True)  # LATER REMOVE BLANK=TRUE TO CAUSE A NOT NULL CONSTRAINT
    signup_date = models.DateTimeField('signup date')
    last_update_date = models.DateTimeField('last update date', auto_now=True)
    account_status = models.CharField(max_length=1, choices=ACCOUNT_STATUS_CHOICES)
    email_verification_status = models.CharField(max_length=1, choices=EMAIL_VERIFICATION_STATUS_CHOICES)
    email_verification_date = models.DateTimeField('email verification date', null=True, blank=True)  # may be null
    email_bounce_status = models.CharField(max_length=1, choices=EMAIL_BOUNCE_STATUS_CHOICES)
    email_bounce_date = models.DateTimeField('email bounce date', null=True, blank=True)  # may be null
    email_marketing_status = models.CharField(max_length=1, choices=EMAIL_MARKETING_STATUS_CHOICES)
    def __unicode__(self):
        return "%s (id:%d)" % (self.username, self.id)

class Page(models.Model):
    user = models.ForeignKey(User)
    page_name = models.CharField(max_length=50)
    url_name = models.SlugField()
    creation_date = models.DateTimeField('creation date', auto_now_add=True)
    last_update_date = models.DateTimeField('last update date', auto_now=True)
    def __unicode__(self):
        return "%s (id:%d, user_id:%d)" % (self.page_name, self.id, self.user_id)

class AssetType(models.Model):
    asset_type_name = models.CharField(max_length=30, unique=True)
    asset_type_label = models.CharField(max_length=100)
    def __unicode__(self):
        return self.asset_type_name

class Asset(models.Model):
    user = models.ForeignKey(User)
    asset_type = models.ForeignKey(AssetType)
    state = models.CharField(max_length=5000)
    last_added_to_repo_date = models.DateTimeField('last added to repository date')
    creation_date = models.DateTimeField('creation date', auto_now_add=True)
    last_update_date = models.DateTimeField('last update date', auto_now=True)
    def __unicode__(self):
        return "Asset (id:%d user_id:%d asset_type_id:%d state_content:%s)" % (self.id, self.user_id, self.asset_type_id, self.state[:50])

class AssetPlacement(models.Model):
    asset = models.ForeignKey(Asset)
    page = models.ForeignKey(Page)
    top = models.IntegerField()
    left = models.IntegerField()
    width = models.IntegerField()
    height = models.IntegerField()
    def __unicode__(self):
        return "AssetPlacement (id:%d asset_id:%d page_id:%d top:%d left:%d)" % (self.id, self.asset_id, self.page_id, self.top, self.left)

class RepoAsset(models.Model):
    asset_id = models.IntegerField()
    contributor_id = models.IntegerField()
    asset_type_name = models.CharField(max_length=30)
    state = models.CharField(max_length=5000)
    image_url = models.CharField(max_length=250)
    image_width = models.IntegerField()
    image_height = models.IntegerField()
    consume_copy_count = models.IntegerField()
    creation_date = models.DateTimeField('creation date', auto_now_add=True)
    last_update_date = models.DateTimeField('last update date', auto_now=True)
    def setAssetId(self, assetId):
        self.asset_id = assetId
    def setContributorId(self, contributorId):
        self.contributor_id = contributorId
    def setAssetTypeName(self, assetTypeName):
        self.asset_type_name = assetTypeName
    def setState(self, state):
        self.state = state
    def setImageUrl(self, url):
        self.image_url = url
    def setImageWidth(self, width):
        self.image_width = width
    def setImageHeight(self, height):
        self.image_height = height
    def incrementConsumeCopyCount(self):
        if self.consume_copy_count:
            self.consume_copy_count += 1
        else:
            self.consume_copy_count = 1
    def initializeConsumeCopyCount(self):
        self.consume_copy_count = 0
    def getAssetTypeName(self):
        return self.asset_type_name
    def getState(self):
        return self.state
    def getImageUrl(self):
        return self.image_url
    def getImageWidth(self):
        return int(self.image_width)
    def getImageHeight(self):
        return int(self.image_height)
    def getConsumeCopyCount(self):
        if not self.consume_copy_count:
            return 0
        return int(self.consume_copy_count)
    def getCreationDate(self):
        return self.creation_date
    def __unicode__(self):
        return "RepoAsset (id:%d asset_id:%d asset_type_name:%s" % (self.id, self.asset_id, self.asset_type_name)

class RepoAssetDailyConsume(models.Model):
    repo_asset = models.ForeignKey(RepoAsset)
    consume_date = models.DateField('consume date')
    consume_copy_count = models.IntegerField()
    def incrementConsumeCopyCount(self):
        if self.consume_copy_count:
            self.consume_copy_count += 1
        else:
            self.consume_copy_count = 1

