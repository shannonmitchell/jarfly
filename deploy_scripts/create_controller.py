#!/usr/bin/env python

import os
import pyrax


# Create networks
def create_network(cnetobj, label, subnet):
    networks = cnetobj.list()
    for network in networks:
        if network.label == label:
            print "A network with the label %s already exists. \
                   Returning match.\n" % (label)
            return network

    print "Creating network with label %s and subnet \
                                %s\n" % (label, subnet)
    newnetwork = cnetobj.create(label, cidr=subnet)
    return newnetwork

def main():

    # Set the credentials file up
    cred_file = "%s/.rackspace_cloud_credentials" % (os.environ['HOME'])
    print "Setting authentication file to %s" % (cred_file)
    pyrax.set_credential_file(cred_file)

    # Check for existing
    csobj = pyrax.cloudservers

    # Get the vyatta image
    images = csobj.list_images()
    for image in images:
        if image.name == "CentOS 6.4":
            vimage = image
            print "Found image: " + vimage.name

    # Get the needed flavor
    flavors = csobj.list_flavors()
    for flavor in flavors:
        if flavor.name == "512MB Standard Instance":
            vflavor = flavor
            print "Found flavor: " + vflavor.name

    # Create your keypair if it doens't already exist
    addkey = 1
    keypairs = csobj.keypairs.list()
    for keypair in keypairs:
        if keypair.name == "my_key":
            print "keypair " + keypair.name + " exists. Skipping creation"
            addkey = 0
    if addkey == 1:
        with open(os.path.expanduser("~/.ssh/id_rsa.pub")) as keyfile:
            csobj.keypairs.create("my_key", keyfile.read())

    # Pull the existing network and get the nic config set up
    cnobj = pyrax.cloud_networks
    appnet = create_network(cnobj, "app", "192.168.34.0/24")
    nics_list = [{'net-id': appnet.id}]

    # Create your server
    addserver = 1
    servers = csobj.servers.list()
    for server in servers:
        if server.name == "controller.linuxrackers.com":
            print "Server " + server.name + " exists. Skipping creation"
            serverafter = server
            addserver = 0

    if addserver == 1:
        server = csobj.servers.create("controller.linuxrackers.com",
                                      vimage.id, vflavor.id, nics=nics_list,
                                      key_name="my_key")
        serverafter = pyrax.utils.wait_until(server, "status",
                                             ["ACTIVE", "ERROR"])

    # print the network & pass info
    print "Server Networks: "
    print serverafter.networks
    print "Server Password "
    print serverafter.adminPass


if __name__ == '__main__':
    main()
