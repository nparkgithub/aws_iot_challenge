#!/bin/bash
# stop script on error
set -e

# run pub/sub sample app using certificates downloaded in package
printf "\nRunning Adapter for AWS_IOT application...\n"
python awsIotAdapter.py -e a3k0ih60smvksw.iot.us-west-2.amazonaws.com -r root-CA.crt -c DANIEL_AWS_IOT.cert.pem -k DANIEL_AWS_IOT.private.key
