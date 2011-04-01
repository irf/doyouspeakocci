#!/usr/bin/python
# -*- coding: utf-8 -*-

# 
# Copyright (c) 2011 Technische Universität Dortmund
# 
# This library is free software; you can redistribute it and/or
# modify it under the terms of the GNU Lesser General Public
# License as published by the Free Software Foundation; either
# version 2.1 of the License, or (at your option) any later version.
# 
# This library is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
# Lesser General Public License for more details.
# 
# You should have received a copy of the GNU Lesser General Public
# License along with this library; if not, write to the Free Software
# Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301 USA
# 

import os
import cgi

from google.appengine.api import users
from google.appengine.ext import db
from google.appengine.ext import webapp
from google.appengine.ext.webapp import template
from google.appengine.ext.webapp.util import run_wsgi_app

from libs import httplib2
import backend

# ----- ComplianceTestRun ------------------------------------------------------
class ComplianceTestRun(db.Model):
    """
    Stores information on each compliance test request.
    TODO: not yet documented.
    """
    date = db.DateTimeProperty(auto_now_add=True)
    service_uri = db.LinkProperty()
    needs_authentication = db.BooleanProperty()
    
    is_reachable = db.BooleanProperty()


# ----- ComplianceTestResult ---------------------------------------------------
class ComplianceTestResult(db.Model):
    """
    Stores statistical data on each compliance test run.
    TODO: not yet documented.
    """
    ref_compliancetestrun = (db.ReferenceProperty(ComplianceTestRun))
    
    pass_version_information = db.BooleanProperty()
    pass_infrastructure_model_for_completness = db.BooleanProperty()
    pass_accept_header = db.BooleanProperty()
    pass_create_kinds = db.BooleanProperty()
    pass_mixins = db.BooleanProperty()
    pass_links = db.BooleanProperty()
    pass_actions = db.BooleanProperty()
    pass_filter = db.BooleanProperty()
    pass_location = db.BooleanProperty()
    pass_syntax = db.BooleanProperty()


# ----- MainPage ---------------------------------------------------------------
class MainPage(webapp.RequestHandler):
    '''
    TODO: not yet commented.
    '''
    def get(self):
        running_since = ComplianceTestRun.all().order('date').get()
        number_of_runs = ComplianceTestRun.all().count()

        template_values = {
            'number_of_runs': number_of_runs,
            'running_since': running_since,
        }

        path = os.path.join(os.path.dirname(__file__), 'index.html')
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
        ct_run = ComplianceTestRun()
        
        ct_run.service_uri = self.request.get('service_uri')
        ct_run.needs_authentication = bool(self.request.get('needs_authentication'))
        
        # test for simple access (via HTTP GET)
        http = httplib2.Http()
        try:
            response, content = http.request(ct_run.service_uri, 'GET')
            ct_run.is_reachable = True;
        except:
            ct_run.is_reachable = False;
        
        ct_run.put()
        
        # if the service is reachable, run the test suite
        if ct_run.is_reachable:
            ct_result = ComplianceTestResult(ct_run)
            
            try: # version information
                backend.test_version_information(ct_run.service_uri, {})
                ct_result.pass_http_versioninfo = True
            except:
                ct_result.pass_http_versioninfo = False
            try: # infrastructure model completeness
                backend.test_infrastructure_model_for_completness(ct_run.service_uri, {})
                ct_result.pass_infra_model = True
            except:
                ct_result.pass_infra_model = False
            try: # accept headers (including content type)
                backend.test_accept_header(ct_run.service_uri, {})
                ct_result.pass_accept_header = True
            except:
                ct_result.pass_accept_header = False
            try: # instantiate compute/storage/network kinds
                backend.test_create_kinds(ct_run.service_uri, {})
                ct_result.pass_create_kinds = True
            except:
                ct_result.pass_create_kinds = False
            try: # correct handling of user-defined mixins
                backend.test_mixins(ct_run.service_uri, {})
                ct_result.pass_mixins = True
            except:
                ct_result.pass_mixins = False
            try: # links between compute/storage/network
                backend.test_links(ct_run.service_uri, {})
                ct_result.pass_links = True
            except:
                ct_result.pass_links = False
            try: # actions on compute/storage/network
                backend.test_actions(ct_run.service_uri, {})
                ct_result.pass_actions = True
            except:
                ct_result.pass_actions = False
            try: # filter mechanisms using categories
                backend.test_filter(ct_run.service_uri, {})
                ct_result.pass_filter = True
            except:
                ct_result.pass_filter = False
            try: # behavior on location and "normal" paths
                backend.test_location(ct_run.service_uri, {})
                ct_result.pass_location = True
            except:
                ct_result.pass_location = False
            try: # syntax checks
                backend.test_syntax(ct_run.service_uri, {})
                ct_result.pass_syntax = True
            except:
                ct_result.pass_syntax = False
                
            ct_result.put()
            
        # produce template value set
        template_values = {
            'service_uri': ct_run.service_uri,
            'pass_http_versioninfo': ct_result.pass_http_versioninfo,
            'pass_infra_model': ct_result.pass_infra_model,
            'pass_accept_header': ct_result.pass_accept_header,
            'pass_create_kinds': ct_result.pass_create_kinds,
            'pass_mixins': ct_result.pass_mixins,
            'pass_links': ct_result.pass_links,
            'pass_actions': ct_result.pass_actions,
            'pass_filter': ct_result.pass_filter,
            'pass_location': ct_result.pass_location,
            'pass_syntax': ct_result.pass_syntax,
        }
        
        # render result page
        path = os.path.join(os.path.dirname(__file__), 'result.html')
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
        # TODO: not yet implemented.


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
