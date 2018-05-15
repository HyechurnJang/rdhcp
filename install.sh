#!/bin/bash

echo "Package Install"
apt update
apt install python-pip mariadb-server libmysqlclient-dev dnsmasq ntp -y
pip install pygics ipaddress netifaces
echo ""

echo "System Setting"
sed -i -e "s/#net.ipv4.ip_forward=1/net.ipv4.ip_forward/g" /etc/sysctl.conf
sysctl -p
systemctl disable dnsmasq
systemctl stop dnsmasq
systemctl enable ntp
systemctl restart ntp
cp xtra/bin/rdhcp /usr/bin/rdhcp
chmod 755 /usr/bin/rdhcp
echo ""

echo "Database Initialization"
mysql_secure_installation
systemctl enable mysql
systemctl restart mysql
echo ""

