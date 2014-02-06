#!/bin/env python

import sys
import pyrax
import time
import jardns
import jarlog
import paramiko


def configureVyattaLogin(vserver, vpass, keytype, keyval, keyid):

    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    jarlog.logit('INFO', "host: " + vserver + " pass: " + vpass)
    client.connect(vserver, username='vyatta', password=vpass)
    commands = """
    /opt/vyatta/sbin/vyatta-cfg-cmd-wrapper begin
    /opt/vyatta/sbin/vyatta-cfg-cmd-wrapper set system login user vyatta authentication public-keys """ + keyid + """ key """ + keyval + """
    /opt/vyatta/sbin/vyatta-cfg-cmd-wrapper set system login user vyatta authentication public-keys """ + keyid + """ type """ + keytype + """
    /opt/vyatta/sbin/vyatta-cfg-cmd-wrapper commit
    /opt/vyatta/sbin/vyatta-cfg-cmd-wrapper end
    /opt/vyatta/sbin/vyatta-cfg-cmd-wrapper save
    """
    jarlog.logit('INFO', "Running initial viatta login config")
    stdin, stdout, stderr = client.exec_command(commands)
    for line in stdout:
        print '... ' + line.strip('\n')

    client.close()


def configureVyattaNats(vserver, vpass, dmznet, appnet, datanet):

    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    jarlog.logit('INFO', "host: " + vserver + " pass: " + vpass)
    client.connect(vserver, username='vyatta', password=vpass)
    commands = """
    /opt/vyatta/sbin/vyatta-cfg-cmd-wrapper begin
    /opt/vyatta/sbin/vyatta-cfg-cmd-wrapper set nat source rule 10 source address """ + dmznet + """
    /opt/vyatta/sbin/vyatta-cfg-cmd-wrapper set nat source rule 10 outbound-interface eth0
    /opt/vyatta/sbin/vyatta-cfg-cmd-wrapper set nat source rule 10 translation address masquerade
    /opt/vyatta/sbin/vyatta-cfg-cmd-wrapper set nat source rule 20 source address """ + appnet + """
    /opt/vyatta/sbin/vyatta-cfg-cmd-wrapper set nat source rule 20 outbound-interface eth0
    /opt/vyatta/sbin/vyatta-cfg-cmd-wrapper set nat source rule 20 translation address masquerade
    /opt/vyatta/sbin/vyatta-cfg-cmd-wrapper set nat source rule 30 source address """ + datanet + """
    /opt/vyatta/sbin/vyatta-cfg-cmd-wrapper set nat source rule 30 outbound-interface eth0
    /opt/vyatta/sbin/vyatta-cfg-cmd-wrapper set nat source rule 30 translation address masquerade
    /opt/vyatta/sbin/vyatta-cfg-cmd-wrapper commit
    /opt/vyatta/sbin/vyatta-cfg-cmd-wrapper save
    /opt/vyatta/sbin/vyatta-cfg-cmd-wrapper end
    """
    jarlog.logit('INFO', "Running initial viatta app config" + commands)
    stdin, stdout, stderr = client.exec_command(commands)
    for line in stdout:
        print '... ' + line.strip('\n')

    client.close()



def configureVyattaVPN(vserver, vpass, vpnshared_pass, vpnuser, vpnpass, range_start, range_end):

    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    jarlog.logit('INFO', "host: " + vserver + " pass: " + vpass)
    client.connect(vserver, username='vyatta', password=vpass)
    commands = """
    /opt/vyatta/sbin/vyatta-cfg-cmd-wrapper begin
    /opt/vyatta/sbin/vyatta-cfg-cmd-wrapper set vpn ipsec ipsec-interfaces interface eth0
    /opt/vyatta/sbin/vyatta-cfg-cmd-wrapper set vpn ipsec nat-traversal enable
    /opt/vyatta/sbin/vyatta-cfg-cmd-wrapper set vpn ipsec nat-networks allowed-network 0.0.0.0/0
    /opt/vyatta/sbin/vyatta-cfg-cmd-wrapper set vpn l2tp remote-access outside-address """ + vserver + """
    /opt/vyatta/sbin/vyatta-cfg-cmd-wrapper set vpn l2tp remote-access client-ip-pool start """ + range_start + """
    /opt/vyatta/sbin/vyatta-cfg-cmd-wrapper set vpn l2tp remote-access client-ip-pool stop """ + range_end + """
    /opt/vyatta/sbin/vyatta-cfg-cmd-wrapper set vpn l2tp remote-access ipsec-settings authentication mode pre-shared-secret
    /opt/vyatta/sbin/vyatta-cfg-cmd-wrapper set vpn l2tp remote-access ipsec-settings authentication pre-shared-secret """ + vpnshared_pass + """
    /opt/vyatta/sbin/vyatta-cfg-cmd-wrapper set vpn l2tp remote-access authentication mode local
    /opt/vyatta/sbin/vyatta-cfg-cmd-wrapper set vpn l2tp remote-access authentication local-users username """ + vpnuser + """ password """ + vpnpass + """
    /opt/vyatta/sbin/vyatta-cfg-cmd-wrapper commit
    /opt/vyatta/sbin/vyatta-cfg-cmd-wrapper save
    /opt/vyatta/sbin/vyatta-cfg-cmd-wrapper end
    """
    jarlog.logit('INFO', "Running initial viatta app config" + commands)
    stdin, stdout, stderr = client.exec_command(commands)
    for line in stdout:
        print '... ' + line.strip('\n')

    client.close()

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

    # Vyatta doesn't respect the ssh keys set via openstack.  Setting it
    # manually here.
    jarlog.logit('INFO', "Setting up vyatta user ssh auth file")
    keyfile = confobj.get("global", "ssh_public_key_file")
    try:
        keystring = open(keyfile).read()
        keytype = keystring.split()[0]
        keyval = keystring.split()[1]
        keyid = keystring.split()[2]

    except IOError:
        jarlog.logit('INFO', "Error opening: %s" % keyfile)
        sys.exit()

    # Create the vyatta server
    addserver = 1
    vyatta_name = confobj.get(curjar, 'vyatta_name')
    servers = csobj.servers.list()
    for server in servers:
        if server.name == vyatta_name:
            jarlog.logit('INFO', "Server " + server.name +
                         " already exists.  Skipping creation")
            addserver = 0
            curserver = server

    if addserver == 1:
        origserver = csobj.servers.create(vyatta_name, vimage.id, vflavor.id,
                                          key_name=keyname, nics=nics_list)

        curserver = pyrax.utils.wait_until(origserver, "status",
                                           ["ACTIVE", "ERROR"])
        print "Server Password "
        print curserver.adminPass

    # Add domain entry for the vyatta device
    jardns.addRecord(vyatta_name, curserver.accessIPv4)

    # print the network & pass info
    print "Server Networks: "
    print curserver.accessIPv4

    # Sleep for a few seconds to wait for things to process before
    # configuration
    time.sleep(10)

    # Configure the Vyatta Login
    configureVyattaLogin(curserver.accessIPv4, curserver.adminPass,
                         keytype, keyval, keyid)

    # Configure the Vyatta Networking
    dmznet = confobj.get(curjar, "dmznet_cidr")
    appnet = confobj.get(curjar, "appnet_cidr")
    datanet = confobj.get(curjar, "datanet_cidr")
    configureVyattaNats(curserver.accessIPv4, curserver.adminPass,
                        dmznet, appnet, datanet)

    # Configure a Vyatta VPN
    vpn_shared_pass = confobj.get(curjar, "vpn_shared_pass")
    vpn_username = confobj.get(curjar, "vpn_username")
    vpn_password = confobj.get(curjar, "vpn_password")
    vpn_client_ip_range_start = confobj.get(curjar, "vpn_client_ip_range_start")
    vpn_client_ip_range_end = confobj.get(curjar, "vpn_client_ip_range_end")
    configureVyattaVPN(curserver.accessIPv4, curserver.adminPass,
                       vpn_shared_pass, vpn_username, vpn_password,
                       vpn_client_ip_range_start,
                       vpn_client_ip_range_end)


