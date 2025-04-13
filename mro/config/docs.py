# -*- coding: utf-8 -*-
# Copyright (c) 2021, Ed Harrison and Contributors
# See license.txt
"""Configuration for docs."""

from __future__ import unicode_literals


source_link = "https://github.com/h84ed/mro"
docs_base_url = "https://h84ed.github.io/mro"
headline = "Functionality centered around inventory, specific to aviation industry: Maintenance, Repair and Overhaul"
sub_heading = "TODO_APP_USAGE"


def get_context(context):
    """Returns the application documentation context.

     :param context: application documentation context"""
    context.brand_html = "mro"
    context.source_link = source_link
    context.docs_base_url = docs_base_url
    context.headline = headline
    context.sub_heading = sub_heading
