jarfly
======

RS cloud environment secured behind an edge device. (Work in Progress)


Description
-----------

I'm creating this mainly to store scripts and cookbooks for creating a cloud edge device which sits in front of private networks for the dmz/webhead, application and database layers.  Its also ment to security access between each network, allow vpn access to the private networks and perform some basic load balancing for the webheads.


Workstation Prep
----------------

We will start out with preparing the workstation.  This was designed for a Rackspace cloud environment, so you will need to set up pyrax on your workstation. You can follow the instructions at the following link to set it up.

https://github.com/rackspace/pyrax


You will probably want to set up the openstack novaclient if you don't want to keep logging into the gui to work with your systems. 

https://github.com/openstack/python-novaclient


We will be using the workstation to create the servers and work with the chef server to configure the systems afterwards.  You can clone the jarfly repository befor getting started.

    # git clone https://github.com/shannonmitchell/jarfly


The python scripts requires a .rackspace_cloud_credentials file in your home directory. 

    # vi ~/.rackspace_cloud_credentials

    [rackspace_cloud]
    username = rackspace_username
    api_key = rackspace_apikey

If you want a different region then DFW you may want create a pyrax config file as well. 

    # vi ~/.pyrax.cfg
    [settings]
    region = ORD





Chef Server Creation
--------------------

create_chef_server.py is a python script that uses pyrax to create the chef server, copy your ssh public key over and run a /root/chef_install.sh script on the new server.  The install script downlowloads and installes chef.  It then ugrades the server and reboots.  The domain of the fqdn must be one created via cloud dns in your cloud account.

    # python deploy_scripts/create_chef_server.py  --fqdn chef.<yourdomain>.com --public_keyfile /root/.ssh/id_rsa.pub


Log into the server and set your password(https://chef.(yourdomain).com).  The password will be given on the front page, so change it quick. 





Configure your Chef Workstation
--------------------------------

We will need to copy the /etc/chef-server/chef-validator.pem(and admin.pem) to your .chef server on the workstation.  In this example we have a 'workstation' user to use.  We are also installing knife-rackspace wich will automatically install the chef client.


    # gem install knife-rackspace


    # mkdir -p ~/.chef
    # scp root@chef.<yourdomain>.com:/etc/chef-server/chef-validator.pem ~/.chef/
    # scp root@chef.<yourdomain>.com:/etc/chef-server/admin.pem ~/.chef/
    # chown -R $USER ~/.chef



    # knife configure --initial
    Overwrite /home/workstation/.chef/knife.rb? (Y/N) Y
    Please enter the chef server URL: [http://curhost.<yourdomain>.com:4000] https://chef.<yourdomain>.com
    Please enter a name for the new user: [shannon.mitchell] workstation
    Please enter the existing admin name: [admin] 
    Please enter the location of the existing admin's private key: [/etc/chef/admin.pem] /home/workstation/.chef/admin.pem
    Please enter the validation clientname: [chef-validator] 
    Please enter the location of the validation key: [/etc/chef/validation.pem] /home/workstation/.chef/chef-validator.pem
    Please enter the path to a chef repository (or leave blank): 
    Creating initial API user...
    Please enter a password for the new user: 
    Created user[workstation]
    Configuration file written to /home/workstation/.chef/knife.rb


    # knife node list



Finish setting up knife-rackspacce.


    # cat <<EOF >> /home/workstation/.chef/knife.rb
    knife[:rackspace_api_username] = "<rackspace username goes here>"
    knife[:rackspace_api_key] = "<openstack api key goes here>"
    knife[:rackspace_version] = "v2"
    knife[:rackspace_auth_url] = "https://identity.api.rackspacecloud.com/v2.0/"
    knife[:rackspace_compute_url] = "https://dfw.servers.api.rackspacecloud.com/v2"
    EOF

    # knife rackspace flavor list
    # knife rackspace image list
    # knife rackspace list





Create the Cloud Edge Device
----------------------------

create_edge_server.py does the following:

  * creates 3 networks(web01, app01 and data01). 
  * creates a new sever with the public, private and 3 nics for the web01, app01 and data01 networks.
  * bootstraps the server using 'knife bootstrap' and ssh keys
  * assigns the edge device its proper chef roles and configures the server

    # python deploy_scripts/create_edge_server.py  --fqdn chef.<yourdomain>.com --public_keyfile /root/.ssh/id_rsa.pub

(work in progress)
