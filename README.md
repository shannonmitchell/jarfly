jarfly
======

RS cloud environment secured behind an edge device. (Work in Progress)


Description
-----------

I'm creating this mainly to store scripts and cookbooks for creating a cloud edge device which sits in front of private networks for the dmz/webhead, application and database layers.  Its also ment to security access between each network, allow vpn access to the private networks and perform some basic load balancing for the webheads.


Workstation
-----------

We will start out with preparing the workstation.  This was designed for a Rackspace cloud environment, so you will need to set up pyrax on your workstation. You can follow the instructions at the following link to set it up.

https://github.com/rackspace/pyrax


You will probably want to set up the openstack novaclient if you don't want to keep logging into the gui to work with your systems. 

https://github.com/openstack/python-novaclient


We will be using the workstation to create the servers and work with the chef server to configure the systems afterwards.  You can clone the jarfly repository befor getting started.

<pre>
    # git clone https://github.com/shannonmitchell/jarfly
</pre>


The python scripts requires a .rackspace_cloud_credentials file in your home directory. 

    # vi ~/.rackspace_cloud_credentials

    [rackspace_cloud]
    username = rackspace_username
    api_key = rackspace_apikey

If you want a different region then DFW you may want create a pyrax config file as well. 

<code>
# vi ~/.pyrax.cfg
[settings]
region = ORD
</code>



Chef Server Creation
--------------------
