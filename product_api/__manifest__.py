# -*- coding: utf-8 -*-
{
    'name': "product_api",

    'summary': """
        Base Module for Product related APIs""",

    'description': """
        This module will contain all the APIs related to Product, etc.
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
    'depends': ['base', 'product', 'eunibase_api', 'stock'],

    # always loaded
    'data': [
        'views/brand_views.xml',
        'views/views.xml',
        'security/ir.model.access.csv',
    ],
    # only loaded in demonstration mode
    'demo': [],
}
