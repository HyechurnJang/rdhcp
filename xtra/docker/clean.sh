#!/bin/bash

docker rm -f -v rdhcp_engine
docker rm -f -v rdhcp_db

docker rmi rdhcp/engine
docker rmi rdhcp/db

