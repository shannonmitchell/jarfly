#!/bin/env python

import sys
import pyrax
import jarlog
import config
import vyatta
import jarnets
import ConfigParser


def addKey(keyname, keyfile):

    # Read the key in and fail if it can't
    jarlog.logit('INFO', "Checking ssh public key %s" % keyname)
    try:
        keystring = open(keyfile).read()
    except IOError:
        jarlog.logit('ERROR', "Failed reading key from " + keyfile)
        sys.exit()

    # Add the key after verifying it doesn't already exist.  Make sure it
    # matches.
    addkeypair = 1
    csobj = pyrax.cloudservers
    keypairs = csobj.keypairs.list()
    for keypair in keypairs:
        if keypair.name == keyname:
            if keypair.public_key == keystring:
                jarlog.logit('INFO', "SSH public key exists")
                addkeypair = 0
            else:
                jarlog.logit('INFO', "SSH public key exists with \
                             different value. Removing")
                keypair.delete()

    if addkeypair == 1:
        jarlog.logit('INFO', "Adding ssh public key %s" % keyname)
        csobj.keypairs.create(keyname, keystring)


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

    # To keep things simple, we are using a single global ssh key for the javad
    # process.  We can easily add support per jar later if needed.
    keyname = confobj.get("global", "ssh_public_key_name")
    keyfile = confobj.get("global", "ssh_public_key_file")
    addKey(keyname, keyfile)

    # Make sure vyatta server exists and is configured
    vyatta.configureDevice(confobj, curjar, dmznet, appnet, datanet, keyname)


def main():

    # Log the startup
    jarlog.logit('INFO', "Starting jarflyd")

    # Get the config
    confobj = config.GetConfig()

    # Set up the identity type
    pyrax.set_setting("identity_type", "rackspace")

    # Set up the credentials file
    cred_file = confobj.get("global", "credentials_file")
    jarlog.logit('INFO', "Authenticating using cred file: %s" % cred_file)
    pyrax.set_credential_file(cred_file)

    # Set up the default region
    globalRegion = confobj.get("global", "region")
    jarlog.logit('INFO', "Setting global region to: %s" % globalRegion)
    pyrax.connect_to_services(region=globalRegion)

    # Start reading in the jar sections
    sections = confobj.sections()
    for section in sections:
        if section.startswith("jar-"):
            processJar(confobj, section)


if __name__ == "__main__":
    main()
