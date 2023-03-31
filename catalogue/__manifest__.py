# -*- coding: utf-8 -*-
{
    'name': "catalogue",
    'version': '1.0',
    'summary': "Catalogue Template along with marketplace",
    'description': "",
    'author': "My Company",
    'website': "http://www.yourcompany.com",
    'category': 'Inventory/Inventory',
    'sequence': 2,
    'depends': ['base', 'product', 'stock'],
    'data': [
        'security/ir.model.access.csv',
        'views/catalogue_actions.xml',
        'views/catalogue_menu.xml',
        'views/views.xml',
        'views/templates.xml',
    ],
    'assets': {
        'web.assets_backend': [
            'catalogue/static/src/js/backend/json_field.js',
        ],
    },
    'demo': [],
    'installable': True,
    'application': True,
    'auto_install': False,
    'license': 'LGPL-3',
}
