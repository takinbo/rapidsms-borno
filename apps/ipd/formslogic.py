#!/usr/bin/env python
# vim: ai ts=4 sts=4 et sw=4

from models import *
from rapidsms.message import StatusCodes
from apps.reporters.models import *
from apps.notifier.models import *
from apps.form.formslogic import FormsLogic
import re

class IPDFormsLogic(FormsLogic):
    ''' This class will hold the Nigeria IPD-specific forms logic.
        I'm not sure whether this will be the right structure
        this was just for getting something hooked up '''
    
    # this is a simple structure we use to describe the forms.  
    # maps token names to db names
    _form_lookups = {
        "report" : {
            "class" : Report,
            "display" : "Report",
            "fields": (
                ("location", "location"),
                ("immunized", "immunized"),
                ("notimmunized", "notimmunized"),
                ("vaccines", "vaccines"),
            )
        },

        "nc" : {
            "class" : NonCompliance,
            "display" : "Non Compliance",
            "fields": (
                ("location", "location"),
                ("reason", "reason"),
                ("cases","cases"),
            )
        },

        "shortage" : {
            "class" : Shortage,
            "display" : "Shortage",
            "fields" : (
                ("location", "location"),
                ("commodity", "commodity"),
            )
        }
    }
    
    _foreign_key_lookups = {"Location" : "code" }

    def validate(self, *args, **kwargs):
        message = args[0]
        form_entry = args[1]
        # in case we need help, build a valid reminder string
        # TODO put this in the db!
        if form_entry.form.code.abbreviation == "report":
            required = ['location', 'immunized', 'notimmunized', 'vaccines']
            data = form_entry.to_dict()

            # check that ALL FIELDS were provided
            missing = [t for t in required if data[t] is None]
            
            # missing fields! collate them, and
            # send back a friendly non-localized
            # error message, then abort
            if missing:
                mis_str = ", ".join(missing)
                return ["Missing fields: %s" % mis_str, help]
            
            # all fields were present and correct, so copy them into the
            # form_entry, for "actions" to pick up again without re-fetching
            form_entry.rep_data = data
            
            # is ready to spawn a Reporter object
            return None
        elif form_entry.form.code.abbreviation in self._form_lookups.keys():
            # we know all the fields in this form are required, so make sure they're set
            # TODO check the token's required flag
            required_tokens = [form_token.token for form_token in form_entry.form.form_tokens.all() if form_token.required]
            for tokenentry in form_entry.tokenentry_set.all():
                if tokenentry.token in required_tokens:
                    # found it, as long as the data isn't empty remove it
                    if tokenentry.data:
                        required_tokens.remove(tokenentry.token)
            if required_tokens:
                req_token_names = [token.abbreviation for token in required_tokens]
                errors = "The following fields are required: " + ", ".join(req_token_names)
                return [errors]
            return None
    
    def actions(self, *args, **kwargs):
        message = args[0]
        form_entry = args[1]

        if self._form_lookups.has_key(form_entry.form.code.abbreviation):
            to_use = self._form_lookups[form_entry.form.code.abbreviation]
            form_class = to_use["class"]
            field_list = to_use["fields"]
            # create and save the model from the form data
            instance = self._model_from_form(message, form_entry, form_class, dict(field_list), self._foreign_key_lookups)
            instance.time = message.date
            
            # if the reporter isn't set then populate the connection object.
            # this means that at least one (actually exactly one) is set
            # the method above sets this property in the instance
            # if it was found.
            if not hasattr(instance, "reporter") or not instance.reporter:
                instance.connection = message.persistant_connection if message.persistant_connection else None
                response = ""
            # personalize response if we have a registered reporter
            else:
                response = "Thank you %s. " % (instance.reporter.first_name)
            instance.save()
            response = response + "Received report for %s %s: " % (form_entry.domain.code.abbreviation.upper(), to_use["display"].upper())
            # this line pulls any attributes that are present into a dictionary
            attrs = dict([[attr[1], str(getattr(instance, attr[1]))] for attr in field_list if hasattr(instance, attr[1])])
            # Instead of having the reason code sent back to the reporter,
            # retrieve and set a more descriptive reason
            if attrs.has_key("reason"):
                attrs['reason'] = NonCompliance.get_reason(attrs['reason'])
            
            # concatenates the inner list on "=" and joins the outer on ", " so we get 
            # attr1=value1, attr2=value2
            response = response + ", ".join([ key + "=" + value for (key, value) in attrs.items() ])
            
            # Since we are not expecting reporters to pre-register, we
            # should suppress generating this.
            # if not instance.reporter:
            #    response = response + ". Please register your phone"
            
            
            '''The following routines will retrieve the alerting groups and send alerts
               to the members of the group'''
            if form_entry.form.code.abbreviation == "shortage" or form_entry.form.code.abbreviation == "nc":
                # Retrieve all the alert_groups attached to this form
                for alert_group in Alerting.objects.filter(form=form_entry.form):
                    # Now we need to retrieve reporters having ancestors equal to the
                    # highest hierarchy defined in the group
                    location_ancestor = instance.location.get_ancestors().get(type=alert_group.location_hierarchy)

                    # retrieve all group members having the same location_ancestor
                    alert_reporters = []
                    for group in alert_group.groups.all():
                        for alert_reporter in group.reporters.all():
                            try:
                                if alert_reporter.location == location_ancestor or alert_reporter.location.get_ancestors().get(type=alert_group.location_hierarchy) == location_ancestor:
                                    alert_reporters.append(alert_reporter)
                                    print "Appended: ", alert_reporter
                                # This could be related to the ancestors of the object itself
                                
                                #if alert_reporter.location.get_ancestors().get(type=alert_group.location_hierarchy) == location_ancestor or alert_reporter.location.get(type=alert_group.location_hierarchy) == location_ancestor:
                                 #   alert_reporters.append(alert_reporter)
                            except Location.DoesNotExist:
                                pass

                for notified_reporter in alert_reporters: 
                    # I think it's much easier to tell someone the number is 0803.* instead of +234803.*
                    if form_entry.form.code.abbreviation == "shortage":  
                        # If the reporter exists, we generate an alert message with the reporters information
                        # if not, we just report the reporter's phone number
                        if instance.reporter:
                            message_to_send = "Hello %s, there is a shortage of %s in %s, reported by %s (%s)" % (notified_reporter.first_name, instance.commodity.upper(), instance.location, instance.reporter, re.sub("^\+?234", "0", instance.reporter.connection().identity))
                        else:
                            message_to_send = "Hello %s, there is a shortage of %s in %s, reported by (%s)" % (notified_reporter.first_name, instance.commodity.upper(), instance.location, re.sub("^\+?234", "0", message.connection.identity))
                            
                    elif form_entry.form.code.abbreviation == "nc":
                        if instance.reporter:
                            message_to_send = "Hello %s, there is a non-compliance report from %s (Reason:%s, Cases:%s), reported by %s (%s)" % (notified_reporter.first_name, instance.location, NonCompliance.get_reason(instance.reason), instance.cases, instance.reporter, re.sub("^\+?234", "0", instance.reporter.connection().identity))
                        else:
                            message_to_send = "Hello %s, there is a non-compliance report from %s (Reason:%s, Cases:%s), reported by (%s)" % (notified_reporter.first_name, instance.location, NonCompliance.get_reason(instance.reason), instance.cases, re.sub("^\+?234", "0", message.connection.identity))

                    alert_message = MessageWaiting()
                    alert_message.backend = instance.connection.backend
                    alert_message.time = instance.time
                    alert_message.destination = notified_reporter.connection().identity
                    alert_message.status = "I"
                    alert_message.text_message = message_to_send
            
                    alert_message.save()
            
            message.respond(response, StatusCodes.OK)
