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

from google.appengine.ext import db


class Suite(db.Model):
    """
    Stores information on each compliance test request.
    TODO: not yet documented.
    """
    date = db.DateTimeProperty(auto_now_add=True)
    user = db.UserProperty()
    service_uri = db.LinkProperty()
    is_compliant = db.BooleanProperty()

    def to_dict(self, with_tests=False, flatten_date=False):
        result = {
            'uuid': self.key().name(),
            'date': self.date.isoformat() if flatten_date else self.date,
            'service_uri': self.service_uri,
            'is_compliant': self.is_compliant
        }
        if with_tests:
            tests = []
            for test in self.tests:
                tests.append({'name': test.name, 'description': test.description, 'result': test.result})
            result['tests'] = tests
        return result


class Test(db.Model):
    """
    Stores statistical data on each compliance test run.
    TODO: not yet documented.
    """
    suite = db.ReferenceProperty(Suite, collection_name='tests')

    name = db.StringProperty()
    description = db.TextProperty()
    result = db.BooleanProperty()

    def to_dict(self, with_details=True):
        result = {
            'name': self.name,
            'description': self.description,
            'result': self.result,
        }
        if with_details:
            details = []
            for detail in self.details:
                details.append({'message': detail.message, 'response': detail.response})
            result['details'] = details
        return result


class Detail(db.Model):
    """

    """
    test = db.ReferenceProperty(Test, collection_name='details')

    message = db.TextProperty()
    response = db.TextProperty()


# eof