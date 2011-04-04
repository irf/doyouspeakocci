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

from tests import test_occi
import getopt
import logging
import sys


'''
Created on Apr 4, 2011

@author: tmetsch
'''

class TextRunner(object):

    def __init__(self, url, username = None, password = None):
        if username is not None and password is not None:
            heads = cookie = test_occi.get_session_cookie(url, username, password)
            heads = {'Cookie': cookie}
        else:
            heads = {}

        print('Examining OCCI service at URL: ' + url)
        print('\n')
        print('NOTE: Passing all tests only indicates that the service')
        print('you are testing is OCCI compliant - IT DOES NOT GUARANTE IT!')
        print('\n')
        print('Version string the service reported: ' + test_occi.get_version(url, heads))
        print('Number of registered categories: ' + str(len(test_occi.get_categories(url, heads))))
        print('\n')

        self.run_tests(url, heads)

    def run_tests(self, url, heads):
        '''
        Run all the tests.
        '''
        self.run_single_test(test_occi.test_version_information, url, heads, 'Verifing version information of the service')
        self.run_single_test(test_occi.test_infrastructure_model_for_completness, url, heads, 'Verifing infrastructure model for completeness')
        self.run_single_test(test_occi.test_accept_header, url, heads, 'Verifing correct handling of Accept headers')
        self.run_single_test(test_occi.test_create_kinds, url, heads, 'Verifing creation of kinds in infra model')
        self.run_single_test(test_occi.test_mixins, url, heads, 'Testing behaviour of used defined mixins')
        self.run_single_test(test_occi.test_links, url, heads, 'Testing behaviour links between resources')
        self.run_single_test(test_occi.test_actions, url, heads, 'Verifing that actions can be triggered  ')
        self.run_single_test(test_occi.test_filter, url, heads, 'Testing filtering mechanisms on paths   ')
        self.run_single_test(test_occi.test_location, url, heads, 'Verifing the behaviour on location paths')
        self.run_single_test(test_occi.test_syntax, url, heads, 'Simple syntax checks for several renderings')

    def run_single_test(self, test, url, heads, label):
        '''
        run a single test.
        '''
        try:
            test(url, heads)
        except Exception as e:
            logging.warning(str(e))
            print(label + '\t\t\tFailed')
        else:
            print(label + '\t\t\tOK')

if __name__ == '__main__':
    try:
        opts, args = getopt.getopt(sys.argv[1:], "ho:v", ["help", "url=", "username=", "password=", "gui"])
    except getopt.GetoptError as err:
        print(str(err))
        sys.exit(2)
    username = None
    password = None
    use_gui = False
    url = 'http://localhost:8888'
    for o, a in opts:
        if o in ("-h", "--help"):
            print ('Usage: test_occi.py url=<URL> [<--username=foo>, <--password=bar>] or test_occi.py --gui')
            sys.exit()
        elif o in ("-u", "--url"):
            url = a
        elif o in ("--username"):
            username = a
        elif o in ("--password"):
            password = a
        elif o in ("--gui"):
            use_gui = True
        else:
            assert False, "unhandled option"

    TextRunner(url, username, password)
