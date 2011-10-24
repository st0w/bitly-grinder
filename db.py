#!/usr/bin/env python
# ---*< bitly_grinder/db.py >*------------------------------------------------
# Copyright (C) 2011 st0w
# 
# This module is part of bit.ly grinder and is released under the MIT License.
# Please see the LICENSE file for details.

"""DB-related functions

Created on Oct 22, 2011

"""
# ---*< Standard imports >*---------------------------------------------------
import json
try:
    # First try pysqlie2, assuming if it exists, it is newer
    from pysqlite2 import dbapi2 as sqlite3
except:
    import sqlite3

# ---*< Third-party imports >*------------------------------------------------

# ---*< Local imports >*------------------------------------------------------
from models import BitlyUrl

# ---*< Initialization >*-----------------------------------------------------
sqlite3.register_converter('json', json.loads)

# ---*< Code >*---------------------------------------------------------------
def init_db_conn(**kwargs):
    db_conn = sqlite3.connect('bitly-grinder.db',
                              detect_types=sqlite3.PARSE_DECLTYPES
                              | sqlite3.PARSE_COLNAMES)
    db_conn.row_factory = sqlite3.Row # fields by names
    setup_db(db_conn)

    return db_conn


def setup_db(db):
    """Creates SQLite tables if needed
    
    """

    db.execute('''
        CREATE TABLE IF NOT EXISTS
        urls(
            url TEXT PRIMARY KEY,
            content_type TEXT,
            updated TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
            status INTEGER,
            data json
        )
    ''')


# ---*< Internal utility functions >*-----------------------------------------
def _process_results(curs):
    """(Internal use only) Processes DB results and prepares them to return
    
    :param curs: `SQLite3.Cursor` object pointing to results
    :rtype: `list` of `BitlyUrl` objects 
    
    """
    rows = curs.fetchall()
    res = []

    for row in rows:
        row = row['data']
        bitly = BitlyUrl(**row)

        res.append(bitly)

    return res


# ---*< Data retrievers >*----------------------------------------------------
def get_result(db, url):
    """Retrieves data on a given short URL
    
    :param db: `SQLite3` DB handle
    :param url: `string` Short URL to retreive data on
    :rtype: `BitlyUrl` or `None`

    """
    curs = db.execute('''
        SELECT data FROM urls WHERE url=?
    ''', (url,))

    return _process_results(curs)


def get_results_by_content_type(db, content_type, status=None):
    """Returns a list of results that match a given content_type
    
    :param db: `SQLite3` handle to DB
    :param content_type: `string` content-type to match
    :param status: (optional) `int` of status code
    :rtype: `list of resulting `BitlyUrl` objects

    """
    if status:
        try:
            status = int(status)
        except ValueError:
            status = None

    if status:
        curs = db.execute('''
            SELECT data FROM urls WHERE status=? AND content_type like ?
        ''', (status, content_type))
    else:
        print 'durka'
        curs = db.execute('''
            SELECT data FROM urls WHERE content_type like ?
        ''', (content_type,))

    return _process_results(curs)


def get_results(db, exclude_content=None, status=None):
    """Returns a list of all results
    
    :param db: `SQLite3` handle to DB with results
    :param status: (optional) `int` of result status codes to show
    :rtype: `list` of resulting `BitlyUrl` objects
    
    """
    if status:
        try:
            status = int(status)
        except ValueError:
            status = None

    if status and exclude_content:
        curs = db.execute('''
            SELECT data FROM urls WHERE status=? AND content_type<>? 
        ''', (status, exclude_content,))

    elif status:
        curs = db.execute('''
            SELECT data FROM urls WHERE status=? 
        ''', (status,))

    elif exclude_content:
        curs = db.execute('''
            SELECT data FROM urls WHERE content_type<>? 
        ''', (exclude_content,))

    else:
        curs = db.execute('''
            SELECT data FROM urls
        ''')

    return _process_results(curs)


def save_result(db, data, commit=True):
    """Saves a result into the SQLite DB
    
    :param db: `SQLite3` DB handle
    :param data: `BitlyUrl` object to save
    :param commit: `Boolean` indicating whether or not to commit.  If
                   performing a large batch of operations, it's
                   significantly quicker to set this to False and then
                   just commit it yourself. 
    :rtype: None 
    
    """
    if not isinstance(data, BitlyUrl):
        raise ValueError('data passed to save_results() must be of type'
                         'BitlyUrl')

    curs = db.cursor()
    data.validate()

    try:
        curs.execute('''
            INSERT OR REPLACE INTO urls (url, status, content_type, data)
            VALUES (?, ?, ?, ?)
        ''', (data.path[0].encode('utf-8'), data.status, data.content_type,
              data.to_json().encode('utf-8')))

    except UnicodeDecodeError:
        """Unicode fail... will have to handle this properly at some point"""
        print 'Unicode fail'
        pass

    else:
        if commit:
            db.commit()



__all__ = (init_db_conn, save_result)

