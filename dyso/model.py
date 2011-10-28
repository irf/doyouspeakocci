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
# along with Foobar.  If not, see <http://www.gnu.org/licenses/>.

from google.appengine.ext import db

class Test(db.Model):
    """
    Stores statistical data on each compliance test run.
    TODO: not yet documented.
    """
    name = db.StringProperty()
    description = db.TextProperty()
    result = db.BooleanProperty()
    details = db.TextProperty()

    def __init__(self, name, description):
        super(Test, self).__init__()
        self.name = name
        self.description = description


class Suite(db.Model):
    """
    Stores information on each compliance test request.
    TODO: not yet documented.
    """
    date = db.DateTimeProperty(auto_now_add=True)
    service_uri = db.LinkProperty()
    is_compliant = db.BooleanProperty()

class Subscriber(db.Model):
    """
    TODO: not yet documented.
    """
    subscriber_uri = db.LinkProperty()

# eof