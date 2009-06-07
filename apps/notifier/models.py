#!/usr/bin/env python
# vim: ai ts=4 sts=4 et sw=4

from django.db import models
from apps.reporters.models import Reporter, PersistantBackend, ReporterGroup, LocationType
from apps.form.models import Form
from datetime import datetime

# TODO: better name
class MessageWaiting(models.Model):
    '''A message waiting to be sent'''
    STATUS_TYPES = (
        ('N', 'Not Sent'), # the message has been received, but not sent
        ('I', 'Incoming'),
        ('S', 'Sent') # the message has been sent
    )
    
    # This is the model the message that comes in to be sent out by the sender_loop
    # TODO: this should be a dual-non-null key if that is possible
    backend = models.ForeignKey(PersistantBackend, null=True, help_text="This contains the backend and contact details of the Reporter")
    destination = models.CharField(max_length=30, null=False, blank=False, help_text="Phone number to send the message to")

    # The time attribute is useful for sending scheduled messages
    time = models.DateTimeField(default=datetime.now(), help_text="The earliest time the message should be sent")
    text_message = models.CharField(max_length=160, help_text="Text message that will be sent")
    status = models.CharField(max_length=1, choices=STATUS_TYPES, help_text="Status of the message (either I, N or S)")    
    def __unicode__(self):
        return self.text_message

    def __json__(self):
	    return {
		    "pk":         self.pk,
            "phone":      self.destination,
		    "text":       self.text_message,
            }

class Alerting(models.Model):
    '''Alerting enables the ability to retrieve groups of reporters
       that should be alerted when a valid form has been received'''
    title = models.CharField(max_length=50, help_text="Descriptive name for this Alerting entry")
    form = models.ForeignKey(Form, blank=False, null=False)
    groups = models.ManyToManyField(ReporterGroup, blank=True)

    # There'll be times when you want to specify up to which level in the location
    # hierarchy that you'll want an alert to be sent
    # A form with location code 081202 has state=08, lga=12, ward=02. If LGA 
    # type is specified as the location_hierarchy, then it will alert all
    # reporters matching the same LGA in the specified groups.
    location_hierarchy = models.ForeignKey(LocationType, blank=False, null=False)

    def __unicode__(self):
        return self.title
