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

import os

from dyso import test_httplib2
from dyso.model import Suite, Test

from test_httplib2 import TestFailure

from google.appengine.ext import webapp
from google.appengine.ext.webapp import template


# ----- ResultPage -------------------------------------------------------------
class ResultPage(webapp.RequestHandler):
    """
    TODO: not yet commented.
    """

    def post(self):
        """
        TODO: not yet commented.
        """
        suite = Suite()
        suite.service_uri = self.request.get('service_uri')


        #        tests = { }
        tests = []
        is_compliant = True

        # run the test suite
        for elem in dir(test_httplib2):
            if elem.find('test_') != -1:
                func = getattr(test_httplib2, elem)
                desc = func.__doc__.strip()

                # run the individual test
                test = Test(func.__name__, desc)
                try:
                    func(suite.service_uri)
                    test.result = True
                except TestFailure, e:
                    test.details = e
                    is_compliant = False
                    #                tests[elem] = test
                tests.append(test)

                # store test to database and add to result set
                test.put()

        # update overall result and store suite to database
        suite.is_compliant = is_compliant
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
    """
    TODO: not yet commented.
    """

    def get(self):
        """
        TODO: not yet commented.
        """

        # retrieve overall test results from datastore
        overall = {
            'compliant_implementations': Suite.all().filter('is_compliant = ', True).count(),
            'noncompliant_implementations': Suite.all().filter('is_compliant = ', False).count()
        }

        # retrieve detailed test results from datastore
        breakdown = []
        for elem in dir(test_httplib2):
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


# eof