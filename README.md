# webdns-openvpn-rewrite
In case your proxy server or DNS does not resolve DynamicDNS names, this script will query an webservice via http and replace the domain in your OpenVPN config with the returned IP.

## Setup and usage

The script is tested with python 3.5.2, it does only require standard python libraries.
There are two scripts, which only need to be copied:

 - openvpn-webdns.py - does just call the webdns and writes the ip to the config
```
# to display help use:
./openvpn-webdns.py -h
# sample call
./openvpn-webvpn.py -f /path/to/config/client.ovpn
```

 - start-openvpn.sh - which wraps around openvpn-webdns.py and starts openvpn as well.
```
# sample call
./start-openvpn.sh /path/to/config/client.ovpn
```
