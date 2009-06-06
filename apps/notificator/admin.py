#!/usr/bin/env python
# vim: ai ts=4 sts=4 et sw=4

from django.contrib import admin
from apps.notificator.models import *

class NotificatorAdmin(admin.ModelAdmin):
    list_display = ['reporter', 'connection', 'time', 'status', 'text_message']
    date_hierarchy = 'time'


admin.site.register(MessageWaiting, NotificatorAdmin)
