#!/usr/bin/env python3
# -*- coding:utf-8 -*-
########################################################################################################################
# This file is a part of Jeyriku.net.
#
# Created: 01.08.2025 19:44:29
# Author: Jeremie Rouzet
#
# Last Modified: 01.08.2025 19:44:38
# Modified By: Jeremie Rouzet
#
# Copyright (c) 2025 Jeyriku.net
########################################################################################################################
from django.urls import path
from . import views

urlpatterns = [
    path('', views.ip_scan_view, name='ip_scan'),
]
