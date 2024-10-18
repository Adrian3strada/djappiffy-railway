#!-*- coding: utf-8 -*-
"""
Authentication backend for handling firebase user.idToken from incoming
Authorization header, verifying, and locally authenticating

Authors: ['César Benjamín García Martínez <mathereall@gmail.com>', ]
License: Apache 2.0
"""

import os
from django.conf import settings
from rest_framework.settings import APISettings
from .utils import map_firebase_uid_to_username
import logging
from . import __title__
import json

log = logging.getLogger(__title__)

FIREBASE_AUTH_CONFIG = getattr(settings, 'FIREBASE_AUTH_CONFIG', None)

DEFAULT_FIREBASE_AUTH_CONFIG = {
    # allow creation of new local user in db
    'FIREBASE_CREATE_LOCAL_USER': os.getenv('FIREBASE_CREATE_LOCAL_USER', True),
    # attempt to split firebase user.display_name and set local user, first_name and last_name
    'FIREBASE_ATTEMPT_CREATE_WITH_DISPLAY_NAME': os.getenv('FIREBASE_ATTEMPT_CREATE_WITH_DISPLAY_NAME',False),
    # Authorization header prefix, commonly JWT or Bearer (e.g. Bearer <token>)
    'FIREBASE_AUTH_HEADER_PREFIX': os.getenv('FIREBASE_AUTH_HEADER_PREFIX', 'Bearer'),
    # verify that JWT has not been revoked
    'FIREBASE_CHECK_JWT_REVOKED': os.getenv('FIREBASE_CHECK_JWT_REVOKED', True),
    # require that firebase user.email_verified is True
    'FIREBASE_AUTH_EMAIL_VERIFICATION': os.getenv('FIREBASE_AUTH_EMAIL_VERIFICATION', False),
    # function should accept firebase_admin.auth.UserRecord as argument and return str
    'FIREBASE_USERNAME_MAPPING_FUNC': map_firebase_uid_to_username,
    # Project ID and Service Account Keyfile JSON: Loads json from env var or gets object from settings
    'FIREBASE_AUTH_PROJECTS':  getattr(settings, 'FIREBASE_AUTH_PROJECTS', []),
}

# List of settings that may be in string import notation. Used only for compatibility.
IMPORT_STRINGS = ()

api_settings = APISettings(FIREBASE_AUTH_CONFIG, DEFAULT_FIREBASE_AUTH_CONFIG, IMPORT_STRINGS)
