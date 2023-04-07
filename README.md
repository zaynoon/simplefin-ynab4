# simplefin-ynab4
simple script to create ynab4 importable csv files from from a simplefin server

## Requirements
this script requires the following modules:
```
pip install requests base64 click humanfriendly
```

## First Run
the first time you run `simplefin-ynab4` it will ask you for the setup token and store it alongside the simplefin-ynab.py script.
```
> ./simplefin-ynab.py
Setup Token? 
```

## settings.ini
The settings file looks like this:
```
[auth]
url = https://user:demo@sfin.server.com/simplefin

[simplefin]
# the last access time is stored here so that every run only downloads new data
last_access_time = 1678731057 

[ynab]
# where to save the csv files
output_dir = ynab4_import

[rename]
# rename file names in case simplefin creates bad names for your accounts
some_acct_name = new_acct_name
```
