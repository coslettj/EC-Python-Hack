#!/usr/bin/python
#
# Bruteforce a password with a SALT
#

import crypt
from termcolor import colored

def crackPass(cryptWord):
    salt = cryptWord[0:2]
    dict = open('dict.txt', 'r')
    for word in dict.readlines():
        word = word.strip('\n')
        cryptpass = crypt.crypt(word, salt)
        if cryptWord == cryptpass:
            print(colored('[+] Found the password {}'.format(word),'green'))
            return(True)
    print('[-] Password not found')
    return(False)

def main():
    try: 
        passfile = open('passwords-salt.txt', 'r')
    except:
        print(colored('[-] No such file.','red'))
        quit()
    for line in passfile.readlines():
        if ":" in line:
            user = line.split(':')[0]
            passwd = line.split(':')[1].strip(' ').strip('\n')
            print('[-] Cracking password for {} / {}.'.format(user, passwd))
            if (crackPass(passwd)):
                print('Exiting')
                quit()


if __name__ == '__main__':
    main()