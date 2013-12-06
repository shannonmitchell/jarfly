#!/bin/env python

import pyrax
import jarlog
import config
import vyatta
import jarnets
import ConfigParser


def processJar(confobj, curjar):

    # Start processing the current jar
    jarlog.logit('INFO', "Processing jar %s" % curjar)

    # Set up the jar region
    try:
        globalRegion = confobj.get("global", "region")
        jarRegion = confobj.get(curjar, "region")
        if jarRegion != globalRegion:
            jarlog.logit('INFO', "Setting jar region to: %s" % jarRegion)
            pyrax.connect_to_services(region=jarRegion)
    except ConfigParser.NoOptionError:
        jarlog.logit('INFO', "Jar region not set, keeping global of %s"
                     % globalRegion)

    # Make sure networks exist
    dmznet = jarnets.configureNetwork(confobj,
                                      confobj.get(curjar, "dmznet_name"),
                                      confobj.get(curjar, "dmznet_cidr"))
    appnet = jarnets.configureNetwork(confobj,
                                      confobj.get(curjar, "appnet_name"),
                                      confobj.get(curjar, "appnet_cidr"))
    datanet = jarnets.configureNetwork(confobj,
                                       confobj.get(curjar, "datanet_name"),
                                       confobj.get(curjar, "datanet_cidr"))

    # Make sure vyatta server exists and is configured
    vyatta.configureDevice(confobj, curjar, dmznet, appnet, datanet)


def main():

    # Log the startup
    jarlog.logit('INFO', "Starting jarflyd")

    # Get the config
    confobj = config.GetConfig()

    # Set up the credentials file
    cred_file = confobj.get("global", "credentials_file")
    jarlog.logit('INFO', "Authenticating using cred file: %s" % cred_file)
    pyrax.set_credential_file(cred_file)

    # Set up the default region
    globalRegion = confobj.get("global", "region")
    jarlog.logit('INFO', "Setting global region to: %s" % globalRegion)
    pyrax.connect_to_services(region=globalRegion)

    # Start reading in the controller sections
    sections = confobj.sections()
    for section in sections:
        if section.startswith("jar-"):
            processJar(confobj, section)


if __name__ == "__main__":
    main()
