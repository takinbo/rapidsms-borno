#!/usr/bin/env python
# vim: ai ts=4 sts=4 et sw=4

from django.contrib.auth.decorators import permission_required
from django.http import HttpResponse, HttpResponseNotAllowed, HttpResponseServerError, Http404
from django.template import RequestContext
from apps.reporters.models import Location, LocationType
from apps.ipd.models import NonCompliance, Shortage, Report
from rapidsms.webui.utils import render_to_response
from django.db import models
# The import here newly added for serializations
from django.core import serializers
from random import randrange, seed
from django.utils import simplejson

import time
import sys

#Parameter for paging reports outputs
ITEMS_PER_PAGE = 20

#This is required for ***unicode*** characters***
# do we really need to reload it?  TIM to check
reload(sys)
sys.setdefaultencoding('utf-8')

#Views for handling summary of Reports Displayed as Location Tree
def index(req, locid=None):
    if not locid:
        locid = 1
    try:
        location = Location.objects.get(id=locid)
        location.non_compliance_total  =  NonCompliance.non_compliance_total(location)
    except Location.DoesNotExist:
        pass

    return render_to_response(req,"ipd/index.html", {'location':location})

def compliance_summary(req, locid=1):
    bar_data=[]
    expected_data=[]
    nets_data=[]
    discrepancy_data = []
    labels=[]
    loc_children=[]
    time_data=[]
    type = ""
    index = 0
    pie_data=[]
    parent=None
    NC_REASONS = (
             ('1', 'OPV Safety'),
             ('2', 'Child Sick'),
             ('3', 'Religious Belief'),
             ('4', 'No Felt Need'),
             ('5', 'Political Differences'),
             ('6', 'No Care Giver Consent'),
             ('7', 'Unhappy With Immunization Personnel'),
             ('8', 'Too Many Rounds'),
             ('9', 'Reason Not Given'),
     )

    try:
        location = Location.objects.get(id=locid)
        parent = location.parent
        location_type = Location.objects.get(pk=locid).type
        loc_children = []
        for reason in NC_REASONS:
            
            pie_data.append({"label": reason, "data":NonCompliance.get_reason_total(reason, location)})

    except:
        pass
    
    return render_to_response(req,"ipd/compliance_summary.html", {'pie_data':pie_data, 'location':location})

def generate(req):
   pass 

def immunization_summary(req, frm, to, range):
    pass

def shortage_summary(req, locid=1):
    pass
