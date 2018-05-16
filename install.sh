#!/bin/bash

echo "Package Install"
apt update
apt install python-pip mariadb-server libmysqlclient-dev dnsmasq ntp nginx tftpd-hpa tftp -y
pip install pygics ipaddress netifaces
echo ""

echo "System Setting"
mkdir -p /opt/data
echo "1. Enable Routing"
sed -i -e "s/#net.ipv4.ip_forward=1/net.ipv4.ip_forward=1/g" /etc/sysctl.conf
sysctl -p
echo "2. Service Init"
echo "2.1. Dnsmasq"
systemctl disable dnsmasq && systemctl stop dnsmasq
echo "2.2. NTP"
systemctl enable ntp && systemctl restart ntp
echo "2.3. NginX"
cat <<EOF> /etc/nginx/nginx.conf
worker_processes  1;
events {
    worker_connections  1024;
}
http {
    include            mime.types;
    default_type       application/octet-stream;
    sendfile           on;
    keepalive_timeout  65;
    server {
        listen         80;
        location / {
            alias /opt/data/;
        }
        error_page     500 502 503 504 /50x.html;
        location = /50x.html {
            root   html;
        }
    }
}
EOF
systemctl enable nginx && systemctl restart nginx
echo "2.4. TFTP"
cat <<EOF> /etc/default/tftpd-hpa
TFTP_USERNAME="tftp"
TFTP_DIRECTORY="/opt/data"
TFTP_ADDRESS=":69"
TFTP_OPTIONS="--secure --create"
EOF
systemctl enable tftpd-hpa && systemctl restart tftpd-hpa
echo "3. Copy rdhcp Binary"
cp xtra/bin/rdhcp /usr/bin/rdhcp
chmod 755 /usr/bin/rdhcp
echo ""

echo "Database Initialization"
mysql_secure_installation
systemctl enable mysql && systemctl restart mysql
echo ""

