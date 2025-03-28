
ip tuntap add name ogstun2 mode tun
ip addr add 10.47.0.0/16 dev ogstun2
ip link set ogstun2 mtu 1400
ip link set ogstun2 up
iptables -t nat -A POSTROUTING -s 10.47.0.0/16 ! -o ogstun2 -j MASQUERADE
iptables -I INPUT -i ogstun2 -j ACCEPT