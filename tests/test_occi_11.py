#!/usr/bin/python
# -*- coding: utf-8 -*-

#
# Copyright (C) 2011 Platform Computing
#
# This library is free software; you can redistribute it and/or
# modify it under the terms of the GNU Lesser General Public
# License as published by the Free Software Foundation; either
# version 2.1 of the License, or (at your option) any later version.
#
# This library is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
# Lesser General Public License for more details.
#
# You should have received a copy of the GNU Lesser General Public
# License along with this library; if not, write to the Free Software
# Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301 USA
#

import httplib2
import logging
import re
import uuid


class TestFailure(Exception):
    '''
    TBD.
    '''
    def __init__(self, msg_list=None):
        if isinstance(msg_list, basestring):
            self.msg_list = [ msg_list ]
        else:
            self.msg_list = msg_list or []

    def __str__(self):
        return '\n'.join(self.msg_list)


def test_query_interface(url):
    '''
    Test the Query Interface as described in section 3.4.1...
    '''
    msg_list = []
    http = httplib2.Http()
    heads = {'Content-type': 'text/occi',
             'Accept': 'text/plain'}

    # retrieval of all kinds, actions and mixins
    response, content = http.request(url + '/.well-known/org/ogf/occi/-/', 'GET')
    if not response.status in [200]:
        msg_list.append('Get on Query Interface failed - ' + str(response.status) + ' ' + response.reason + ' ' + content)

    # filter based on category
    get_headers = heads.copy()
    get_headers['Accept'] = 'text/occi'
    get_headers['Category'] = 'compute; scheme="http://schemas.ogf.org/occi/infrastructure#"'
    response, content = http.request(url + '/.well-known/org/ogf/occi/-/', 'GET', headers=get_headers)
    if not response.status in [200]:
        msg_list.append('Failed to filter the query interface - ' + str(response.status) + ' ' + response.reason + ' ' + content)
    if len(response['category'].split(',')) > 1:
        msg_list.append('The filter mechanism does not work - should only contain the compute category definition - but was: ' + str(response['category']))

    # remove the mixin if it exists first to avoid conflicts
    get_headers = heads.copy()
    get_headers['Category'] = 'my_stuff; scheme="http://example.com/occi/my_stuff#"'
    response, content = http.request(url + '/.well-known/org/ogf/occi/-/', 'GET', headers=get_headers)
    if response.status in [200]:
        del_heads = heads.copy()
        del_heads['Category'] = 'my_stuff; scheme="http://example.com/occi/my_stuff#"'
        response, content = http.request(url + '/.well-known/org/ogf/occi/-/', 'DELETE', headers=del_heads)

    # adding a mixin definition
    post_heads = heads.copy()
    post_heads['Category'] = 'my_stuff; scheme="http://example.com/occi/my_stuff#"; class="mixin"; rel="http://example.com/occi/something_else#mixin"; location="/my_stuff/"'
    response, content = http.request(url + '/.well-known/org/ogf/occi/-/', 'POST', headers=post_heads)
    if not response.status in [200]:
        msg_list.append('Failed to add a user defined mixin - ' + str(response.status) + ' ' + response.reason + ' ' + content)

    # removing a mixin definition
    delete_heads = heads.copy()
    delete_heads['Category'] = 'my_stuff; scheme="http://example.com/occi/my_stuff#"; class="mixin";'
    response, content = http.request(url + '/.well-known/org/ogf/occi/-/', 'DELETE', headers=delete_heads)
    if not response.status in [200]:
        msg_list.append('Failed to remove a  mixin - ' + str(response.status) + ' ' + response.reason + ' ' + content)

    if msg_list:
        raise TestFailure(msg_list)
    return 'OK'


def test_operations_on_mixins_or_kinds(url):
    '''
    Test operations on mixins or kinds as described in section 3.4.[2,3]...
    '''
    msg_list = []
    http = httplib2.Http()
    heads = {'Content-Type': 'text/occi',
             'Accept': 'text/occi'}
    unique_hostname = "foo %s bar" % uuid.uuid4()

    # POST some compute instances
    post_heads = heads.copy()
    post_heads['Category'] = 'compute;scheme="http://schemas.ogf.org/occi/infrastructure#"'
    response, content = http.request(url, 'POST', headers=post_heads)
    post_heads['X-OCCI-Attribute'] = 'occi.compute.hostname="%s"' % unique_hostname
    response, content = http.request(url, 'POST', headers=post_heads)

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
    post_heads['Category'] = 'my_stuff; scheme="http://example.com/occi/my_stuff#"; class="mixin"; rel="http://example.com/occi/something_else#mixin"; location="/my_stuff/"'
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
    return 'OK'


def test_operations_on_resource_instances(url):
    '''
    Test operations on resource instances as described in section 3.4.4...
    '''
    msg_list = []
    http = httplib2.Http()
    heads = {'Content-Type': 'text/occi',
             'Accept': 'text/occi'}

    # POST to create
    post_heads = heads.copy()
    post_heads['Category'] = 'compute;scheme="http://schemas.ogf.org/occi/infrastructure#"'
    response, content = http.request(url, 'POST', headers=post_heads)
    if response.status == 201 or (response.status == 200 and 'location' in response):
        loc = response['location']
    elif response.status == 200:
        logging.warn('Seems like OCCI server responded with 200...not 201 and location...')
        response, content = http.request(url + '/compute/', 'GET', headers=heads)
        loc = response['x-occi-location'].split(',')[0].strip()
    else:
        msg_list.append('Could not create compute kind...')

    # trigger action...
    response, content = http.request(loc, 'GET', headers=heads)
    links = response['link'].split(',')
    for link in links:
        if link.find('?action=start>') != -1:
            action_url = url + link[1:link.find('>')]
            action_heads = heads.copy()
            action_heads['Category'] = 'start; scheme="http://schemas.ogf.org/occi/infrastructure/compute/action#"'
            response, content = http.request(action_url, 'POST', headers=action_heads)
            if not response.status == 200:
                msg_list.append('could not triggered action: ' + repr(response) + content)
        else:
            logging.warn('Start action not applicable - might be correct...')

    # POST - partial update
    post_heads = heads.copy()
    post_heads['X-OCCI-Attribute'] = 'occi.compute.hostname="foo"'
    response, content = http.request(loc, 'POST', headers=post_heads)
    if not response.status == 200:
        msg_list.append('Unable to do an update on the resource: ' + loc)

    # PUT create
    put_url = url + '/123'
    put_heads = heads.copy()
    put_heads['Category'] = 'compute;scheme="http://schemas.ogf.org/occi/infrastructure#"'
    put_heads['X-OCCI-Attribute'] = 'example.test="foo"'
    response, content = http.request(put_url, 'PUT', headers=put_heads)
    # RN: A server is allowed to refuse the request. #3.4.4 footnote 6.
    if response.status == 400:
        logging.warn('Server refused PUT /123, this is OK according to section 3.4.4')
        put_url = loc
    elif not response.status in [200, 201]:
        msg_list.append('Failed to put a new compute resource at /123, response: ' + repr(response) + content)

    # PUT for full update
    put_heads = heads.copy()
    put_heads['Category'] = 'compute;scheme="http://schemas.ogf.org/occi/infrastructure#"'
    put_heads['X-OCCI-Attribute'] = 'occi.core.title="My Compute instance"'
    response, content = http.request(put_url, 'PUT', headers=put_heads)
    if not response.status == 200:
        msg_list.append('Failed to do a full update on compute resource at /123, response: ' + repr(response) + content)

    # GET
    response, content = http.request(loc, 'GET', headers=heads)
    if not response.status == 200:
        msg_list.append('Unable to do retrieve the resource: ' + loc)

    # DELETE
    response, content = http.request(loc, 'DELETE', headers=heads)
    if not response.status == 200:
        msg_list.append('Unable to delete the resource: ' + loc)
    if loc != put_url:
        response, content = http.request(put_url, 'DELETE', headers=heads)
        if not response.status == 200:
            msg_list.append('Unable to do delete the resource: ' + loc)

    if msg_list:
        raise TestFailure(msg_list)
    return 'OK'


def test_handling_link_instances(url):
    '''
    Test handling of link instances as described in section 3.4.5...
    '''
    msg_list = []
    http = httplib2.Http()
    heads = {'Content-Type': 'text/occi'}

    # create compute
    compute_heads = heads.copy()
    compute_heads['Category'] = 'compute;scheme="http://schemas.ogf.org/occi/infrastructure#"'
    response, content = http.request(url, 'POST', headers=compute_heads)
    if 'location' not in response and response.status not in (201, 200):
        logging.warn('Creation failed - this might be okay - please examine output! ' + repr(response) + content)
        logging.warn('Test needs to be updated to discover location by doing a GET on /compute/')
        return 'UNDEFINED'
    compute_loc = response['location']

    # create network
    network = heads.copy()
    network['Category'] = 'network;scheme="http://schemas.ogf.org/occi/infrastructure#"'
    response, content = http.request(url, 'POST', headers=network)
    if response.status not in [200, 201]:
        logging.warn('Creation failed - this might be okay - please examine output! ' + repr(response) + content)
    network_loc = response['location']

    # now create a network link...
    link = heads.copy()
    link['Category'] = 'networkinterface;scheme="http://schemas.ogf.org/occi/infrastructure#"'
    link['X-OCCI-Attribute'] = 'occi.core.source="' + compute_loc + '", occi.core.target="' + network_loc + '"'
    response, content = http.request(url, 'POST', headers=link)
    if response.status not in [200, 201]:
        msg_list.append('Creation failed -  please examine output! ' + repr(response) + content)
    link_loc = response['location']

    # check if links has source, target attributes
    get_heads = heads.copy()
    get_heads['Accept'] = 'text/occi'
    response, content = http.request(link_loc, 'GET', headers=get_heads)
    if response.has_key('x-occi-attribute'):
        if response['x-occi-attribute'].find('occi.core.source') == -1 or response['x-occi-attribute'].find('occi.core.target') == -1:
            msg_list.append('The link seems to be missing source an target attributes. Response' + repr(response) + content)
    else:
        msg_list.append('Something did go wrong during the GET on the link. Response: ' + repr(response) + content)

    # 1st cleanup...
    response, content = http.request(compute_loc, 'DELETE', headers=heads)
    if not response.status == 200:
        msg_list.append('Unable to do delete the resource: ' + compute_loc)

    # now create compute again but with inline...
    compute_heads = heads.copy()
    compute_heads['Category'] = 'compute;scheme="http://schemas.ogf.org/occi/infrastructure#"'
    compute_heads['Link'] = '<' + network_loc + '>; rel="http://schemas.ogf.org/occi/infrastructure#network"; category="http://schemas.ogf.org/occi/infrastructure#networkinterface";'

    response, content = http.request(url, 'POST', headers=compute_heads)
    if response.status not in [200, 201]:
        logging.warn('Creation failed - this might be okay - please examine output! ' + repr(response) + content)
    compute_loc = response['location']

    # Now check if compute has inline link rendering...
    get_heads = heads.copy()
    get_heads['Accept'] = 'text/occi'
    response, content = http.request(compute_loc, 'GET', headers=get_heads)
    if not response.has_key('link'):
        msg_list.append('Inline link rendering for the compute resource seems to be missing. Response: ' + repr(response) + content)

    # 2nd cleanup...
    response, content = http.request(compute_loc, 'DELETE', headers=heads)
    if not response.status == 200:
        msg_list.append('Unable to do delete the resource: ' + compute_loc)
    # no need to delete link since that should be in the lifecycle of the compute resource...
    response, content = http.request(network_loc, 'DELETE', headers=heads)
    if not response.status == 200:
        msg_list.append('Unable to do delete the resource: ' + network_loc)

    if msg_list:
        raise TestFailure(msg_list)
    return 'OK'


def test_syntax(url):
    '''
    Test Syntax and Semantics of the Rendering as described in section 3.5...
    '''
    msg_list = []

    # TODO: add checks for syntax of links, locations, attributes...

    regex = r'\w+; \bscheme=[a-z:./#"]*; \bclass="(?:action|kind|mixin)"'

    heads = {'Accept': 'text/plain'}
    discovery_url = url + '/-/'
    http = httplib2.Http()
    response, content = http.request(discovery_url, 'GET', headers=heads)
    cat_rend = content.split('\n')[1].strip()

    cat_rend = cat_rend[10:]
    p = re.compile(regex)

    m = p.match(cat_rend)
    if m is None:
        msg_list.append('There is an error in the syntax for rendering text/plain. Category should be setup like <term>;scheme="<url>";class=[kind,action,mixin]')

    heads['Accept'] = 'text/occi'
    response, content = http.request(discovery_url, 'GET', headers=heads)
    cat_rend = response['category'].strip()
    p = re.compile(regex)
    m = p.match(cat_rend)
    if m is None:
        msg_list.append('There is an error in the syntax for rendering text/occi. Category should be setup like <term>;scheme="<url>";class=[kind,action,mixin]')

    # Test escaping of quotes
    post_heads = {'Content-Type': 'text/occi'}
    post_heads['Category'] = 'compute;scheme="http://schemas.ogf.org/occi/infrastructure#"'
    post_heads['X-OCCI-Attribute'] = 'occi.compute.memory=3.6, ' + \
            'occi.core.title="How\'s your quotes escaping? \\", occi.compute.memory=1.0"'
    response, content = http.request(url, 'POST', headers=post_heads)
    if not response.get('location') or response.status not in (200, 201):
        msg_list.append('Failed to create a Compute instance with X-OCCI-Attribute: %s' %
                post_heads['X-OCCI-Attribute'])
        raise TestFailure(msg_list)
    compute_loc = response.get('location')

    response, content = http.request(compute_loc, 'GET', headers={'Accept': 'text/plain'})
    if not response.status == 200:
        msg_list.append('Unable to retrieve the resource: ' + compute_loc)
    # If memory=1.0 quote parsing failed, should be 3.6
    found = False

    for line in content.split('\n'):
        l = line.split(':', 1)
        if len(l) < 2: continue
        header = l[0].strip()
        value = l[1].strip()
        if header.lower() != 'x-occi-attribute':
            continue
        l = value.split('=', 1)
        if len(l) < 2: continue
        if l[0] == 'occi.compute.memory':
            memory = l[1].strip('\s"')
            try:
                memory = float(memory)
            except ValueError:
                break
            else:
                if memory == 3.6:
                    found = True
    if not found:
        msg_list.append('Escaping of quotes is not parsed correctly')

    if msg_list:
        raise TestFailure(msg_list)
    return 'OK'


def test_versioning(url):
    '''
    Test that the correct version number can be found as described in section 3.6.5...
    '''
    msg_list = []
    http = httplib2.Http()

    heads = {
        'Accept': 'text/occi',
       }

    response, content = http.request(url + '/', 'GET')
    if response.get('server').find('OCCI/1.1') == -1:
        msg_list.append('Server does not correctly expose version OCCI/1.1. Server responded: ' + response.get('server'))

    if msg_list:
        raise TestFailure(msg_list)
    return 'OK'


def test_content_type_and_accept_headers(url):
    '''
    Test Content-type and Accept headers as described in section 3.6.6...
    '''
    # TODO: check post commands...
    msg_list = []
    heads = {'Accept': 'text/plain'}
    url = url + '/-/'
    http = httplib2.Http()

    response, content = http.request(url, 'GET', headers=heads)
    content_type = response.get('content-type')
    if content_type: content_type = content_type.split(';')[0].strip()
    if not content_type == 'text/plain':
        msg_list.append('When requesting text/plain - The Content-type text/plain should be exposed by the server.')

    heads = {'Accept': 'text/occi'}
    response, content = http.request(url, 'GET', headers=heads)
    content_type = response.get('content-type')
    if content_type: content_type = content_type.split(';')[0].strip()
    if not content_type == 'text/occi':
        msg_list.append('When requesting text/occi - The Content-type text/occi should be exposed by the server.')

    if msg_list:
        raise TestFailure(msg_list)
    return 'OK'


def test_rfc5785_compliance(url):
    '''
    Test RFC5785 Compliance as described in section 3.6.7...
    '''
    msg_list = []

    heads = {'Accept': 'text/occi'}

    # retrieval of all kinds, actions and mixins
    http = httplib2.Http()
    response1, content1 = http.request(url + '/.well-known/org/ogf/occi/-/', 'GET', headers=heads)
    if not response1.status in [200]:
        msg_list.append('Get on Query Interface failed - ' + str(response1.status) + ' ' + response1.reason + ' ' + content1)

    # retrieval of all kinds, actions and mixins
    response2, content2 = http.request(url + '/-/', 'GET', headers=heads)
    if not response2.status in [200]:
        msg_list.append('Get on Query Interface failed - ' + str(response2.status) + ' ' + response2.reason + ' ' + content2)

    if response1['category'] != response2['category']:
        msg_list.append('Reponse differ for /-/ and .well-known/...')

    if msg_list:
        raise TestFailure(msg_list)
    return 'OK'


def check_if_complete(rendering, rel, attributes, actions):
    '''
    Checks if a certain kind, mixin, action is complete...
    '''
    for item in rendering:
        item = item.strip().split('=')
        if item[0] == 'rel':
            if item[1].find(rel) == -1:
                raise TestFailure('Could not find the correct related. Should be "' + rel + '". Found: ' + item[1])
        elif item[0] == 'attributes':
            for attr in attributes:
                if item[1].find(attr) == -1:
                    raise TestFailure('Mandatory attribute "' + attr + '" was not found for: ' + rendering[0].strip() + '. Found: ' + item[1])
        elif item[0] == 'actions':
            for action in actions:
                if item[1].find(action) == -1:
                    raise TestFailure('Mandatory action "' + action + '" was not found for: ' + rendering[0].strip() + '. Found: ' + item[1])


def test_occi_infrastructure(url):
    '''
    Test if the Iaas model is complete as defined in the Infrastructure specification...
    '''
    msg_list = []

    heads = {'Accept': 'text/plain'}
    url = url + '/-/'
    http = httplib2.Http()
    response, content = http.request(url, 'GET', headers=heads)

    infra_model = []
    for line in content.split('\n'):
        cur = line.lstrip('Category:').split(';')
        # check if compute has all attributes & actions & rels
        #----------------------------------------------------------------- Kinds
        if cur[0].strip() == 'compute' and cur[1].strip() == 'scheme="http://schemas.ogf.org/occi/infrastructure#"':
            rel = 'http://schemas.ogf.org/occi/core#resource'
            attr = ['occi.compute.architecture', 'occi.compute.cores', 'occi.compute.hostname', 'occi.compute.speed', 'occi.compute.memory', 'occi.compute.state']
            actions = ['start', 'stop', 'suspend', 'restart']
            check_if_complete(cur, rel, attr, actions)
            infra_model.append('compute')
        elif cur[0].strip() == 'network' and cur[1].strip() == 'scheme="http://schemas.ogf.org/occi/infrastructure#"':
            rel = 'http://schemas.ogf.org/occi/core#resource'
            attr = ['occi.network.vlan', 'occi.network.label', 'occi.network.state']
            actions = ['up', 'down']
            check_if_complete(cur, rel, attr, actions)
            infra_model.append('network')
        elif cur[0].strip() == 'storage' and cur[1].strip() == 'scheme="http://schemas.ogf.org/occi/infrastructure#"':
            rel = 'http://schemas.ogf.org/occi/core#resource'
            attr = ['occi.storage.size', 'occi.storage.state']
            actions = ['online', 'offline', 'backup', 'snapshot', 'resize']
            check_if_complete(cur, rel, attr, actions)
            infra_model.append('storage')
        #----------------------------------------------------------------- Links
        elif cur[0].strip() == 'storagelink' and cur[1].strip() == 'scheme="http://schemas.ogf.org/occi/infrastructure#"':
            rel = 'http://schemas.ogf.org/occi/core#link'
            attr = ['occi.storagelink.deviceid', 'occi.storagelink.mountpoint', 'occi.storagelink.state']
            actions = []
            check_if_complete(cur, rel, attr, actions)
            infra_model.append('storagelink')
        elif cur[0].strip() == 'networkinterface' and cur[1].strip() == 'scheme="http://schemas.ogf.org/occi/infrastructure#"':
            rel = 'http://schemas.ogf.org/occi/core#link'
            attr = ['occi.networkinterface.state', 'occi.networkinterface.mac', 'occi.networkinterface.interface']
            actions = []
            check_if_complete(cur, rel, attr, actions)
            infra_model.append('networkinterface')
        #---------------------------------------------------------------- mixins
        elif cur[0].strip() == 'ipnetwork' and cur[1].strip() == 'scheme="http://schemas.ogf.org/occi/infrastructure/network#"':
            rel = 'http://schemas.ogf.org/occi/core#link'
            attr = ['occi.network.address', 'occi.network.gateway', 'occi.network.allocation']
            actions = []
            check_if_complete(cur, rel, attr, actions)
            infra_model.append('ipnetwork')
        #--------------------------------------------------------------- actions
        elif cur[0].strip() == 'start' and cur[1].strip() == 'scheme="http://schemas.ogf.org/occi/infrastructure/compute/action#"':
            rel = ''
            attr = []
            actions = []
            check_if_complete(cur, rel, attr, actions)
            infra_model.append('start')
        elif cur[0].strip() == 'stop' and cur[1].strip() == 'scheme="http://schemas.ogf.org/occi/infrastructure/compute/action#"':
            rel = ''
            #attr = ['graceful', 'acpioff', 'poweroff']
            attr = ['method']
            actions = []
            check_if_complete(cur, rel, attr, actions)
            infra_model.append('stop')
        elif cur[0].strip() == 'restart' and cur[1].strip() == 'scheme="http://schemas.ogf.org/occi/infrastructure/compute/action#"':
            rel = ''
            #attr = ['graceful', 'warm', 'cold']
            attr = ['method']
            actions = []
            check_if_complete(cur, rel, attr, actions)
            infra_model.append('restart')
        elif cur[0].strip() == 'suspend' and cur[1].strip() == 'scheme="http://schemas.ogf.org/occi/infrastructure/compute/action#"':
            rel = ''
            #attr = ['hibernate', 'suspend']
            attr = ['method']
            actions = []
            check_if_complete(cur, rel, attr, actions)
            infra_model.append('suspend')
        elif cur[0].strip() == 'up' and cur[1].strip() == 'scheme="http://schemas.ogf.org/occi/infrastructure/network/action#"':
            rel = ''
            attr = []
            actions = []
            check_if_complete(cur, rel, attr, actions)
            infra_model.append('up')
        elif cur[0].strip() == 'down' and cur[1].strip() == 'scheme="http://schemas.ogf.org/occi/infrastructure/network/action#"':
            rel = ''
            attr = []
            actions = []
            check_if_complete(cur, rel, attr, actions)
            infra_model.append('down')
        elif cur[0].strip() == 'online' and cur[1].strip() == 'scheme="http://schemas.ogf.org/occi/infrastructure/storage/action#"':
            rel = ''
            attr = []
            actions = []
            check_if_complete(cur, rel, attr, actions)
            infra_model.append('online')
        elif cur[0].strip() == 'offline' and cur[1].strip() == 'scheme="http://schemas.ogf.org/occi/infrastructure/storage/action#"':
            rel = ''
            attr = []
            actions = []
            check_if_complete(cur, rel, attr, actions)
            infra_model.append('offline')
        elif cur[0].strip() == 'resize' and cur[1].strip() == 'scheme="http://schemas.ogf.org/occi/infrastructure/storage/action#"':
            rel = ''
            attr = ['size']
            actions = []
            check_if_complete(cur, rel, attr, actions)
            infra_model.append('resize')
        elif cur[0].strip() == 'backup' and cur[1].strip() == 'scheme="http://schemas.ogf.org/occi/infrastructure/storage/action#"':
            rel = ''
            attr = []
            actions = []
            check_if_complete(cur, rel, attr, actions)
            infra_model.append('backup')
        elif cur[0].strip() == 'snapshot' and cur[1].strip() == 'scheme="http://schemas.ogf.org/occi/infrastructure/storage/action#"':
            rel = ''
            attr = []
            actions = []
            check_if_complete(cur, rel, attr, actions)
            infra_model.append('snapshot')

    if not 'compute' in infra_model:
        msg_list.append('Missing compute kind.')
    if not 'network' in infra_model:
        msg_list.append('Missing network kind.')
    if not 'storage' in infra_model:
        msg_list.append('Missing storage kind.')
    if not 'storagelink' in infra_model:
        msg_list.append('Missing storagelink link.')
    if not 'networkinterface' in infra_model:
        msg_list.append('Missing networkinterface link.')
    if not 'ipnetwork' in infra_model:
        msg_list.append('Missing ipnetwork mixin.')
    if not 'start' in infra_model:
        msg_list.append('Missing start action definition.')
    if not 'stop' in infra_model:
        msg_list.append('Missing stop action definition.')
    if not 'restart' in infra_model:
        msg_list.append('Missing restart action definition.')
    if not 'suspend' in infra_model:
        msg_list.append('Missing suspend action definition.')
    if not 'up' in infra_model:
        msg_list.append('Missing up action definition.')
    if not 'down' in infra_model:
        msg_list.append('Missing down action definition.')
    if not 'snapshot' in infra_model:
        msg_list.append('Missing snapshot action definition.')
    if not 'resize' in infra_model:
        msg_list.append('Missing resize action definition.')
    if not 'online' in infra_model:
        msg_list.append('Missing online action definition.')
    if not 'offline' in infra_model:
        msg_list.append('Missing offline action definition.')
    if not 'backup' in infra_model:
        msg_list.append('Missing backup action definition.')

    if msg_list:
        raise TestFailure(msg_list)
    return 'OK'
