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

# List of ASCII values to try in URLs - all digits, lower + uppercase alpha
CHARSET = range(48, 58) + range(65, 91) + range(97, 123)


# ---*< Code >*---------------------------------------------------------------
def resolve_url(db, url):
    """Resolves a URL to its final destination URL
    
    This will rescursively call itself until the status is anything
    other than 301 or 302.
    
    :param db: `SQLite3` db handle
    :param url: `string` containing the URL to resolve
    :rtype: `tuple` in the format (`int`, `string`, `string`, file-like
            object, as returned by `urllib2.urlopen()`).
            The `int` is the status code returned when requesting the
            final URL in the resolution process.
            
            The first `string` is the initially-requested URL.
            
            The second `string` is the final URL in the resolution
            process.
            
            The last object is the file-like object returned by
            `urllib2.urlopen()`

    """
    headers = {
        'User-Agent': choice(USER_AGENTS),
    }

    req = urllib2.Request(url, headers=headers)

    try:
        resp = urllib2.urlopen(req)
    except urllib2.HTTPError, e:
        return (e.code, url, url, None)

    if resp.getcode() in (301, 302):
        print 'recursing'
        return resolve_url(db, resp.geturl())

    return (resp.getcode(), url, resp.geturl(), resp)


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
            bitly = BitlyUrl(base_url='%s%s%s' % (base_url, chr(i), chr(j)))

            # If skipping existing entries, check for this URL and skip
            # if we already have it
            if not resolve_dupes:
                existing = get_result(db, bitly.base_url)

                if existing:
                    continue

            try:
                (bitly.status,
                 bitly.base_url,
                 bitly.resolved_url, resp) = resolve_url(db, bitly.base_url)
            except urllib2.URLError:
                """If URL is invalid, just skip it"""
                continue

            if resp:
                bitly.content_type = resp.headers.type
            else:
                bitly.content_type = 'Unknown'

            if bitly.status != 404:
                sys.stdout.write('%s\t%s\n' % (bitly.content_type,
                                               bitly.resolved_url))
    #            sys.stdout.write('%d %s\t-> %s\n' % (bitly.status, bitly.base_url,
    #                                             bitly.resolved_url))

            save_result(db, bitly)


if __name__ == "__main__":

    if len(sys.argv) != 2:
        sys.stderr.write('Usage: %s url\n' % sys.argv[0])
        sys.exit(1)

    main(sys.argv[1], resolve_dupes=False)

__all__ = ()
