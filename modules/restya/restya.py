#!/usr/bin/env python3

import sys
import requests


# def _do_get_request(url, auth, params, data):
#     if auth is not None:
#         r = requests.get(url, auth=auth)
#     elif data is not None:
#         r = requests.get(
#             url,
#             params=params,
#             json=data
#         )
#     else:
#         r = requests.get(
#             url,
#             params=params
#         )
#     return r


# def _do_post_request(url, params, data):
#     if data is not None:
#         r = requests.post(
#             url,
#             params=params,
#             json=data)
#     else:
#         r = requests.post(
#             url,
#             params=params
#         )
#     return r


# def _do_put_request(url, params, data):
#     if data is not None:
#         r = requests.put(
#             url,
#             params=params,
#             json=data
#         )
#     else:
#         r = requests.put(
#             url,
#             params=params
#         )
#     return r
#
#
# def _do_delete_request(url, params, data):
#     if data is not None:
#         r = requests.delete(
#             url,
#             params=params,
#             json=data)
#     else:
#         r = requests.delete(
#             url,
#             params=params)
#     return r


class RestyaboardBase(object):
    def __init__(self, base_api_url):
        self.base_api_url = base_api_url

    def _do_get_request(self, endpoint, auth, params, data):
        if auth is not None:
            r = requests.get(
                self.base_api_url + endpoint,
                auth=auth
            )
        elif data is not None:
            r = requests.get(
                self.base_api_url + endpoint,
                params=params,
                json=data
            )
        else:
            r = requests.get(
                self.base_api_url + endpoint,
                params=params
            )
        return r

    def _do_post_request(self, endpoint, params, data):
        if data is not None:
            r = requests.post(
                self.base_api_url + endpoint,
                params=params,
                json=data)
        else:
            r = requests.post(
                self.base_api_url + endpoint,
                params=params
            )
        return r

    def _do_put_request(self, endpoint, params, data):
        if data is not None:
            r = requests.put(
                self.base_api_url + endpoint,
                params=params,
                json=data
            )
        else:
            r = requests.put(
                self.base_api_url + endpoint,
                params=params
            )
        return r

    def _do_delete_request(self, endpoint, params, data):
        if data is not None:
            r = requests.delete(
                self.base_api_url + endpoint,
                params=params,
                json=data)
        else:
            r = requests.delete(
                self.base_api_url + endpoint,
                params=params)
        return r

    def __str__(self):
        return str(vars(self))


class RestyaboardItem(RestyaboardBase):
    def __init__(self, user_access_token, base_api_url, item_id, item_name):
        RestyaboardBase.__init__(self, base_api_url)
        self.user_access_token = user_access_token
        self.position = 0
        self.id = item_id
        self.name = item_name

    def match_name(self, item_name):
        if self.name == item_name:
            return True
        else:
            return False

    def match_id(self, item_id):
        if self.id == item_id:
            return True
        else:
            return False


class Restyaboard(RestyaboardBase):
    """docstring for Restyaboard"""

    def __init__(self, params):
        if 'username' in params:
            self.username = params['username']
        if 'password' in params:
            self.password = params['password']
        if 'server' in params:
            self.server = params['server']
        if 'port' in params:
            self.port = params['port']
        else:
            self.port = 80

        RestyaboardBase.__init__(self, 'http://' + self.server + ':' + str(self.port) + '/api')
        self.organizations = []
        self.users = []
        self.access_token = None
        self.user_access_token = None

    def get_access_token(self):
        # Get the authent token
        response = self._do_get_request('/v1/oauth.json', (self.username, self.password), None, None)
        if response.status_code != requests.codes.ok:
            print("Error getting access token")
            print(response.json())
            sys.exit(1)
        self.access_token = response.json()['access_token']

    def login(self, email, password):
        params = {
            'token': self.access_token
        }
        payload = {
            'email': email,
            'password': password
        }
        response = self._do_post_request('/v1/users/login.json', params, payload)
        if response.status_code != requests.codes.ok:
            print("Error login to the system")
            print(response.json())
            sys.exit(1)
        self.user_access_token = response.json()['access_token']

    # In progress
    def get_all(self):
        params = {
            'token': self.user_access_token
        }
        response = self._do_get_request('/v1/organizations.json', None, params, None)
        if response.status_code != requests.codes.ok:
            print("Error retrieving data ")
            print(response.json())
            sys.exit(1)

        # Parse output
        for org in response.json():
            # Create a new organization
            new_org = RestyaboardOrganization(
                self.user_access_token,
                self.base_api_url,
                org['id'],
                org['name'],
                org['organization_visibility'],
            )
            self.organizations.append(new_org)

            # Create the boards attached to this organization
            if org['boards_listing'] is not None:
                for board in org['boards_listing']:
                    new_board = RestyaboardBoard(
                        self.user_access_token,
                        self.base_api_url,
                        board['id'],
                        board['name'],
                        board['board_visibility'],
                        board['organization_id'],
                        board['is_closed']
                    )
                    new_org.add_existing_board(new_board)

                    # Create the lists attached to this board
                    if board['lists'] is not None:
                        for board_list in board['lists']:
                            new_list = RestyaboardList(
                                self.user_access_token,
                                self.base_api_url,
                                board_list['id'],
                                board_list['name'],
                                board_list['board_id'],
                                board_list['position']
                            )
                            new_board._add_existing_list(new_list)

                            # Create the cards attached to this list
                            if board_list['cards'] is not None:
                                for list_card in board_list['cards']:
                                    new_card = RestyaboardCard(
                                        self.user_access_token,
                                        self.base_api_url,
                                        list_card['id'],
                                        list_card['name'],
                                        list_card['list_id'],
                                        list_card['position'],
                                        list_card['is_archived'],
                                    )
                                    new_list._add_existing_card(new_card)

    def get_all_organizations(self):
        if not self.organizations:
            self.get_all()
        return(self.organizations)

    # Check if an organization's name already exists
    # Return None if name is free
    # Return the RestyaboardOrganization object otherwise
    def get_organization(self, params):
        if not self.organizations:
            self.get_all()
        for org in self.organizations:
            if 'id' in params:
                if org.match_id(params['id']):
                    return(org)
            elif 'name' in params:
                if org.match_name(params['name']):
                    return(org)
        return(None)

    # Create an organization
    def create_organization(self, org_name, org_visibility):
        # Check if the specified name is already taken or not
        if self.get_organization({'name': org_name}) is not None:
            return(None)

        params = {
            'token': self.user_access_token
        }
        payload = {
            'name': org_name
        }
        response = self._do_post_request('/v1/organizations.json', params, payload)
        if response.status_code != requests.codes.ok:
            print("Error creating the organization")
            print(response.json())
            sys.exit(1)
        org = RestyaboardOrganization(
                self.user_access_token,
                self.base_api_url,
                int(response.json()['id']),
                org_name,
                org_visibility
            )
        org.set_visibility(org_visibility)
        self.organizations.append(org)
        return(org)

    def delete_organization(self, params):
        # Check if the specified organization is really present or not
        org_to_del = None
        if 'id' in params:
            org_to_del = self.get_organization({'id': params['id']})
        elif 'name' in params:
            org_to_del = self.get_organization({'name': params['name']})

        if org_to_del is None:
            return None

        params = {
            'token': self.user_access_token,
            'organizationId': id
        }
        response = self._do_delete_request('/v1/organizations/' + str(org_to_del.id) + '.json', params, None)
        if response.status_code != requests.codes.ok:
            print("Error deleting the organization")
            print(response.json())
            sys.exit(1)
        self.organizations.remove(self.get_organization({'id': org_to_del.id}))
        return True

    # Need testing
    def get_all_users(self):
        self.users = []
        params = {'token': self.user_access_token}
        response = self._do_get_request('/v1/users.json', None, params, None)
        if response.status_code != requests.codes.ok:
            print("Error getting users data")
            print(response.json())
            sys.exit(1)

        for key in response.json()['data']:
            self.users.append(
                RestyaboardUser(
                    self.user_access_token,
                    self.base_api_url,
                    key['id'],
                    key['email'],
                    key['username']
                ))


class RestyaboardOrganization(RestyaboardItem):
    # Values for org_visibility
    # 1 : public
    # 2 : private
    def __init__(self, user_access_token, base_api_url, org_id, org_name, org_visibility):
        RestyaboardItem.__init__(self, user_access_token, base_api_url, org_id, org_name)
        self.org_visibility = org_visibility
        self.org_boards = []

    def add_existing_board(self, board):
        self.org_boards.append(board)

    def set_visibility(self, org_visibility):
        params = {
            'token': self.user_access_token,
            'organizationId': int(self.id)
        }
        payload = {
            'organization_visibility': org_visibility,
        }
        response = self._do_put_request(
            '/v1/organizations/' + str(self.id) + '.json',
            params,
            payload
        )
        if response.status_code != requests.codes.ok:
            print("Error setting visibilty for organization %s" %
                  (self.name))
            print(response.json())
            sys.exit(1)

    # Values for board_visibility
    # 0 : private
    # 1 : organization
    # 2 : public
    def create_board(self, board_name, board_visibility):
        # Check if the specified name is already taken or not
        if self.get_board({'name': board_name}) is not None:
            return None

        params = {
            'token': self.user_access_token
        }
        payload = {
            'name': board_name,
            'board_visibility': board_visibility
        }
        response = self._do_post_request(
            '/v1/boards.json',
            params,
            payload
        )
        if response.status_code != requests.codes.ok:
            print("Error creating the board")
            print(response.json())
            sys.exit(1)

        board = RestyaboardBoard(
            self.user_access_token,
            self.base_api_url,
            response.json()['id'],
            board_name,
            board_visibility,
            self.id,
            0
        )
        self.add_board(board, board_visibility)
        self.add_existing_board(board)
        return board

    # Values for board_visibility
    # 0 : private
    # 1 : organization
    # 2 : public
    def add_board(self, board, board_visibility):
        params = {
            'token': self.user_access_token,
            'boardId': int(board.id)
        }
        payload = {
            'name': board.name,
            'board_visibility': board_visibility,
            'organization_id': int(self.id)
        }
        response = self._do_put_request(
            '/v1/boards/' + str(board.id) + '.json',
            params,
            payload
        )
        if response.status_code != requests.codes.ok:
            print("Error adding the board %s (%s) to the organization %s" %
                  (self.name, board.id, self.id))
            print(response.json())
            sys.exit(1)

    def delete_board(self, board_name):
        # {0: {board_id: "5"}, action_id: {action_id: "3"}}
        # [{0: {board_id: "8"}, 1: {board_id: "7"}, action_id: {action_id: "3"}}]
        board = self.get_board({'name': board_name})
        params = {
            'token': self.user_access_token,
        }
        payload = [{
            0: {'board_id': str(board.id)},
            'action_id': {'action_id': "3"},
        }]

        response = self._do_post_request(
            '/v1/boards/bulk_action.json',
            params,
            payload
        )
        if response.status_code != requests.codes.ok:
            print("Error deleting board %s (%s)  fromorganization %s" %
                  (self.name, board.name, self.id))
            print(response.json())
            sys.exit(1)
        self.org_boards.remove(board)

    def get_board(self, params):
        if self.org_boards:
            for board in self.org_boards:
                if 'id' in params:
                    if board.match_id(params['id']):
                        return board
                elif 'name' in params:
                    if board.match_name(params['name']):
                        return board
        return None

    def get_all_boards(self):
        return self.org_boards

    def close_board(self, params):
        if 'id' in params:
            board = self.get_board({'id': params['id']})
        elif 'name' in params:
            board = self.get_board({'name': params['name']})

        if board is not None:
            params = {
                'token': self.user_access_token,
                'boardId': int(board.id)
            }
            payload = {
                'name': board.name,
                'is_closed': "1"
            }
            response = self._do_put_request(
                '/v1/boards/' + str(board.id) + '.json',
                params,
                payload
            )
            if response.status_code != requests.codes.ok:
                print("Error adding the board %s (%s) to the organization %s" % (board.name, board.id, self.id))
                print(response.json())
                sys.exit(1)
            board.board_is_closed = 1
        else:
            return None


class RestyaboardBoard(RestyaboardItem):
    # Todo
    # Explain different values for board_visibility
    def __init__(self, user_access_token, base_api_url, board_id, board_name, board_visibility, org_id, board_is_closed):
        RestyaboardItem.__init__(self, user_access_token, base_api_url, board_id, board_name)
        self.board_visibility = board_visibility
        self.board_org_id = org_id
        self.board_is_closed = board_is_closed
        self.users_member = []
        self.board_lists = []

    def _add_existing_list(self, board_list):
        self.board_lists.append(board_list)

    def get_last_position(self):
        last_position = 0
        if self.board_lists:
            for b_list in self.board_lists:
                if last_position < b_list.list_position:
                    last_position = b_list.list_position
        return last_position

    def get_list(self, params):
        if self.board_lists:
            for b_list in self.board_lists:
                if 'id' in params:
                    if b_list.match_id(params['id']):
                        return b_list
                elif 'name' in params:
                    if b_list.match_name(params['name']):
                        return b_list
        return None

    def get_all_lists(self):
        if self.board_lists:
            return self.board_lists
        else:
            return None

    def create_list(self, list_name, position):
        # Check if the specified name is already taken or not
        if self.get_list({'name': list_name}) is not None:
            return None

        params = {
            'token': self.user_access_token,
            'boardId': int(self.id)
        }
        payload = {
            'board_id': self.id,
            'is_archived': 0,
            'name': list_name,
            'position': position,
        }
        response = self._do_post_request(
            '/v1/boards/' + str(self.id) + '/lists.json',
            params,
            payload
        )
        if response.status_code != requests.codes.ok:
            print("Error creating the list")
            print(response.json())
            sys.exit(1)

        new_list = RestyaboardList(
            self.user_access_token,
            self.base_api_url,
            response.json()['id'],
            list_name,
            self.id,
            position,
        )
        # self.add_list(new_list, position)
        self._add_existing_list(new_list)
        return new_list

    # # Replace user_id by user name
    # def add_user_to_board(self, user_id):
    #     params = {'token': self.user_access_token}
    #     payload = {
    #         'board_user_role_id': "1",
    #         'user_id': user_id,
    #         'is_admin': '1'
    #     }
    #     response = _do_post_request(
    #         self.restyaboard.base_api_url + '/v1/boards/' + self.board_id + '/users.json',
    #         params,
    #         payload
    #     )
    #     if response.status_code != requests.codes.ok:
    #         print("Error adding user %s to the board %s" %
    #               (user_id, self.board_id))
    #         print(response.json())
    #         sys.exit(1)
    #     self.users_member.append(user_id)

    # def add_list(self, list):
    #     params = {
    #         'token': self.user_access_token,
    #         'boardId': int(self.board_id)
    #     }
        # payload = {
        #     'board_id': self.board_id,
        #     'is_archived': 0,
        #     'name': l,
        #     'position': position
        # }
        #     response = _do_post_request(
        #         self.restyaboard.base_api_url + '/v1/boards/' + self.board_id + '/lists.json',
        #         params,
        #         payload
        #     )
        #     if response.status_code != requests.codes.ok:
        #         print("Error adding default lists to the board %s" %
        #               (self.board_id))
        #         print(response.json())
        #         sys.exit(1)
        #     self.lists.append(RestyaboardList(self.restyaboard), l, response.json()['id'])

    # def add_cards_to_list(self, list_name, cards):
    #     position = 0
    #     for c in cards:
    #         params = {
    #             'token': self.user_access_token,
    #             'boardId': int(self.board_id),
    #             'list-id': list_name  # must be replaced by list_id
    #         }
    #         payload = {
    #             'board_id': self.board_id,
    #             'list_id': list_name,  # must be replaced by list_id
    #             'name': c,
    #             'position': position
    #         }
    #         response = _do_post_request(
    #             self.restyaboard.base_api_url + '/v1/boards/' + self.board_id + '/lists/' +
    #             list_name + '/cards.json',
    #             params,
    #             payload
    #         )
    #         if response.status_code != requests.codes.ok:
    #             print("Error adding default lists to the board %s" %
    #                   (self.board_id))
    #             print(response.json())
    #             sys.exit(1)
    #         position += 1
    #         # Add the card to the RestyaboardList object
    #         # self.lists.append(RestyaboardList(self.restyaboard), l, response.json()['id'])


class RestyaboardList(RestyaboardItem):
    def __init__(self, user_access_token, base_api_url, list_id, list_name, list_board_id, list_position):
        RestyaboardItem.__init__(self, user_access_token, base_api_url, list_id, list_name)
        self.list_board_id = list_board_id
        self.list_position = list_position
        self.list_cards = []

    def _add_existing_card(self, list_card):
        self.list_cards.append(list_card)

    def get_last_position(self):
        last_position = 0
        if self.list_cards:
            for card in self.list_cards:
                if last_position < card.card_position:
                    last_position = card.card_position
        return last_position

    def get_card(self, params):
        if self.list_cards:
            for b_card in self.list_cards:
                if 'id' in params:
                    if b_card.match_id(params['id']):
                        return b_card
                elif 'name' in params:
                    if b_card.match_name(params['name']):
                        return b_card
        return None

    def get_all_cards(self):
        if self.list_cards:
            return self.list_cards
        else:
            return None

    def create_card(self, card_name, card_position):
        # Check if the specified name is already taken or not
        if self.get_card({'name': card_name}) is not None:
            return None

        if card_position is None:
            card_position = self.get_last_position() + 1

        params = {
            'token': self.user_access_token,
            'boardId': int(self.list_board_id),
            'listId': int(self.id)
        }
        payload = {
            'board_id': self.list_board_id,
            'list_id': self.id,
            'name': card_name,
            'position': card_position,
        }
        response = self._do_post_request(
            '/v1/boards/' + str(self.list_board_id) + '/lists/' + str(self.id) + '/cards.json',
            params,
            payload
        )
        if response.status_code != requests.codes.ok:
            print("Error creating the card")
            print(response.json())
            sys.exit(1)

        new_card = RestyaboardCard(
            self.user_access_token,
            self.base_api_url,
            response.json()['id'],
            card_name,
            self.id,
            card_position,
            0
        )
        # self.add_list(new_list, position)
        self._add_existing_card(new_card)
        return new_card


class RestyaboardCard(RestyaboardItem):
    def __init__(self, user_access_token, base_api_url, card_id, card_name, list_id, card_position, card_is_archived):
        RestyaboardItem.__init__(self, user_access_token, base_api_url, card_id, card_name)
        self.card_list_id = list_id
        self.card_position = card_position
        self.card_is_archived = card_is_archived


class RestyaboardUser(object):
    def __init__(self, user_access_token, base_api_url, id, email, username):
        self.user_access_token = user_access_token
        self.id = id
        self.email = email
        self.username = username
