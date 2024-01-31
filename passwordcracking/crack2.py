#!/usr/bin/python

# 
# Read a file from the internet and a hash from the terminal to find the password
#

import hashlib
from urllib.request import urlopen
from termcolor import colored

pwdURL = 'https://raw.githubusercontent.com/danielmiessler/SecLists/master/Passwords/Common-Credentials/10-million-password-list-top-10000.txt'

def main():
    pwdhash = input('[*] Enter the SHA1 hash to crack: ')
    passlist = str(urlopen(pwdURL).read(), 'utf-8')
    
    for password in passlist.split('\n'):
        passwordhash = hashlib.sha1(bytes(password, 'utf-8')).hexdigest()
        if pwdhash == passwordhash:
            print(colored('[+] The password is : {}'.format(password),'green'))
            quit()
        else:
            print(colored('[-] The password {} does not match.'.format(password),'red'))
    
    print(colored('Password is not in the list'),'red')
    
if __name__ == '__main__':
    main()