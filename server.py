# -*- coding: utf-8 -*-
'''
Created on 2018. 4. 27.
@author: HyechurnJang
'''

import os
import pygics
import argparse

if __name__ == '__main__':
#     parser = argparse.ArgumentParser()
#     
#     parser.add_argument('-a', '--apic', help='APIC IP Address or Domain Name', required=True)
#     parser.add_argument('-u', '--username', help='APIC User Name', required=True)
#     parser.add_argument('-p', '--password', help='APIC Password', required=True)
#     parser.add_argument('-m', '--mariadb', default='adun_db', help='MariaDB IP Address or Domain Name')
#     parser.add_argument('-r', '--mdbroot', default='root', help='MariaDB Super User Name')
#     parser.add_argument('-s', '--mdbpass', default='1234Qwer', help='MariaDB Super Password')
#     parser.add_argument('-q', '--quarantine', default='0', help='Default Quarantine VLan Number')
#     parser.add_argument('-d', '--debug', dest='debug', action='store_true', help='Debug Mode')
#     parser.set_defaults(debug=False)
#     
#     args = parser.parse_args()
#     
#     os.environ['APIC_IP'] = args.apic
#     os.environ['APIC_USERNAME'] = args.username
#     os.environ['APIC_PASSWORD'] = args.password
#     os.environ['APIC_DEBUG'] = str(args.debug).lower()
#     os.environ['MDB_IP'] = args.mariadb
#     os.environ['MDB_ROOT'] = args.mdbroot
#     os.environ['MDB_PASS'] = args.mdbpass
#     os.environ['QUARANTINE_VLAN'] = str(args.quarantine)
    
    pygics.server('0.0.0.0', 8080, 'engine')