#!/bin/env python

import pyrax
import jarlog


def configureNetwork(confobj, name, subnet):

    # Start processing the current jar
    jarlog.logit('INFO', "Checking for network %s(%s)" % (name, subnet))

    # Create cloudservers object
    cnobj = pyrax.cloud_networks

    # Return the network if it exists
    networks = cnobj.list()
    for network in networks:
        if network.label == name:
            if network.cidr != subnet:
                network.delete()
                jarlog.logit('INFO', "No cidr match removing net %s" % name)
            else:
                jarlog.logit('INFO', "Network %s exists" % name)
                return network

    # Create a new network and return it
    jarlog.logit('INFO', "Creating network %s with subnet of %s" % (name, subnet))
    newnetwork = cnobj.create(name, cidr=subnet)
    return newnetwork
