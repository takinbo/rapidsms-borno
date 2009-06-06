#!/usr/bin/env python
# vim: ai ts=4 sts=4 et sw=4

import rapidsms
import threading
from apps.notificator.models import *
from apps.reporters.models import *
from rapidsms.message import Message, StatusCodes
from rapidsms.connection import Connection
import time

class App (rapidsms.app.App):
    '''The notificator app sends out blasts to notification 
	officals who are meant to respond to certain situation 
	alerts eg Shortage of commodity eg OPV''' 
    
    
    def start (self):
        """Configuration of notificator app in the start phase."""
        # Start the Responder Thread -----------------------------------------
        
        self.info("[Notificator] Starting up...")
        # interval to check for sending (in seconds)

        polling_interval = 10

        # start a thread for sending message
        sender_thread = threading.Thread(
                target=self.sender_loop,
                args=(polling_interval,))
        sender_thread.daemon = True
        sender_thread.start()
    
    def parse (self, message):
        """Parse and annotate messages in the parse phase."""
        pass

    def cleanup (self, message):
        pass

    def outgoing (self, message):
        """Handle outgoing message notifications."""
        pass

    def stop (self):
        """Perform global app cleanup when the application is stopped."""
        pass
    
    @classmethod
    def message_counter(self, status, type='S'):
        # returns JUST the number of incoming, sent, or not-sent(for one reason or the other) messages
        self.status = status
        self.type = type
    	return MessageWaiting.objects.filter(status=self.status, type=self.type).count()
    
    
    @classmethod
    def message(self, status, type='S'):

        # return all of the message whose status has been specified
        self.status = status
        self.type = type
        return MessageWaiting.objects.filter(status=self.status, type=self.type)
    
    
    # Sender Thread --------------------
    def sender_loop(self, seconds=10):
        self.info("Starting sender...")
        while True:
            # look for any new waiting messages
            # in the database, and send them
            for message_waiting in MessageWaiting.objects.filter(status="I"):
                self.info("Sending (%s) alert.", str(message_waiting))
                db_connection = message_waiting.get_connection()
                if db_connection is not None:
                    db_backend = db_connection.backend
                    real_backend = self.router.get_backend(db_backend.slug)
                    

                    #receivers = ReporterGroup.objects.get(title="Commodity Control").reporters.all()
                        
                    if real_backend:
                        for receiver in receivers:
                            connection = Connection(real_backend, receiver.connection().identity)
                            message_to_send = "Hello %s, %s" % (receiver.alias, message_waiting.text_message)
                            alert_msg = Message(connection, message_to_send)
                            self.router.outgoing(alert_msg)
                    else:
                            # TODO: should we fail harder here?  This will permanently
                        	# disable responses to this message which is bad.  
                        self.error("Can't find backend %s.  Messages will not be sent")
                            # mark the original message as sent
                    message_waiting.status="S"
                    message_waiting.save()
                
                if message_waiting.type == "N":
                    db_connection = message_waiting.get_connection()
                    if db_connection is not None:
                        db_backend = db_connection.backend
                        # we need to get the real backend from the router
                        # to actually send it

                        real_backend = self.router.get_backend(db_backend.slug)

                        #we also want to obtain the list of key persons to recieve this alerts
                        #TODO: retreive real key users here, remove static key user used for testing
                        receivers_groups = [] 
                        
                        #we want to send responses to targetted groups based on alerts they are expected to act upon
                        
#                        for group in ReporterGroup.objects.all():
#                            receivers_groups.append(group.reporters.all())

                        receivers = ReporterGroup.objects.get(title="ipd_notification").reporters.all()
                        
                    	if real_backend:
                            for receiver in receivers:
                                connection = Connection(real_backend, receiver.connection().identity)
                                message_to_send = "Hello %s, %s" % (receiver.first_name, message_waiting.text_message)
                                alert_msg = Message(connection, message_to_send)
                                self.router.outgoing(alert_msg)
                    	else:
                            # TODO: should we fail harder here?  This will permanently
                        	# disable responses to this message which is bad.  
                            self.error("Can't find backend %s.  Messages will not be sent")
                            # mark the original message as sent
                        message_waiting.status="S"
                        message_waiting.save()
    #wait until it's time to check again
            time.sleep(seconds)

