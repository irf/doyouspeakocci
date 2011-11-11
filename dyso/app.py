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
import logging
import uuid

from dyso.main import MainPage
from dyso.model import Detail, Test, Suite

from dyso.statistics import StatisticsPage

from google.appengine.ext import webapp
from google.appengine.ext.webapp.util import run_wsgi_app


application = webapp.WSGIApplication([
    ('/', MainPage),
    ('/statistics', StatisticsPage),
], debug=True
)


def main():
    """
    TODO: not yet commented.
    """
    logging.debug('Starting dyso WSGI application...')
    run_wsgi_app(application)
    logging.debug('dyso WSGI application is up and running!')


# ----- default initialization -------------------------------------------------
if __name__ == "__main__":
    main()

    
# eof