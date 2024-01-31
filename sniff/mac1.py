#!/usr/bin/python

import subprocess

def changemac(interface, newmac):
    subprocess.call(['ifconfig',interface,'down'])
    subprocess.call(['ifconfig',interface,'hw ether',newmac])
    subprocess.call(['ifconfig',interface,'up'])

def main():
    interface = input('[*] Enter the interface to change the MAC of: ')
    newmac = input('[*] Enter the new MAC address: ')
    
    beforemac = subprocess.check_output(['interface',interface])
    changemac(interface, newmac) 
    aftermac = subprocess.check_output(['ifconfig',interface])
    if beforemac == aftermac:
        print('[-] Failed to change the mac of {} to {}').format(interface, newmac)
    else:
        print('[+] MAC address of {} changed to {}').format(interface, newmac)
        
if __name__ == '__main__':
    main()