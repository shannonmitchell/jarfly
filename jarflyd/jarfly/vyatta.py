#!/bin/env python

import pyrax
import syslog


def configureDevice(confobj, curjar, dmznet, appnet, datanet):

    # Set up the credentials file
    cred_file = confobj.get("global", "credentials_file")
    syslog.syslog(syslog.LOG_INFO | syslog.LOG_DAEMON,
                  "Authenticating using cred file: %s" % cred_file)
    pyrax.set_credential_file(cred_file)

    # Start processing the current jar
    syslog.syslog(syslog.LOG_INFO | syslog.LOG_DAEMON,
                  "Checking vyatta config for: %s" % curjar)

    # Create cloudservers object
    csobj = pyrax.cloudservers

    # Check for image
    images = csobj.list_images()
    for image in images:
        if image.name == confobj.get(curjar, "vyatta_image"):
            vimage = image

    # Check for flavor
    flavors = csobj.list_flavors()
    for flavor in flavors:
        if flavor.name == confobj.get(curjar, "vyatta_flavor"):
            vflavor = flavor

    # Configure nics argument
    nics_list = [{'net-id': '00000000-0000-0000-0000-000000000000'},
                 {'net-id': '11111111-1111-1111-1111-111111111111'},
                 {'net-id': dmznet.id},
                 {'net-id': appnet.id},
                 {'net-id': datanet.id}]

