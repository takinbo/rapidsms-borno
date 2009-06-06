# vim: ai sts=4 ts=4 et sw=4
from django.db import models
from apps.reporters.models import Location, Reporter, PersistantConnection
import time as taim
from apps.form.models import Domain
from datetime import datetime,timedelta

class Report(models.Model):
    '''The Report model is used in storing Ward Summary Reports necessary
    for tracking number of children both immunized and not immunized and also
    the number of vaccines used in vaccinating the children are recorded so 
    as to track vaccine usage and check wastage'''
    reporter = models.ForeignKey(Reporter, null=True, blank=True)
    connection = models.ForeignKey(PersistantConnection, null=True, blank=True)
    location = models.ForeignKey(Location)
    time = models.DateTimeField()
    immunized = models.PositiveIntegerField(blank=True, null=True, help_text="Total Children Immunized")
    notimmunized = models.PositiveIntegerField(blank=True, null=True, help_text="Total Children not Immunized")
    vaccines = models.PositiveIntegerField(blank=True, null=True, help_text="Total Vaccines Used")

    def __unicode__(self):
        return "%s (%s) => %s, %s, %s" % (self.location, self.reporter, self.immunized, self.notimmunized, self.vaccines)

class NonCompliance(models.Model):
    NC_REASONS = (
            ('1', 'OPV Safety'),
            ('2', 'Child Sick'),
            ('3', 'Religious Belief'),
            ('4', 'No Felt Need'),
            ('5', 'Political Differences'),
            ('6', 'No Care Giver Consent'),
            ('7', 'Unhappy With Immunization Personnel'),
            ('8', 'Too Many Rounds'),
            ('9', 'Reason Not Given'),
    )
     
    reporter = models.ForeignKey(Reporter, null=True, blank=True)
    connection = models.ForeignKey(PersistantConnection, null=True, blank=True)
    location = models.ForeignKey(Location)
    time = models.DateTimeField()
    reason = models.CharField(blank=True, null=True, max_length=1, choices=NC_REASONS, help_text="This is the reason for non-compliance")
    cases = models.PositiveIntegerField()

    def __unicode__(self):
        return "%s (%s) %s %s" % (self.location, self.reporter, self.reason, self.cases)

    @staticmethod
    def summed_data(location):
        pass

    @staticmethod
    def get_reason(reason):
        if int(reason) in range(1, 9):
            return NonCompliance.NC_REASONS[int(reason) - 1][1]
        else:
            return NonCompliance.NC_REASONS[8][1]

class Alert(models.Model):
    '''Model for storing alerts once they've gone out.
    This should eventually be on it's own app'''
    reporter = models.ForeignKey(Reporter)
    notice = models.CharField(max_length=160)
    received = models.DateTimeField(auto_now_add=True)
    #resolved = models.DateTimeField(blank=True, null=True)
    #domain = models.ForeignKey(Domain)

    # TODO do we want to save a resolver?
    # Probably Not. I commented out the two lines above since
    # I feel saving the domain isn't necessary - The app is 
    # already a table prefix and will not be confused with 
    # another Alert or Report in another app. Secondly, there
    # is no way of tracking issue resolution so no need to have
    # it in the DB

    def __unicode__(self):
        return "%s (%s)" % (self.reporter, self.received)
    

class Shortage(models.Model):
    '''Model for storing shortage reports'''
    # I'm suspecting that this might be a better way to store
    # the commodities.
    SHORTAGE_COMMODITIES = (
        ('1', 'Vitamin A'),
        ('2', 'OPV'),
        ('3', 'DPT'),
    )
    reporter = models.ForeignKey(Reporter, null=True, blank=True)
    # What's the case for storing the connection since the report has one?
    # connection = models.ForeignKey(PersistantConnection, null=True, blank=True)
    location = models.ForeignKey(Location)
    time = models.DateTimeField()
    commodity = models.CharField(max_length=10)

    def __unicode__(self):
        return "%s (%s) => %s" % (self.reporter, self.location, self.commodity)
