#!/bin/env python

import pyrax
import jarlog


def configureDevice(confobj, curjar, dmznet, appnet, datanet):

    # Start processing the current jar
    jarlog.logit('INFO', "Checking vyatta config for: %s" % curjar)

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

