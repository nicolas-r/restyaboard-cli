#!/usr/bin/env python3

import sys
import os
import pprint

sys.path.append(os.path.dirname(os.path.abspath(__file__)) + '/modules')
from restya.restya import Restyaboard


pp = pprint.PrettyPrinter(indent=2)

restya = Restyaboard({
    'username': 'admin',
    'password': 'restya',
    'server': 'centos-docker',
    'port': 1234,
})
print(restya.access_token)

restya.login('board@restya.com', 'restya')
print(restya.user_access_token)
print()

restya.get_all()
# print(restya)
for o in restya.organizations:
    print('Organization: %s' % (o))
    for b in o.org_boards:
        print('Board: %s' % (b))
        for l in b.board_lists:
            print('List: %s' % (l))
sys.exit(0)

# Create an organization
print("add_organization")
org = restya.add_organization('Linux Patching 04/02/2017')
if org is not None:
    print("%d:%s" % (org.id, org.name))
else:
    print('Organization\'s (%s) name already taken' % ('Linux Patching 04/02/2017'))
print()


# Delete an organization
print("delete_organization")
restya.delete_organization(9)
print()

# Get all organizations
print("get_all_organization")
organizations = restya.get_all_organizations()
for org in organizations:
    print("%d:%s" % (org.id, org.name))
print('End get_all_organization')
print()

# Get details about one organization
print("get_organization by id")
org = restya.get_organization({'id': 3})
print("%d:%s" % (org.id, org.name))
print()
print("get_organization by name")
org = restya.get_organization({'name': 'Linux Patching 04/02/2017'})
print("%d:%s" % (org.id, org.name))


