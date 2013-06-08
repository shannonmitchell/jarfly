default["iptables"]["filter"]["chain"]["INPUT"] = [ 
	"-A INPUT -m state --state ESTABLISHED,RELATED -j ACCEPT",
	"-A INPUT -p icmp -j ACCEPT",
	"-A INPUT -i lo -j ACCEPT",
	"-A INPUT -m state --state NEW -m tcp -p tcp --dport 22 -j ACCEPT",
	"-A INPUT -j LOG",
	"-A INPUT -j REJECT --reject-with icmp-host-prohibited",
]

default["iptables"]["filter"]["chain"]["FORWARD"] = [ 
	"-A FORWARD -m state --state RELATED,ESTABLISHED -j ACCEPT",
	"-A FORWARD -s 192.168.44.0/24 -j ACCEPT",
	"-A FORWARD -s 192.168.55.0/24 -j ACCEPT",
	"-A FORWARD -s 192.168.66.0/24 -j ACCEPT",
	"-A FORWARD -j REJECT --reject-with icmp-host-prohibited",
]

default["iptables"]["nat"]["chain"]["POSTROUTING"] = [ 
	"-A POSTROUTING -o eth0 -j MASQUERADE", 
]

default["iptables"]["filter"]["chain"]["INPUT_JUMPS"] = [ 
	"-A INPUT -j OPENVPN_INPUT",
]

default["iptables"]["filter"]["chain"]["FORWARD_JUMPS"] = [ 
	"-A FORWARD -j OPENVPN_FORWARD",
]


default["iptables"]["filter"]["chains"] = [
	":OPENVPN_INPUT - [0:0]",
	":OPENVPN_FORWARD - [0:0]",
]

default["iptables"]["filter"]["chain"]["OPENVPN_INPUT"] = [
	"-A OPENVPN_INPUT -p udp -m udp --dport 1194 -j ACCEPT",
	"-A OPENVPN_INPUT -s 10.8.0.0/24 -j ACCEPT",
]	

default["iptables"]["filter"]["chain"]["OPENVPN_FORWARD"] = [
	"-A OPENVPN_FORWARD -s 10.8.0.0 -d 192.168.44.0/24 -j ACCEPT",
	"-A OPENVPN_FORWARD -s 10.8.0.0 -d 192.168.55.0/24 -j ACCEPT",
	"-A OPENVPN_FORWARD -s 10.8.0.0 -d 192.168.66.0/24 -j ACCEPT",
]	

