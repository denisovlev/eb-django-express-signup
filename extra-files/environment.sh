#!/bin/bash
export DEBUG="True"
export STARTUP_SIGNUP_TABLE="gsg-signup-table"
export AWS_REGION="eu-west-1"
export NEW_SIGNUP_TOPIC="arn:aws:sns:eu-west-1:124119229493:gsg-signup-notifications"
printenv | grep "DEBUG\|STARTUP_SIGNUP_TABLE\|AWS_REGION\|NEW_SIGNUP_TOPIC"