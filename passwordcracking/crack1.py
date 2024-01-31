#!/usr/bin/python

#
# Generate hashes of a password entered by the user
#


import hashlib

def main():
    
    hashvalue = input('[*] Enter a string to hash : ')
    print('The hashes of {} are:'.format(hashvalue))
    hashobject1 = hashlib.md5()
    hashobject1.update(hashvalue.encode())
    print('MD5: {}'.format(hashobject1.hexdigest()))
    
    hashobject2 = hashlib.sha1()
    hashobject2.update(hashvalue.encode())
    print('SHA1: {}'.format(hashobject2.hexdigest()))

    hashobject3 = hashlib.sha256()
    hashobject3.update(hashvalue.encode())
    print('SHA256:  {}'.format(hashobject3.hexdigest()))
    
    hashobject4 = hashlib.sha512()
    hashobject4.update(hashvalue.encode())
    print('SHA512: {}'.format(hashobject4.hexdigest()))

if __name__ == '__main__':
    main()