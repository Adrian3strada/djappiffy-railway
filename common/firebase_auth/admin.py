#!-*- coding: utf-8 -*-
"""
Authentication backend for handling firebase user.idToken from incoming
Authorization header, verifying, and locally authenticating

Authors: ['César Benjamín García Martínez <mathereall@gmail.com>', ]
License: Apache 2.0
"""

from django.contrib import admin
from .models import FirebaseUser, FirebaseUserProvider

admin.site.register(FirebaseUser)
admin.site.register(FirebaseUserProvider)
