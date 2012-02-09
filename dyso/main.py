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
import datetime

#from google.appengine.dist import use_library

#use_library('django', '1.2')

import base64
import os
import uuid

import tests
from model import Suite, Test

from django.utils import simplejson

from google.appengine.api.channel import channel
from google.appengine.ext import webapp
from google.appengine.ext.webapp import template


class MainPage(webapp.RequestHandler):
    """
    TODO: not yet commented.
    """
    def get(self):
        """
        TODO: not yet commented.
        """
        client = uuid.uuid4().__str__()
        token = channel.create_channel(client)

        try:
            running_since = Suite.all().order('date').get().date
        except:
            running_since = datetime.date

        number_of_runs = Suite.all().count()

        t = {}
        # run the test suite
        for elem in tests.available_functions:
            t[elem.__name__] = elem.__doc__.strip()

        template_values = {
            'client': client,
            'token': token,
            'number_of_runs': number_of_runs,
            'running_since': running_since,
            'tests': t,
            }

        path = os.path.join(os.path.dirname(__file__), '../templates/index.html')
        #path = 'templates/index.html'
        self.response.out.write(template.render(path, template_values))

    def post(self):
        """
        TODO: not yet commented.
        """
        suite = Suite(key_name=uuid.uuid4().__str__())
        suite.put()

        # run the test suite
        is_compliant = True
        suite.service_uri = self.request.get('url')

        for elem in dir(tests):
            if elem.find('ctf_') != -1:
                func = getattr(tests, elem)

                # initialize a new test object
                test = Test(suite=suite)
                test.put()

                test.name = func.__name__
                test.description = func.__doc__.strip()

                # run the individual test
                auth = self.request.get('auth')
                if auth:
                    token = base64.b64encode(self.request.get('user') + ':' + self.request.get('pass'))
                    test.result = func(test, suite.service_uri, token)
                else:
                    test.result = func(test, suite.service_uri)

                is_compliant &= test.result

                # store test to database and add to result set
                test.put()
                channel.send_message(self.request.get('client'), simplejson.dumps(test.to_dict()))

        suite.is_compliant = is_compliant
        suite.put()
        #channel.send_message(self.request.get('client'), simplejson.dumps(suite.to_dict()))

        self.response.set_status(202)
        self.response.headers['Content-type'] = str('application/json')
        self.response.headers.add_header(str('Location'), str(self.request.url + '/archive/' + suite.key().name()))
        self.response.out.write(simplejson.dumps(suite.to_dict()))


# eof