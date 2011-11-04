#!/usr/bin/python
# -*- coding: utf-8 -*-
# $Id$

# This file is part of doyouspeakOCCI.
#
# doyouspeakOCCI is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# doyouspeakOCCI is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with doyouspeakOCCI.  If not, see <http://www.gnu.org/licenses/>.

import os

from dyso import tests
from dyso.model import Suite, Test
from dyso.tests import ComplianceError

from google.appengine.ext import webapp
from google.appengine.ext.webapp import template


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

        compliance_tests = []
        is_compliant = True

        # run the test suite
        for elem in dir(tests):
            if elem.find('ctf_') != -1:
                func = getattr(tests, elem)
                desc = func.__doc__.strip()

                # run the individual test
                test = Test(suite)
                test.name = func.__name__
                test.description = desc
                try:
                    func(suite.service_uri)
                    test.result = True
                except ComplianceError, e:
                    test.details = e.__str__()
                    is_compliant = False
                compliance_tests.append(test)

                # store test to database and add to result set
                test.put()

        # update overall result and store suite to database
        suite.is_compliant = is_compliant
        suite.put()

        # produce template value set
        template_values = {
            'suite': suite,
            'tests': compliance_tests
        }

        # render result page
        path = os.path.join(os.path.dirname(__file__), '../templates/result.html')
        self.response.out.write(template.render(path, template_values))


# eof