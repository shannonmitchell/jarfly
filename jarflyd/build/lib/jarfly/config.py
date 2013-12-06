#!/bin/env python

import ConfigParser


def GetConfig():
    configfile = "/etc/jarfly/jarflyd.conf"
    myconfig = ConfigParser.ConfigParser()
    myconfig.read(configfile)
    return myconfig

