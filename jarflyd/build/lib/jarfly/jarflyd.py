#!/bin/env python

import syslog
import config
import vyatta
import jarnets


def processJar(confobj, curjar):

    # Start processing the current jar
    syslog.syslog(syslog.LOG_INFO | syslog.LOG_DAEMON,
                  "Processing jar %s" % curjar)

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

    # Get the config
    confobj = config.GetConfig()

    # Log the startup
    syslog.syslog(syslog.LOG_INFO | syslog.LOG_DAEMON, "Starting jarflyd")

    # Start reading in the controller sections
    sections = confobj.sections()
    for section in sections:
        if section.startswith("jar-"):
            processJar(confobj, section)


if __name__ == "__main__":
    main()
