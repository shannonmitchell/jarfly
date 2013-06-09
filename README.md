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

The following can be used to deploy it.

    # python deploy_scripts/create_edge_server.py  --fqdn chef.<yourdomain>.com --public_keyfile /root/.ssh/id_rsa.pub



Configure the Edge Device with Chef
-----------------------------------

Some of this is manual now as I'm still in the process of learning chef.  This will be cleaned up in the future. 


Install 3rd Party Cookbooks

    # knife cookbook site download yum
    Downloading yum from the cookbooks site at version 2.2.2 to /root/yum-2.2.2.tar.gz
    Cookbook saved: /root/yum-2.2.2.tar.gz
    # tar -zxvf yum-2.2.2.tar.gz
    # knife cookbook upload --cookbook-path ./ yum
    Uploading yum            [2.2.2]
    Uploaded 1 cookbook.


    # knife cookbook site download openvpn
    Downloading openvpn from the cookbooks site at version 1.1.0 to /root/cookbooks/openvpn-1.1.0.tar.gz
    Cookbook saved: /root/cookbooks/openvpn-1.1.0.tar.gz
    # tar -zxvf openvpn-1.1.0.tar.gz 
    # knife cookbook upload --cookbook-path ./ openvpn



Upload the Edge Device Cookbook

    # knife cookbook upload --cookbook-path ~/jarfly/cookbooks/ cloud_edge_cookbook
    Uploading cloud_edge_cookbook [0.1.0]
    Uploaded 1 cookbook.



Assign the Cookbook to the Edge Device

    # knife node run_list add edge01.linuxrackers.com 'cloud_edge_cookbook'


Log in the edg01 device and test with chef-client

    # chef-client



Adding VPN Keys and Configuring the Client
-------------------------------------------

The openvpn cookbook uses a 'users' databag to create certificates for vpn connectivity.  You an do the following to create a databag user and re-run chef-client on the host.

    # knife data bag create users shannonmitchell
    {
      "id": "shannonmitchell"
    }

   [root@edge01]# chef-client


This will create a .tar.gz file under /etc/openvpn/keys. You can send this to the user needing to connect.  It contains the private key, ca cert and user cert.


Configuring VPN Client(NetworkManager/Fedora Tested)
----------------------------------------------------

Copy the username.tar.gz from the /etc/openvpn/keys directory to your vpn client.  If you have selinux enabled you will need to fix the context(works on fedora 18)

    # chcon -t openvpn_t <username>.crt
    # chcon -t openvpn_t <username>.key
    # chcon -t openvpn_t ca.crt


  *  Network Manger → Network Settings
  *  Click '+' ⇒ 'VPN' ⇒ 'Create' ⇒ 'OpenVPN' ⇒ 'Create'
  *  Connection name: <something descriptive>
  *  Ipv4 Settings(Tab) ⇒ 'Routes' ⇒ 'Use this connection only for resources on its network'
  *  VPN(Tab) ⇒ Gateway: <ip address of edge device>
  *  VPN(Tab) ⇒ User Cert, Private Key and CA Cert(copy these from /etc/openvpn/easy-rsa/keys and select them.
  *  VPN(Tab) ⇒ 'Advanced' ⇒ Unselect 'Use a TCP Connection' and select 'Use LZO data compression'


If you have issues, run a tail on /var/log/messages to find the errors. You will get a tls connect error if you didn't copy and select the ca.cert from the server. 


