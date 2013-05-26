#!/usr/bin/env python

import os
import sys
import time
import pyrax
import argparse


# Create a function to take care of the dns record creation
def create_dns(cdnsobj, fqdn, ip_address):

    # Add the domain record
    domains = cdnsobj.list()
    for domain in domains:
        if fqdn.endswith(domain.name):
            print "Found a matching domain: " + domain.name + " for fqdn: " \
                + fqdn
            recs = [{'type': 'A', 'name': fqdn, 'data': ip_address,
                    'ttl': 6000}]

            # Check if the record already exists and return it instead
            records = domain.list_records()
            for record in records:
                if record.name == fqdn and record.data == ip_address:
                    print "Record already exists. Skipping"
                    return 0

             # Add record if we made it this far and return from function
            print "Adding record: \n\t" + fqdn + "   IN  A  " + ip_address
            cdnsobj.add_records(domain, recs)
            return 0


# Check for an existing domain
def check_dns(cdnsobj, fqdn):

    # Add the domain record
    domains = cdnsobj.list()
    found_domain = 0
    for domain in domains:
        if fqdn.endswith(domain.name):
            found_domain = 1

    # Bounce if the domain doesn't exist
    if found_domain != 1:
        print "Domain for FQDN of " + fqdn + " doesn't exist for this account."
        sys.exit(1)


# Get the flavor id from the name
def get_flavor_from_id_or_name(csobj, given_flavor_value):

    flavors = csobj.flavors.list()
    flavor_id = ""
    for flavor in flavors:
        if flavor.id == given_flavor_value or \
           flavor.name == given_flavor_value:
            print "Found flavor with name of \"" + flavor.name + "\""
            flavor_id = flavor.id
    if flavor_id == "":
        print "\nFlavor with name or id of " + given_flavor_value + \
            " does not exist. Please use a flavor id or name from \
            the following available values:\n"
        for flavor in flavors:
            print "id: %s  =>  name: \"%s\"" % (flavor.id, flavor.name)
        sys.exit(1)
    return flavor_id


# Get the image id from the name
def get_image_from_id_or_name(csobj, given_image_value):

    images = csobj.images.list()
    image_id = ""
    for image in images:
        if image.id == given_image_value or image.name == given_image_value:
            print "Found image with name of \"" + image.name + "\""
            image_id = image.id
    if image_id == "":
        print "\nImage with name or id of " + given_image_value + \
            " does not exist. Please use a image id or name from \
            the following available values:\n"
        for image in images:
            print "id: %s  =>  name: \"%s\"" % (image.id, image.name)
        sys.exit(1)
    return image_id


# Check the public key file and return the dictionary for server creation
def check_pub_key_file(given_filename):

    if os.path.isfile(given_filename):
        print "Public Key File " + given_filename + " exists."
        try:
            pkfile = open(given_filename, 'r')
            content = pkfile.read()
            retfiles = {"/root/.ssh/authorized_keys": content}
            return retfiles
        except IOError as e:
            print "Sorry, but we had trouble opening file " + \
                given_filename + ". exiting"
            print("({})".format(e))
            sys.exit(1)
    else:
        print "Public key file " + given_filename + " does exist. \
                Please create using a ssh-keygen and run again."


# Create the instance
def create_server(csobj, instance_name, flavor_id, image_id, files_dict):

    # Get the server list
    servers = csobj.servers.list()
    for server in servers:
        if server.name == instance_name:
            print "Server by the name of " + instance_name + \
                " already exists."
            return server

    print "Creating new server by the name of " + instance_name
    newserver = csobj.servers.create(instance_name, image_id, flavor_id,
                                     files=files_dict)
    return newserver


# Wait for created servers finish building and return object
def wait_and_update(csobj, server_obj):

    # Loop and wait until the server is in an ACTIVE status
    while 1:
        curserver = csobj.servers.get(server_obj.id)

        if curserver.status == 'ACTIVE':
            return curserver
        else:
            print "Waiting for server to finish building. Sleeping \
                    60 seconds."
            time.sleep(60)


# Print useful data
def print_info(passwd, server_obj):
    print "\n\n"
    print "#########################"
    print "# Chef Server Information"
    print "#########################"
    print "cloud id: %s\n" % (server_obj.id)
    print "fqdn:     %s\n" % (server_obj.name)
    print "password: %s\n" % (passwd)
    print "ipaddr:   %s\n" % (server_obj.accessIPv4)


def main():

    # Parse the command line arguments
    parser = argparse.ArgumentParser(
        description="Create chef server for cloud edge env.",
        prog='create_chef_server.py')
    parser.add_argument(
        '--image', help='image id or name Ubuntu 12.10 \
        (Quantal Quetzal)', default='Ubuntu 12.10 (Quantal Quetzal)')
    parser.add_argument(
        '--flavor', help='flavor id or name (default: 512MB Standard \
        Instance)', default='512MB Standard Instance')
    parser.add_argument(
        '--region', help='Region (default: DFW)', default="DFW")
    parser.add_argument(
        '--fqdn', help='fully qualified domain name', required=True)
    parser.add_argument(
        '--public_keyfile', help='ssh public key file', required=True)
    args = parser.parse_args()

    # Authenticate using a credentials file: "~/.rackspace_cloud_credentials"
    cred_file = "%s/.rackspace_cloud_credentials" % (os.environ['HOME'])
    print "Setting authentication file to %s" % (cred_file)
    pyrax.set_credential_file(cred_file)

    # Instantiate a cloudservers object
    print "Instantiating cloudservers object"
    csobj = pyrax.cloudservers

    # Instantiate a clouddns object
    print "Instantiating cloud_dns object"
    cdnsobj = pyrax.cloud_dns

    # Get the flavor id
    flavor_id = get_flavor_from_id_or_name(csobj, args.flavor)

    # Get the image id
    image_id = get_image_from_id_or_name(csobj, args.image)

    # Lets check the domain existance for the fqdn before going on
    check_dns(cdnsobj, args.fqdn)

    # Check public key file
    cs_files = check_pub_key_file(args.public_keyfile)

    # Create the servers by server_count
    orig_server = create_server(csobj, args.fqdn, flavor_id, image_id,
                                cs_files)

    # Call function to wait on it to build
    updated_server = wait_and_update(csobj, orig_server)

    # Create a DNS entry for the server
    create_dns(cdnsobj, args.fqdn, updated_server.accessIPv4)

    # Print server information and exit
    print_info(orig_server.adminPass, updated_server)


if __name__ == "__main__":
    main()
