#!/bin/bash

echo "Build Database"
sudo docker build -t rdhcp/db:latest -f ./resource/database.docker .
echo ""

echo "Build Engine"
sudo docker build -t rdhcp/engine:latest -f ./resource/engine.docker .
echo ""

