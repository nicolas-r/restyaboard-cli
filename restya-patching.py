#!/usr/bin/env python3

import os
import sys
import requests
import csv
import argparse

sys.path.append(os.path.dirname(os.path.abspath(__file__)) + '/modules')
from restya.restya import *
# import logging

# # These two lines enable debugging at httplib level (requests->urllib3->http.client)
# # You will see the REQUEST, including HEADERS and DATA, and RESPONSE with HEADERS but without DATA.
# # The only thing missing will be the response.body which is not logged.
# try:
#     import http.client as http_client
# except ImportError:
#     # Python 2
#     import httplib as http_client
# http_client.HTTPConnection.debuglevel = 1

# # You must initialize logging, otherwise you'll not see debug output.
# logging.basicConfig()
# logging.getLogger().setLevel(logging.DEBUG)
# requests_log = logging.getLogger("requests.packages.urllib3")
# requests_log.setLevel(logging.DEBUG)
# requests_log.propagate = True

# Main program
# parser = argparse.ArgumentParser()
# parser.add_argument('--version', action='version', version='0.0.1')

# parent_org_parser = argparse.ArgumentParser(add_help=False)
# parent_org_parser.add_argument('--name', '-n', help='Name of the object')
# subparsers = parser.add_subparsers(help='commands')

# # Action on organizations
# org_parser = subparsers.add_parser('organization', parents=[parent_org_parser], help='Actions on organizations')
# org_parser.add_argument('--create', action='store_true', help='Create organization')

# # Action on cards
# cards_parser = subparsers.add_parser('card', parents=[parent_org_parser], help='Actions on cards')
# cards_parser.add_argument('--create', action='store_true', help='Action to do')
# cards_parser.add_argument('--move', action='store_true', help='Action to do')
# cards_parser.add_argument('-o', action='store', dest='org_name', help='Organization name')
# cards_parser.add_argument('-b', action='store', dest='board_name', help='Board name')
# cards_parser.add_argument('-c', action='store', dest='org_name', help='Organization name')

# args = parser.parse_args()


# Read the data file
# print("Load patching data...", end="")
# with open('data.csv', 'rb') as csvfile:
#     csv_data = csv.reader(csvfile, delimiter=';')
#     for row in csv_data:
#         if row[1] not in patching_data:
#             patching_data[row[1]] = []
#         patching_data[row[1]].append(row[0])
#     csvfile.close()
# print(" done.")

# Create Restyaboard object and get the authen token
restya = Restyaboard({
    'username': 'admin',
    'password': 'restya',
    'server': 'centos-docker',
    'port': 1234,
})

# Login to the system
restya.login('board@restya.com', 'restya')


# sys.exit(0)

# Create the organization
print('Create the organization... ', end='')
patching_org = restya.get_organization({'name': 'Unix Patching'})
if patching_org is None:
    patching_org = restya.create_organization('Unix Patching', 1)
    print('Done.')
else:
    print('Skipped (organization already present).')

# Create boards for a patching campaign
default_boards = ('2017/02/04 & 05', '2017/02/18 & 19')
print("Create the boards...")
for my_board in default_boards:
    print('\t%s... ' % (my_board), end="")
    patching_board = patching_org.get_board({'name': my_board})
    if patching_board is None:
        patching_board = patching_org.create_board(my_board, 1, patching_org.org_id)
        print('Done')
    else:
        print('Skipped (board already exists)')

    # Add default lists
    default_lists = ('Saturday', 'Sunday', 'With comments', 'Excluded', 'Patched', 'Restarted', 'Done')
    print("Create the default lists... ")
    position = 0
    for my_list in default_lists:
        print('\t%s... ' % (my_list), end="")
        patching_board_list = patching_board.get_list({'name': my_list})
        if patching_board_list is None:
            patching_board_list = patching_board.create_list(my_list, position)
            print('Done')
        else:
            print('Skipped (list already exists)')
        position += 1
