from django.contrib.gis.db import models


class Category(models.Model):
    code = models.CharField(max_length=48)


class OrganisationType(models.Model):
    name = models.CharField(max_length=48)


class Organisation(models.Model):
    name = models.CharField(max_length=255)
    website = models.URLField(null=True, blank=True)
    contracted = models.BooleanField(default=True)
    type = models.ForeignKey('OrganisationType')


class Location(models.Model):
    address = models.CharField(max_length=255)
    city = models.CharField(max_length=48)
    postcode = models.CharField(max_length=16)
    point = models.PointField()

    objects = models.GeoManager()

    def __str__(self):
        return ', '.join([
            self.address.replace('\n', ', '),
            self.city,
            self.postcode])

    def organisation(self):
        if self.office_set.count():
            return self.office_set.all()[0].organisation.name
        if self.outreachservice_set.count():
            return self.outreachservice_set.all()[0].office.organisation.name

    def location_type(self):
        if self.office_set.count():
            return 'Office'
        elif self.outreachservice_set.count():
            return self.outreachservice_set.all()[0].type.name
        return ''


class Office(models.Model):
    telephone = models.CharField(max_length=48)
    account_number = models.CharField(max_length=10, unique=True)
    organisation = models.ForeignKey('Organisation')
    location = models.ForeignKey('Location')


class OutreachType(models.Model):
    name = models.CharField(max_length=48)


class OutreachService(models.Model):
    office = models.ForeignKey('Office')
    location = models.ForeignKey('Location')
    type = models.ForeignKey('OutreachType')