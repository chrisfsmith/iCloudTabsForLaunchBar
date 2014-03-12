#!/usr/bin/python

import os
import sys
import subprocess
import shutil
import tempfile
import plistlib


def create_temporary_copy(path):
    temp_dir = tempfile.gettempdir()
    temp_path = os.path.join(temp_dir, 'safari_sync_plist_copy.plist')
    shutil.copy2(os.path.expanduser(path), temp_path)
    return temp_path


def get_device_tabs():
    temp_plist = create_temporary_copy('~/Library/SyncedPreferences/com.apple.Safari.plist')
    os.system('plutil -convert xml1 %s' % temp_plist)
    info = plistlib.readPlist(temp_plist)
    os.remove(temp_plist)

    # Pull out the device elements from the info dict for easier parsing later
    device_tabs = []

    for uid in info['values'].values():
        try:
            device_tabs.append([uid['value']['DeviceName'], uid['value']['Tabs']])
        except:
            pass

    return device_tabs


def icloud_devices():
    hostname_proc = subprocess.Popen(
        ['scutil --get LocalHostName'], stdout=subprocess.PIPE, shell=True)
    (hostname_out, hostname_err) = hostname_proc.communicate()
    hostname = hostname_out.strip()

    computer_name_proc = subprocess.Popen(
        ['scutil --get ComputerName'], stdout=subprocess.PIPE, shell=True)
    (computer_name_out, computer_name_err) = computer_name_proc.communicate()
    computer_name = computer_name_out.strip()

    json = '[\n'

    for device in get_device_tabs():
        device_name = device[0]

        if device_name not in [hostname, computer_name.decode("utf-8")] and len(device[1]):
            json += '    {\n'
            json += '       "title": "%s",\n' % device_name
            json += '       "subtitle": "%s",\n' % len(device[1])
            json += '       "url": "x-launchbar:perform-service?name=iCloud Tabs for Device&string=%s",\n' % device_name
            json += '       "icon": "/Applications/LaunchBar.app/Contents/Resources/CloudDocuments.icns"\n'
            json += '    }\n'

    json += ']\n'

    return json


def icloud_tabs_for_device(device_name):
    json = '[\n'

    for device in get_device_tabs():
        if device[0] == device_name:
            for tab in device[1]:
                json += '    {\n'
                json += '       "url": "%s",\n' % (tab['URL'])
                json += '       "title": "%s"\n' % (tab['Title'])
                json += '    }\n'

    json += ']\n'

    return json

output = ''
if len(sys.argv) > 1:
    output = icloud_tabs_for_device(sys.argv[1])
else:
    output = icloud_devices()

print output.encode('utf8')
