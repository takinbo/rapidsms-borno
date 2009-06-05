#!/usr/bin/env python
# vim: ai ts=4 sts=4 et sw=4

import os
from django.conf.urls.defaults import *
import apps.ipd.views as views

urlpatterns = patterns('',
    url(r'^ipd/locgen/?$', views.generate),
    url(r'^ipd/?$', views.index),
    url(r'^ipd/summary/(?P<locid>\d*)/?$', views.index),
    url(r'^ipd/json/?$', views.location_tree),
    url(r'^ipd/compliance/summary/(?P<range>.*)/?(?P<from>.*)/?(?P<to>.*)/?$', views.compliance_summary),
    url(r'^ipd/immunization/summary/(?P<locid>\d*)/?$', views.immunization_summary),
    url(r'^ipd/shortage/summary/(?P<locid>\d*)/?$', views.shortage_summary),
    url(r'^ipd/test/?$', views.index)
)
