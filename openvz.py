#!/usr/bin/env python

# Groups are determined by the description field of openvz guests
# multiple groups can be seperated by commas: webserver,dbserver

from subprocess import Popen,PIPE
import sys
import json

# List openvz hosts
vzhosts = ['d5401','d2669']
# Add openvz hosts to the inventory and Add "_meta" trick
inventory = {'vzhosts': {'hosts': vzhosts}, '_meta': {'hostvars': {}}}
# Default group, when description not defined
default_group = ['vzguest']

def get_guests():
    # Loop through vzhosts
    for h in vzhosts:
        # SSH to vzhost and get the list of guests in json
        pipe = Popen(['ssh', h, 'sudo', '/usr/sbin/vzlist', '-j'], stdout=PIPE, universal_newlines=True)

        # Load Json info of guests
        json_data = json.loads(pipe.stdout.read())

        # Loop through guests
        for j in json_data:
            if j['status'] == 'running':
                # Get IP address only from private network range
                ip = [ip for ip in j['ip'] if ip.startswith('192.168')][0]
                # Add information to host vars
                inventory['_meta']['hostvars'][j['hostname']] = {'ctid': j['ctid'], 'private_path': j['private'], 'root_path': j['root'], 'ansible_host': ip, 'hn': h}

            # Determine group from guest description
            if j['description'] is not None:
                groups = j['description'].split(",")
            else:
                groups = default_group

            # Add guest to inventory
            for g in groups:
                if g not in inventory:
                    inventory[g] = {'hosts': []}

                inventory[g]['hosts'].append(j['hostname'])

    return inventory

if len(sys.argv) == 2 and sys.argv[1] == '--list':
    inv_json = get_guests()
    print json.dumps(inv_json, sort_keys=True, indent=4)
elif len(sys.argv) == 3 and sys.argv[1] == '--host':
    print json.dumps({});
else:
    print "Need an argument, either --list or --host <host>"
