from django.contrib.auth.models import User
from django.contrib.gis.db import models


# Python 3 compatibility
try:
    unicode("")  # Python 2
except NameError:
    unicode = str  # Python 3

# We can't add category name to model because the categories data
# gets reset during the upload of the provider spreadsheet
# https://github.com/ministryofjustice/laa-legal-adviser-api/blob/master/laalaa/apps/advisers/tasks.py#L55
PROVIDER_CATEGORIES = {
    "aap": "Claims Against Public Authorities",
    "med": "Clinical negligence",
    "com": "Community care",
    "crm": "Crime",
    "deb": "Debt",
    "disc": "Discrimination",
    "edu": "Education",
    "mat": "Family",
    "fmed": "Family mediation",
    "hou": "Housing",
    "immas": "Immigration or asylum",
    "mhe": "Mental health",
    "pl": "Prison law",
    "pub": "Public law",
    "wb": "Welfare benefits",
    "mosl": "Modern slavery",
}


class Category(models.Model):
    code = models.CharField(max_length=8)
    civil = models.BooleanField(default=True)

    def __unicode__(self):
        return unicode(self.code)

    @property
    def name(self):
        return PROVIDER_CATEGORIES.get(self.code.lower())


class OrganisationType(models.Model):
    name = models.CharField(max_length=48)

    def __unicode__(self):
        return unicode(self.name)


class Organisation(models.Model):
    firm = models.IntegerField(null=True)  # TODO: shouldn't this be unique?
    name = models.CharField(max_length=255)
    website = models.URLField(null=True, blank=True)
    contracted = models.BooleanField(default=True)
    type = models.ForeignKey("OrganisationType", on_delete=models.CASCADE)

    def __unicode__(self):
        return unicode(self.name)


class LocationManager(models.Manager):
    def get_queryset(self):
        return (
            super(LocationManager, self)
            .get_queryset()
            .select_related(
                "office",
                "office__organisation",
                "outreachservice",
                "outreachservice__type",
                "outreachservice__office__organisation",
            )
            .prefetch_related("office__categories", "outreachservice__categories")
        )


class Location(models.Model):
    address = models.CharField(max_length=255)
    city = models.CharField(max_length=48)
    postcode = models.CharField(max_length=16)
    point = models.PointField(null=True)

    objects = LocationManager()

    def __unicode__(self):
        return u", ".join([unicode(self.address.replace("\n", ", ")), unicode(self.city), unicode(self.postcode)])

    def organisation(self):
        return self.place.organisation

    @property
    def place(self):
        try:
            return self.office
        except Office.DoesNotExist:
            return self.outreachservice

    def type(self):
        if isinstance(self.place, OutreachService):
            return self.outreachservice.type.name
        return self.place.__class__.__name__

    @property
    def telephone(self):
        return self.place.telephone

    @property
    def categories(self):
        return self.place.categories

    @property
    def location(self):
        return self


class Office(models.Model):
    telephone = models.CharField(max_length=48)
    account_number = models.CharField(max_length=10, unique=True)
    organisation = models.ForeignKey("Organisation", on_delete=models.CASCADE)
    location = models.OneToOneField("Location", null=True, on_delete=models.CASCADE)
    categories = models.ManyToManyField(Category)


class OutreachType(models.Model):
    name = models.CharField(max_length=48)

    def __unicode__(self):
        return unicode(self.name)


class OutreachService(models.Model):
    office = models.ForeignKey("Office", on_delete=models.CASCADE)
    location = models.OneToOneField("Location", null=True, on_delete=models.CASCADE)
    type = models.ForeignKey("OutreachType", on_delete=models.CASCADE)
    categories = models.ManyToManyField(Category)

    @property
    def telephone(self):
        return self.office.telephone

    @property
    def organisation(self):
        return self.office.organisation


class Choices(object):
    def __init__(self, *pairs):
        self._choices = pairs
        self.__dict__.update(pairs)

    def __iter__(self):
        return iter(self._choices)


IMPORT_STATUSES = Choices(
    ("RUNNING", "running"), ("SUCCESS", "success"), ("FAILURE", "failure"), ("ABORTED", "aborted")
)


class Import(models.Model):
    task_id = models.CharField(max_length=50, default="")
    started = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=7, choices=list(IMPORT_STATUSES))
    filename = models.TextField()
    user = models.ForeignKey(User, null=True, on_delete=models.CASCADE)
