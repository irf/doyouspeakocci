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
import re
import uuid

from google.appengine.api import urlfetch
from dyso.model import Detail


__URLFETCH_DEADLINE = 10

__QI_OCCI = '/-/'
__QI_RFC = '/.well-known/org/ogf/occi/-/'

__MIME_TEXTPLAIN = 'text/plain'
__MIME_TEXTOCCI = 'text/occi'
__MIME_TEXTURILIST = 'text/uri-list'

__X_OCCI_LOC = 'x-occi-location'

__DYSO_SCHEME_MIXIN = 'http://doyouspeakocci.appspot.com/mixin#'

__DYSO_TERM_IDO = 'i_do'
__DYSO_TERM_DOYOU = 'do_you'

__DYSO_CAT_IDO = '%(t)s; scheme="%(s)s"' % {'t': __DYSO_TERM_IDO, 's': __DYSO_SCHEME_MIXIN}
__DYSO_CAT_DOYOU = '%(t)s; scheme="%(s)s"' % {'t': __DYSO_TERM_DOYOU, 's': __DYSO_SCHEME_MIXIN}

__DYSO_REL_IDO = '%(s)s%(t)s' % {'t': __DYSO_TERM_IDO, 's': __DYSO_SCHEME_MIXIN}
__DYSO_REL_DOYOU= '%(s)s%(t)s' % {'t': __DYSO_TERM_DOYOU, 's': __DYSO_SCHEME_MIXIN}

__DYSO_LOC_IDO = '/dyso/'

__OCCI_SCHEME_INFRA = 'http://schemas.ogf.org/occi/infrastructure#'

__OCCI_TERM_COMPUTE = 'compute'
__OCCI_TERM_NET = 'network'
__OCCI_TERM_NETIFACE = 'networkinterface'

__OCCI_CAT_COMPUTE = '%(t)s; scheme="%(s)s"' % {'t': __OCCI_TERM_COMPUTE, 's': __OCCI_SCHEME_INFRA}
__OCCI_CAT_NET = '%(t)s; scheme="%(s)s"' % {'t': __OCCI_TERM_NET, 's': __OCCI_SCHEME_INFRA}
__OCCI_CAT_NETIFACE = '%(t)s; scheme="%(s)s"' % {'t': __OCCI_TERM_NETIFACE, 's': __OCCI_SCHEME_INFRA}

__OCCI_REL_COMPUTE = '%(s)s%(t)s' % {'t': __OCCI_TERM_COMPUTE, 's': __OCCI_SCHEME_INFRA}
__OCCI_REL_NET = '%(s)s%(t)s' % {'t': __OCCI_TERM_NET, 's': __OCCI_SCHEME_INFRA}
__OCCI_REL_NETIFACE = '%(s)s%(t)s' % {'t': __OCCI_TERM_NETIFACE, 's': __OCCI_SCHEME_INFRA}

__OCCI_LOC_COMPUTE = '/compute/'


def _prettyprint(output):
    result = 'Status Code: ' + output.status_code + '\n'

    result += 'Header:\n'
    for k, v in output.headers.iteritems():
        result += k + ': ' + v + '\n'

    result += '\nContent:\n' + output.content

    return result


def _create_details(test, message, response='Response not available.'):
    details = Detail(test=test)
    details.message = message
    details.response = response
    details.put()
    return False


def _create_headers(**args):
    result = {
        'Cache-control': 'max-age=0',
        'Content-type': __MIME_TEXTOCCI,
        }
    result.update(args)
    return result


def ctf_341(test, url, auth=None):
    """
Tests the query interface as described in section 3.4.1 of the Open Cloud
Computing Interface - RESTful HTTP Rendering specification.
    """
    passed = True

    qi_rfc_url = url + __QI_RFC

    # query interface retrieval
    h = _create_headers(Accept=__MIME_TEXTPLAIN)
    if auth:
        h['Authorization'] = auth
    result = urlfetch.fetch(qi_rfc_url, headers=h)
    if not result.status_code in [200]:
        logging.debug(
            'test[%(t)s] failed on %(u)s during query interface retrieval (%(s)i)'
                % {'t': test.name, 'u': qi_rfc_url, 's': result.status_code }
        )
        passed = _create_details(test, 'The query interface appears to be missing.', _prettyprint(result))

    # category-based filtering
    h = _create_headers(Accept=__MIME_TEXTOCCI, Category=__OCCI_CAT_COMPUTE)
    if auth:
        h['Authorization'] = auth
    result = urlfetch.fetch(
        qi_rfc_url,
        headers=h,
        deadline=__URLFETCH_DEADLINE
    )

    if not result.status_code in [200]:
        logging.debug(
            'test[%(t)s] failed on %(u)s during category-based filtering (%(s)i)'
                % {'t': test.name, 'u': qi_rfc_url, 's': result.status_code }
        )
        passed = _create_details(
            test,
            'The category-based filtering for term "%(t)s" on the query interface failed.' % {'t': __OCCI_TERM_COMPUTE},
            _prettyprint(result)
        )
    if len(result.headers['category'].split(',')) > 1:
        logging.debug(
            'test[%(t)s] failed on %(u)s during category-based filtering (%(s)i)'
                % {'t': test.name, 'u': qi_rfc_url, 's': result.status_code }
        )
        passed = _create_details(
            test,
            'The category-based filtering for term "%(t)s" on the query interface failed: expected "%(c)s" instances only.'
                % {'t': __OCCI_TERM_COMPUTE, 'c': __OCCI_CAT_COMPUTE},
            _prettyprint(result)
        )

    # cleanup: remove stale instance of test mixin
    h = _create_headers(Accept=__MIME_TEXTPLAIN, Category=__DYSO_CAT_IDO)
    if auth:
        h['Authorization'] = auth
    result = urlfetch.fetch(
        qi_rfc_url,
        headers=h,
        deadline=__URLFETCH_DEADLINE
    )
    if result.status_code in [200]:
        logging.info('Cleanup: removed stale instance of "%(m)s" mixin' % {'m': __DYSO_REL_IDO})
        h = _create_headers(Accept=__MIME_TEXTPLAIN, Category=__DYSO_CAT_IDO)
        if auth:
            h['Authorization'] = auth
        urlfetch.fetch(
            qi_rfc_url,
            method=urlfetch.DELETE,
            headers=h,
            deadline=__URLFETCH_DEADLINE
        )

    # addition of a user defined mixin
    h = _create_headers(
        Accept=__MIME_TEXTPLAIN,
        Category='%(cat)s; class="mixin"; rel="%(rel)s"; location="%(loc)s"'
            % {'cat': __DYSO_CAT_IDO, 'rel': __DYSO_REL_DOYOU, 'loc': __DYSO_LOC_IDO}
    )
    if auth:
        h['Authorization'] = auth
    result = urlfetch.fetch(
        qi_rfc_url,
        method=urlfetch.POST,
        headers=h,
        deadline=__URLFETCH_DEADLINE
    )
    if not result.status_code in [200]:
        logging.debug(
            'test[%(t)s::%(i)s] failed on %(u)s during addition of a user-defined mixin (%(s)i)'
                % {'t': test.name, 'i': test.key(), 'u': qi_rfc_url, 's': result.status_code }
        )
        passed = _create_details(
            test,
            'Addition of user-defined mixin on query interface failed.',
            _prettyprint(result)
        )

    # removal of a user-defined mixin
    h = _create_headers(Accept=__MIME_TEXTPLAIN, Category=__DYSO_CAT_IDO)
    if auth:
        h['Authorization'] = auth
    result = urlfetch.fetch(
        qi_rfc_url,
        method=urlfetch.DELETE,
        headers=h,
        deadline=__URLFETCH_DEADLINE
    )
    if not result.status_code in [200]:
        logging.debug(
            'test[%(t)s::%(i)s] failed on %(u)s during removal of a user-defined mixin (%(s)i)'
                % {'t': test.name, 'i': test.key(), 'u': qi_rfc_url, 's': result.status_code }
        )
        passed = _create_details(test, 'Removal of user-defined mixin on query interface failed.', _prettyprint(result))

    return passed


def ctf_342_343(test, url, auth=None):
    """
Tests operations on mixins or kinds as described in section 3.4.2 and 3.4.3
of the Open Cloud Computing Interface - RESTful HTTP Rendering specification.
    """
    passed = True

    hostname = "dyso::" + uuid.uuid4().__str__()

    # prepare: creation of compute instances
    h = _create_headers(Accept=__MIME_TEXTOCCI, Category=__OCCI_CAT_COMPUTE)
    if auth:
        h['Authorization'] = auth
    result = urlfetch.fetch(
        url,
        method=urlfetch.POST,
        headers=h,
        deadline=__URLFETCH_DEADLINE
    )
    logging.debug(
        'setup[%(t)s::%(i)s]: creation of compute instance %(u)s succeeded (%(s)i)'
            % {'t': test.name, 'i': test.key(), 'u': result.headers['location'], 's': result.status_code }
    )

    h = _create_headers(Accept=__MIME_TEXTOCCI, Category=__OCCI_CAT_COMPUTE)
    if auth:
        h['Authorization'] = auth
    h['X-OCCI-Attribute'] = 'occi.compute.hostname="' + hostname + '"'
    result = urlfetch.fetch(
        url,
        method=urlfetch.POST,
        headers=h,
        deadline=__URLFETCH_DEADLINE)
    logging.debug(
        'setup[%(t)s::%(i)s]: creation of compute instance %(u)s succeeded (%(s)i)'
            % {'t': test.name, 'i': test.key(), 'u': result.headers['location'], 's': result.status_code }
    )


    # comparison of text/plain and text/occi rendering
    h = _create_headers(Accept=__MIME_TEXTOCCI)
    if auth:
        h['Authorization'] = auth
    result_textocci = urlfetch.fetch(
        url + __OCCI_LOC_COMPUTE,
        headers=h,
        deadline=__URLFETCH_DEADLINE
    )

    h = _create_headers(Accept=__MIME_TEXTURILIST)
    if auth:
        h['Authorization'] = auth
    result_texturilist = urlfetch.fetch(
        url + __OCCI_LOC_COMPUTE,
        headers=h,
        deadline=__URLFETCH_DEADLINE
    )

    content = [item.strip() for item in result_texturilist.content.split('\n')]
    for item in result_textocci.headers[__X_OCCI_LOC].split(','):
        if item.strip() not in content:
            logging.debug(
                'test[%(t)s::%(i)s] failed on comparison of "%(p)s"  and "%(o)s" rendering'
                    % {'t': test.name, 'i': test.key(), 'p': __MIME_TEXTPLAIN, 'o': __MIME_TEXTOCCI}
            )
            passed = _create_details(
                test,
                'X-OCCI-Location and uri-list do not return the same values for the compute collection.'
            )

    # action triggering on collection
    h = _create_headers(
        Accept=__MIME_TEXTOCCI,
        Category='start; scheme="http://schemas.ogf.org/occi/infrastructure/compute/action#"'
    )
    if auth:
        h['Authorization'] = auth
    result = urlfetch.fetch(
        url + '/compute/?action=start',
        method=urlfetch.POST,
        headers=h,
        deadline=__URLFETCH_DEADLINE)
    if result.status_code != 200:
        logging.debug(
            'test[%(t)s::%(i)s] failed on action triggering on collection (%(s)i)'
                % {'t': test.name, 'i': test.key(), 's': result.status_code}
        )
        passed = _create_details(test, 'Action triggering on collection failed', _prettyprint(result))

    # creation of a user defined mixin
    computeinstance_first = result_textocci.headers[__X_OCCI_LOC].split(', ')[0]
    computeinstance_second = result_textocci.headers[__X_OCCI_LOC].split(', ')[1]

    h = _create_headers(
        Accept=__MIME_TEXTPLAIN,
        Category='%(cat)s; class="mixin"; rel="%(rel)s"; location="%(loc)s"'
            % {'cat': __DYSO_CAT_IDO, 'rel': __DYSO_REL_DOYOU, 'loc': __DYSO_LOC_IDO }
    )
    if auth:
        h['Authorization'] = auth
    result = urlfetch.fetch(
        url + __QI_OCCI,
        method=urlfetch.POST,
        headers=h,
        deadline=__URLFETCH_DEADLINE
    )
    if result.status_code != 200:
        logging.debug(
            'test[%(t)s::%(i)s] failed on creation of a user-defined mixin (%(s)i)'
                % {'t': test.name, 'i': test.key(), 's': result.status_code}
        )
        passed = _create_details(test, 'Unable to create a user-defined mixin', _prettyprint(result))

    # attachment of a compute instance
    h = _create_headers(Accept=__MIME_TEXTOCCI)
    if auth:
        h['Authorization'] = auth
    h['X-OCCI-Location'] = computeinstance_first
    loc = url + __DYSO_LOC_IDO
    result = urlfetch.fetch(loc, method=urlfetch.POST, headers=h, deadline=__URLFETCH_DEADLINE)
    if result.status_code != 200:
        logging.debug(
            'test[%(t)s::%(i)s] failed on attachment of compute instance <%(u)s> to <%(m)s> (%(s)i)'
                % {'t': test.name, 'i': test.key(), 'u': computeinstance_first, 'm': loc, 's': result.status_code}
        )
        passed = _create_details(
            test,
            'Unable to add compute instance <%(c)s> to user-defined mixin <%(m)s>'
                % {'c': computeinstance_first, 'm': loc},
            _prettyprint(result)
        )

    # check if the user defined mixin was added to the compute instance
    h = _create_headers(Accept=__MIME_TEXTOCCI)
    if auth:
        h['Authorization'] = auth
    result = urlfetch.fetch(
        computeinstance_first,
        headers=h,
        deadline=__URLFETCH_DEADLINE
    )
    if result.headers['category'].find(__DYSO_TERM_IDO) is - 1:
        logging.debug(
            'test[%(t)s::%(i)s] failed on check if mixin "%(m)s" was added to compute instance <%(u)s> (%(s)i)'
                % {'t': test.name, 'i': test.key(), 'u': computeinstance_first, 'm': __DYSO_REL_IDO, 's': result.status_code}
        )
        passed = _create_details(test, 'Adding mixin to resource seems to be broken.', _prettyprint(result))

    # check whether mixin location contains compute location
    h = _create_headers(Accept=__MIME_TEXTOCCI)
    if auth:
        h['Authorization'] = auth
    result = urlfetch.fetch(url, headers=h, deadline=__URLFETCH_DEADLINE)
    if not len(result.headers[__X_OCCI_LOC].split(',')):
        logging.debug(
            'test[%(t)s::%(i)s] failed on check whether mixin location <%(m)s> contains compute location <%(u)s>'
                % {'t': test.name, 'i': test.key(), 'u': computeinstance_first, 'm': loc}
        )
        passed = _create_details(test, 'Mixin collection unexpectedly empty.', _prettyprint(result))

    # run full update on mixin collection locations, replacing old members
    h = _create_headers(Accept=__MIME_TEXTOCCI)
    if auth:
        h['Authorization'] = auth
    h['X-OCCI-Location'] = computeinstance_second
    result = urlfetch.fetch(url + __DYSO_LOC_IDO, method=urlfetch.PUT, headers=h, deadline=__URLFETCH_DEADLINE)
    if result.status_code != 200:
        logging.debug(
            'test[%(t)s::%(i)s] failed on full update of mixin collection <%(m)s> (%(s)s)'
                % {'t': test.name, 'i': test.key(), 'm': loc, 's': result.status_code}
        )
        passed = _create_details(test, 'Running full update on resource seems to be broken.', _prettyprint(result))

    # check whether replacement succeeded
    h = _create_headers(Accept=__MIME_TEXTOCCI)
    if auth:
        h['Authorization'] = auth
    result = urlfetch.fetch(
        url + __DYSO_LOC_IDO,
        headers=h,
        deadline=__URLFETCH_DEADLINE
    )
    if result.headers.get(__X_OCCI_LOC) != computeinstance_second:
        logging.debug(
            'test[%(t)s::%(i)s] failed replacement of member instances in mixin collection <%(m)s>'
                % {'t': test.name, 'i': test.key(), 'm': loc}
        )
        passed = _create_details(
            test,
            'The replacement of member instances in the mixin collection <%(m)s> failed.',
            _prettyprint(result)
        )

    # filtering /compute/ using the test mixin
    h = _create_headers(Accept=__MIME_TEXTOCCI, Category=__DYSO_CAT_IDO)
    if auth:
        h['Authorization'] = auth
    result = urlfetch.fetch(
        url + __OCCI_LOC_COMPUTE,
        headers=h,
        deadline=__URLFETCH_DEADLINE
    )
    if result.headers.get(__X_OCCI_LOC) != computeinstance_second:
        logging.debug(
            'test[%(t)s::%(i)s] failed on filtering <%(u)s> using mixin "%(m)s"'
                % {'t': test.name, 'i': test.key(), 'u': __OCCI_LOC_COMPUTE,  'm': __DYSO_REL_IDO}
        )
        passed = _create_details(test, 'Category-based filtering seems to be broken.', _prettyprint(result))

    # filtering on /compute/ using the test attribute
    h = _create_headers(Accept=__MIME_TEXTOCCI)
    if auth:
        h['Authorization'] = auth
    h['X-OCCI-Attribute'] = 'occi.compute.hostname="' + hostname + '"'
    result = urlfetch.fetch(url + __OCCI_LOC_COMPUTE, headers=h, deadline=__URLFETCH_DEADLINE)
    if not result.headers.get(__X_OCCI_LOC) or len(result.headers[__X_OCCI_LOC].split()) != 1:
        logging.debug(
            'test[%(t)s::%(i)s] failed on filtering using attributes'
                % {'t': test.name, 'i': test.key()}
        )
        passed = _create_details(test, 'Attribute-based filtering seems to be broken', _prettyprint(result))

    # deletion of last item in mixin collection
    h = _create_headers(Accept=__MIME_TEXTOCCI)
    if auth:
        h['Authorization'] = auth
    h['X-OCCI-Location'] = computeinstance_second
    result = urlfetch.fetch(url + __DYSO_LOC_IDO, method=urlfetch.DELETE, headers=h, deadline=__URLFETCH_DEADLINE)
    if result.status_code != 200:
        logging.debug(
            'test[%(t)s::%(i)s] failed on deletion of last item in mixin collection (%(s)s)'
                % {'t': test.name, 'i': test.key(), 's': result.status_code}
        )
        passed = _create_details(test, 'Unable to remove last entity from mixin', _prettyprint(result))

    # check whether deletion was successful
    h = _create_headers(Accept=__MIME_TEXTOCCI)
    if auth:
        h['Authorization'] = auth
    result = urlfetch.fetch(
        url + __DYSO_LOC_IDO,
        headers=h,
        deadline=__URLFETCH_DEADLINE
    )
    if hasattr(result.headers, __X_OCCI_LOC):
        logging.debug(
            'test[%(t)s::%(i)s] failed on check whether deletion of last mixin collection item was successful'
                % {'t': test.name, 'i': test.key()}
        )
        passed = _create_details(test, 'Unexpected item in collection.', _prettyprint(result))

    # deletion of mixin
    h = _create_headers(Accept=__MIME_TEXTOCCI, Category=__DYSO_CAT_IDO)
    if auth:
        h['Authorization'] = auth
    result = urlfetch.fetch(
        url + __QI_OCCI,
        method=urlfetch.DELETE,
        headers=h,
        deadline=__URLFETCH_DEADLINE
    )
    if result.status_code != 200:
        logging.debug(
            'test[%(t)s::%(i)s] failed on deletion of mixin "%(m)s" (%(s)s)'
                % {'t': test.name, 'i': test.key(), 'm': __DYSO_REL_IDO, 's': result.status_code}
        )
        passed = _create_details(test, 'Unable to delete user-defined mixin.', _prettyprint(result))

    # and delete all compute instances
    h = _create_headers(Accept=__MIME_TEXTOCCI)
    if auth:
        h['Authorization'] = auth
    result = urlfetch.fetch(
        url + __OCCI_LOC_COMPUTE,
        method=urlfetch.DELETE,
        headers=h,
        deadline=__URLFETCH_DEADLINE
    )
    if result.status_code != 200:
        logging.debug(
            'test[%(t)s::%(i)s] failed on deletion of compute instances at <%(u)s> (%(s)s)'
                % {'t': test.name, 'i': test.key(), 'u': url + __OCCI_LOC_COMPUTE, 's': result.status_code}
        )
        passed = _create_details(test, 'Unable to delete compute instance.', _prettyprint(result))

    return passed
        

def ctf_344(test, url, auth=None):
    """
Operations on resource instances as described in section 3.4.4 of the
Open Cloud Computing Interface - RESTful HTTP Rendering specification.
    """
    passed = True
    
    hostname = "dyso::" + uuid.uuid4().__str__()

    # POST to create
    h = _create_headers(Accept=__MIME_TEXTOCCI, Category=__OCCI_CAT_COMPUTE)
    if auth:
        h['Authorization'] = auth
    result = urlfetch.fetch(
        url,
        method=urlfetch.POST,
        headers=h,
        deadline=__URLFETCH_DEADLINE
    )
    if result.status_code == 201 or (result.status_code == 200 and 'location' in result.headers):
        loc_post = result.headers['location']
    elif result.status_code == 200:
        logging.warn('Seems like OCCI server responded with 200...not 201 and location...')
        h = _create_headers(Accept=__MIME_TEXTOCCI)
        if auth:
            h['Authorization'] = auth
        result = urlfetch.fetch(
            url + __OCCI_LOC_COMPUTE,
            headers=h,
            deadline=__URLFETCH_DEADLINE
        )
        loc_post = result.headers[__X_OCCI_LOC].split(',')[0].strip()
    else:
        passed = _create_details(test, 'Creation of "compute" kind instance failed.', _prettyprint(result))
        return passed

    # trigger action...
    h = _create_headers(Accept=__MIME_TEXTOCCI)
    if auth:
        h['Authorization'] = auth
    result = urlfetch.fetch(loc_post, headers=h, deadline=__URLFETCH_DEADLINE)
    links = result.headers['link'].split(',')
    for link in links:
        if link.find('?action=start>') != -1:
            action = url + link[1:link.find('>')]
            h = _create_headers(
                Accept=__MIME_TEXTOCCI,
                Category='start; scheme="http://schemas.ogf.org/occi/infrastructure/compute/action#"'
            )
            if auth:
                h['Authorization'] = auth
            result = urlfetch.fetch(
                action,
                method=urlfetch.POST,
                headers=h,
                deadline=__URLFETCH_DEADLINE)
            if not result.status_code == 200:
                passed = _create_details(test, 'Triggering of action failed.', _prettyprint(result))
        else:
            logging.warn('Start action not applicable - might be correct...')

    # POST - partial update
    h = _create_headers(Accept=__MIME_TEXTOCCI)
    if auth:
        h['Authorization'] = auth
    h['X-OCCI-Attribute'] = 'occi.compute.hostname="' + hostname + '"'
    result = urlfetch.fetch(loc_post, method=urlfetch.POST, headers=h, deadline=__URLFETCH_DEADLINE)
    if not result.status_code == 200:
        passed = _create_details(test, 'Update on resource <%(loc)s> failed.' % {'loc': loc_post}, _prettyprint(result))

    # PUT create
    loc_put = url + '/123'

    h = _create_headers(Accept=__MIME_TEXTOCCI, Category=__OCCI_CAT_COMPUTE)
    if auth:
        h['Authorization'] = auth
    h['X-OCCI-Attribute'] = 'com.appspot.doyouspeakocci.do_you="i_do"'
    result = urlfetch.fetch(loc_put, method=urlfetch.PUT, headers=h, deadline=__URLFETCH_DEADLINE)
    if result.status_code == 400: # RN: A server is allowed to refuse the request. #3.4.4 footnote 6.
        logging.warn('Server refused PUT create at <%(u)s>, this is OK according to section 3.4.4.' % {'u': loc_put})
        loc_put = loc_post
    elif not result.status_code in [200, 201]:
        passed = _create_details(
            test,
            'Adding named "compute" kind instance at <%(loc)s> failed.' % {'loc': loc_put},
            _prettyprint(result)
        )

    # PUT for full update
    h = _create_headers(Accept=__MIME_TEXTOCCI, Category=__OCCI_CAT_COMPUTE)
    if auth:
        h['Authorization'] = auth
    h['X-OCCI-Attribute'] = 'occi.core.title="doyouspeakOCCI Compute Instance"'
    result = urlfetch.fetch(loc_put, method=urlfetch.PUT, headers=h, deadline=__URLFETCH_DEADLINE)
    if not result.status_code == 200:
        passed = _create_details(
            test,
            'Full update on "compute" kind instance at <%(loc)s> failed.' % {'loc': loc_put},
            _prettyprint(result)
        )

    # GET
    h = _create_headers(Accept=__MIME_TEXTOCCI)
    if auth:
        h['Authorization'] = auth
    result = urlfetch.fetch(loc_post, headers=h, deadline=__URLFETCH_DEADLINE)
    if not result.status_code == 200:
        passed = _create_details(
            test,
            'Resource retrieval at <%(loc)s> failed.' % {'loc': loc_post},
            _prettyprint(result)
        )

    # DELETE
    h = _create_headers(Accept=__MIME_TEXTOCCI)
    if auth:
        h['Authorization'] = auth
    result = urlfetch.fetch(
        loc_post,
        method=urlfetch.DELETE,
        headers=h,
        deadline=__URLFETCH_DEADLINE
    )
    if not result.status_code == 200:
        passed = _create_details(
            test,
            'Resource deletion of <%(loc)s> failed.' % {'loc': loc_post},
            _prettyprint(result)
        )
    if loc_post != loc_put:
        h = _create_headers(Accept=__MIME_TEXTOCCI)
        if auth:
            h['Authorization'] = auth
        result = urlfetch.fetch(
            loc_put,
            method=urlfetch.DELETE,
            headers=h,
            deadline=__URLFETCH_DEADLINE
        )
        if not result.status_code == 200:
            passed = _create_details(
                test,
                'Resource deletion of <%(loc)s> failed.' % {'loc': loc_post},
                _prettyprint(result)
            )

    return passed


def ctf_345(test, url, auth=None):
    """
Handling of link instances as described in section 3.4.5 of the Open
Cloud Computing Interface - RESTful HTTP Rendering specification.
    """
    passed = True

    # create compute
    h = _create_headers(Accept=__MIME_TEXTOCCI, Category=__OCCI_CAT_COMPUTE)
    if auth:
        h['Authorization'] = auth
    result = urlfetch.fetch(
        url,
        method=urlfetch.POST,
        headers=h,
        deadline=__URLFETCH_DEADLINE
    )
    if 'location' not in result.headers and result.status_code not in (201, 200):
        logging.warn('Creation failed - this might be okay - please examine output! ' , _prettyprint(result))
        logging.warn('Test needs to be updated to discover location by doing a GET on /compute/')
        return passed
    loc_compute = result.headers['location']

    # create network
    h = _create_headers(Accept=__MIME_TEXTOCCI, Category=__OCCI_CAT_NET)
    if auth:
        h['Authorization'] = auth
    result = urlfetch.fetch(
        url,
        method=urlfetch.POST,
        headers=h,
        deadline=__URLFETCH_DEADLINE
    )
    if result.status_code not in [200, 201]:
        logging.warn('Creation failed - this might be okay - please examine output! ' , _prettyprint(result))
    loc_network = result.headers['location']

    # now create a network link...
    h = _create_headers(Accept=__MIME_TEXTOCCI, Category=__OCCI_CAT_NETIFACE)
    if auth:
        h['Authorization'] = auth
    h['X-OCCI-Attribute'] = 'occi.core.source="' + loc_compute + '", occi.core.target="' + loc_network + '"'
    result = urlfetch.fetch(
        url,
        method=urlfetch.POST,
        headers=h,
        deadline=__URLFETCH_DEADLINE)
    if result.status_code not in [200, 201]:
        passed = _create_details(
            test,
            'Creation of a "%(t)s" link instance failed.' % {'t': __OCCI_TERM_NETIFACE},
            _prettyprint(result)
        )
    link_loc = result.headers['location']

    # check if links has source, target attributes
    h = _create_headers(Accept=__MIME_TEXTOCCI)
    if auth:
        h['Authorization'] = auth
    result = urlfetch.fetch(link_loc, headers=h, deadline=__URLFETCH_DEADLINE)
    if result.headers.has_key('x-occi-attribute'):
        if result.headers['x-occi-attribute'].find('occi.core.source') == -1\
        or result.headers['x-occi-attribute'].find('occi.core.target') == -1:
            passed = _create_details(test, 'Missing "source" and/or "target" attribute on link.' , _prettyprint(result))
    else:
        passed = _create_details(test, 'Link retrieval seems to be broken.' , _prettyprint(result))

    # 1st cleanup...
    h = _create_headers(Accept=__MIME_TEXTOCCI)
    if auth:
        h['Authorization'] = auth
    result = urlfetch.fetch(
        loc_compute,
        method=urlfetch.DELETE,
        headers=h,
        deadline=__URLFETCH_DEADLINE
    )
    if not result.status_code == 200:
        passed = _create_details(
            test,
            'Resource deletion of <%(loc)s> failed.' % {'loc': loc_compute},
            _prettyprint(result)
        )

    # now create compute again but with inline...
    h = _create_headers(Accept=__MIME_TEXTOCCI, Category=__OCCI_CAT_COMPUTE)
    if auth:
        h['Authorization'] = auth
    h['Link'] = '<%(loc)s>; rel="%(rel)s"; category="%(cat)s";'\
        % {'loc': loc_network, 'rel': __OCCI_REL_NET, 'cat': __OCCI_REL_NETIFACE}
    result = urlfetch.fetch(url, method=urlfetch.POST, headers=h, deadline=__URLFETCH_DEADLINE)
    if result.status_code not in [200, 201]:
        logging.warn('Creation failed - this might be okay - please examine output! ' , _prettyprint(result))
    loc_compute = result.headers['location']

    # Now check if compute has inline link rendering...
    h = _create_headers(Accept=__MIME_TEXTOCCI)
    if auth:
        h['Authorization'] = auth
    result = urlfetch.fetch(loc_compute, headers=h, deadline=__URLFETCH_DEADLINE)
    if not result.headers.has_key('link'):
        passed = _create_details(
            test,
            'Inline link rendering for "compute" resource seems to be missing.'
            , _prettyprint(result)
        )

    # 2nd cleanup...
    h = _create_headers(Accept=__MIME_TEXTOCCI)
    if auth:
        h['Authorization'] = auth
    result = urlfetch.fetch(
        loc_compute,
        method=urlfetch.DELETE,
        headers=h,
        deadline=__URLFETCH_DEADLINE
    )
    if not result.status_code == 200:
        passed = _create_details(
            test,
            'Resource deletion of <%(loc)s> failed.' % {'loc': loc_compute},
            _prettyprint(result)
        )
    # no need to delete link since that should be in the lifecycle of the compute resource...
    h = _create_headers(Accept=__MIME_TEXTOCCI)
    if auth:
        h['Authorization'] = auth
    result = urlfetch.fetch(
        loc_network,
        method=urlfetch.DELETE,
        headers=h,
        deadline=__URLFETCH_DEADLINE
    )
    if not result.status_code == 200:
        passed = _create_details(
            test,
            'Resource deletion of <%(loc)s> failed.' % {'loc': loc_network},
            _prettyprint(result)
        )

    return passed


def ctf_35(test, url, auth=None):
    """
Syntax and semantics of the rendering as described in section 3.5 of
the Open Cloud Computing Interface - RESTful HTTP Rendering specification.
    """
    passed = True

    # TODO: add checks for syntax of links, locations, attributes...

    regex = r'\w+; \bscheme=[a-z:./#"]*; \bclass="(?:action|kind|mixin)"'

    h = _create_headers(Accept=__MIME_TEXTPLAIN)
    if auth:
        h['Authorization'] = auth
    result = urlfetch.fetch(
        url + __QI_OCCI,
        headers=h,
        deadline=__URLFETCH_DEADLINE
    )
    cat_rend = result.content.split('\n')[1].strip()

    cat_rend = cat_rend[10:]
    p = re.compile(regex)

    m = p.match(cat_rend)
    if m is None:
        passed = _create_details(
            test,
            'Syntax error in "text/plain" rendering (should adhere to <term>;scheme="<url>";class=[kind,action,mixin]).',
            _prettyprint(result)
        )

    h = _create_headers(Accept=__MIME_TEXTOCCI)
    if auth:
        h['Authorization'] = auth
    result = urlfetch.fetch(
        url + __QI_OCCI,
        headers=h,
        deadline=__URLFETCH_DEADLINE
    )
    cat_rend = result.headers['category'].strip()
    p = re.compile(regex)
    m = p.match(cat_rend)
    if m is None:
        passed = _create_details(
            test,
            'Syntax error in "text/occi" rendering (should adhere to <term>;scheme="<url>";class=[kind,action,mixin]).',
            _prettyprint(result)
        )

    # Test escaping of quotes
    h = _create_headers(Accept=__MIME_TEXTOCCI, Category=__OCCI_CAT_COMPUTE)
    if auth:
        h['Authorization'] = auth
    h['X-OCCI-Attribute'] = 'occi.compute.memory=3.6, occi.core.title="Quote escaping m\'kay? \\", occi.compute.memory=1.0"'
    result = urlfetch.fetch(url, method=urlfetch.POST, headers=h, deadline=__URLFETCH_DEADLINE)
    if not result.headers.get('location') or result.status_code not in (200, 201):
        passed = _create_details(
            test,
            'Creation of "compute" resource with "X-OCCI-Attribute: %(attr)s" failed.' %
                {'attr': h['X-OCCI-Attribute']},
            _prettyprint(result)
        )

    loc_compute = result.headers.get('location')
    h = _create_headers(Accept=__MIME_TEXTPLAIN)
    if auth:
        h['Authorization'] = auth
    result = urlfetch.fetch(
        loc_compute,
        headers=h,
        deadline=__URLFETCH_DEADLINE
    )
    if not result.status_code == 200:
        passed = _create_details(
            test,
            'Resource retrieval of <%(loc)s> failed.' % {'loc': loc_compute},
            _prettyprint(result)
        )

    found = False # If memory=1.0 quote parsing failed, should be 3.6
    for line in result.content.split('\n'):
        l = line.split(':', 1)
        if len(l) < 2: continue
        header = l[0].strip()
        value = l[1].strip()
        if header.lower() != 'x-occi-attribute':
            continue
        l = value.split('=', 1)
        if len(l) < 2: continue
        if l[0] == 'occi.compute.memory':
            memory = l[1].strip('\s"')
            try:
                memory = float(memory)
            except ValueError:
                break
            else:
                if memory == 3.6:
                    found = True
    if not found:
        passed = _create_details(test, 'Quotation escaping is not parsed correctly.' , _prettyprint(result))

    return passed


def ctf_365(test, url, auth=None):
    """
Versioning as described in section 3.6.5 of the Open Cloud Computing
Interface - RESTful HTTP Rendering specification.
    """
    passed = True

    h = _create_headers(Accept=__MIME_TEXTOCCI)
    if auth:
        h['Authorization'] = auth
    result = urlfetch.fetch(url + '/', headers=h, deadline=__URLFETCH_DEADLINE)
    if result.headers.get('server').find('OCCI/1.1') == -1:
        passed = _create_details(test, 'Server does not correctly expose version OCCI/1.1.', result.headers )

    return passed


def ctf_366(test, url, auth=None):
    """
Correct handling of "Content-type" and "Accept" headers as described
in section 3.6.6 of the Open Cloud Computing Interface - RESTful HTTP Rendering
specification.
    """
    passed = True

    url += __QI_OCCI

    h = _create_headers(Accept=__MIME_TEXTPLAIN)
    if auth:
        h['Authorization'] = auth
    result = urlfetch.fetch(url, headers=h, deadline=__URLFETCH_DEADLINE)
    content_type = result.headers.get('content-type')
    if content_type: content_type = content_type.split(';')[0].strip()
    if not content_type == __MIME_TEXTPLAIN:
        _create_details(
            test,
            'On "Accept: text/plain", "Content-type: text/plain" was not exposed by the server.',
            _prettyprint(result)
        )

    h = _create_headers(Accept=__MIME_TEXTOCCI)
    if auth:
        h['Authorization'] = auth
    result = urlfetch.fetch(url, headers=h, deadline=__URLFETCH_DEADLINE)
    content_type = result.headers.get('content-type')
    if content_type: content_type = content_type.split(';')[0].strip()
    if not content_type == __MIME_TEXTOCCI:
        _create_details(
            test,
            'On "Accept: text/occi", "Content-type: text/occi" was not exposed by the server.',
            _prettyprint(result)
        )

    return passed


def ctf_367(test, url, auth=None):
    """
RFC5785 compliance as described in section 3.6.7 of the Open Cloud
Computing Interface - RESTful HTTP Rendering specification.
    """
    passed = True

    h = _create_headers(Accept=__MIME_TEXTOCCI)
    if auth:
        h['Authorization'] = auth

    # retrieval of all kinds, actions and mixins
    result_first = urlfetch.fetch(url + __QI_OCCI, headers=h, deadline=__URLFETCH_DEADLINE)
    if not result_first.status_code in [200]:
        passed = _create_details(test, 'GET on query interface failed.', _prettyprint(result_first))

    # retrieval of all kinds, actions and mixins
    result_second = urlfetch.fetch(url + __QI_RFC, headers=h, deadline=__URLFETCH_DEADLINE)
    if not result_second.status_code in [200]:
        passed = _create_details('GET on query interface failed.', _prettyprint(result_second))


    if result_first.headers['category'] != result_second.headers['category']:
        passed = _create_details(
            test,
            'Differing GET results for <%(qi_occi)s> and <%(qi_rfc)s>'
                % {'qi_occi': url + __QI_OCCI, 'qi_rfc': url + __QI_RFC}
        )

    return passed


def _test_model_completeness(rendering, rel, attributes, actions):
    """
Completeness of the model, i.e. instance attributes and actions
wrt. to the category they represent.
    """
    for item in rendering:
        item = item.strip().split('=')
        if item[0] == 'rel':
            if item[1].find(rel) == -1:
                return False
        elif item[0] == 'attributes':
            for attr in attributes:
                if item[1].find(attr) == -1:
                    return False
        elif item[0] == 'actions':
            for action in actions:
                if item[1].find(action) == -1:
                    return False

    return True

def ctf_gfd184(test, url, auth=None):
    """
Completeness of the IaaS model with respect to the Open Cloud
Computing Interface - Infrastructure specification.
    """
    passed = True

    h = _create_headers(Accept=__MIME_TEXTPLAIN)
    if auth:
        h['Authorization'] = auth
    result = urlfetch.fetch(url + __QI_OCCI, headers=h, deadline=__URLFETCH_DEADLINE
    )

    for line in result.content.split('\n'):
        cur = line.lstrip('Category:').split(';')
        # check if compute has all attributes & actions & rels
        #----------------------------------------------------------------- Kinds
        if cur[0].strip() == 'compute' and cur[1].strip() == 'scheme="http://schemas.ogf.org/occi/infrastructure#"':
            rel = 'http://schemas.ogf.org/occi/core#resource'
            attr = ['occi.compute.architecture', 'occi.compute.cores', 'occi.compute.hostname', 'occi.compute.speed', 'occi.compute.memory', 'occi.compute.state']
            actions = ['start', 'stop', 'suspend', 'restart']
            if not _test_model_completeness(cur, rel, attr, actions):
                passed = _create_details(test, 'Infrastructure model is missing "compute" kind.')
        elif cur[0].strip() == 'network' and cur[1].strip() == 'scheme="http://schemas.ogf.org/occi/infrastructure#"':
            rel = 'http://schemas.ogf.org/occi/core#resource'
            attr = ['occi.network.vlan', 'occi.network.label', 'occi.network.state']
            actions = ['up', 'down']
            if not _test_model_completeness(cur, rel, attr, actions):
                passed = _create_details(test, 'Infrastructure model is missing "network" kind.')
        elif cur[0].strip() == 'storage' and cur[1].strip() == 'scheme="http://schemas.ogf.org/occi/infrastructure#"':
            rel = 'http://schemas.ogf.org/occi/core#resource'
            attr = ['occi.storage.size', 'occi.storage.state']
            actions = ['online', 'offline', 'backup', 'snapshot', 'resize']
            if not _test_model_completeness(cur, rel, attr, actions):
                passed = _create_details(test, 'Infrastructure model is missing "storage" kind.')
        #----------------------------------------------------------------- Links
        elif cur[0].strip() == 'storagelink' and cur[1].strip() == 'scheme="http://schemas.ogf.org/occi/infrastructure#"':
            rel = 'http://schemas.ogf.org/occi/core#link'
            attr = ['occi.storagelink.deviceid', 'occi.storagelink.mountpoint', 'occi.storagelink.state']
            actions = []
            if not _test_model_completeness(cur, rel, attr, actions):
                passed = _create_details(test, 'Infrastructure model is missing "storagelink" link.')
        elif cur[0].strip() == 'networkinterface' and cur[1].strip() == 'scheme="http://schemas.ogf.org/occi/infrastructure#"':
            rel = 'http://schemas.ogf.org/occi/core#link'
            attr = ['occi.networkinterface.state', 'occi.networkinterface.mac', 'occi.networkinterface.interface']
            actions = []
            if not _test_model_completeness(cur, rel, attr, actions):
                passed = _create_details(test, 'Infrastructure model is missing "networkinterface" link.')
        #---------------------------------------------------------------- mixins
        elif cur[0].strip() == 'ipnetwork' and cur[1].strip() == 'scheme="http://schemas.ogf.org/occi/infrastructure/network#"':
            rel = 'http://schemas.ogf.org/occi/core#link'
            attr = ['occi.network.address', 'occi.network.gateway', 'occi.network.allocation']
            actions = []
            if not _test_model_completeness(cur, rel, attr, actions):
                passed = _create_details(test, 'Infrastructure model is missing "ipnetwork" mixin.')
        #--------------------------------------------------------------- actions
        elif cur[0].strip() == 'start' and cur[1].strip() == 'scheme="http://schemas.ogf.org/occi/infrastructure/compute/action#"':
            rel = ''
            attr = []
            actions = []
            if not _test_model_completeness(cur, rel, attr, actions):
                passed = _create_details(test, 'Infrastructure model is missing "start" action definition.')
        elif cur[0].strip() == 'stop' and cur[1].strip() == 'scheme="http://schemas.ogf.org/occi/infrastructure/compute/action#"':
            rel = ''
            #attr = ['graceful', 'acpioff', 'poweroff']
            attr = ['method']
            actions = []
            if not _test_model_completeness(cur, rel, attr, actions):
                passed = _create_details(test, 'Infrastructure model is missing "stop" action definition.')
        elif cur[0].strip() == 'restart' and cur[1].strip() == 'scheme="http://schemas.ogf.org/occi/infrastructure/compute/action#"':
            rel = ''
            #attr = ['graceful', 'warm', 'cold']
            attr = ['method']
            actions = []
            if not _test_model_completeness(cur, rel, attr, actions):
                passed = _create_details(test, 'Infrastructure model is missing "restart" action definition.')
        elif cur[0].strip() == 'suspend' and cur[1].strip() == 'scheme="http://schemas.ogf.org/occi/infrastructure/compute/action#"':
            rel = ''
            #attr = ['hibernate', 'suspend']
            attr = ['method']
            actions = []
            if not _test_model_completeness(cur, rel, attr, actions):
                passed = _create_details(test, 'Infrastructure model is missing "suspend" action definition.')
        elif cur[0].strip() == 'up' and cur[1].strip() == 'scheme="http://schemas.ogf.org/occi/infrastructure/network/action#"':
            rel = ''
            attr = []
            actions = []
            if not _test_model_completeness(cur, rel, attr, actions):
                passed = _create_details(test, 'Infrastructure model is missing "up" action definition.')
        elif cur[0].strip() == 'down' and cur[1].strip() == 'scheme="http://schemas.ogf.org/occi/infrastructure/network/action#"':
            rel = ''
            attr = []
            actions = []
            if not _test_model_completeness(cur, rel, attr, actions):
                passed = _create_details(test, 'Infrastructure model is missing "down" action definition.')
        elif cur[0].strip() == 'online' and cur[1].strip() == 'scheme="http://schemas.ogf.org/occi/infrastructure/storage/action#"':
            rel = ''
            attr = []
            actions = []
            if not _test_model_completeness(cur, rel, attr, actions):
                passed = _create_details(test, 'Infrastructure model is missing "online" action definition.')
        elif cur[0].strip() == 'offline' and cur[1].strip() == 'scheme="http://schemas.ogf.org/occi/infrastructure/storage/action#"':
            rel = ''
            attr = []
            actions = []
            if not _test_model_completeness(cur, rel, attr, actions):
                passed = _create_details(test, 'Infrastructure model is missing "offline" action definition.')
        elif cur[0].strip() == 'resize' and cur[1].strip() == 'scheme="http://schemas.ogf.org/occi/infrastructure/storage/action#"':
            rel = ''
            attr = ['size']
            actions = []
            if not _test_model_completeness(cur, rel, attr, actions):
                passed = _create_details(test, 'Infrastructure model is missing "resize" action definition.')
        elif cur[0].strip() == 'backup' and cur[1].strip() == 'scheme="http://schemas.ogf.org/occi/infrastructure/storage/action#"':
            rel = ''
            attr = []
            actions = []
            if not _test_model_completeness(cur, rel, attr, actions):
                passed = _create_details(test, 'Infrastructure model is missing "backup" action definition.')
        elif cur[0].strip() == 'snapshot' and cur[1].strip() == 'scheme="http://schemas.ogf.org/occi/infrastructure/storage/action#"':
            rel = ''
            attr = []
            actions = []
            if not _test_model_completeness(cur, rel, attr, actions):
                passed = _create_details(test, 'Infrastructure model is missing "snapshot" action definition.')

    return passed

 # eof