#!/bin/sh
./openvpn-webdns.py -f $1
DIR=$(dirname $1)
cd "$(dirname "$1")"
openvpn $1