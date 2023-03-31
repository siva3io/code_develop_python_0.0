# -*- coding: utf-8 -*-
{
    'name': "Eunimart Base API",

    'summary': """
        Base Module for APIs, User and company management""",

    'description': """
        This module will contain all the APIs related to authentication, user management, company management, etc.
    """,

    'author': "Eunimart",
    'website': "https://eunimart.com/",
    'license': 'OPL-1',

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/14.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Uncategorized',
    'version': '15.0.1.0.0',

    # any module necessary for this one to work correctly
    'depends': ['base'],

    # always loaded
    'data': [
        # 'security/ir.model.access.csv',
        'views/views.xml',
        'views/templates.xml',
    ],
    # only loaded in demonstration mode
    'demo': [],
}
