#!/bin/bash

IF_MGMT=$1

function usages {
	echo "Usages: start.sh <MGMT_INTERFACE_NAME>"
	echo ""
	exit 1
}

if [ -z "$IF_MGMT" ]; then
	usages
fi

screen -dmS rdhcp python server.py -m $IF_MGMT
