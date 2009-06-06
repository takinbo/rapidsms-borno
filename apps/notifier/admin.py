#!/usr/bin/env python
# vim: ai ts=4 sts=4 et sw=4

from django.contrib import admin
from apps.notifier.models import *

class NotifierAdmin(admin.ModelAdmin):
    list_display = ['connection', 'time', 'status', 'text_message']
    date_hierarchy = 'time'


admin.site.register(MessageWaiting, NotifierAdmin)
