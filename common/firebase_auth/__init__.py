#!-*- coding: utf-8 -*-
"""
Authentication backend for handling firebase user.idToken from incoming
Authorization header, verifying, and locally authenticating

Authors: ['César Benjamín García Martínez <mathereall@gmail.com>', ]

License: Apache 2.0

This package is a fork of drf-firebase-auth
with some fixes and improvements.
This package also adds support for login
with email and password, and also adds support for
custom user models.

"""

__title__ = 'firebase_auth'
__version__ = '24.5.3'
__description__ = (
    'Custom Django Rest Framework authentication backend for '
    'parsing Firebase uid tokens and storing as local users.'
    'This package is a fork of django-firebase-auth '
    'with some fixes and improvements. '
    'This package also adds support for login '
    'with email and password, and also adds support for '
    'custom user models. And is fully integrated with idmty.'
)
__url__ = 'https://github.com'
__author__ = 'César Benjamín García Martínez'
__author_email__ = 'mathereall@gmail.com'
__license__ = 'Apache 2.0'
VERSION = __version__
