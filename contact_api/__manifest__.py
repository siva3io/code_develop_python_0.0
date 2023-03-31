# -*- coding: utf-8 -*-
{
    'name': "Contact API",

    'summary': """
        Module for APIs for contacts""",

    'description': """
        This module will contain all the APIs related to Contact.
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
    'depends': ['base', 'eunibase_api'],

    # always loaded
    'data': [
        # 'security/ir.model.access.csv',
        # 'views/views.xml',
    ],
    # only loaded in demonstration mode
    'demo': [],
}
