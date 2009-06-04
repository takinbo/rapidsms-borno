#!/usr/bin/env python
# vim: ai ts=4 sts=4 et sw=4

from django.contrib.auth.decorators import permission_required
from django.http import HttpResponse, HttpResponseNotAllowed, HttpResponseServerError, Http404
from django.template import RequestContext
from apps.reporters.models import Location, LocationType
from apps.supply.models import Shipment, Transaction, Stock, PartialTransaction
from apps.bednets import constants
from apps.bednets.models import NetDistribution, CardDistribution 
from rapidsms.webui.utils import render_to_response
from django.db import models
# The import here newly added for serializations
from django.core import serializers
from django.core.paginator import *
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
    pass

def location_tree(req):
    pass

def compliance_summary(req, locid):
    pass

def generate(req):
   pass 

def immunization_summary(req, frm, to, range):
    pass

def shortage_summary(req, locid=1):
    pass
