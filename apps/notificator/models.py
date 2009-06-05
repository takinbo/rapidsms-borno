#!/usr/bin/env python
# vim: ai ts=4 sts=4 et sw=4

from django.db import models
from apps.reporters.models import Reporter, PersistantConnection

# TODO: better name
class MessageWaiting(models.Model):
    '''A message waiting for a sending.'''
    STATUS_TYPES = (
        ('N', 'Not Sent'), # the message has been received, but not sent
        ('I', 'Incoming'),
        ('S', 'Sent') # the message has been sent
    )
    
    MESSAGE_TYPES = (
        ('S','Shortage'),
        ('N','Non Compliance'),
        ('R','Report')
        
    )
    # This is the model the message that comes in to be sent out by the sender_loop
    # TODO: this should be a dual-non-null key if that is possible
    reporter = models.ForeignKey(Reporter, null=True, blank=True)
    connection = models.ForeignKey(PersistantConnection, null=True, blank=True)
    time = models.DateTimeField()
    text_message = models.CharField(max_length=160)
    status = models.CharField(max_length=1, choices=STATUS_TYPES)
    type = models.CharField(max_length=1, choices=MESSAGE_TYPES)

    
    @classmethod
    def incoming_message(klass, msg):
        return klass(
            text_message=msg.text,
            time=msg.date,
            status="I",
            
            # link the stored message to the reporter
            # or connection, whichever we have
            **msg.persistance_dict)

    def get_connection(self):
        if self.reporter:
             return self.reporter.connection()
        return self.connection

    def __unicode__(self):
        return self.text_message

    def __str__(self):
        return self.type

    def __json__(self):
	    return {
		    "pk":         self.pk,
		    "text":       self.text_message,
		    "reporter":   self.reporter,
		    "connection": self.connection
            }

    @classmethod
    def outgoing_message(klass, msg):
        return klass(
            text_message = msg.text, 
            time = msg.date,
            status = "S"
        )

    @classmethod
    def not_sent(klass, msg):
        return klass(
            text_message = msg.text,
            time = msg.text,
            status = 'N'
        )
