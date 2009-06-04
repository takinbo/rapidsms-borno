# vim: ai sts=4 ts=4 et sw=4
from django.db import models
from apps.reporters.models import Location, Reporter, PersistantConnection
import time as taim
from apps.form.models import Domain
from datetime import datetime,timedelta

class Report(models.Model):

    reporter = models.ForeignKey(Reporter, null=True, blank=True)
    connection = models.ForeignKey(PersistantConnection, null=True, blank=True)
    location = models.ForeignKey(Location)
    time = models.DateTimeField()
    immunized = models.PositiveIntegerField(blank=True, null=True, help_text="Total Children Immunized")
    notimmunized = models.PositiveIntegerField(blank=True, null=True, help_text="Total Children not Immunized")
    vaccines = models.PositiveIntegerField(blank=True, null=True, help_text="Total Vaccine Used")
    domain = models.ForeignKey(Domain)



    def __unicode__(self):
        pass


class NonCompliance(models.Model):
    NC_REASONS = (
            ('1', 'OPV Safety'),
            ('2', 'Child Sick'),
            ('3', 'Religious Belief'),
            ('4', 'No Felt Need'),
            ('5', 'Political Differences'),
            ('6', 'No Care Giver Consent'),
            ('7', 'Unhappy With Immunization Personnel'),
            ('8', 'Too many Rounds'),
            ('9', 'Reason Not given'),

    )
     
    reporter = models.ForeignKey(Reporter, null=True, blank=True)
    connection = models.ForeignKey(PersistantConnection, null=True, blank=True)
    location = models.ForeignKey(Location)
    time = models.DateTimeField()
    reason = models.CharField(blank=True, null=True, max_length=1, choices=NC_REASONS, help_text="This is the reason for non-compliance")
    domain = models.ForeignKey(Domain)


    def __unicode__(self):
        return "%s (%s) %s" % (self.location, self.reporter, self.time)

    @staticmethod
    def summed_data(location):
        pass

    
class Alert(models.Model):
    reporter = models.ForeignKey(Reporter)
    notice = models.CharField(max_length=160)
    received = models.DateTimeField(auto_now_add=True)
    resolved = models.DateTimeField(blank=True, null=True)
    domain = models.ForeignKey(Domain)

    # TODO do we want to save a resolver?

    def __unicode__(self):
        return "%s (%s) %s" % (self.reporter, self.received)
    

class Shortage(models.Model):
    reporter = models.ForeignKey(Reporter, null=True, blank=True)
    connection = models.ForeignKey(PersistantConnection, null=True, blank=True)
    location = models.ForeignKey(Location)
    time = models.DateTimeField()
    reason = models.CharField(blank=True, null=True, max_length=1, choices=NC_REASONS, help_text="Reported commodity with shortage")
    domain = models.ForeignKey(Domain)


    def __unicode__(self):
        return "%s (%s) %s" % (self.reporter, self.location)
