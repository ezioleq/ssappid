#!/usr/bin/env python

import urllib.request
import argparse
import os.path
import sqlite3
import json

DATABASE_PATH = os.path.expanduser('~') + '/.cache/ssappid.sqlite'
STEAM_APPS_URL = 'https://api.steampowered.com/ISteamApps/GetAppList/v2'

# Register and get args
parser = argparse.ArgumentParser(description=(
    "Search Steam AppID, ssappid in short\n"
    "A simple script to get Steam app name by appid and vice-versa"
), formatter_class=argparse.RawTextHelpFormatter)

parser.add_argument('-f', '--force', action='store_true',
                    help="Force refresh apps database (may take a while)")

parser.add_argument('-a', '--appid', action='store',
                    help='Find corresponding name to given appid')

parser.add_argument('-n', '--name', action='store',
                    help='Find corresponding appid/s to given name')

parser.add_argument('-w', '--with-name', action='store_true',
                    help='Print appids with names next to it')

parser.add_argument('-d', '--descending', action='store_true',
                    help='Order by descending appids (default: ascending)', default=False)

options = parser.parse_args()

# Oh, there's no database yet, let's create one
if not os.path.isfile(DATABASE_PATH):
    options.force = True;

# Force remove old database if it already exist
if options.force:
    print('Removing old database...')
    try:
        os.remove(DATABASE_PATH)
    except OSError:
        pass # Woopsie

# Connect or create database and set cursor
conn = sqlite3.connect(DATABASE_PATH)
c = conn.cursor()

# Create database
c.execute('CREATE TABLE IF NOT EXISTS apps (appid INTEGER, name TEXT, UNIQUE(appid, name))')
conn.commit()

# Force update appids in database
if options.force:
    print('Retrieving apps list...')
    webUrl = urllib.request.urlopen(STEAM_APPS_URL)
    decoded_json = json.loads(webUrl.read())

    for app in decoded_json['applist']['apps']:
        c.execute('INSERT OR IGNORE INTO apps VALUES ({}, \'{}\')'.format(app["appid"], app["name"].replace("'", "''")));
    conn.commit()

# Search by appid
if options.appid is not None:
    for row in c.execute('SELECT * FROM apps WHERE appid = {}'.format(int(options.appid))):
        print(row[1])

# Search by name
if options.name is not None:
    for row in c.execute('SELECT * FROM apps WHERE name LIKE "%{}%" ORDER BY appid {}'
                         .format(options.name, ['ASC', 'DESC'][int(options.descending)])):
        if options.with_name:
            print("{} {}".format(row[0], row[1]))
        else:
            print(row[0])

conn.close()
