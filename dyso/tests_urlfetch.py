#!/usr/bin/python
# -*- coding: utf-8 -*-
# $Id$

#
# This file is part of doyouspeakOCCI.
#
# doyouspeakOCCI is free software; you can redistribute it and/or
# modify it under the terms of the GNU Lesser General Public
# License as published by the Free Software Foundation; either
# version 2.1 of the License, or (at your option) any later version.
#
# doyouspeakOCCI is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
# Lesser General Public License for more details.
#
# You should have received a copy of the GNU Lesser General Public
# License along with this library; if not, write to the Free Software
# Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301 USA
#

import uuid

from google.appengine.api import urlfetch

class ComplianceError(Exception):
    """
    TODO: not yet documented.
    """

    def __init__(self, msg_list=None):
        if isinstance(msg_list, basestring):
            self.msg_list = [msg_list]
        else:
            self.msg_list = msg_list or []

    def __str__(self):
        return '\n'.join(self.msg_list)


def test_query_interface(url):
    """
    Tests the query interface as described in the Open Cloud Computing Interface - RESTful HTTP Rendering, section 3.4.1
    """
    messages = []
    headers = {
        'Content-type': 'text/occi',
        'Accept': 'text/plain'
    }

    # retrieval of all kinds, actions and mixins
    result = urlfetch.fetch(url + '/.well-known/org/ogf/occi/-/', method=urlfetch.GET)
    if not result.status_code in [200]:
        messages.append(
            'GET on query interface failed ('
            + str(result.status_code) + '): ' + result.content)

    # filter based on category
    get_headers = headers.copy()
    get_headers['Accept'] = 'text/occi'
    get_headers['Category'] = 'compute; scheme="http://schemas.ogf.org/occi/infrastructure#"'

    result = urlfetch.fetch(url + '/.well-known/org/ogf/occi/-/', method=urlfetch.GET, headers=get_headers)

    if not result.status_code in [200]:
        messages.append(
            'Category-based filtering on query interface failed ('
            + str(result.status_code) + ') ' + result.content)
    if len(result.headers['category'].split(',')) > 1: # TODO
        messages.append(
            'Filtering on query interface failed: '
            + 'expected \'http://schemas.ogf.org/occi/infrastructure#compute\' category representation; '
            + 'received ' + str(result.headers['category'])) # TODO

    # remove the mixin if it exists first to avoid conflicts
    get_headers = headers.copy()
    get_headers['Category'] = 'my_stuff; scheme="http://example.com/occi/my_stuff#"'
    result = urlfetch.fetch(url + '/.well-known/org/ogf/occi/-/', method=urlfetch.GET, headers=get_headers)
    if result.status_code in [200]:
        del_heads = headers.copy()
        del_heads['Category'] = 'my_stuff; scheme="http://example.com/occi/my_stuff#"'
        result = urlfetch.fetch(url + '/.well-known/org/ogf/occi/-/', method=urlfetch.DELETE, headers=del_heads)

    # adding a mixin definition
    post_heads = headers.copy()
    post_heads[
    'Category'] = 'my_stuff; scheme="http://example.com/occi/my_stuff#"; class="mixin"; rel="http://example.com/occi/something_else#mixin"; location="/my_stuff/"'
    result = urlfetch.fetch(url + '/.well-known/org/ogf/occi/-/', method=urlfetch.POST, headers=post_heads)
    if not result.status_code in [200]:
        messages.append(
            'Addition of user-defined mixin on query interface failed ('
            + str(result.status_code) + '): ' + result.content)

    # removing a mixin definition
    delete_heads = headers.copy()
    delete_heads['Category'] = 'my_stuff; scheme="http://example.com/occi/my_stuff#"; class="mixin";'
    result = urlfetch.fetch(url + '/.well-known/org/ogf/occi/-/', method=urlfetch.DELETE, headers=delete_heads)
    if not result.status_code in [200]:
        messages.append(
            'Removal of user-defined mixin on query interface failed ('
            + str(result.status_code) + '): ' + result.content)

    if messages:
        raise ComplianceError(messages)


def test_operations_on_mixins_or_kinds(url):
    """
    Test operations on mixins or kinds as described in section 3.4.[2,3]...
    """
    msg_list = []
    heads = {'Content-Type': 'text/occi',
             'Accept': 'text/occi'}
    unique_hostname = "doyouspeakocci::" + uuid.uuid4()

    # POST some compute instances
    post_heads = heads.copy()
    post_heads['Category'] = 'compute;scheme="http://schemas.ogf.org/occi/infrastructure#"'
    urlfetch.fetch(url, method=urlfetch.POST, headers=post_heads)
    post_heads['X-OCCI-Attribute'] = 'occi.compute.hostname="%s"' % unique_hostname
    urlfetch.fetch(url, method=urlfetch.POST, headers=post_heads)

    # get them as described in section 3.4.2 - text/plain and text/uri-list should contain the same infos...
    response1, content = http.request(url + '/compute/', 'GET', headers=heads)

    get_heads = {'Accept': 'text/uri-list'}
    response, content = http.request(url + '/compute/', 'GET', headers=get_heads)

    content = [item.strip() for item in content.split('\n')]
    for item in response1['x-occi-location'].split(','):
        if item.strip() not in content:
            msg_list.append('X-OCCI-Location and uri-list do not return the same values for the compute collection...')

    # trigger action on collection
    action_heads = heads.copy()
    action_heads['Category'] = 'start; scheme="http://schemas.ogf.org/occi/infrastructure/compute/action#"'
    response, content = http.request(url + '/compute/?action=start', 'POST', headers=action_heads)
    if not response.status == 200:
        msg_list.append('Could not triggered action: ' + repr(response) + content)

    # create a user defined mixin and add a compute instance
    compute_loc = response1['x-occi-location'].split(', ')[0]
    compute_loc2 = response1['x-occi-location'].split(', ')[1]

    post_heads = heads.copy()
    post_heads[
    'Category'] = 'my_stuff; scheme="http://example.com/occi/my_stuff#"; class="mixin"; rel="http://example.com/occi/something_else#mixin"; location="/my_stuff/"'
    response, content = http.request(url + '/-/', 'POST', headers=post_heads)
    if response.status != 200:
        msg_list.append('Unable to create a user-defined mixin. Response: ' + repr(response) + content)

    post_heads = heads.copy()
    post_heads['X-OCCI-Location'] = compute_loc
    response, content = http.request(url + '/my_stuff/', 'POST', headers=post_heads)
    if response.status != 200:
        msg_list.append('Unable to add a kind to a user-defined mixin. Response: ' + repr(response) + content)

    # check if the user defined mixin was added to the compute instance
    response, content = http.request(compute_loc, 'GET', headers=heads)
    if response['category'].find('my_stuff') is - 1:
        msg_list.append('Mixin was not added to resource: ' + repr(response) + content)

    # check if a get on the location of the user-defined mixin return the compute_loc
    response, content = http.request(url, 'GET', headers=heads)
    if len(response['x-occi-location'].split(',')) == 0:
        msg_list.append('Collection seems to be empty: ' + repr(response) + content)

    # replace the collection and only add compute_loc2 as the new collection
    put_heads = heads.copy()
    put_heads['X-OCCI-Location'] = compute_loc2
    response, content = http.request(url + '/my_stuff/', 'PUT', headers=put_heads)
    if response.status != 200:
        msg_list.append('The full update seems not to be working: ' + repr(response) + content)

    response, content = http.request(url + '/my_stuff/', 'GET', headers=heads)
    if response.get('x-occi-location') != compute_loc2:
        msg_list.append('Full update seems not to be working...' + repr(response) + content)

    # filter on /compute/ based on category my_stuff...
    get_heads = heads.copy()
    get_heads['Category'] = 'my_stuff; scheme="http://example.com/occi/my_stuff#"'
    response, content = http.request(url + '/compute/', 'GET', headers=get_heads)
    if response.get('x-occi-location') != compute_loc2:
        msg_list.append('Filtering based on categories seems not to be working...' + repr(response) + content)

    # filter on /copmute/ based on attribute and prev set hostname...
    get_heads = heads.copy()
    get_heads['X-OCCI-Attribute'] = 'occi.compute.hostname="%s"' % unique_hostname
    response, content = http.request(url + '/compute/', 'GET', headers=get_heads)
    if not response.get('x-occi-location') or len(response['x-occi-location'].split()) != 1:
        msg_list.append('Filtering based on attributes seems not to be working...' + repr(response) + content)

    # now also delete the second compute
    delete_heads = heads.copy()
    delete_heads['X-OCCI-Location'] = compute_loc2
    response, content = http.request(url + '/my_stuff/', 'DELETE', headers=delete_heads)
    if response.status != 200:
        raise TestFailure('Unable to remove last entity from mixin. Response: ' + repr(response) + content)

    response, content = http.request(url + '/my_stuff/', 'GET', headers=heads)
    if hasattr(response, 'x-occi-location'):
        msg_list.append('The collection should be empty but server responded: ' + repr(response) + content)

    # finally delete the mixin
    put_heads = heads.copy()
    put_heads['Category'] = 'my_stuff; scheme="http://example.com/occi/my_stuff#"; class="mixin"'
    response, content = http.request(url + '/-/', 'DELETE', headers=put_heads)
    if response.status != 200:
        raise TestFailure('Unable to delete a user-defined mixin. Response: ' + repr(response) + content)

    # and delete all compute instances
    del_heads = heads.copy()
    response, content = http.request(url + '/compute/', 'DELETE')
    if response.status != 200:
        raise TestFailure('Unable to delete a compute instances. Response: ' + repr(response) + content)

    if msg_list:
        raise TestFailure(msg_list)

# eof