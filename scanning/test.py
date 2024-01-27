#!/usr/bin/python
# 

import os

f = open('exploits.txt','r')
#lines = f.readlines()

#for l in lines:
for l in f.readlines():
    print(l.strip('\n'))
    if 'SSH-2.0-OpenSSH_8.9p1 Ubuntu-3ubuntu0.5' in l:
        print('FUCK')
    print(l.strip('\n').find('SSH-2.0-OpenSSH_8.9p1 Ubuntu-3ubuntu0.5'))
    
f.close()