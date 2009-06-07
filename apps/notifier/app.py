#!/usr/bin/env python
# vim: ai ts=4 sts=4 et sw=4

import rapidsms
import threading
from apps.notifier.models import *
from apps.reporters.models import *
from rapidsms.message import Message, StatusCodes
from rapidsms.connection import Connection
import time
from datetime import datetime

class App (rapidsms.app.App):
    '''The notifier app sends out blasts to notification 
	officals who are meant to respond to certain situation 
	alerts eg Shortage of commodity eg OPV''' 
    
    
    def start (self):
        """Configuration of notifier app in the start phase."""
        # Start the Responder Thread -----------------------------------------
        
        self.info("[Notifier] Starting up...")
        # interval to check for sending (in seconds)

        polling_interval = 5

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
    def message(self, status):
        # return all of the message whose status has been specified
        self.status = status
        return MessageWaiting.objects.filter(status=self.status)
    
    
    # Sender Thread --------------------
    def sender_loop(self, seconds=5):
        '''Routine to fetch pending messages and push them to the router
           for sending through the backend.'''
        self.info("Starting sender...")
        while True:
            # look for any new waiting messages
            # in the database to be sent now, and send them
            for message_waiting in MessageWaiting.objects.filter(status="I", time__lte=datetime.now()):
                self.info("Sending (%s) alert.", str(message_waiting))
                db_backend = message_waiting.backend
                real_backend = self.router.get_backend(db_backend.slug)

                if real_backend:
                    connection = Connection(real_backend, message_waiting.destination)
                    alert_msg = Message(connection, message_waiting.text_message)
                    self.router.outgoing(alert_msg)

                    # mark message as sent
                    message_waiting.status="S"
                else:
                    # TODO: should we fail harder here?  This will permanently
                    # disable responses to this message which is bad.  
                    self.error("Can't find backend %s.  Messages will not be sent", real_backend)
                    # mark the message as not sent
                    message_waiting.status="N"
                
                message_waiting.save()
                
            # wait until it's time to check again
            time.sleep(seconds)

