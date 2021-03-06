#!/usr/bin/python
# -*- coding: utf-8 -*-
# $Id$

# Copyright (c) 2011, 2012 Technische Universität Dortmund
#
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

import tests
import model

import base64
import os
import uuid
from django.utils import simplejson
from google.appengine.api import users
from google.appengine.api.channel import channel
from google.appengine.ext import webapp
from google.appengine.ext.webapp import template


class IndexPage(webapp.RequestHandler):
    """
    TODO: not yet commented.
    """
    def get(self):
        """
        TODO: not yet commented.
        """
        template_values = get_base_template(self.request.path)

        # generate and retain client id for inbound AJAX channel
        template_values['client'] = uuid.uuid4().__str__()

        # create channel and retain security token
        template_values['token'] = channel.create_channel(template_values['client'])

        ctfs = {}
        # extract ctf name and descriptions
        for ctf in tests.ctfs:
            ctfs[ctf.__name__] = ctf.__doc__.strip()
        template_values['tests'] = ctfs

        # load and render result page
        path = os.path.join(os.path.dirname(__file__), '../templates/index.html')
        self.response.out.write(template.render(path, template_values))

    def post(self):
        """
        TODO: not yet commented.
        """
        suite = model.Suite(key_name=uuid.uuid4().__str__())

        user = users.get_current_user()
        if user:
            suite.user = user

        suite.put()

        # run the test suite
        is_compliant = True
        suite.service_uri = self.request.get('url')

        for ctf in tests.ctfs:
            # initialize a new test object
            test = model.Test(suite=suite)
            test.put()

            test.name = ctf.__name__
            test.description = ctf.__doc__.strip()

            # run the individual test
            auth = self.request.get('auth')
            if auth:
                token = base64.b64encode(self.request.get('user') + ':' + self.request.get('pass'))
                # XXX: add better handling for HTTP Basic Auth
                test.result = ctf(test, suite.service_uri, 'Basic ' + token)
            else:
                test.result = ctf(test, suite.service_uri)

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
        self.response.out.write(simplejson.dumps(suite.to_dict(flatten_date=True)))


class ArchivePage(webapp.RequestHandler):
    """
    TODO: not yet commented.
    """

    def get(self, suite_key):
        """
        TODO: not yet commented.
        """
        template_values = get_base_template(self.request.path)
        user = users.get_current_user()

        # check whether a specific suite was requested (i.e. the path contains a UUID)
        if len(suite_key) > 1: # yes: check whether the requested key exists
            suite = model.Suite.get_by_key_name(suite_key[1:])
            if suite is None: # no: generate and render error page
                self.response.set_status(404)
                path = os.path.join(os.path.dirname(__file__), '../templates/error.html')
                self.response.out.write(template.render(path, template_values))
            else: # yes: produce template value set and render result page
                template_values['suite'] = suite.to_dict()
                template_values['tests'] = [t.to_dict(True) for t in suite.tests.fetch(len(tests.ctfs))]

                path = os.path.join(os.path.dirname(__file__), '../templates/result.html')
                self.response.out.write(template.render(path, template_values))
        else: # no: generate and render overview page
            if user:
                template_values['number_of_records'] = model.Suite.all().filter('user', user).count()
                template_values['succeeded_runs'] = model.Suite.all().filter('user', user).filter('is_compliant', True).count()
                template_values['suites'] = model.Suite.all().filter('user', user).order('-date')
            else:
                template_values['number_of_records'] = 0

            path = os.path.join(os.path.dirname(__file__), '../templates/archive.html')
            self.response.out.write(template.render(path, template_values))


class StatisticsPage(webapp.RequestHandler):
    """
    TODO: not yet commented.
    """

    def get(self):
        """
        TODO: not yet commented.
        """
        template_values = get_base_template(self.request.path)

        # retrieve overall test results from datastore
        template_values['overall'] = {
            'compliant_implementations': model.Suite.all().filter('is_compliant = ', True).count(),
            'noncompliant_implementations': model.Suite.all().filter('is_compliant = ', False).count()
        }

        # retrieve detailed test results from datastore
        breakdown = []
        for ctf in tests.ctfs:
            test = {
                'name': ctf.__name__,
                'number_of_passes': model.Test.all().filter('name = ', ctf.__name__).filter('result = ', True).count(),
                'number_of_fails': model.Test.all().filter('name = ', ctf.__name__).filter('result = ', False).count()
            }
            breakdown.append(test)
        template_values['breakdown'] = breakdown

        # load and render result page
        path = os.path.join(os.path.dirname(__file__), '../templates/statistics.html')
        self.response.out.write(template.render(path, template_values))


class AboutPage(webapp.RequestHandler):
    """

    """

    def get(self):
        """

        """
        template_values = get_base_template(self.request.path)

        # load and render result page
        path = os.path.join(os.path.dirname(__file__), '../templates/about.html')
        self.response.out.write(template.render(path, template_values))


def get_base_template(path):
    """

    """
    result = {}

    user = users.get_current_user()
    if user:
        result['userid'] = user.nickname()
        result['logout_url'] = users.create_logout_url(dest_url=path)
    else:
        result['login_url_google'] = users.create_login_url(dest_url=path, federated_identity='google.com/accounts/o8/id')
        result['login_url_yahoo'] = users.create_login_url(dest_url=path, federated_identity='yahoo.com')

    running_since = model.Suite.all().order('date').get()
    if running_since:
        result['running_since'] = running_since.date
    result['number_of_runs'] = model.Suite.all().count()

    return result


# eof