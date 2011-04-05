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

def do_get(url, content_type = 'text/plain', accept = 'text/plain', categories = [], attributes = []):
    """
    Do a HTTP GET operation on an given URL
    
    Handles request and response based on content_type and accept which are both 'text/plain' by default.
    
    Returns a set of categories, attributes, links and locations or the appropiate HTTP error.
    
    Keyword arguments:
    url -- The url
    content_type -- The content_type determining how the data is rendered in the request (default text/plain)
    accept -- The accept header determining how the data should be returned by the service (default text/plain)
    categories -- A list of categories (default empty)
    attributes -- A list of attribtues (default empty)
    """
    return [], [], [], []

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
