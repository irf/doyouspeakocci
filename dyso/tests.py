#!/usr/bin/python
# -*- coding: utf-8 -*-
# $Id$

#
# This file is part of doyouspeakOCCI.
#
# doyouspeakOCCI is free software; you can redistribute it and/or
# modify it under the terms of the GNU General Public
# License as published by the Free Software Foundation; either
# version 2.1 of the License, or (at your option) any later version.
#
# doyouspeakOCCI is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
# Lesser General Public License for more details.
#
# You should have received a copy of the GNU General Public
# License along with this library; if not, write to the Free Software
# Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301 USA
#

import logging
import re
import uuid

from google.appengine.api import urlfetch

class ComplianceError(Exception):
    """
Indicates the failure of one or more test steps during a test function run on
an OCCI service under inspection.

Attributes:
  messages -- A list of error messages collected during one test function run
    """
    messages = []

    def __init__(self, messages=None, *args, **kwargs):
        """
        
        """
        Exception.__init__(self, *args, **kwargs)
        if isinstance(messages, basestring):
            self.messages = [messages]
        else:
            self.messages = messages or []

    def __str__(self):
        """
        
        """
        return '\n'.join(self.messages)


def ctf_341(url):
    """
Tests the query interface as described in section 3.4.1 of the Open Cloud
Computing Interface - RESTful HTTP Rendering specification.
    """
    messages = []
    headers = {
        'Content-type': 'text/occi',
        'Accept': 'text/plain',
        'Cache-control': 'max-age=0',
    }

    # retrieval of all kinds, actions and mixins
    result = urlfetch.fetch(url + '/.well-known/org/ogf/occi/-/', headers=headers, deadline=60)
    if not result.status_code in [200]:
        messages.append(
            'GET on query interface failed ('
            + str(result.status_code) + '): ' + result.content)

    # filter based on category
    get_headers = headers.copy()
    get_headers['Accept'] = 'text/occi'
    get_headers['Category'] = 'compute; scheme="http://schemas.ogf.org/occi/infrastructure#"'

    result = urlfetch.fetch(url + '/.well-known/org/ogf/occi/-/', headers=get_headers, deadline=60)

    if not result.status_code in [200]:
        messages.append(
            'Category-based filtering on query interface failed ('
            + str(result.status_code) + ') ' + result.content)
    if len(result.headers['category'].split(',')) > 1:
        messages.append(
            'Filtering on query interface failed: '
            + 'expected \'http://schemas.ogf.org/occi/infrastructure#compute\' category representation; '
            + 'received ' + str(result.headers['category']))

    # remove the mixin if it exists first to avoid conflicts
    get_headers = headers.copy()
    get_headers['Category'] = 'my_stuff; scheme="http://example.com/occi/my_stuff#"'
    result = urlfetch.fetch(url + '/.well-known/org/ogf/occi/-/', headers=get_headers, deadline=60)
    if result.status_code in [200]:
        del_heads = headers.copy()
        del_heads['Category'] = 'my_stuff; scheme="http://example.com/occi/my_stuff#"'
        urlfetch.fetch(url + '/.well-known/org/ogf/occi/-/', method=urlfetch.DELETE, headers=del_heads, deadline=60)

    # adding a mixin definition
    post_heads = headers.copy()
    post_heads['Category'] = 'my_stuff; scheme="http://example.com/occi/my_stuff#"; class="mixin"; rel="http://example.com/occi/something_else#mixin"; location="/my_stuff/"'
    result = urlfetch.fetch(url + '/.well-known/org/ogf/occi/-/', method=urlfetch.POST, headers=post_heads, deadline=60)
    if not result.status_code in [200]:
        messages.append(
            'Addition of user-defined mixin on query interface failed ('
            + str(result.status_code) + '): ' + result.content)

    # removing a mixin definition
    delete_heads = headers.copy()
    delete_heads['Category'] = 'my_stuff; scheme="http://example.com/occi/my_stuff#"; class="mixin";'
    result = urlfetch.fetch(url + '/.well-known/org/ogf/occi/-/', method=urlfetch.DELETE, headers=delete_heads, deadline=60)
    if not result.status_code in [200]:
        messages.append(
            'Removal of user-defined mixin on query interface failed ('
            + str(result.status_code) + '): ' + result.content)

    if messages:
        raise ComplianceError(messages)


def ctf_342_343(url):
    """
Tests operations on mixins or kinds as described in section 3.4.2 and 3.4.3
of the Open Cloud Computing Interface - RESTful HTTP Rendering specification.
    """
    messages = []
    headers = {
        'Content-Type': 'text/occi',
        'Accept': 'text/occi',
        'Cache-control': 'max-age=0',
    }
    unique_hostname = "doyouspeakocci::" + uuid.uuid4().__str__()

    # POST some compute instances
    post_heads = headers.copy()
    post_heads['Category'] = 'compute;scheme="http://schemas.ogf.org/occi/infrastructure#"'
    urlfetch.fetch(url, method=urlfetch.POST, headers=post_heads, deadline=60)
    post_heads['X-OCCI-Attribute'] = 'occi.compute.hostname="' + unique_hostname + '"'
    urlfetch.fetch(url, method=urlfetch.POST, headers=post_heads, deadline=60)

    # get them as described in section 3.4.2 - text/plain and text/uri-list should contain the same result
    result_textocci = urlfetch.fetch(url + '/compute/', headers=headers, deadline=60)

    get_heads = {'Accept': 'text/uri-list', 'Cache-control': 'max-age=0'}
    result_texturilist = urlfetch.fetch(url + '/compute/', headers=get_heads, deadline=60)

    content = [item.strip() for item in result_texturilist.content.split('\n')]
    for item in result_textocci.headers['x-occi-location'].split(','):
        if item.strip() not in content:
            messages.append('X-OCCI-Location and uri-list do not return the same values for the compute collection.')

    # trigger action on collection
    action_heads = headers.copy()
    action_heads['Category'] = 'start; scheme="http://schemas.ogf.org/occi/infrastructure/compute/action#"'
    result = urlfetch.fetch(url + '/compute/?action=start', method=urlfetch.POST, headers=action_heads, deadline=60)
    if result.status_code != 200:
        messages.append(
            'Action triggering on collection failed: response was "' + repr(result) + '"'
        )

    # create a user defined mixin and add a compute instance
    computeinstance_first = result_textocci.headers['x-occi-location'].split(', ')[0]
    logging.debug(computeinstance_first)
    computeinstance_second = result_textocci.headers['x-occi-location'].split(', ')[1]
    logging.debug(computeinstance_second)

    post_heads = headers.copy()
    post_heads['Category']\
        = 'my_stuff; scheme="http://example.com/occi/my_stuff#"; class="mixin"; rel="http://example.com/occi/something_else#mixin"; location="/my_stuff/"'
    result = urlfetch.fetch(url + '/-/', method=urlfetch.POST, headers=post_heads, deadline=60)
    if result.status_code != 200:
        messages.append('Unable to create a user-defined mixin: response was "' + repr(result) + '"')

    post_heads = headers.copy()
    post_heads['X-OCCI-Location'] = computeinstance_first
    result = urlfetch.fetch(url + '/my_stuff/', method=urlfetch.POST, headers=post_heads, deadline=60)
    if result.status_code != 200:
        messages.append('Unable to add a kind to a user-defined mixin: response was "' + repr(result) + '"')

    # check if the user defined mixin was added to the compute instance
    result = urlfetch.fetch(computeinstance_first, headers=headers, deadline=60)
    logging.debug(repr(result.headers))
    if result.headers['category'].find('my_stuff') is - 1:
        messages.append('Adding mixin to resource seems to be broken: response was "' + repr(result) + '"')

    # check if a get on the location of the user-defined mixin return the compute_loc
    result = urlfetch.fetch(url, headers=headers, deadline=60)
    if not len(result.headers['x-occi-location'].split(',')):
        messages.append('Mixin collection unexpectedly empty: response was "' + repr(result) + '"')

    # replace the collection and only add compute_loc2 as the new collection
    put_heads = headers.copy()
    put_heads['X-OCCI-Location'] = computeinstance_second
    result = urlfetch.fetch(url + '/my_stuff/', method=urlfetch.PUT, headers=put_heads, deadline=60)
    if result.status_code != 200:
        messages.append('Running full update on resource seems to be broken: response was "' + repr(result) + '"')

    result = urlfetch.fetch(url + '/my_stuff/', headers=headers, deadline=60)
    if result.headers.get('x-occi-location') != computeinstance_second:
        messages.append('Running full udpate on resource seems to be broken: response was "' + repr(result) + '"')

    # filter on /compute/ based on category my_stuff...
    get_heads = headers.copy()
    get_heads['Category'] = 'my_stuff; scheme="http://example.com/occi/my_stuff#"'
    result = urlfetch.fetch(url + '/compute/', headers=get_heads, deadline=60)
    if result.headers.get('x-occi-location') != computeinstance_second:
        messages.append('Category-based filtering seems to be broken:  response was "' + repr(result) + '"')

    # filter on /copmute/ based on attribute and prev set hostname...
    get_heads = headers.copy()
    get_heads['X-OCCI-Attribute'] = 'occi.compute.hostname="' + unique_hostname + '"'
    result = urlfetch.fetch(url + '/compute/', headers=get_heads, deadline=60)
    if not result.headers.get('x-occi-location') or len(result.headers['x-occi-location'].split()) != 1:
        messages.append('Attribute-based filtering seems to be broken: response was "' + repr(result) + '"')

    # now also delete the second compute
    delete_heads = headers.copy()
    delete_heads['X-OCCI-Location'] = computeinstance_second
    result = urlfetch.fetch(url + '/my_stuff/', method=urlfetch.DELETE, headers=delete_heads, deadline=60)
    if result.status_code != 200:
        raise ComplianceError('Unable to remove last entity from mixin: response was "' + repr(result) + '"')

    result = urlfetch.fetch(url + '/my_stuff/', headers=headers, deadline=60)
    if hasattr(result.headers, 'x-occi-location'):
        messages.append('Unexpected item in collection: response was "' + repr(result) + '"')

    # finally delete the mixin
    put_heads = headers.copy()
    put_heads['Category'] = 'my_stuff; scheme="http://example.com/occi/my_stuff#"; class="mixin"'
    result = urlfetch.fetch(url + '/-/', method=urlfetch.DELETE, headers=put_heads, deadline=60)
    if result.status_code != 200:
        raise ComplianceError('Unable to delete a user-defined mixin: response was "' + repr(result) + '"')

    # and delete all compute instances
    del_heads = headers.copy()
    result = urlfetch.fetch(url + '/compute/', method=urlfetch.DELETE, headers=del_heads, deadline=60)
    if result.status_code != 200:
        raise ComplianceError('Unable to delete a compute instances: response was "' + repr(result) + '"')

    if messages:
        raise ComplianceError(messages)


def ctf_344(url):
    """
Tests operations on resource instances as described in section 3.4.4 of the
Open Cloud Computing Interface - RESTful HTTP Rendering specification.
    """
    messages = []
    headers = {
        'Content-Type': 'text/occi',
        'Accept': 'text/occi',
        'Cache-control': 'max-age=0',
    }

    # POST to create
    loc = None
    post_heads = headers.copy()
    post_heads['Category'] = 'compute;scheme="http://schemas.ogf.org/occi/infrastructure#"'
    result = urlfetch.fetch(url, method=urlfetch.POST, headers=post_heads, deadline=60)
    if result.status_code == 201 or (result.status_code == 200 and 'location' in result.headers):
        loc = result.headers['location']
    elif result.status_code == 200:
        logging.warn('Seems like OCCI server responded with 200...not 201 and location...')
        result = urlfetch.fetch(url + '/compute/', headers=headers)
        loc = result.headers['x-occi-location'].split(',')[0].strip()
    else:
        messages.append('Creation of "compute" kind instance failed: response was "' + repr(result) + '"')

    # trigger action...
    result = urlfetch.fetch(loc, headers=headers, deadline=60)
    links = result.headers['link'].split(',')
    for link in links:
        if link.find('?action=start>') != -1:
            action_url = url + link[1:link.find('>')]
            action_heads = headers.copy()
            action_heads['Category'] = 'start; scheme="http://schemas.ogf.org/occi/infrastructure/compute/action#"'
            result = urlfetch.fetch(action_url, method=urlfetch.POST, headers=action_heads, deadline=60)
            if not result.status_code == 200:
                messages.append('Triggering of action failed: response was "' + repr(result) + '"')
        else:
            logging.warn('Start action not applicable - might be correct...')

    # POST - partial update
    post_heads = headers.copy()
    post_heads['X-OCCI-Attribute'] = 'occi.compute.hostname="foo"'
    result = urlfetch.fetch(loc, method=urlfetch.POST, headers=post_heads, deadline=60)
    if not result.status_code == 200:
        messages.append('Update on resource <' + loc + '> failed: response was "' + repr(result) + '"')

    # PUT create
    put_url = url + '/123'
    put_heads = headers.copy()
    put_heads['Category'] = 'compute;scheme="http://schemas.ogf.org/occi/infrastructure#"'
    put_heads['X-OCCI-Attribute'] = 'example.test="foo"'
    result = urlfetch.fetch(put_url, method=urlfetch.PUT, headers=put_heads, deadline=60)
    # RN: A server is allowed to refuse the request. #3.4.4 footnote 6.
    if result.status_code == 400:
        logging.warn('Server refused PUT create at <' + put_url + '>, this is OK according to section 3.4.4')
        put_url = loc
    elif not result.status_code in [200, 201]:
        messages.append('Adding named "compute" kind instance at <' + put_url + '> failed: response was "' + repr(result) + '"')

    # PUT for full update
    put_heads = headers.copy()
    put_heads['Category'] = 'compute;scheme="http://schemas.ogf.org/occi/infrastructure#"'
    put_heads['X-OCCI-Attribute'] = 'occi.core.title="My Compute instance"'
    result = urlfetch.fetch(put_url, method=urlfetch.PUT, headers=put_heads, deadline=60)
    if not result.status_code == 200:
        messages.append('Full update on "compute" kind instance at <' + put_url + '> failed: response was "' + repr(result) + '"')

    # GET
    result = urlfetch.fetch(loc, headers=headers, deadline=60)
    if not result.status_code == 200:
        messages.append('Resource retrieval at <' + loc + '> failed: response was "' + repr(result))

    # DELETE
    result = urlfetch.fetch(loc, method=urlfetch.DELETE, headers=headers, deadline=60)
    if not result.status_code == 200:
        messages.append('Resource deletion of <' + loc + '> failed: response was "' + repr(result))
    if loc != put_url:
        result = urlfetch.fetch(put_url, method=urlfetch.DELETE, headers=headers, deadline=60)
        if not result.status_code == 200:
            messages.append('Resource deletion of <' + loc + '> failed: response was "' + repr(result))

    if messages:
        raise ComplianceError(messages)


def ctf_345(url):
    """
Tests the handling of link instances as described in section 3.4.5 of the Open
Cloud Computing Interface - RESTful HTTP Rendering specification.
    """
    messages = []
    headers = {
        'Content-Type': 'text/occi',
        'Cache-control': 'max-age=0',
    }

    # create compute
    compute_heads = headers.copy()
    compute_heads['Category'] = 'compute;scheme="http://schemas.ogf.org/occi/infrastructure#"'
    result = urlfetch.fetch(url, method=urlfetch.POST, headers=compute_heads, deadline=60)
    if 'location' not in result.headers and result.status_code not in (201, 200):
        logging.warn('Creation failed - this might be okay - please examine output! ' + repr(result) + '"')
        logging.warn('Test needs to be updated to discover location by doing a GET on /compute/')
        return 'UNDEFINED'
    compute_loc = result.headers['location']

    # create network
    network = headers.copy()
    network['Category'] = 'network;scheme="http://schemas.ogf.org/occi/infrastructure#"'
    result = urlfetch.fetch(url, method=urlfetch.POST, headers=network, deadline=60)
    if result.status_code not in [200, 201]:
        logging.warn('Creation failed - this might be okay - please examine output! ' + repr(result) + '"')
    network_loc = result.headers['location']

    # now create a network link...
    link = headers.copy()
    link['Category'] = 'networkinterface;scheme="http://schemas.ogf.org/occi/infrastructure#"'
    link['X-OCCI-Attribute'] = 'occi.core.source="' + compute_loc + '", occi.core.target="' + network_loc + '"'
    result = urlfetch.fetch(url, method=urlfetch.POST, headers=link, deadline=60)
    if result.status_code not in [200, 201]:
        messages.append('Creation of a "networkinterface" link instance failed: response was "' + repr(result) + '"')
    link_loc = result.headers['location']

    # check if links has source, target attributes
    get_heads = headers.copy()
    get_heads['Accept'] = 'text/occi'
    result = urlfetch.fetch(link_loc, headers=get_heads, deadline=60)
    if result.headers.has_key('x-occi-attribute'):
        if result.headers['x-occi-attribute'].find('occi.core.source') == -1 or result.headers['x-occi-attribute'].find('occi.core.target') == -1:
            messages.append('Missing "source" and/or "target" attribute on link: response was "' + repr(result) + '"')
    else:
        messages.append('Link retrieval seems to be broken: response was "' + repr(result) + '"')

    # 1st cleanup...
    result = urlfetch.fetch(compute_loc, method=urlfetch.DELETE, headers=headers, deadline=60)
    if not result.status_code == 200:
        messages.append('Resource deletion of <' + compute_loc + '> failed: response was "' + repr(result))

    # now create compute again but with inline...
    compute_heads = headers.copy()
    compute_heads['Category'] = 'compute;scheme="http://schemas.ogf.org/occi/infrastructure#"'
    compute_heads['Link'] = '<' + network_loc + '>; rel="http://schemas.ogf.org/occi/infrastructure#network"; category="http://schemas.ogf.org/occi/infrastructure#networkinterface";'

    result = urlfetch.fetch(url, method=urlfetch.POST, headers=compute_heads, deadline=60)
    if result.status_code not in [200, 201]:
        logging.warn('Creation failed - this might be okay - please examine output! ' + repr(result) + '"')
    compute_loc = result.headers['location']

    # Now check if compute has inline link rendering...
    get_heads = headers.copy()
    get_heads['Accept'] = 'text/occi'
    result = urlfetch.fetch(compute_loc, headers=get_heads, deadline=60)
    if not result.headers.has_key('link'):
        messages.append('Inline link rendering for "compute" resource seems to be missing: response was "' + repr(result) + '"')

    # 2nd cleanup...
    result = urlfetch.fetch(compute_loc, method=urlfetch.DELETE, headers=headers, deadline=60)
    if not result.status_code == 200:
        messages.append('Resource deletion of <' + compute_loc + '> failed: response was "' + repr(result))
    # no need to delete link since that should be in the lifecycle of the compute resource...
    result = urlfetch.fetch(network_loc, method=urlfetch.DELETE, headers=headers, deadline=60)
    if not result.status_code == 200:
        messages.append('Resource deletion of <' + network_loc + '> failed: response was "' + repr(result))

    if messages:
        raise ComplianceError(messages)


def ctf_35(url):
    """
Tests the syntax and semantics of the rendering as described in section 3.5 of
the Open Cloud Computing Interface - RESTful HTTP Rendering specification.
    """
    messages = []

    # TODO: add checks for syntax of links, locations, attributes...

    regex = r'\w+; \bscheme=[a-z:./#"]*; \bclass="(?:action|kind|mixin)"'

    heads = {
        'Accept': 'text/plain',
        'Cache-control': 'max-age=0',
    }
    discovery_url = url + '/-/'
    
    result = urlfetch.fetch(discovery_url, headers=heads, deadline=60)
    cat_rend = result.content.split('\n')[1].strip()

    cat_rend = cat_rend[10:]
    p = re.compile(regex)

    m = p.match(cat_rend)
    if m is None:
        messages.append('Syntax error in "text/plain" rendering (should adhere to <term>;scheme="<url>";class=[kind,action,mixin]): response was "' + repr(result) + '"')

    heads['Accept'] = 'text/occi'
    logging.debug(heads)
    result = urlfetch.fetch(discovery_url, headers=heads, deadline=60)
    cat_rend = result.headers['category'].strip()
    p = re.compile(regex)
    m = p.match(cat_rend)
    if m is None:
        messages.append('Syntax error in "text/occi" rendering (should adhere to <term>;scheme="<url>";class=[kind,action,mixin]): response was "' + repr(result) + '"')

    # Test escaping of quotes
    post_heads = {
        'Content-Type': 'text/occi',
        'Category': 'compute;scheme="http://schemas.ogf.org/occi/infrastructure#"',
        'X-OCCI-Attribute': 'occi.compute.memory=3.6, occi.core.title="How\'s your quotes escaping? \\", occi.compute.memory=1.0"'
    }
    result = urlfetch.fetch(url, method=urlfetch.POST, headers=post_heads, deadline=60)
    if not result.headers.get('location') or result.status_code not in (200, 201):
        messages.append('Creation of "compute" resource with "X-OCCI-Attribute: {attr}" failed: response was "{resp}"' %
                {'attr': post_heads['X-OCCI-Attribute'], 'resp': repr(result)})
        raise ComplianceError(messages)
    compute_loc = result.headers.get('location')

    result = urlfetch.fetch(compute_loc, headers={'Accept': 'text/plain', 'Cache-control': 'max-age=0',}, deadline=60)
    if not result.status_code == 200:
        messages.append('Resource retrieval of <' + compute_loc + '> failed: response was "' + repr(result) + '"')
    # If memory=1.0 quote parsing failed, should be 3.6
    found = False

    for line in result.content.split('\n'):
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
        messages.append('Quotation escaping is not parsed correctly: response was "' + repr(result) + '"')

    if messages:
        raise ComplianceError(messages)


def ctf_365(url):
    """
Tests the versioning as described in section 3.6.5 of the Open Cloud Computing
Interface - RESTful HTTP Rendering specification.
    """
    messages = []
    

    headers = {
        'Accept': 'text/occi',
        'Cache-control': 'max-age=0',
       }

    result = urlfetch.fetch(url + '/', headers=headers, deadline=60)
    if result.headers.get('server').find('OCCI/1.1') == -1:
        messages.append('Server does not correctly expose version OCCI/1.1: response was "' + result.headers.get('server') + '"')

    if messages:
        raise ComplianceError(messages)


def ctf_366(url):
    """
Tests the correct handling of "Content-type" and "Accept" headers as described
in section 3.6.6 of the Open Cloud Computing Interface - RESTful HTTP Rendering
specification.
    """
    msg_list = []
    heads = {'Accept': 'text/plain', 'Cache-control': 'max-age=0'}
    url += '/-/'
    

    result = urlfetch.fetch(url, headers=heads, deadline=60)
    content_type = result.headers.get('content-type')
    if content_type: content_type = content_type.split(';')[0].strip()
    if not content_type == 'text/plain':
        msg_list.append('On "Accept: text/plain", "Content-type: text/plain" was not exposed by the server: response was "' + repr(result) + '"')

    heads = {'Accept': 'text/occi'}
    result = urlfetch.fetch(url, headers=heads, deadline=60)
    content_type = result.headers.get('content-type')
    if content_type: content_type = content_type.split(';')[0].strip()
    if not content_type == 'text/occi':
        msg_list.append('On "Accept: text/occi", "Content-type: text/occi" was not exposed by the server: response was "' + repr(result) + '"')

    if msg_list:
        raise ComplianceError(msg_list)
    return 'OK'


def ctf_367(url):
    """
Tests RFC5785 compliance as described in section 3.6.7 of the Open Cloud
Computing Interface - RESTful HTTP Rendering specification.
    """
    messages = []
    headers = {
        'Accept': 'text/occi',
        'Cache-control': 'max-age=0',
    }

    # retrieval of all kinds, actions and mixins
    
    result_first = urlfetch.fetch(url + '/.well-known/org/ogf/occi/-/', headers=headers, deadline=60)
    if not result_first.status_code in [200]:
        messages.append(
            'GET on query interface failed ('
            + str(result_first.status_code) + '): ' + result_first.content
        )

    # retrieval of all kinds, actions and mixins
    result_second = urlfetch.fetch(url + '/-/', headers=headers, deadline=60)
    if not result_second.status_code in [200]:
        messages.append(
            'GET on query interface failed ('
            + str(result_second.status_code) + '): ' + result_second.content
        )


    if result_first.headers['category'] != result_second.headers['category']:
        messages.append('Differing GET results for <' + url + '/-/> and <' + url + '/.well-known/org/ogf/occi/-/>')

    if messages:
        raise ComplianceError(messages)
    return 'OK'


def _test_model_completeness(rendering, rel, attributes, actions):
    """
Tests whether a given instace is complete wrt. to the category it
represents.
    """
    for item in rendering:
        item = item.strip().split('=')
        if item[0] == 'rel':
            if item[1].find(rel) == -1:
                raise ComplianceError('Corresponding "rel" is missing: should be "' + rel + '", but found "' + item[1] + '"')
        elif item[0] == 'attributes':
            for attr in attributes:
                if item[1].find(attr) == -1:
                    raise ComplianceError('Mandatory attribute "' + attr + '" was missing on ' + rendering[0].strip() + '. Instead, "' + item[1] + '" was found')
        elif item[0] == 'actions':
            for action in actions:
                if item[1].find(action) == -1:
                    raise ComplianceError('Mandatory action "' + action + '" was missing on ' + rendering[0].strip() + '. Instead, ' + item[1] + '" was found')


def ctf_gfd184(url):
    """
Tests whether the IaaS model is complete with respoect to the Open Cloud
Computing Interface - Infrastructure specification.
    """
    messages = []

    headers = {
        'Accept': 'text/plain',
        'Cache-control': 'max-age=0',
    }
    url += '/-/'
    
    result = urlfetch.fetch(url, headers=headers, deadline=60)

    infra_model = []
    for line in result.content.split('\n'):
        cur = line.lstrip('Category:').split(';')
        # check if compute has all attributes & actions & rels
        #----------------------------------------------------------------- Kinds
        if cur[0].strip() == 'compute' and cur[1].strip() == 'scheme="http://schemas.ogf.org/occi/infrastructure#"':
            rel = 'http://schemas.ogf.org/occi/core#resource'
            attr = ['occi.compute.architecture', 'occi.compute.cores', 'occi.compute.hostname', 'occi.compute.speed', 'occi.compute.memory', 'occi.compute.state']
            actions = ['start', 'stop', 'suspend', 'restart']
            _test_model_completeness(cur, rel, attr, actions)
            infra_model.append('compute')
        elif cur[0].strip() == 'network' and cur[1].strip() == 'scheme="http://schemas.ogf.org/occi/infrastructure#"':
            rel = 'http://schemas.ogf.org/occi/core#resource'
            attr = ['occi.network.vlan', 'occi.network.label', 'occi.network.state']
            actions = ['up', 'down']
            _test_model_completeness(cur, rel, attr, actions)
            infra_model.append('network')
        elif cur[0].strip() == 'storage' and cur[1].strip() == 'scheme="http://schemas.ogf.org/occi/infrastructure#"':
            rel = 'http://schemas.ogf.org/occi/core#resource'
            attr = ['occi.storage.size', 'occi.storage.state']
            actions = ['online', 'offline', 'backup', 'snapshot', 'resize']
            _test_model_completeness(cur, rel, attr, actions)
            infra_model.append('storage')
        #----------------------------------------------------------------- Links
        elif cur[0].strip() == 'storagelink' and cur[1].strip() == 'scheme="http://schemas.ogf.org/occi/infrastructure#"':
            rel = 'http://schemas.ogf.org/occi/core#link'
            attr = ['occi.storagelink.deviceid', 'occi.storagelink.mountpoint', 'occi.storagelink.state']
            actions = []
            _test_model_completeness(cur, rel, attr, actions)
            infra_model.append('storagelink')
        elif cur[0].strip() == 'networkinterface' and cur[1].strip() == 'scheme="http://schemas.ogf.org/occi/infrastructure#"':
            rel = 'http://schemas.ogf.org/occi/core#link'
            attr = ['occi.networkinterface.state', 'occi.networkinterface.mac', 'occi.networkinterface.interface']
            actions = []
            _test_model_completeness(cur, rel, attr, actions)
            infra_model.append('networkinterface')
        #---------------------------------------------------------------- mixins
        elif cur[0].strip() == 'ipnetwork' and cur[1].strip() == 'scheme="http://schemas.ogf.org/occi/infrastructure/network#"':
            rel = 'http://schemas.ogf.org/occi/core#link'
            attr = ['occi.network.address', 'occi.network.gateway', 'occi.network.allocation']
            actions = []
            _test_model_completeness(cur, rel, attr, actions)
            infra_model.append('ipnetwork')
        #--------------------------------------------------------------- actions
        elif cur[0].strip() == 'start' and cur[1].strip() == 'scheme="http://schemas.ogf.org/occi/infrastructure/compute/action#"':
            rel = ''
            attr = []
            actions = []
            _test_model_completeness(cur, rel, attr, actions)
            infra_model.append('start')
        elif cur[0].strip() == 'stop' and cur[1].strip() == 'scheme="http://schemas.ogf.org/occi/infrastructure/compute/action#"':
            rel = ''
            #attr = ['graceful', 'acpioff', 'poweroff']
            attr = ['method']
            actions = []
            _test_model_completeness(cur, rel, attr, actions)
            infra_model.append('stop')
        elif cur[0].strip() == 'restart' and cur[1].strip() == 'scheme="http://schemas.ogf.org/occi/infrastructure/compute/action#"':
            rel = ''
            #attr = ['graceful', 'warm', 'cold']
            attr = ['method']
            actions = []
            _test_model_completeness(cur, rel, attr, actions)
            infra_model.append('restart')
        elif cur[0].strip() == 'suspend' and cur[1].strip() == 'scheme="http://schemas.ogf.org/occi/infrastructure/compute/action#"':
            rel = ''
            #attr = ['hibernate', 'suspend']
            attr = ['method']
            actions = []
            _test_model_completeness(cur, rel, attr, actions)
            infra_model.append('suspend')
        elif cur[0].strip() == 'up' and cur[1].strip() == 'scheme="http://schemas.ogf.org/occi/infrastructure/network/action#"':
            rel = ''
            attr = []
            actions = []
            _test_model_completeness(cur, rel, attr, actions)
            infra_model.append('up')
        elif cur[0].strip() == 'down' and cur[1].strip() == 'scheme="http://schemas.ogf.org/occi/infrastructure/network/action#"':
            rel = ''
            attr = []
            actions = []
            _test_model_completeness(cur, rel, attr, actions)
            infra_model.append('down')
        elif cur[0].strip() == 'online' and cur[1].strip() == 'scheme="http://schemas.ogf.org/occi/infrastructure/storage/action#"':
            rel = ''
            attr = []
            actions = []
            _test_model_completeness(cur, rel, attr, actions)
            infra_model.append('online')
        elif cur[0].strip() == 'offline' and cur[1].strip() == 'scheme="http://schemas.ogf.org/occi/infrastructure/storage/action#"':
            rel = ''
            attr = []
            actions = []
            _test_model_completeness(cur, rel, attr, actions)
            infra_model.append('offline')
        elif cur[0].strip() == 'resize' and cur[1].strip() == 'scheme="http://schemas.ogf.org/occi/infrastructure/storage/action#"':
            rel = ''
            attr = ['size']
            actions = []
            _test_model_completeness(cur, rel, attr, actions)
            infra_model.append('resize')
        elif cur[0].strip() == 'backup' and cur[1].strip() == 'scheme="http://schemas.ogf.org/occi/infrastructure/storage/action#"':
            rel = ''
            attr = []
            actions = []
            _test_model_completeness(cur, rel, attr, actions)
            infra_model.append('backup')
        elif cur[0].strip() == 'snapshot' and cur[1].strip() == 'scheme="http://schemas.ogf.org/occi/infrastructure/storage/action#"':
            rel = ''
            attr = []
            actions = []
            _test_model_completeness(cur, rel, attr, actions)
            infra_model.append('snapshot')

    if not 'compute' in infra_model:
        messages.append('Infrastructure model is missing "compute" kind.')
    if not 'network' in infra_model:
        messages.append('Infrastructure model is missing "network" kind.')
    if not 'storage' in infra_model:
        messages.append('Infrastructure model is missing "storage" kind.')
    if not 'storagelink' in infra_model:
        messages.append('Infrastructure model is missing "storagelink" link.')
    if not 'networkinterface' in infra_model:
        messages.append('Infrastructure model is missing "networkinterface" link.')
    if not 'ipnetwork' in infra_model:
        messages.append('Infrastructure model is missing "ipnetwork" mixin.')
    if not 'start' in infra_model:
        messages.append('Infrastructure model is missing "start" action definition.')
    if not 'stop' in infra_model:
        messages.append('Infrastructure model is missing "stop" action definition.')
    if not 'restart' in infra_model:
        messages.append('Infrastructure model is missing "restart" action definition.')
    if not 'suspend' in infra_model:
        messages.append('Infrastructure model is missing "suspend" action definition.')
    if not 'up' in infra_model:
        messages.append('Infrastructure model is missing "up" action definition.')
    if not 'down' in infra_model:
        messages.append('Infrastructure model is missing "down" action definition.')
    if not 'snapshot' in infra_model:
        messages.append('Infrastructure model is missing "snapshot" action definition.')
    if not 'resize' in infra_model:
        messages.append('Infrastructure model is missing "resize" action definition.')
    if not 'online' in infra_model:
        messages.append('Infrastructure model is missing "online" action definition.')
    if not 'offline' in infra_model:
        messages.append('Infrastructure model is missing "offline" action definition.')
    if not 'backup' in infra_model:
        messages.append('Infrastructure model is missing "backup" action definition.')

    if messages:
        raise ComplianceError(messages)


 # eof