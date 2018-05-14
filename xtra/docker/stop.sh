#!/bin/bash

echo "Stop RDHCP Engine"
docker rm -f -v rdhcp_engine
echo ""

echo "Stop RDHCP Database"
docker rm -f -v rdhcp_db
echo ""

echo "Completed"
echo ""

