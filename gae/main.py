#!/usr/bin/python
# -*- coding: utf-8 -*-

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

import logging

import os

from google.appengine.ext import db
from google.appengine.ext import webapp
from google.appengine.ext.webapp import template
from google.appengine.ext.webapp.util import run_wsgi_app

from tests import test_occi_11
from tests.test_occi_11 import TestFailure

# ----- ComplianceTestResult ---------------------------------------------------
class Test(db.Model):
    """
    Stores statistical data on each compliance test run.
    TODO: not yet documented.
    """
    name = None
    description = None
    result = False
    details = None

    def __init__(self, name, description):
        self.name = name
        self.description = description


# ----- Suite ------------------------------------------------------------------
class Suite(db.Model):
    """
    Stores information on each compliance test request.
    
    """
    date = db.DateTimeProperty(auto_now_add=True)
    service_uri = db.LinkProperty()
    is_compliant = db.BooleanProperty()


# ----- MainPage ---------------------------------------------------------------
class MainPage(webapp.RequestHandler):
    '''
    TODO: not yet commented.
    '''
    def get(self):
        running_since = Suite.all().order('date').get()
        number_of_runs = Suite.all().count()

        template_values = {
            'do_you_speak' : 'do you speak',
            'number_of_runs': number_of_runs,
            'running_since': running_since,
        }

        path = os.path.join(os.path.dirname(__file__), 'templates/index.html')
        self.response.out.write(template.render(path, template_values))


# ----- ResultPage -------------------------------------------------------------
class ResultPage(webapp.RequestHandler):
    '''
    TODO: not yet commented.
    '''
    def post(self):
        '''
        TODO: not yet commented.
        '''
        suite = Suite()
        suite.service_uri = self.request.get('service_uri')


        tests = {  }

        # run the test suite
        for elem in dir(test_occi_11):
            if elem.find('test_') != -1:
                func = getattr(test_occi_11, elem)
                desc = func.__doc__.strip()

                # run the individual test
                test = Test(func, desc)
                try:
                    result = func(suite.service_uri)
                    test.result = True
                except TestFailure, e:
                    test.details = e
                    suite.is_compliant = False
                tests[elem] = test

                # store test to database and add to result set
                test.put()

        # store suite to database
        suite.put()

        # produce template value set
        template_values = {
            'suite': suite,
            'tests': tests
        }

        # render result page
        path = os.path.join(os.path.dirname(__file__), 'templates/result.html')
        self.response.out.write(template.render(path, template_values))


# ----- StatisticsPage ---------------------------------------------------------
class StatisticsPage(webapp.RequestHandler):
    '''
    TODO: not yet commented.
    '''
    def get(self):
        '''
        TODO: not yet commented.
        '''

        # retrieve overall test results from datastore
        overall = {
            'compliant_implementations': 0,
            'noncompliant_implementations': 0
        }
        overall['compliant_implementations'] = Suite.all().filter('is_compliant = ', True).count()
        overall['noncompliant_implementations'] = Suite.all().filter('is_compliant = ', False).count()

        # retrieve detailed test results from datastore
        breakdown = []
        for elem in dir(test_occi_11):
            if elem.find('test_') != -1:
                test = {
                    'name': elem,
                    'number_of_passes': Test.all().filter('name = ', elem).filter('result = ', True).count(),
                    'number_of_fails': Test.all().filter('name = ', elem).filter('result = ', False).count()
                }
                breakdown.append(test)

        # produce template value set
        template_values = {
            'overall': overall,
            'breakdown': breakdown
        }

        # render result page
        path = os.path.join(os.path.dirname(__file__), 'templates/statistics.html')
        self.response.out.write(template.render(path, template_values))


# ----- WSGI intialization -----------------------------------------------------
'''
TODO: not yet commented.
'''
application = webapp.WSGIApplication(
                                     [('/', MainPage),
                                      ('/result', ResultPage),
                                      ('/statistics', StatisticsPage)],
                                     debug=True)


# ----- main() -----------------------------------------------------------------
def main():
    '''
    TODO: not yet commented.
    '''
    run_wsgi_app(application)


# ----- default initialization -------------------------------------------------
if __name__ == "__main__":
    main()
