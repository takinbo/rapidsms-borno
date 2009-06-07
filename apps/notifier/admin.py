#!/usr/bin/env python
# vim: ai ts=4 sts=4 et sw=4

from django.contrib import admin
from apps.notifier.models import *

class MessageWaitingAdmin(admin.ModelAdmin):
    list_display = ['backend', 'destination', 'text_message', 'time', 'status']
    date_hierarchy = 'time'

admin.site.register(MessageWaiting, MessageWaitingAdmin)
admin.site.register(Alerting)
