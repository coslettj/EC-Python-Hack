#!/usr/bin/python
#
# Read a hash from the terminal and a password file to find passwords
#

from termcolor import colored
import hashlib

def main():
    passhash = input('[*] Enter MD5 hash value : ')
    wordlist = input('[*] Enter the path to the hash file : ')

    try: 
        passfile = open(wordlist, 'r')
    except:
        print(colored('[-] No such file.','red'))
        quit()
    for password in passfile:
        print('[-] Hashing {} into MD5'.format(password.strip('\n')))
        md5pass = hashlib.md5(password.strip('\n').encode('utf-8')).hexdigest()
        if passhash == md5pass:
            print(colored('[+] Found the password : {}'.format(password.strip('\n')),'green'))
            quit()
    print(colored('[-] Password not in list','red'))

if __name__ == '__main__':
    main()