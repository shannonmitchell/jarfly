#
# Cookbook Name:: cloud_edge_cookbook
# Recipe:: default
#
# Copyright 2013, YOUR_COMPANY_NAME
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
#


#######################
# Enable ip forwarding
#######################
bash "enable_ip_forwarding" do
	user    "root"
	cwd     "/root"
	creates "/etc/sysctl.conf.before_ip_forward"
	code <<-EOH
	egrep '^net.ipv4.ip_forward.*=.*0$' /etc/sysctl.conf > /dev/null
	if [ $? == 0 ]
	then
	  /bin/sed -i.before_ip_forward -e 's/net.ipv4.ip_forward.*/net.ipv4.ip_forward = 1/' /etc/sysctl.conf
	  /sbin/sysctl -p > /dev/null 2>&1
	fi
	exit 0
	EOH
end


##############################################
# Create the iptables firewall via a template
##############################################
template "/etc/sysconfig/iptables" do
	source "iptables.erb"
	mode 0600
	owner "root"
	group "root"
	variables({
		:iptables_filter_chains => node[:iptables][:filter][:chains],
		:iptables_filter_chain_input => node[:iptables][:filter][:chain][:INPUT],
		:iptables_filter_chain_forward => node[:iptables][:filter][:chain][:FORWARD],
		:iptables_nat_chain_postrouting => node[:iptables][:nat][:chain][:POSTROUTING],
		:iptables_filter_chain_inputjumps => node[:iptables][:filter][:chain][:INPUT_JUMPS],
		:iptables_filter_chain_forwardjumps => node[:iptables][:filter][:chain][:FORWARD_JUMPS],
		:iptables_filter_chain_openvpn_input => node[:iptables][:filter][:chain][:OPENVPN_INPUT],
		:iptables_filter_chain_openvpn_forward => node[:iptables][:filter][:chain][:OPENVPN_FORWARD],
	})
end


service "iptables" do
	action [:enable, :start]
	subscribes :restart, resources("template[/etc/sysconfig/iptables]"), :immediately
end


##################
# Set up OpenVPN
##################
include_recipe "yum::epel"

node.override['openvpn']['gateway'] = "edge01.linuxrackers.com"
node.override['openvpn']['subnet'] = "10.8.0.0"
node.override['openvpn']['netmask'] = "255.255.255.0"
node.override['openvpn']['key']['country'] = "US"
node.override['openvpn']['key']['province'] = "TX"
node.override['openvpn']['key']['city'] = "San Antonio"
node.override['openvpn']['key']['org'] = "edge01.linuxrackers.com"
node.override['openvpn']['key']['email'] = "shannon.mitchell@linuxrackers.com"
node.override['openvpn']['routes'] = [
	"push 'route 192.168.44.0 255.255.255.0'", 
	"push 'route 192.168.55.0 255.255.255.0'",
	"push 'route 192.168.66.0 255.255.255.0'"
]

include_recipe "openvpn"
include_recipe "openvpn::users"
