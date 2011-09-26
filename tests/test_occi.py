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
import sys
import urllib

#===============================================================================
# Convenience routines
#===============================================================================

def get_session_cookie(url, user, password):
    '''
    Returns a cookie with the session information.
    '''
    http = httplib2.Http()
    login_url = url + '/login'
    body = {'name': user, 'pass': password}
    headers = {'Content-type': 'application/x-www-form-urlencoded'}
    response, content = http.request(login_url, 'POST', headers = headers,
                                     body = urllib.urlencode(body))

    if not response['status'] == '302':

        print(response, content)
        raise AttributeError('Something went wrong during lo-gin...')

    return response['set-cookie']

def get_version(url, heads):
    '''
    First called to check what service is running. Also very simple connection 
    test.
    '''
    http = httplib2.Http()
    try:
        response, content = http.request(url, 'GET', headers = heads)
    except:
        logging.warn('Could not do a simple GET! Maybe service requires login?')
        sys.exit(1)
    return response['server']

def get_categories(url, heads):
    url = url + '/-/'
    http = httplib2.Http()
    response, content = http.request(url, 'GET', headers = heads)
    result = []
    for line in content.split('\n'):
        result.append(line)
    return result

#===============================================================================
# The tests...
#===============================================================================

def test_version_information(url, heads):
    '''
    Verifies that OCCI/1.1 can be found in the Server header string.
    '''
    http = httplib2.Http()
    response, content = http.request(url, 'GET', headers = heads)
    if response['server'].find('OCCI/1.1') is - 1:
        raise AttributeError('OCCI implementation should include OCCI/1.1 - '
                     + 'Service did return: ' + response['server'])

def check_if_complete(rendering, rel, attributes, actions):
    '''
    Checks if a certain kind, mixin, action is complete...
    '''
    for item in rendering:
        item = item.strip().split('=')
        if item[0] == 'rel':
            if item[1].find(rel) == -1:
                raise AttributeError('Could not find the correct related. Should be "' + rel + '". Found: ' + item[1])
        elif item[0] == 'attributes':
            for attr in attributes:
                if item[1].find(attr) == -1:
                    raise AttributeError('Mandatory attribute "' + attr + '" was not found for: ' + rendering[0].strip() + '. Found: ' + item[1])
        elif item[0] == 'actions':
            for action in actions:
                if item[1].find(action) == -1:
                    raise AttributeError('Mandatory action "' + action + '" was not found for: ' + rendering[0].strip() + '. Found: ' + item[1])

def test_infrastructure_model_for_completness(url, heads):
    '''
    Verifies if the infrastructure model is implemented as specified.
    '''
    heads['Accept'] = 'text/plain'
    url = url + '/-/'
    http = httplib2.Http()
    response, content = http.request(url, 'GET', headers = heads)
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
        raise AttributeError('Missing compute kind.')
    elif not 'network' in infra_model:
        raise AttributeError('Missing network kind.')
    elif not 'storage' in infra_model:
        raise AttributeError('Missing storage kind.')
    elif not 'storagelink' in infra_model:
        raise AttributeError('Missing storagelink link.')
    elif not 'networkinterface' in infra_model:
        raise AttributeError('Missing networkinterface link.')
    elif not 'ipnetwork' in infra_model:
        raise AttributeError('Missing ipnetwork mixin.')
    elif not 'start' in infra_model:
        raise AttributeError('Missing start action definition.')
    elif not 'stop' in infra_model:
        raise AttributeError('Missing stop action definition.')
    elif not 'restart' in infra_model:
        raise AttributeError('Missing restart action definition.')
    elif not 'suspend' in infra_model:
        raise AttributeError('Missing suspend action definition.')
    elif not 'up' in infra_model:
        raise AttributeError('Missing up action definition.')
    elif not 'down' in infra_model:
        raise AttributeError('Missing down action definition.')
    elif not 'snapshot' in infra_model:
        raise AttributeError('Missing snapshot action definition.')
    elif not 'resize' in infra_model:
        raise AttributeError('Missing resize action definition.')
    elif not 'online' in infra_model:
        raise AttributeError('Missing online action definition.')
    elif not 'offline' in infra_model:
        raise AttributeError('Missing offline action definition.')
    elif not 'backup' in infra_model:
        raise AttributeError('Missing backup action definition.')

def test_accept_header(url, heads):
    '''
    Checks if correct content-types are returned for certain Accept headers.
    '''
    # GETs
    heads['Accept'] = 'text/plain'
    url = url + '/-/'
    http = httplib2.Http()
    response, content = http.request(url, 'GET', headers = heads)
    if not response['content-type'] == 'text/plain':
        raise AttributeError('When requesting text/plain - The Content-type text/plain should be exposed by the server.')

    heads['Accept'] = 'text/occi'
    http = httplib2.Http()
    response, content = http.request(url, 'GET', headers = heads)
    if not response['content-type'] == 'text/occi':
        raise AttributeError('When requesting text/occi - The Content-type text/occi should be exposed by the server.')
    if not response['status'] == '200':
        raise AttributeError('could not triggered action: ' + repr(response) + content)
    # POSTs
    #TODO...

def test_create_kinds(url, heads):
    '''
    tests the basic creation of kinds.
    '''
    loc = ''
    heads['Content-Type'] = 'text/occi'

    # POST
    post_heads = heads.copy()
    post_heads['Category'] = 'compute;scheme="http://schemas.ogf.org/occi/infrastructure#"'
    http = httplib2.Http()
    response, content = http.request(url, 'POST', headers = post_heads)
    if not response['status'] is '200' or response['status'] is '201':
        logging.warn('Creation failed - this might be okay - please examine output! ' + repr(response) + ' ' + content)
        raise AttributeError("Test did no run completly!")
    try:
        loc = response['location']
    except KeyError:
        raise AttributeError('OCCI implementation should expose the URI of the newly created resource.')

    # PUT
    put_heads = heads.copy()
    put_heads['X-OCCI-Attribute'] = 'occi.compute.hostname=foo'
    http = httplib2.Http()
    response, content = http.request(loc, 'PUT', headers = put_heads)
    if not response['status'] == '200' or response['status'] == '201':
        raise AttributeError('Unable to do an update on the resource: ' + loc)

    # GET
    http = httplib2.Http()
    response, content = http.request(loc, 'GET', headers = heads)
    if not response['status'] == '200' or response['status'] == '201':
        raise AttributeError('Unable to do retrieve the resource: ' + loc)

    # DELETE
    http = httplib2.Http()
    response, content = http.request(loc, 'DELETE', headers = heads)
    if not response['status'] == '200' or response['status'] == '201':
        raise AttributeError('Unable to do delete the resource: ' + loc)

def test_mixins(url, heads):
    '''
    Tests if a mixin can be created, retrieved and deleted.
    '''
    heads['Content-Type'] = 'text/occi'

    put_heads = heads.copy()
    put_heads['Category'] = 'my_stuff;scheme="http://example.com/occi#";location="/my_stuff/"'
    http = httplib2.Http()
    response, content = http.request(url + '/-/', 'POST', headers = put_heads)
    if not response['status'] == '200' or response['status'] == '202':
        raise AttributeError('Unable to create a user-defined mixin. Response: ' + repr(response) + content)

    http = httplib2.Http()
    response, content = http.request(url + '/-/', 'GET', headers = heads)
    if response['category'].find('my_stuff') == -1:
        raise AttributeError('Unable to find the previously defined mixin in the query interface!')

    put_heads = heads.copy()
    put_heads['Category'] = 'my_stuff;scheme="http://example.com/occi#"'
    http = httplib2.Http()
    response, content = http.request(url + '/-/', 'DELETE', headers = put_heads)
    if not response['status'] == '200' or response['status'] == '202':
        raise AttributeError('Unable to delete a user-defined mixin. Response: ' + repr(response) + content)

def test_links(url, heads):
    '''
    Tests if links are properly supported.
    '''
    heads['Content-Type'] = 'text/occi'

    # POST
    compute_heads = heads.copy()
    compute_heads['Category'] = 'compute;scheme="http://schemas.ogf.org/occi/infrastructure#"'
    http = httplib2.Http()
    response, content = http.request(url, 'POST', headers = compute_heads)
    if not response['status'] == '200' or response['status'] == '201':
        logging.warn('Creation failed - this might be okay - please examine output! ' + repr(response) + content)
        raise AttributeError("Test did no run completly!")
    compute_loc = response['location']

    network = heads.copy()
    network['Category'] = 'network;scheme="http://schemas.ogf.org/occi/infrastructure#"'
    http = httplib2.Http()
    response, content = http.request(url, 'POST', headers = network)
    if not response['status'] == '200' or response['status'] == '201':
        logging.warn('Creation failed - this might be okay - please examine output! ' + repr(response) + content)
        raise AttributeError("Test did no run completly!")
    network_loc = response['location']

    # now create a link...
    link = heads.copy()
    link['Category'] = 'networkinterface;scheme="http://schemas.ogf.org/occi/infrastructure#"'
    link['X-OCCI-Attribute'] = 'source=' + compute_loc + ',target=' + network_loc
    http = httplib2.Http()
    response, content = http.request(url, 'POST', headers = link)
    if not response['status'] == '200' or response['status'] == '201':
        logging.warn('Creation failed - this might be okay - please examine output! ' + repr(response) + content)
        raise AttributeError("Test did no run completly!")
    link_loc = response['location']

    # cleanup...    
    http = httplib2.Http()
    response, content = http.request(link_loc, 'DELETE', headers = heads)
    http = httplib2.Http()
    response, content = http.request(compute_loc, 'DELETE', headers = heads)
    http = httplib2.Http()
    response, content = http.request(network_loc, 'DELETE', headers = heads)

def test_actions(url, heads):
    '''
    Tests if actions can be triggered.
    '''
    heads['Content-Type'] = 'text/occi'

    # POST
    compute_heads = heads.copy()
    compute_heads['Category'] = 'compute;scheme="http://schemas.ogf.org/occi/infrastructure#"'
    http = httplib2.Http()
    response, content = http.request(url, 'POST', headers = compute_heads)
    if not response['status'] == '200' or response['status'] == '201':
        logging.warn('Creation failed - this might be okay - please examine output!' + repr(response) + content)
        raise AttributeError("Test did no run completly!")
    compute_loc = response['location']

    http = httplib2.Http()
    response, content = http.request(compute_loc, 'GET', headers = heads)
    links = response['link'].split(',')
    for link in links:
        if link == '<' + compute_loc + '?action=start>':
            action_url = link.lstrip('<').rstrip('>')
            http = httplib2.Http()
            action_heads = heads.copy()
            action_heads['Category'] = 'start;scheme="http://schemas.ogf.org/occi/infrastructure/compute/action#"'
            response, content = http.request(action_url, 'POST', headers = action_heads)
            if not response['status'] == '200':
                raise AttributeError('could not triggered action: ' + repr(response) + content)

    http = httplib2.Http()
    response, content = http.request(compute_loc, 'DELETE', headers = heads)
    if not response['status'] == '200':
        raise AttributeError('could not delete resource: ' + repr(response) + content)

def test_filter(url, heads):
    '''
    Tests if the filtering mechanisms work.
    '''

    # POST
    compute_heads = heads.copy()
    compute_heads['Category'] = 'compute;scheme="http://schemas.ogf.org/occi/infrastructure#"'
    http = httplib2.Http()
    response, content = http.request(url, 'POST', headers = compute_heads)
    if not response['status'] == '200' or response['status'] == '201':
        logging.warn(response['status'])
        logging.warn('Creation failed - this might be okay - please examine output!' + repr(response) + content)
        raise AttributeError("Test did no run completly!")
    compute_loc = response['location']

    network = heads.copy()
    network['Category'] = 'network;scheme="http://schemas.ogf.org/occi/infrastructure#"'
    http = httplib2.Http()
    response, content = http.request(url, 'POST', headers = network)
    if not response['status'] == '200' or response['status'] == '201':
        logging.warn('Creation failed - this might be okay - please examine output!' + repr(response) + content)
        raise AttributeError("Test did no run completly!")
    network_loc = response['location']

    # test if filtering works...
    filter_heads = heads.copy()
    filter_heads['Category'] = 'network;scheme="http://schemas.ogf.org/occi/infrastructure#"'
    http = httplib2.Http()
    response, content = http.request(url, 'GET', headers = filter_heads)
    if not response['x-occi-location'].find(compute_loc) is - 1:
        raise AttributeError('Filtering seems not have to be done reponse still include compute: ' + repr(response) + content)

    http = httplib2.Http()
    response, content = http.request(compute_loc, 'DELETE', headers = heads)
    if not response['status'] == '200':
        raise AttributeError('could not delete resource: ' + repr(response) + content)

    http = httplib2.Http()
    response, content = http.request(network_loc, 'DELETE', headers = heads)
    if not response['status'] == '200':
        raise AttributeError('could not delete resource: ' + repr(response) + content)

def test_location(url, heads):
    '''
    Do some ops on a location path.
    '''
    heads['Content-Type'] = 'text/occi'

    compute_heads = heads.copy()
    compute_heads['Category'] = 'compute;scheme="http://schemas.ogf.org/occi/infrastructure#"'
    http = httplib2.Http()
    response, content = http.request(url, 'POST', headers = compute_heads)
    if not response['status'] == '200' or response['status'] == '201':
        logging.warn('Creation failed - this might be okay - please examine output!' + repr(response) + content)
        raise AttributeError("Test did no run completly!")
    compute_loc = response['location']

    put_heads = heads.copy()
    put_heads['Category'] = 'my_stuff;scheme="http://example.com/occi#";location=/my_stuff/'
    http = httplib2.Http()
    response, content = http.request(url + '/-/', 'POST', headers = put_heads)
    if not response['status'] == '200' or response['status'] == '201':
        raise AttributeError('Unable to create a user-defined mixin. Response: ' + repr(response) + content)

    put_heads = heads.copy()
    put_heads['X-OCCI-Location'] = compute_loc
    http = httplib2.Http()
    response, content = http.request(url + '/my_stuff/', 'PUT', headers = put_heads)
    if not response['status'] == '200' or response['status'] == '202':
        raise AttributeError('Unable to add a kind to a user-defined mixin. Response: ' + repr(response) + content)

    http = httplib2.Http()
    response, content = http.request(compute_loc, 'GET', headers = heads)
    if response['category'].find('my_stuff') is - 1:
        raise AttributeError('Mixin was not added to resource: ' + repr(response) + content)

    http = httplib2.Http()
    response, content = http.request(compute_loc, 'DELETE', headers = heads)
    if not response['status'] == '200':
        raise AttributeError('could not delete resource: ' + repr(response) + content)

    put_heads = heads.copy()
    put_heads['Category'] = 'my_stuff;scheme="http://example.com/occi#"'
    http = httplib2.Http()
    response, content = http.request(url + '/-/', 'DELETE', headers = put_heads)
    if not response['status'] == '200' or response['status'] == '202':
        raise AttributeError('Unable to delete a user-defined mixin. Response: ' + repr(response) + content)

def test_syntax(url, heads):
    '''
    Simple syntax checks - see if Category is setup correctly. 
    '''
    # TODO add checks for syntac of links, locations, attributes...

    regex = r'\w+; \bscheme=[a-z:./#"]*; \bclass="(?:action|kind|mixin)"'

    heads['Accept'] = 'text/plain'
    url = url + '/-/'
    http = httplib2.Http()
    response, content = http.request(url, 'GET', headers = heads)
    cat_rend = content.split('\n')[1].strip()

    cat_rend = cat_rend[10:]
    p = re.compile(regex)
    print cat_rend, p.match(cat_rend)
    m = p.match(cat_rend)
    if m is None:
        raise AttributeError('There is an error in the syntax for rendering text/plain. Category should be setup like <term>;scheme="<url>";class=[kind,action,mixin]')

    heads['Accept'] = 'text/occi'
    http = httplib2.Http()
    response, content = http.request(url, 'GET', headers = heads)
    cat_rend = response['category'].strip()
    p = re.compile(regex)
    m = p.match(cat_rend)
    if m is None:
        raise AttributeError('There is an error in the syntax for rendering text/occi. Category should be setup like <term>;scheme="<url>";class=[kind,action,mixin]')
