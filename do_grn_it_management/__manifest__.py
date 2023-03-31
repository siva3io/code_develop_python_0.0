# -*- coding: utf-8 -*-
{
    'name': "e_do_grn_it_management",

    'summary': """
        Delivery Order, Internal Transfers, GRN""",

    'description': """
        Delivery Order, Internal Transfers, GRN
    """,

    'author': "Eunimart",
    'website': "https://eunimart.com/",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/14.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Inventory',
    'version': '15.0.1.0.0',

    # any module necessary for this one to work correctly
    'depends': ['base', 'stock', 'asn_management', 'sale', 'purchase', 'fims_return_order_management'],

    # always loaded
    'data': [
        # 'security/ir.model.access.csv',
        'views/views.xml',
        'views/templates.xml',
    ],
    # only loaded in demonstration mode
    'demo': [],
}
