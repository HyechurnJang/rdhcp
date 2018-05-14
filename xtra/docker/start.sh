#!/bin/bash

MGMT=$1

function usages {
	echo "Usages: start.sh <MGMT_IF_NAME>"
	echo ""
	exit 1
}

if [ -z "$MGMT" ]; then
	usages
fi

echo "Start RDHCP Database"
sudo docker run --name rdhcp_db --network=host --privileged -d rdhcp/db
echo "Wait Database 10 Seconds"
echo ""
sleep 10

echo "Start RDHCP Engine"
sudo docker run --name rdhcp_engine --network=host --privileged -e RDHCP_IF_MGMT=$MGMT -d rdhcp/engine
echo ""

echo "OK Let's Start RDHCP !!!"
echo ""

echo "### Engine Logs ###"
echo ""
sudo docker logs -f rdhcp_engine
