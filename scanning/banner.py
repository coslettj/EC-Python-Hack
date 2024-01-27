#!/usr/bin/python
import socket

def retBanner(ip, port):
    try:
        socket.setdefaulttimeout(2)
        s = socket.socket()
        s.connect((ip,port))
        print(s)
        banner = s.recv(1024)
        return banner
    except:
        print('Error')
        return
    
def main():
    banner = retBanner('192.168.1.43', 22)
    print(len(banner))
    print('|{}|'.format(banner))
    if banner:
        print('[+] Banner:{}'.format(banner))
        
main()