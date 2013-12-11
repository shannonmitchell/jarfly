#!/bin/env python

import pyrax
import jardns
import jarlog


def configureDevice(confobj, curjar, dmznet, appnet, datanet, keyname):

    # Start processing the current jar
    jarlog.logit('INFO', "Checking vyatta config for: %s" % curjar)

    # Create cloudservers object
    csobj = pyrax.cloudservers

    # Check for image
    images = csobj.list_images()
    for image in images:
        if image.name == confobj.get(curjar, "vyatta_image"):
            jarlog.logit('INFO', "Found image: %s" % image.name)
            vimage = image

    # Check for flavor
    flavors = csobj.list_flavors()
    for flavor in flavors:
        if flavor.name == confobj.get(curjar, "vyatta_flavor"):
            jarlog.logit('INFO', "Found flavor: %s" % flavor.name)
            vflavor = flavor

    # Configure nics argument
    nics_list = [{'net-id': '00000000-0000-0000-0000-000000000000'},
                 {'net-id': '11111111-1111-1111-1111-111111111111'},
                 {'net-id': dmznet.id},
                 {'net-id': appnet.id},
                 {'net-id': datanet.id}]

    # Create the vyatta server
    addserver = 1
    vyatta_name = confobj.get(curjar, 'vyatta_name')
    servers = csobj.servers.list()
    for server in servers:
        if server.name == vyatta_name:
            jarlog.logit('INFO', "Server" + server.name +
                         " already exists.  Skipping creation")
            addserver = 0
            curserver = server

    if addserver == 1:
        origserver = csobj.servers.create(vyatta_name, vimage.id, vflavor.id,
                                          key_name=keyname, nics=nics_list)

        finserver = pyrax.utils.wait_until(origserver, "status",
                                           ["ACTIVE", "ERROR"])
        print "Server Password "
        print finserver.adminPass

    # Add domain entry for the vyatta device
    jardns.addRecord(vyatta_name, curserver.accessIPv4)

    # print the network & pass info
    print "Server Networks: "
    print curserver.accessIPv4
