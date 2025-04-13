# -*- coding: utf-8 -*-
# Copyright (c) 2021, Ed Harrison and Contributors
# See license.txt
"""Configuration for desktop."""

from __future__ import unicode_literals

from frappe import _


def get_data():
    """Returns the application desktop icons configuration."""
    return [
        {
            "module_name": "mro",
            "color": "grey",
            "icon": "octicon octicon-file-directory",
            "type": "module",
            "label": _("MRO")
        }
    ]
