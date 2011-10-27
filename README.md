# doyouspeakOCCI Compliance Testing Facility
The doyouspeakOCCI Compliance Testing Facility is a [Google App Engine (GAE)]
(http://code.google.com/appengine/)-based checking tool for the
[Open Cloud Computing Interface (OCCI)](http://occi-wg.org/) family of
specifications. More specifically, it provides a full compliance test suite for
the [OCCI Core (GFD.183)](http://ogf.org/documents/GFD.183.pdf),
[OCCI Infrastructure (GFD.184)](http://ogf.org/documents/GFD.184.pdf), and
[OCCI RESTful HTTP Rendering (GFD.185)](http://ogf.org/documents/GFD.185.pdf)
specifications.

doyouspeakOCCI is written in [Python](http://www.python.org) and heavily
building on the GAE services, mainly [Task Queue]
(http://code.google.com/appengine/docs/python/taskqueue/), [URL Fetch]
(http://code.google.com/appengine/docs/python/urlfetch/), and the [webapp
Framework](http://code.google.com/appengine/docs/python/tools/webapp/).

Note that doyouspeakOCCI not to be considered the "official" testing suite
for OCCI endorsed by the Open Grid Forum, but rather than that, a third-party
contribution which aims to be as close as possible. For a more thorough
explanation, please take a look at [the wiki pages]
(https://github.com/irf/doyouspeakOCCI/wiki/is-dyso-normative).


## How to use
doyouspeakOCCI was hard to implement, but is simple to use. Just point your browser
to http://doyouspeakocci.appspot.com, enter the base URL of your OCCI implementation,
and press "Go!".

Optionally, you can provide credentials for HTTP basic auth, if your service is
secured. We strongly recommend to use a one-time test account; although we promise
to use the credentials only for the compliance test, we cannot guarantee what others
on the way (especially GAE) will do with them.

Please note that doyouspeakOCCI records data on every test run in the [GAE DataStore]
(http://code.google.com/appengine/docs/python/gettingstarted/usingdatastore.html).
This is done solely for the sake of [displaying usage statistics]
(http://doyouspeakocci.appspot.com/statistics). Within the limitations of applicable jurisdiction
and the [GAE Terms of Service](http://code.google.com/appengine/terms.html), we will not
disclose this data to anyone beyond what is being displayed on the doyouspeakOCCI web presence.

For other questions, please also take a look at the [FAQ]
(https://github.com/irf/doyouspeakocci/wiki/faq).


## Where to get
doyouspeakOCCI is available as a source code release only, which can be obtained by
two ways:

 * By [checking out](http://help.github.com/git-cheat-sheets/) the source code
   via `git checkout`
 * By fetching a repository [tarball](https://github.com/irf/doyouspeakocci/tarball/master)
   or [zipfile](https://github.com/irf/doyouspeakocci/tarball/master)

Alternatively, you might want to pick one of the advertised downloads (click on
the "Downloads" button in the upper right of the doyouspeakOCCI home at
[GitHub](https://github.com/irf/doyouspeakocci).

If you wish to run the service on your local system for testing purposes, please take a look at the
[doyouspeakOCCI Installation Guide](https://github.com/irf/doyouspeakOCCI/wiki/installation) for
a detailed explanation on how to setup the environment.

## Contributing
doyouspeakOCCI aims to be a community effort, and help is always welcome. Please contact
us on the mailing lists to learn more.

### License
We think that doyouspeakOCCI should be available to everyone with the upmost amount of
freedom. To make sure that contributions to doyouspeakOCCI itself remain perpetually free,
the code has been developed under the [GNU General Public License, Version 3](http://www.gnu.org/licenses/gpl-3.0.html).
The documentation coming with doyouspeakocci is available under a
[Creative Commons Attribution Share-Alike 3.0 License](http://creativecommons.org/licenses/by-sa/3.0/).

### Issues
If you think that you have discovered a bug in doyouspeakOCCI, or you would like to see
an additional feature in the future, please use the
[doyouspeakOCCI GitHub Tracker](https://github.com/irf/doyouspeakocci/issues) to submit an issue.

### Patches
You are welcome to contribute code for any kind of recorded issue. However, patches
via email are not accepted. Rather than that, please [fork](http://help.github.com/fork-a-repo/)
our repository, commit the patch, and send us a [pull request](http://help.github.com/send-pull-requests/)
&mdash;we will then have a look at it. Remember to add a link to the issue you aim to fix.
