#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys
import os
import click
sys.path.append(os.path.dirname(os.path.abspath(__file__)) + '/modules')
from restya.restya import *


@click.group()
@click.pass_context
def cli(ctx):
    """First paragraph.

    This is a very long second paragraph and as you
    can see wrapped very early in the source text
    but will be rewrapped to the terminal width in
    the final output.

    \b
    This is
    a paragraph
    without rewrapping.

    And this is a paragraph
    that will be rewrapped again.
    """

    ctx.obj = {}
    ctx.obj['restyaboard'] = Restyaboard({
        'username': 'admin',
        'password': 'restya',
        'server': 'centos-docker',
        'port': 1234,
    })
    # Get access token
    ctx.obj['restyaboard'].get_access_token()
    # Login to the system
    ctx.obj['restyaboard'].login('board@restya.com', 'restya')
    # pass


##########################
# Organizations function #
##########################


def organization_create(restya, params):
    if restya.create_organization(params['org_name'], 1) is not None:
        print("Organizaton %s created." % (params['org_name']))
    else:
        print("Organization '%s' already exists." % (params['org_name']))


def organization_delete(restya, params):
    if restya.delete_organization({'name': params['org_name']}) is not None:
            print("Organization %s deleted successfully" % (params['org_name']))
    else:
        print("Organization %s unknown" % (params['org_name']))


def organization_list(restya, params):
    for org in restya.get_all_organizations():
        print("Name: %s, id: %d" % (org.name, org.id))


def organization_list_boards(restya, params):
    org = restya.get_organization({'name': params['org_name']})
    if org is not None:
        for b in org.get_all_boards():
            print("Name: %s, id: %d" % (b.name, b.id))
    else:
        print("Organization %s unknown" % (params['org_name']))


def organization_close_board(restya, params):
    org = restya.get_organization({'name': params['org_name']})
    if org is not None:
        if org.get_board({'name': params['board_name']}) is not None:
            org.close_board({'name': params['board_name']})
            print("Board '%s' closed successfully." % (params['board_name']))
        else:
            print("board not found")
    else:
        print("org not found")


# Todo
# - Manage visibility
def organization_create_board(restya, params):
    org = restya.get_organization({'name': params['org_name']})
    if org is not None:
        if org.get_board({'name': params['board_name']}) is None:
            org.create_board(params['board_name'], 1)
            print("Board '%s' created inside '%s' successfully." % (params['board_name'], params['org_name']))
        else:
            print("Board already exists")
    else:
        print("Organization %s unknown" % (params['org_name']))


def organization_delete_board(restya, params):
    org = restya.get_organization({'name': params['org_name']})
    if org is not None:
        if org.get_board({'name': params['board_name']}) is not None:
            org.delete_board(params['board_name'])
            print("Board '%s' deleted successfully from '%s'." % (params['board_name'], params['org_name']))
        else:
            print("board not found")
    else:
        print("org not found")


def validate_actions(ctx, param, value):
    possible_values = ('close-board', 'create', 'create-board', 'delete', 'delete-board', 'list', 'list-boards')
    if value in possible_values:
        return(value)
    else:
        raise click.BadParameter("must be one of " + ', '.join(possible_values))


@cli.command(short_help='Action on organizations')
@click.argument('action', callback=validate_actions)
@click.option('--org-name', '-o', help='Name of the organization')
@click.option('--board-name', '-b', help='Name of the board')
@click.pass_context
def organization(ctx, **kwargs):
    """\b
        ACTION can be on the following keywords:
            close-board
            create
            create-board
            delete
            delete-board
            list
            list-boards
    """

    dispatcher = {
        'close-board': organization_close_board,
        'create': organization_create,
        'create-board': organization_create_board,
        'delete': organization_delete,
        'delete-board': organization_delete_board,
        'list': organization_list,
        'list-boards': organization_list_boards,
    }

    # if kwargs['action'] in ('create', 'delete', 'list-boards'):
    if kwargs['org_name'] is None and kwargs['action'] != 'list':
        print("You must specify an organization name.")
        sys.exit(1)

    if kwargs['board_name'] is None and kwargs['action'] in ('close-board', 'create-board', 'delete-board'):
        print("You must specify a board name.")
        sys.exit(1)

    dispatcher[kwargs['action']](ctx.obj['restyaboard'], kwargs)


###################
# Boards function #
###################

def board_add_list(restya, params):
    org = restya.get_organization({'name': params['org_name']})
    if org is not None:
        board = org.get_board({'name': params['board_name']})
        if board is not None:
            last_position = board.get_last_position() + 1
            if board.get_list({'name': params['list_name']}) is None:
                board.create_list(params['list_name'], last_position)
                print("List '%s' successfully created into '%s'." % (params['list_name'], params['board_name']))
            else:
                print("Skipped - card '%s' already exists." % (params['list_name']))
        else:
            print("board not found")
    else:
        print("org not found")


def board_list_lists(restya, params):
    org = restya.get_organization({'name': params['org_name']})
    if org is not None:
        board = org.get_board({'name': params['board_name']})
        if board is not None:
            b_list = board.get_all_lists()
            if b_list is not None:
                for l in b_list:
                    print("Name: %s, id: %d, position: %s" % (l.name, l.id, l.position))
            else:
                print("This board has no lists yet.")
        else:
            print("board not found")
    else:
        print("org not found")
    return(True)


def validate_actions_board(ctx, param, value):
    possible_values = ('add-list', 'close', 'create', 'delete', 'list-lists')
    if value in possible_values:
        return(value)
    else:
        raise click.BadParameter("must be one of " + ', '.join(possible_values))


@cli.command(short_help='Action on boards')
@click.argument('action', callback=validate_actions_board)
@click.option('--org-name', '-o', help='Name of the organization')
@click.option('--board-name', '-b', help='Name of the board')
@click.option('--list-name', '-l', help='Name of the list')
@click.pass_context
def board(ctx, **kwargs):
    """\b
        ACTION can be on the following keywords:
            add-list      Add a list to the specified board. The list will be placed at the end
            list-lists    Display all the lists of the specified board
    """
    dispatcher = {
        'add-list': board_add_list,
        'list-lists': board_list_lists,
    }

    if kwargs['org_name'] is None:
        print('You must specify an organization name with --org-name')
        sys.exit(1)

    if kwargs['board_name'] is None:
        print('You must specify a board name with --board-name')
        sys.exit(1)

    if kwargs['action'] == 'add-list' and kwargs['list_name'] is None:
        print('You must specify a list name with --list-name')
        sys.exit(1)

    dispatcher[kwargs['action']](ctx.obj['restyaboard'], kwargs)


##################
# lists function #
##################

def list_add_card(restya, params):
    org = restya.get_organization({'name': params['org_name']})
    if org is not None:
        board = org.get_board({'name': params['board_name']})
        if board is not None:
            b_list = board.get_list({'name': params['list_name']})
            if b_list is not None:
                if b_list.create_card(params['card_name'], None) is not None:
                    print("Card '%s' successfully created into '%s'." % (params['card_name'], params['list_name']))
                else:
                    print("Card '%s' already exists." % (params['card_name']))
            else:
                print("List '%s' not found" % (params['list_name']))
        else:
            print("board not found")
    else:
        print("org not found")


def board_list_cards(restya, params):
    org = restya.get_organization({'name': params['org_name']})
    if org is not None:
        board = org.get_board({'name': params['board_name']})
        if board is not None:
            b_list = board.get_list({'name': params['list_name']})
            if b_list is not None:
                try:
                    for card in b_list.get_all_cards():
                        print(card)
                except TypeError:
                    print("No cards.")
        else:
            print("board not found")
    else:
        print("org not found")
    return(True)


def validate_actions_list(ctx, param, value):
    possible_values = ('add-card', 'delete', 'list-cards', 'move-all-cards')
    if value in possible_values:
        return(value)
    else:
        raise click.BadParameter("must be one of " + ', '.join(possible_values))


@cli.command(short_help='Action on lists')
@click.argument('action', callback=validate_actions_list)
@click.option('--org-name', '-o', help='Name of the organization')
@click.option('--board-name', '-b', help='Name of the board')
@click.option('--list-name', '-l', help='Name of the list')
@click.option('--card-name', '-c', help='Name of the card')
@click.pass_context
def list(ctx, **kwargs):
    """\b
        ACTION can be on the following keywords:
            add-card           Add a card to the specified
            delete             Delete the specified list from the specified board
            list-cards         Display all the lists of the specified board
            move-all-cards     Move all cards from the lists to a new list in the same board
    """
    dispatcher = {
        'add-card': list_add_card,
        'delete-card': board_delete,
        'list-cards': board_list_cards,
        'move-all-cards': True,
    }

    if kwargs['org_name'] is None:
        print('You must specify a board name with --org-name')
        sys.exit(1)
    if kwargs['board_name'] is None:
        print('You must specify an organization name with --board-name')
        sys.exit(1)
    if kwargs['list_name'] is None:
        print('You must specify a list name with --list-name')
        sys.exit(1)
    if kwargs['action'] == 'add-card' and kwargs['card_name'] is None:
        print('You must specify a card name with --card-name')
        sys.exit(1)

    dispatcher[kwargs['action']](ctx.obj['restyaboard'], kwargs)


if __name__ == '__main__':
    cli()
