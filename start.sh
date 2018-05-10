#!/bin/bash

IF_MGMT=$1

screen -dmS rdhcp python server.py -m "$IF_MGMT"
