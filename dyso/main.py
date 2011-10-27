#!/usr/bin/python
# -*- coding: utf-8 -*-
# $Id$

# 
# This file is part of doyouspeakOCCI.
# 
# doyouspeakOCCI is free software; you can redistribute it and/or
# modify it under the terms of the GNU General Public
# License as published by the Free Software Foundation; either
# version 2.1 of the License, or (at your option) any later version.
# 
# doyouspeakOCCI is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
# Lesser General Public License for more details.
# 
# You should have received a copy of the GNU General Public
# License along with this library; if not, write to the Free Software
# Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301 USA
#

import os

from dyso.model import Suite
from dyso.results import ResultPage, StatisticsPage
from dyso.subscriptions import ScheduledPage

from google.appengine.ext import webapp
from google.appengine.ext.webapp import template
from google.appengine.ext.webapp.util import run_wsgi_app

class MainPage(webapp.RequestHandler):
    """
    TODO: not yet commented.
    """

    def get(self):
        running_since = Suite.all().order('date').get().date
        number_of_runs = Suite.all().count()

        template_values = {
            'do_you_speak': 'do you speak',
            'number_of_runs': number_of_runs,
            'running_since': running_since,
            }

        path = os.path.join(os.path.dirname(__file__), '../templates/index.html')
        self.response.out.write(template.render(path, template_values))


# ----- WSGI intialization -----------------------------------------------------
"""
TODO: not yet commented.
"""
application = webapp.WSGIApplication([
    ('/', MainPage),
    ('/result', ResultPage),
    ('/statistics', StatisticsPage),
    (r'/scheduled/(.*)', ScheduledPage)
], debug=True
)


def main():
    """
    TODO: not yet commented.
    """
    run_wsgi_app(application)


# ----- default initialization -------------------------------------------------
if __name__ == "__main__":
    main()

# eof