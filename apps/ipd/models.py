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
    def non_compliance_total(location):
        all = NonCompliance.objects.all().filter(location__pk=location.pk)

        return {"cases": sum(all.values_list("cases", flat=True))
        }

    def get_reason(reason):
        if int(reason) in range(1, 9):
            return NonCompliance.NC_REASONS[int(reason) - 1][1]
        else:
            return NonCompliance.NC_REASONS[8][1]

    @staticmethod
    def get_reason(reason):
        if int(reason) in range(1, 9):
            return NonCompliance.NC_REASONS[int(reason) - 1][1]
        else:
            return NonCompliance.NC_REASONS[8][1]
    def get_reason_total(reason, location):
        all = NonCompliance.objects.all().filter(location__code__startswith=location.code, reason=reason)

        reason_total = sum(all.values_list('cases', flat=True))
        return reason_total
        
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
    # TODO: This has to go!
    connection = models.ForeignKey(PersistantConnection, null=True, blank=True)
    location = models.ForeignKey(Location)
    time = models.DateTimeField()
    commodity = models.CharField(max_length=10)

    def __unicode__(self):
        return "%s (%s) => %s" % (self.reporter, self.location, self.commodity)
