#!/bin/env python

import pyrax
import jarlog


def checkDomain(domainname, domainemail):

    # Start processing the current jar
    jarlog.logit('INFO', "Checking for domain %s" % domainname)

    # Create cloudservers object
    cdnsobj = pyrax.cloud_dns

    # Return the network if it exists
    createdomain = 1
    domains = cdnsobj.list()
    for domain in domains:
        if domain.name == domainname:
            createdomain = 0
            jarlog.logit('INFO', "Domain %s exists" % domainname)

    if createdomain == 1:
        jarlog.logit('INFO', "Creating Domain %s" % domainname)
        cdnsobj.create(name=domainname, emailAddress=domainemail)


def addRecord(recordname, recordvalue):

    # Start processing the record
    jarlog.logit('INFO', "Checking for record %s" % recordname)

    # Create cloudservers object
    cdnsobj = pyrax.cloud_dns

    # Create the record if needed
    domains = cdnsobj.list()
    addrecord = 0
    for domain in domains:
        if recordname.endswith(domain.name):
            jarlog.logit('INFO', "Found domain %s for record %s"
                         % (domain.name, recordname))
            curdomain = domain
            addrecord = 1

    # Skip if domain doesn't exist
    if addrecord == 0:
        jarlog.logit('INFO', "Couldn't find domain for %s, Skipping record creation" % recordname)
        return 1


    records = curdomain.list_records()
    addrecord = 1
    for record in records:
        if record.name == recordname:
            addrecord = 0
            # Check its value and fix if needed
            if record.data != recordvalue:
                jarlog.logit('INFO', "Updating record %s value to %s"
                             % (recordname, recordvalue))
                record.update(data=recordvalue)

    if addrecord == 1:
        insrecord = {"type": "A",
                     "name": recordname,
                     "data": recordvalue,
                     "ttl": 300}
        jarlog.logit('INFO', "Adding record %s with value of %s"
                     % (recordname, recordvalue))
        curdomain.add_records(insrecord)
