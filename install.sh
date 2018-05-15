#!/bin/bash

apt update
apt install python-pip mariadb-server libmysqlclient-dev dnsmasq ntp -y
pip install pygics ipaddress netifaces

systemctl disable dnsmasq
systemctl stop dnsmasq
systemctl enable ntp
systemctl restart ntp

mysql_secure_installation
systemctl enable mysql
systemctl restart mysql

