#!/bin/sh

# User web servers run without privilege to bind to port 80.
# Forward port 80 to a user web server running on port 5000.

# This uses fedora firewalld and does NOT work
# for connections from localhost

# Fedora already runs a firewall
# it supports port forwarding, so I don't drop to raw iptables

# this affects the current firewall.
# it does not make it persistent.
#
# (to do so, it is possible to open the firewall configuration gui,
# use Options -> Runtime to Permanent).

firewall-cmd --add-forward-port=port=80:proto=tcp:toport=5000
