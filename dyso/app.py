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

from dyso.main import MainPage

from dyso.results import ResultPage, StatisticsPage

from google.appengine.ext import webapp
from google.appengine.ext.webapp.util import run_wsgi_app


application = webapp.WSGIApplication([
    ('/', MainPage),
    ('/result', ResultPage),
    ('/statistics', StatisticsPage),
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