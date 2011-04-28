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

import httplib
import urllib

VERSION_STRING = 'OCCI/1.1'
USER_AGENT_STRING = 'occi-client/1.1 (python) httplib' + VERSION_STRING

def do_post(url, content_type = 'text/plain', accept = 'text/plain', categories = [], attributes = [], links = [], locations = []):
    """
    Do a HTTP POST operation on an given URL
    
    Handles request and response based on content_type and accept which are both 'text/plain' by default.
    
    Returns a set of categories, attributes, links and locations or the appropiate HTTP error.
    
    Keyword arguments:
    url -- The url
    content_type -- The content_type determining how the data is rendered in the request (default text/plain)
    accept -- The accept header determining how the data should be returned by the service (default text/plain)
    categories -- A list of categories (default empty)
    attributes -- A list of attribtues (default empty)
    links -- A list of links (default empty)
    locations -- A list of locations (default empty)
    """
    return [], [], [], []

def do_get(host, url, content_type = 'text/plain', accept = 'text/plain', categories = [], attributes = []):
    """
    Do a HTTP GET operation on an given URL
    
    Handles request and response based on content_type and accept which are both 'text/plain' by default.
    
    Returns a set of return code, categories, attributes, links and locations or the appropiate HTTP error.
    
    Keyword arguments:
    url -- The url
    content_type -- The content_type determining how the data is rendered in the request (default text/plain)
    accept -- The accept header determining how the data should be returned by the service (default text/plain)
    categories -- A list of categories (default empty)
    attributes -- A list of attribtues (default empty)
    """
    conn = httplib.HTTPConnection(host)

    body = None
    headers = {
        'Content-Type': content_type,
        'Accept': accept,
        'User-Agent': USER_AGENT_STRING
        }

    # TODO: pack given information into appropiate rendering...

    # create connection retrieve body & headers
    if body is None:
        conn.request('GET', url, body=body, headers=headers)
    else:
        conn.request('GET', url, body=urllib.encode(body), headers=headers)
        
    response = conn.getresponse()
    response_code = response.status
    response_body = response.read()
    response_headers = response.getheaders()
    conn.close()

    # Verifies that the OCCI version # is in the response.
    for item in response_headers:
        if item[0] == 'server':
            if item[1].find(VERSION_STRING) == -1:
                raise AttributeError('Service did not expose the correct OCCI version number')

    # Verifies that the service responded with the corrent content-type
    reponse_content_type = response.getheader('Content-Type')
    if reponse_content_type != accept:
        raise AttributeError('Client requested that service reponses with Content-Type :', accept, ' Instead got: ', reponse_content_type)

    # TODO: unpack information from rendering...
    
    return response_code, [], [], [], []

def do_put(url, content_type = 'text/plain', accept = 'text/plain', categories = [], attributes = [], links = [], locations = []):
    """
    Do a HTTP PUT operation on an given URL
    
    Handles request and response based on content_type and accept which are both 'text/plain' by default.
    
    Returns a set of categories, attributes, links and locations or the appropiate HTTP error.
    
    Keyword arguments:
    url -- The url
    content_type -- The content_type determining how the data is rendered in the request (default text/plain)
    accept -- The accept header determining how the data should be returned by the service (default text/plain)
    categories -- A list of categories (default empty)
    attributes -- A list of attribtues (default empty)
    links -- A list of links (default empty)
    locations -- A list of locations (default empty)
    """
    return [], [], [], []

def do_delete(url, content_type = 'text/plain', accept = 'text/plain', locations = []):
    """
    Do a HTTP GET operation on an given URL
    
    Handles request and response based on content_type and accept which are both 'text/plain' by default.
    
    Returns a set of categories, attributes, links and locations or the appropiate HTTP error.
    
    Keyword arguments:
    url -- The url
    content_type -- The content_type determining how the data is rendered in the request (default text/plain)
    accept -- The accept header determining how the data should be returned by the service (default text/plain)
    locations -- A list of locations (default empty)
    """
    return [], [], [], []
