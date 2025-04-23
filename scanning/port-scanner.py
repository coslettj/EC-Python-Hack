from socket import *
import threading
from queue import Queue
import time
import optparse

verbose = False
timeout = 1

# Wrapper function to handle threading
def wrapper(targets):
    threads = []
    results = Queue()
    portState = []

    # Define a worker function to process the queue
    def portScan(targetIP, portNumber):
        # Check if the port is open
        portState = {}
        portState['target'] = targetIP
        portState['port'] = portNumber

        try:
            sock = socket(AF_INET, SOCK_STREAM)
            sock.settimeout(timeout)
            sock.connect((targetIP, portNumber))
            try:
                banner = sock.recv(1024).decode()
                if banner:
                    portState['banner'] = banner.strip('\n')
                else:
                    portState['banner'] = 'No banner available'
            except Exception as e:
                portState['banner'] = f'Unable to retrieve banner ({e})'

            portState['state'] = 'open'
            sock.close()
            
        except:
            portState['state'] = 'closed'
            portState['banner'] = 'N/A'
        # Add the result to the queue
        results.put(portState)
    
    # Process all the targets
    for target in targets:
        t = threading.Thread(target=portScan, args=(target['tgtIP'],target['tgtPort']))
        threads.append(t)
        t.start()
    for t in threads:
        t.join()
    
    # Collect all the results
    while not results.empty():
        portState.append(results.get())

    # Return the results
    return portState    
    

def main():
    try:
        # Start the clock
        startTime = time.time()
        # Add the options to the parser
        parser = optparse.OptionParser('Usage: ' + ' - H <target hosts> -p <ports, use ALL for ports 1-65535>')
        parser.add_option('-H', dest='tgtHost', type='string', help='Specify target hosts seperated by comma')
        parser.add_option('-p', dest='tgtPort', type='string', help='Specify target ports seperated by comma. Specify ALL for all ports or COMMON for common ports. Default is COMMON. ')
        parser.add_option('-v', dest='verbose', action='store_true', help='Enable verbose output')
        parser.add_option('-D', dest='display', type='string', help='Display scan results for all [ALL] ports or only open [OPEN] ports. Default is OPEN')
        parser.add_option('-t', dest='timeout', type='int', default=1, help='Number of seconds to wait for a response. Default is 10.')

        [options, args] = parser.parse_args()

        # Check the Verbose parameter
        if options.verbose:
            verbose = True
            print('[+] Verbose mode enabled')
        else:
            verbose = False
        # Check the Display parameter
        if options.display == 'ALL':
            display = 'ALL'
            if verbose: print('[+] Displaying ALL ports')
        else:
            display = 'OPEN'
            if verbose: print('[+] Displaying OPEN ports')

        if options.timeout != None:
            timeout = options.timeout
        if verbose: print(f'[+] Timeout set to {timeout} seconds')

        if options.tgtHost == None:
            # print(parser.usage)
            # exit(0)
            # For debugging, set to an IP or range
            tgtHosts = ['192.168.1.1', '192.168.1.22']
        else:
            # Get the target hosts from the command line
            tgtHosts = str(options.tgtHost).split(',')
            if verbose: print(f'[+] Target hosts: {tgtHosts}')
        if options.tgtPort == None:
            tgtPorts = ['22', '23', '25', '53', '80', '110', '139', '143', '389', '443', '445', '636', '1512', '2049', '3306', '3389', '8080', '8443']
            print('[+] Scanning default ports: 22, 23, 25, 53, 80, 110, 139, 143, 389, 443, 445, 636, 1512, 2049, 3306, 3389, 8080, 8443')
        elif options.tgtPort == 'ALL':
            print('[+] Scanning all ports, the CPU is going to love this!')
            tgtPorts = [str(i) for i in range(1, 65536)]
        else:
            tgtPorts = str(options.tgtPort).split(',')

        if (tgtHosts[0] == None) | (tgtPorts[0] == None):
            print(parser.usage)
            exit(0)
        else:
            targets = []
            if verbose: print(f'[+] Creating target list')
            for host in tgtHosts:
                try:
                    tgtIP = gethostbyname(host)
                except:
                    print(f'[-] Unable to resolve {host}')
                    tgtIP = host
                    continue
                # add target to the list
                for port in tgtPorts:
                    target = {}
                    target['tgtIP'] = tgtIP
                    target['tgtPort'] = int(port)
                    targets.append(target)

            # Call the wrapper function
            if verbose: print(f'[+] Starting scan for {len(targets)} targets/ports')
            results = wrapper(targets)
            # Sort the results
            if verbose: print(f'[+] Scan completed, sorting results')
            results.sort(key=lambda x: (x['target'], x['port']))
            # Print the results
            for result in results:
                if display == 'ALL' or result['state'] == 'open':
                    print(f'[+] {result["target"]}:{result["port"]} is {result["state"]} ', end='')
                    if result['banner'] != 'N/A':
                        print(f'Banner: {result["banner"]}')
                    else:
                        print('No banner available')
                    
            endTime = time.time()
            elapsedTime = endTime - startTime
            print(f'[+] Scan complete, time taken: {elapsedTime:.2f} seconds')
    except Exception as e:
        print(f'[-] Error: {e}')
        exit(1)

if __name__ == '__main__':
    main()