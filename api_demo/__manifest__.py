# -*- coding: utf-8 -*-
{
    'name': "Api Demo",
    'version': '1.1',
    'summary': "Api demo Catalogue Template along with marketplace",
    'description': "",
    'author': "My Company",
    'website': "http://www.yourcompany.com",
    'category': 'Inventory/Inventory',
    'sequence': 2,
    'depends': ['catalogue'],
    'data': [
        'views/templates.xml',
    ],
    'assets': {
        'web.assets_frontend': [
            'catalogue/static/src/js/backend/api_demo.js',
        ],
    },
    'demo': [
        'demo/demo.xml',
    ],
    'installable': True,
    'application': True,
    'auto_install': False,
    'license': 'LGPL-3',
}
