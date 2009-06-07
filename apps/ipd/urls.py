#!/usr/bin/env python
# vim: ai ts=4 sts=4 et sw=4

import os
from django.conf.urls.defaults import *
import apps.ipd.views as views

urlpatterns = patterns('',
    url(r'^ipd/?$', views.index),
    url(r'^ipd/summary/(?P<locid>\d*)/?$', views.index),
    url(r'^ipd/compliance/summary/(?P<locid>\d*)/?$', views.compliance_summary),

)
