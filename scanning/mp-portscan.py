#!/usr/bin/python
from socket import *
import optparse
import multiprocessing as mp
import time

# Set the number of threads to create on each CPI for multiprocessing
THREADSPERCPU = 2

# Get the number of CPU cores available
cpu_count = mp.cpu_count()

def scanPort(targetIP, portNumber):
    # Check if the port is open
    portState = {}
    portState['target'] = targetIP
    portState['port'] = portNumber

    try:
        sock = socket(AF_INET, SOCK_STREAM)
        sock.settimeout(1)
        sock.connect((targetIP, portNumber))
        try:
            banner = sock.recv(1024).decode()
            print(f'[+] Received banner: {banner}')
            if banner:
                banner = banner.decode('utf-8').strip('\n')
            else:
                banner = 'No banner available'
        except:
            banner = 'Unable to retrieve banner'
        portState['state'] = 'open'
        portState['banner'] = banner
        sock.close()
        
    except:
        portState['state'] = 'closed'
        portState['banner'] = 'N/A'

    return portState

def mpWrapper(targets):
    try:
        print(f'Target: {targets['tgtIP']}, Port: {targets['tgtPort']}')
        ps = scanPort(targets['tgtIP'], targets['tgtPort'])
        return ps
    except Exception as e:
        print(f'[-] Error: {e}')
        return None
    
def main():
    parser = optparse.OptionParser('Usage: ' + ' - H <target hosts> -p <ports, use ALL for ports 1-65535>')
    parser.add_option('-H', dest='tgtHost', type='string', help='Specify target hosts seperated by comma')
    parser.add_option('-p', dest='tgtPort', type='string', help='Specify target ports seperated by comma')
    [options, args] = parser.parse_args()
    tgtHosts = str(options.tgtHost).split(',')
    tgtPorts = str(options.tgtPort).split(',')

    # For testing purposes, we will use a list of hosts and ports
    if len(tgtHosts) == 0:
        tgtHosts = ['192.168.1.1']
    if len(tgtPorts) == 0:
        tgtPorts = ['22', '80', '443']

    if (tgtHosts[0] == None) | (tgtPorts[0] == None):
        print(parser.usage)
        exit(0)
    else:
        startTime = time.time()
        # Create a list to hold the processes
        # Create a dictionary with the host and port
        targets = []
        for host in tgtHosts:
            try:
                tgtIP = gethostbyname(host)
            except:
                print('[-] Unable to resolve {}}'.format(host))
                tgtIP = host
                continue
            # add target to the list
            for port in tgtPorts:
                target = {}
                print(f'[+] Adding {tgtIP}/{port} to the scan list')
                target['tgtIP'] = tgtIP
                target['tgtPort'] = int(port)
                targets.append(target)

        # Set the thread pool size
        p = mp.Pool(processes=cpu_count * THREADSPERCPU)
        
        try:
            results = p.map(mpWrapper, targets)
        except KeyboardInterrupt:
            print('[-] User terminated the scan')
            p.terminate()
            exit(0)
        except Exception as e:
            print(f'[-] Error: {e}')
            p.terminate()
            exit(0)
        p.close()
        p.join()
        # Print the results 
        for result in results:
            print(f'[+] Scan results for {result['target']} - {result['port']} = {result['state']}', result['banner'])
            # if result['state'] == 'open':
            #     print(f'[+] {['port']}/tcp Banner: {result['banner']}')
            # else:
            #     print(f'[-] {result['port']}/tcp is closed')
        endTime = time.time()
        print(f'[+] Scan completed in {endTime - startTime:0.2f} seconds')
                
if __name__ == '__main__':
    main()