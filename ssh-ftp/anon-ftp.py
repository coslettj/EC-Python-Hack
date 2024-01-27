#!/usr/bin/python

import ftplib

def anonLogin(hostname):
    try:
        ftp = ftplib.FTP(hostname)
        ftp.login('anonymous', 'anonymous')
        print('[+] {} login successful'.format(hostname))
        ftp.quit
        return True
    except Exception as e:
        print('[-] {} login failed'.format(hostname))
        print('[-] {}'.format(e))

host = input('Enter the IP address : ')
anonLogin(host)
