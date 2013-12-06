#!/bin/env python

import pyrax
import syslog


def configureNetwork(confobj, name, subnet):

    # Set up the credentials file
    cred_file = confobj.get("global", "credentials_file")
    syslog.syslog(syslog.LOG_INFO | syslog.LOG_DAEMON,
                  "Authenticating using cred file: %s" % cred_file)
    pyrax.set_credential_file(cred_file)

    # Start processing the current jar
    syslog.syslog(syslog.LOG_INFO | syslog.LOG_DAEMON,
                  "Checking network %s(%s)" % (name, subnet))

    # Create cloudservers object
    cnobj = pyrax.cloud_networks

    # Return the network if it exists
    networks = cnobj.list()
    for network in networks():
        print network
        if network.label == name:
            return network

    # Create a new network and return it
    #newnetwork = cnobj.create(name, cidr=subnet)
    #return newnetwork
