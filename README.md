# nordvpn-checker

A simple Python script to check if NordVPN accounts listed in a file are valid.

## NOTE: This script only works in Linux.

# Requirements

- The NordVPN CLI tool. [Get it from here](https://nordvpn.com/download/linux/).
- [Python 3.7](https://www.python.org/downloads/).
- An input file containing NordVPN login entries in `email:password` format.

# Installation

- Clone the repo with `git clone https://github.com/behnambm/nordvpn-checker`

# Usage

- The syntax is
  > `nord-checker.py [--file | -f] path/to/file [--output | -o] path/to/file`

For example, `cd` into the recently cloned directory and run:

```
$ python3 nord-checker.py --file accounts.txt --output success.txt
```

- The successful entries are appended to the specified output file.


### Contact

- [My Telgram](https://t.me/behnam_1121)
