#!/usr/bin/env python
# ---*< bitly_grinder/bitly_grinder.py >*-------------------------------------
# Copyright (C) 2011 st0w
# 
# This module is part of project and is released under the MIT License.
# Please see the LICENSE file for details.

"""Grinds random bit.ly URLs looking for interesting info

Created on Oct 22, 2011

By default, will follow sequential URLs.  This is to allow for starting
and stopping without hitting the same URL twice.

Works recursively.  Start with a URL, it keeps following redirects until
getting something other than 301/302.  This will be inaccurate when
loading a site, thus reaching the final URL, which then redirects based
on User-Agent, javascript, or anything else.  This should be cleaned up.

bit.ly URLs are case sensitive, which significantly increases the search
space.

tinyurl.com short URLs are not case sensitive.

Need to have a schema for representing a shortening service - one that
allows for defining things like case sensitivity, length, format, etc.

"""
# ---*< Standard imports >*---------------------------------------------------
from random import choice
import sys
import urllib2

# ---*< Third-party imports >*------------------------------------------------

# ---*< Local imports >*------------------------------------------------------
from db import init_db_conn, get_result, save_result
from models import BitlyUrl

# ---*< Initialization >*-----------------------------------------------------
# List of ASCII values to try in URLs - all digits, lower + uppercase alpha
CHARSET = range(48, 58) + range(65, 91) + range(97, 123)
USER_AGENTS = [
    'Mozilla/5.0 (Windows; U; Windows NT 5.1; de; rv:1.9.2.3) Gecko/20100401 '
    'Firefox/3.6.3 (FM Scene 4.6.1)',

    'Mozilla/4.0 (compatible; MSIE 5.0; Windows ME) Opera 5.11 [en]',

    'Mozilla/5.0 (Windows; U; Windows NT 5.1; en-US; rv:1.9.0.1) '
    'Gecko/2008092215 Firefox/3.0.1 Orca/1.1 beta 3',

    'Mozilla/5.0 (Macintosh; U; PPC Mac OS X; en-US) AppleWebKit/xx '
    '(KHTML like Gecko) OmniWeb/v5xx.xx',

    '',
]


# ---*< Code >*---------------------------------------------------------------
class RedirectHandler(urllib2.HTTPRedirectHandler, object):
    """Override HTTP redirections, so we can track redirection path
    
    """
    path = None

    def reset(self):
        self.path = []

    def redirect_request(self, req, fp, code, msg, hdrs, newurl):

        if len(self.path) == 0:
            self.path.append(req.get_full_url())

        self.path.append(newurl)
        res = super(RedirectHandler, self).redirect_request(req, fp, code,
                                                            msg, hdrs, newurl)

        return res


def resolve_url(url):
    """Resolves a URL to its final destination URL
    
    This will rescursively call itself until the status is anything
    other than 301 or 302.
    
    :param url: `string` containing the URL to resolve
    :rtype: `BitlyUrl` object representing the lengthened short URL

    """
    headers = {
        'User-Agent': choice(USER_AGENTS),
    }
    longener = BitlyUrl(
        status=1,
        path=[url, ],
        content_type='Unknown',
    )

    resp = None

    print '=== %s ===' % url
    req = urllib2.Request(url, headers=headers)
    redirect = RedirectHandler()
    redirect.reset()
    opener = urllib2.build_opener(redirect)

    try:
        resp = opener.open(req)
        longener.status = resp.getcode()
        longener.content_type = resp.headers.type

    except urllib2.HTTPError, e:
        if e.code in (410,):
            e.code = 404

        longener.status = e.code

        if longener.status not in (301, 302, 400, 401, 403, 404, 406,
                                   500, 502, 503, 504):
            """Raise if don't know how to handle"""
            raise e

    except urllib2.URLError, e:
        if e.reason.errno == 60:
            """Timed out
            
            So technically, this isn't a 504 (gateway timeout), but it's
            the closest 
            """
            longener.status = 504

        elif e.reason.errno in (51, 54, 61):
            """
            51 = Network unreachable
            54 = Connection reset by peer
            61 = Connection refused
            
            Treat it as 'service unavailable' - close enough
            """
            longener.status = 503

        elif e.reason.errno == 8:
            """DNS fail"""
            longener.status = 503

        else:
            print 'urlerror ', e.reason.errno, e
            raise urllib2.URLError(e)

    # Only attempt to set the longener path if there's stuff there
    if len(redirect.path) > 0:
        print 'setting it'
        longener.path = redirect.path

    print 'Final path: ', longener.path

    return longener


def main(url, resolve_dupes=True):
    """Simple wrapper, just calls the resolver for now
    
    Drops the last letter of the passed `url` and then grabs all URLs
    that start with the remaining `string`
    
    :param url: `string` of the base URL to start with
    :param resolve_dupes: `Boolean` whether or not to re-process
                          existing entries.
    :rtype: None
    
    """
    db = init_db_conn()

    base_url = url[:-2]
    for i in CHARSET:
        for j in CHARSET:
            url = '%s%s%s' % (base_url, chr(i), chr(j))

            # If skipping existing entries, check for this URL and skip
            # if we already have it
            if not resolve_dupes:
                existing = get_result(db, url)

                if existing:
                    continue

            bitly = resolve_url(url)

            if bitly.status != 404:
                sys.stdout.write('%s\t%s\n' % (bitly.content_type,
                                               bitly.path[-1]))

            save_result(db, bitly)


if __name__ == "__main__":

    if len(sys.argv) != 2:
        sys.stderr.write('Usage: %s url\n' % sys.argv[0])
        sys.exit(1)

    main(sys.argv[1], resolve_dupes=False)

__all__ = ()
