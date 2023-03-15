# simplefin-ynab4
simple script to create ynab4 importable csv files from from a simplefin server

## Requirements
this script requires the followin gmodules:
```
pip install requests base64 click humanfriendly
```

## First Run
the first time you run `simplefin-ynab4` it will as you for the setup token and store it $HOME/sfin_ynab/settings.ini
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
# wher to save the csv files
output_dir = ynab4_import

[rename]
# rename file names incase simplefin creates poor names for your acounts
some_acct_name = new_acct_name
```