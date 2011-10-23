# ---*< bitly_grinder/models.py >*--------------------------------------------
# Copyright (C) 2011 st0w
# 
# This module is part of bit.ly grinder and is released under the MIT License.
# Please see the LICENSE file for details.

"""Data model definitions

Created on Oct 22, 2011

"""
# ---*< Standard imports >*---------------------------------------------------

# ---*< Third-party imports >*------------------------------------------------
from dictshield.document import Document
from dictshield.fields import IntField, ListField, StringField

# ---*< Local imports >*------------------------------------------------------

# ---*< Initialization >*-----------------------------------------------------

# ---*< Code >*---------------------------------------------------------------
class BitlyUrl(Document):
    """Data related to URL shortener resolution
    
    path is a list of URLs encountered in the resolution process
    path[0] is the base URL, and path[-1] will be the final URL
    
    """
    _public_fields = ('base_url', 'resolved_url', 'status', 'path')

#    base_url = StringField(required=True)
#    resolved_url = StringField(required=True)
    status = IntField()
    path = ListField(StringField(), required=True)
    content_type = StringField(required=True)


__all__ = (BitlyUrl)
