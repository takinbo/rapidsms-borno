#!/usr/bin/env python
# vim: ai ts=4 sts=4 et sw=4


from django import template

register = template.Library()

from datetime import datetime, timedelta
from apps.reporters.models import *
from apps.supply.models import *
from apps.ipd.models import *
from apps.bednets import constants
from apps.bednets.models import *

@register.inclusion_tag("ipd/partials/recent.html")
def recent_reporters(number=4):
    last_connections = PersistantConnection.objects.filter(reporter__isnull=False).order_by("-last_seen")[:number]
    last_reporters = [conn.reporter for conn in last_connections]
    return { "reporters": last_reporters }


@register.inclusion_tag("ipd/partials/stats.html")
def ipd_stats():
    return { "stats": [
#        {
#            "caption": "Callers",
#            "value":   PersistantConnection.objects.count()
#        },
        {
            "caption": "Reporters",
            "value":   Reporter.objects.count()
        },
        {
            "caption": "Active Locations",
            "value": Report.objects.values("location").distinct().count()
        },
        {
            "caption": "Immunization Reports",
            "value":   Report.objects.count()
        },
        {
            "caption": "Reported Shortages",
            "value":   Shortage.objects.count()
        },
        {
            "caption": "Total Immunized",
            "value":   sum(Report.objects.values_list("immunized", flat=True))
        },
        {
            "caption": "Total Missed",
            "value":   sum(Report.objects.values_list("notimmunized", flat=True))
        },
        {
            "caption": "Active Responders",
            "value":   len(Reporter.objects.filter(location__type=LocationType.objects.get(name__startswith="LGA")))
        },
#        {
#            "caption": "Coupon Recipients",
#            "value":   sum(CardDistribution.objects.values_list("people", flat=True))
#        }
    ]}


@register.inclusion_tag("ipd/partials/progress.html")
def daily_progress():
    start = datetime(2009, 06, 06)
    end = datetime(2009, 06, 11)
    days = []
    
    
    # how high should we aim?
    # 48 wards * 9 mobilization teams = 482?
    # but at least 2 lgas are summing teams
    # and reporting once by ward, so maybe 48 * 4?
    report_target    = 192.0

    # Dawakin Kudu      99,379
    # Garum Mallam      51,365
    # Kano Municipal    161,168
    # Kura              63,758
    coupon_target    = 375670.0

    # Dawakin Kudu      248,447
    # Garun Mallam      128,412
    # Kano Municipal    402,919
    # Kura              159,394
    recipient_target = 939172.0
    
    
    for d in range(0, (end - start).days):
        date = start + timedelta(d)
        
        args = {
            "time__year":  date.year,
            "time__month": date.month,
            "time__day":   date.day
        }
        
        data = {
            "number": d+1,
            "date": date,
            "in_future": date > datetime.now()
        }
        
        if not data["in_future"]:
            data.update({
                "reports": Report.objects.filter(**args).count(),
                "immunized": sum(Report.objects.filter(**args).values_list("immunized", flat=True)),
                "notimmunized": sum(Report.objects.filter(**args).values_list("notimmunized", flat=True))
            })
        
            data.update({
                "reports_perc":    int((data["reports"]    / report_target)    * 100) if (data["reports"]    > 0) else 0,
                "immunized_perc":    int((data["immunized"]    / coupon_target)    * 100) if (data["immunized"]    > 0) else 0,
                "notimmunizeds_perc":    int((data["notimmunized"]    / recipient_target)    * 100) if (data["notimmunized"]    > 0) else 0,
            })
        days.append(data)
    
    total_immunized = sum(Report.objects.all().values_list("immunized", flat=True))
    netcards_stats = int(float(total_immunized) / coupon_target * 100) if (total_immunized > 0) else 0

    total_notimmunized = sum(Report.objects.all().values_list("notimmunized", flat=True))
    beneficiaries_stats = int(float(total_notimmunized) / recipient_target * 100) if (total_notimmunized > 0) else 0

    return { "days": days, 
            "netcards_stats": netcards_stats, 
            "beneficiaries_stats": beneficiaries_stats,
            "total_immunized": total_immunized,
            "total_notimmunized": total_notimmunized}


@register.inclusion_tag("ipd/partials/pilot.html")
def pilot_summary():
    
    # fetch all of the LGAs that we want to display
    lga_names_kano = ["DAWAKIN KUDU", "GARUN MALLAM", "KURA", "KANO MUNICIPAL"]
    lga_names = ["JERE", "MAIDUGURI"]
    lgas = LocationType.objects.get(name="LGA").locations.filter(name__in=lga_names)
    
    # called to fetch and assemble the
    # data structure for each pilot ward
    def __ward_data(ward):
        locations = ward.get_descendants(True)
        reports = CardDistribution.objects.filter(location__in=locations)
        nets_reports = NetDistribution.objects.filter(location__in=locations)
        nc_reports = NonCompliance.objects.filter(location__in=locations)
        immunization_reports = Report.objects.filter(location__in=locations)

        style = "" 
        if reports.count() == 0:
            style = "warning" 

        return {
            "name":          ward.name,
            "contact":       ward.one_contact('WS', True),
            "reports":       reports.count(),
            "immunization_reports": immunization_reports.count(),
            "nets_reports":  nets_reports.count(),
            "nc_reports":    nc_reports.count(),
            "netcards":      sum(reports.values_list("distributed", flat=True)),
            "immunized":     sum(immunization_reports.values_list("immunized", flat=True)),
            "notimmunized":  sum(immunization_reports.values_list("notimmunized", flat=True)),
            "vaccines":      sum(immunization_reports.values_list("vaccines", flat=True)),
            "cases":         sum(nc_reports.values_list("cases", flat=True)),
            "nets":          sum(nets_reports.values_list("distributed", flat=True)),
            "beneficiaries": sum(reports.values_list("people", flat=True)),
            "class":         style}
    
    # called to fetch and assemble the
    # data structure for each pilot LGA
    def __lga_data(lga):
        projections = {
            "population" : {
                        "JERE" : 56726.0,
                        "MAIDUGURI" : 133714.0
            }
        }

        wards = lga.children.all()
        reporters = Reporter.objects.filter(location__in=wards)
        supervisors = reporters.filter(role__code__iexact="WS")
        summary = "%d supervisors in %d wards" % (supervisors.count(), wards.count())
        
        ward_data = map(__ward_data, wards)
        def __wards_total(key):
            return sum(map(lambda w: w[key], ward_data))
        
        def __stats(key):
            return int(float(__wards_total(key)) / projections[key][str(lga.name)] * 100) if (__wards_total(key) > 0) else 0 

        # This method to return % of nets/netcards issued. It is believed there could be a better method.
        def __nets_stats(key):
            return int (float(__wards_total(key)/__wards_total("netcards")) * 100 ) if (__wards_total(key) > 0 ) else 0
            
        return {
            "name":                     lga.name,
            "summary":                  summary,
            #"netcards_projected":       int(projections['netcards'][str(lga.name)]),
            "netcards_total":           int(__wards_total("netcards")),
            "population_projected":  int(projections['population'][str(lga.name)]),
            "immunized_total":      int(__wards_total("immunized")),
            "notimmunized_total":   int(__wards_total("notimmunized")),
            "vaccines_used":             int(__wards_total("vaccines")),
            "wards":                    ward_data,
            "reports":                  __wards_total("reports"),
            "netcards":                 __wards_total("netcards"),
            "beneficiaries":            __wards_total("beneficiaries"),
            "nets_total":               __wards_total("nets"),
            "nets_reports":             __wards_total("nets_reports"),
            "netcards_stats":           __stats("netcards"),
            "nets_stats":               __nets_stats("nets"),
            "beneficiaries_stats":      __stats("beneficiaries")
        }

    return { "pilot_lgas": map(__lga_data, lgas) }


@register.inclusion_tag("ipd/partials/logistics.html")
def logistics_summary():

    # called to fetch and assemble the data structure
    # for each LGA, containing the flow of stock
    def __lga_data(lga):
        incoming = PartialTransaction.objects.filter(destination=lga, type__in=["R", "I"]).order_by("-date")
        outgoing = PartialTransaction.objects.filter(origin=lga, type__in=["R", "I"]).order_by("-date")
        return {
            "name":         unicode(lga),
            "transactions": incoming | outgoing, 
            "logistician": lga.one_contact('SM', True)}
    
    # process and return data for ALL LGAs for this report
    return { "lgas": map(__lga_data, LocationType.objects.get(name="LGA").locations.filter(code__in=constants.KANO_PILOT_LGAS).all()) }

@register.inclusion_tag("ipd/partials/immunization_summary_charts.html")
def immunization_summary_charts():
    summary = pilot_summary()
    netcards_projected = []
    netcards_total = []
    nets_total = []
    population_projected = []
    immunized_total = []
    notimmunized_total = []
    vaccines_used = []
    lga_names = []
    pie_data = []
    data =[]
    #TODO: This must definitely be removed from here. It's a wild hack.
    compliance_summary = lambda x: int(sum(NonCompliance.objects.filter(reason=x).values_list('cases', flat=True)))
    # data = [ {"label":reason, "data":compliance_summary(reason_id)} for (reason_id, reason) in NonCompliance.NC_REASONS} ]

    #TODO: These should definitely leave here, and reside in their appropriate methods
    for reason_id, reason in NonCompliance.NC_REASONS:
        if compliance_summary(reason_id):
            pie_data.append((compliance_summary(reason_id), reason))

    pie_data_str = "[%s]" % ",".join(["{\"label\": \"%s\", \"data\": %d}" % (label,data) for (data, label) in pie_data])

    pilot_lgas = summary['pilot_lgas']
    for lga in pilot_lgas:
        #netcards_projected.append("[%d, %d]" % (pilot_lgas.index(lga) * 3 + 1, lga['netcards_projected']))
        netcards_total.append("[%d, %d]" % (pilot_lgas.index(lga) * 3 + 2, lga['netcards_total']))
        nets_total.append("[%d, %d]" % (pilot_lgas.index(lga) * 3 + 3, lga['nets_total']))
        population_projected.append("[%f, %f]" % (pilot_lgas.index(lga) * 4 + 0.5, lga['population_projected']))
        immunized_total.append("[%d, %d]" % (pilot_lgas.index(lga) * 4 + 1, lga['immunized_total']))
        notimmunized_total.append("[%f, %f]" % (pilot_lgas.index(lga) * 4 + 1.5, lga['notimmunized_total']))
        vaccines_used.append("[%d, %d]" % (pilot_lgas.index(lga) * 4 + 2, lga['vaccines_used']))
        lga_names.append("[%d, '%s']" % (pilot_lgas.index(lga) * 3 + 2, lga['name']))

    print "Loaded population"
    print population_projected
    
    return {
        "population_projected": "[%s]" % ",".join(population_projected),
        "immunized_total": "[%s]" % ",".join(immunized_total),
        "notimmunized_total": "[%s]" % ",".join(notimmunized_total),
        "vaccines_used": "[%s]" % ",".join(vaccines_used),
        "netcards_projected": "[%s]" % ",".join(netcards_projected),
        "netcards_total": "[%s]" % ",".join(netcards_total),
        "pie_data": pie_data_str,
        "nets_total": "[%s]" % ",".join(nets_total),
        "lgas": "[%s]" % ",".join(lga_names)
    }
