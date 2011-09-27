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


def test_query_interface(url):
    '''
    Testing the Query Interface as described in section 3.4.1...
    '''
    msg = ''

    # retrieval of all kinds, actions and mixins
    http = httplib2.Http()
    response, content = http.request(url + '/.well-known/org/ogf/occi/-/', 'GET')
    if not response.status in [200]:
        msg += 'Get on Query Interface failed - ' + str(response.status) + ' ' + response.reason + ' ' + content

    # adding a mixin definition
    http = httplib2.Http()

    heads = {
        'Content-type': 'text/occi',
        'Accept': 'text/occi',
        'Category': 'my_stuff; scheme="http://example.com/occi/my_stuff#"; class="mixin"; rel="http://example.com/occi/something_else#mixin"; location="/my_stuff/"'
    }

    response, content = http.request(url + '/.well-known/org/ogf/occi/-/', 'POST', headers=heads)
    if not response.status in [200]:
        msg += 'Failed to add a mixin - ' + str(response.status) + ' ' + response.reason + ' ' + content

    # removing a mixin definition
    http = httplib2.Http()

    heads = {
        'Content-type': 'text/occi',
        'Accept': 'text/occi',
        'Category': 'my_stuff; scheme="http://example.com/occi/my_stuff#"; class="mixin";'
    }

    response, content = http.request(url + '/.well-known/org/ogf/occi/-/', 'DELETE', headers=heads)
    if not response.status in [200]:
        msg += 'Failed to remove a  mixin - ' + str(response.status) + ' ' + response.reason + ' ' + content

    if msg is not '':
        raise AttributeError('One of the test failed! - Server response: ', msg)
    return 'OK'


def test_operations_on_paths(url):
    '''
    Test operations on paths in the namespace as described in section 3.4.2...
    '''
    msg = ''

    # retrieving the state of the ns hierarchy
    # TODO

    # retrieving all instances below a path
    # TODO

    # Deletion of all isntances below a path...
    # TODO

    if msg is not '':
        raise AttributeError('One of the test failed! - Server response: ', msg)
    return 'OK'


def test_operations_on_mixins_or_kinds(url):
    '''
    Test operations on mixins or kinds as described in section 3.4.3...
    '''
    msg = ''

    # TODO

    if msg is not '':
        raise AttributeError('One of the test failed! - ', msg)
    return 'OK'


def test_operations_on_resource_instances(url):
    '''
    Test operations on resource instances as described in section 3.4.4...
    '''
    msg = ''

    # TODO

    if msg is not '':
        raise AttributeError('One of the test failed! - ', msg)
    return 'OK'


def test_handling_link_instances(url):
    '''
    Test handling of link instances as described in section 3.4.5...
    '''
    msg = ''

    # TODO

    if msg is not '':
        raise AttributeError('One of the test failed! - ', msg)
    return 'OK'


def test_syntax(url):
    '''
    TODO test syntax
    '''
    # TODO
    msg = ''

    if msg is not '':
        raise AttributeError(msg)
    return 'OK'


def test_versioning(url):
    '''
    Test that the correct version number can be found as described in section 3.6.5
    '''
    msg = ''
    http = httplib2.Http()

    heads = {
        'Accept': 'text/occi',
       }

    response, content = http.request(url + '/', 'GET')
    if response.get('server').find('OCCI/1.1') == -1:
        msg += 'Server does not correctly expose version OCCI/1.1. Server responded: ' + response.get('server')

    if msg is not '':
        raise AttributeError(msg)
    return 'OK'


def test_content_type_and_accept_headers(url):
    '''
    TODO test headers
    '''
    # TODO
    msg = ''

    if msg is not '':
        raise AttributeError(msg)
    return 'OK'


def test_rfc5785_compliance(url):
    '''
    TODO test qi on both paths...
    '''
    # TODO
    msg = ''

    if msg is not '':
        raise AttributeError(msg)
    return 'OK'


def test_occi_infrastructure(url):
    '''
    Test if the OCCI infrastructure is complete as defined in the spec...
    '''
    # TODO
    msg = ''

    if msg is not '':
        raise AttributeError(msg)
    return 'OK'


if __name__ == '__main__':

    URL = 'http://localhost:8888'
