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
                  "Checking for network %s(%s)" % (name, subnet))

    # Create cloudservers object
    cnobj = pyrax.cloud_networks

    # Return the network if it exists
    networks = cnobj.list()
    for network in networks:
        if network.label == name:
            if network.cidr != subnet:
                network.delete()
                syslog.syslog(syslog.LOG_INFO | syslog.LOG_DAEMON,
                              "No cidr match removing net %s" % name)
            else:
                syslog.syslog(syslog.LOG_INFO | syslog.LOG_DAEMON,
                              "Network %s exists" % name)
                return network

    # Create a new network and return it
    syslog.syslog(syslog.LOG_INFO | syslog.LOG_DAEMON,
                  "Creating network %s with subnet of %s" % (name, subnet))
    newnetwork = cnobj.create(name, cidr=subnet)
    return newnetwork
