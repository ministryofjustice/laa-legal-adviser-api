from django.contrib.gis.db import models


class Office(models.Model):
    address = models.CharField(max_length=255)
    city = models.CharField(max_length=48)
    postcode = models.CharField(max_length=16)
    phone = models.CharField(max_length=32)
    lat = models.FloatField()
    lon = models.FloatField()

    objects = models.GeoManager()
