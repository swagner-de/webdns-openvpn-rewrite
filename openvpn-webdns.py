#!/usr/bin/env python3

import sys
import argparse
import re
import requests

def queryForIp(type, domain, proxies):
    if proxies == '': r = requests.get('https://dns-api.org/%s/%s' % (type, domain))
    else: r = requests.get('https://dns-api.org/%s/%s' % (type, domain), proxies=proxies)
    if r.status_code != 200: terminate(1, 'Could not contact webservice' + r.status_code)
    json = r.json()[0]
    return json['value'] if domain == json['name'] else terminate(1, 'Could not resolve name ' + domain)

def main():

    parser = argparse.ArgumentParser(description='Replaces a Dynamic DNS name with an IP in an Open', prog='openvpn-webdns')
    mand = parser.add_argument_group('mandatory pararmeters')

    parser.add_argument(
        '-p', type=str, nargs='?', dest='proxy', required=False, help='Proxy to use (e.g 172.19.200.1:8080')
    parser.add_argument(
        '-c', type=str, nargs='?', dest='proxy_credentials', required=False, help='Credentials for proxy (e.g. user:pass')
    parser.add_argument(
        '-e', type=str, nargs='?', dest='encoding', required=False, default='utf-8', help='Encoding of OpenVPN file (default: utf-8)')
    mand.add_argument(
        '-f', type=str, nargs='?', dest='file', required=True, help='OpenVPN file to use')
    parser.add_argument(
        '--version', action='version', version='%(prog)s 1.0', help='displays the scripts version')
    args = parser.parse_args()

    file, encoding = args.file,  args.encoding

    try:
        ovpn_file = open(file, 'r', encoding=encoding)
        ovpn = ovpn_file.read()
        ovpn_file.close()
        re_domain = re.compile('remote [a-zA-Z0-9\-\.]+')
        re_ip = re.compile('remote (?:(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.){3}(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)')
        remote_domains = []
        remote_ips = []
        proxies = ''
        for line in ovpn.split('\n'):
            if re_domain.search(line):
                if re_ip.search(line): remote_ips.append(line)
                else: remote_domains.append(line)
            if 'http-proxy' in line:
                Null, proxy, port = line.split(' ')
                proxies = {'http': 'http://' + proxy + ':' + port, 'https': 'https://' + proxy + ':' + port}

        if len(remote_domains) == 0: terminate(1,'No OpenVPN remote found! Ensure to have the line "remote my.domain.com <port>" in the ovpn-file')

        for remote_ip in remote_ips:
            if '#' not in remote_ip: ovpn = ovpn.replace(remote_ip + '\n', '')

        re_domain = re.compile('[a-zA-Z0-9\-\.]+')
        for remote_domain in remote_domains:
            domain = re_domain.search(remote_domain.replace('remote ', '')).group(0)
            ip = queryForIp('A', domain, proxies)
            print(('%s has been resolved to %s') % (domain, ip))
            replacement_string = (remote_domain if '#' in remote_domain else '#' + remote_domain) + '\n' + remote_domain.replace(domain, ip).strip('#')
            ovpn = ovpn.replace(remote_domain, replacement_string)

        try:
            f = open(file, 'w', encoding=encoding)
            f.write(ovpn)
            f.close()
        except(OSError, IOError) as e:
            terminate(1, 'Could not write to file: ' + e)

    except(OSError, IOError) as e:
        terminate(1, 'Could not open file: ' + e)

def terminate(exitcode, message=None):
    if exitcode == 0 and message: print(message+'\n')
    else: sys.stderr.write(message + '\n')
    sys.exit(exitcode)

if __name__ == "__main__":
   main()