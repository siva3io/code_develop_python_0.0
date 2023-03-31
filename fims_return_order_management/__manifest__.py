# -*- coding: utf-8 -*-
###############################################################################
#
# Fortutech IMS Pvt. Ltd.
# Copyright (C) 2016-TODAY Fortutech IMS Pvt. Ltd.(<http://www.fortutechims.com>).
#
###############################################################################
{
    'name': 'Return Order Management (ROM)',
    'category': 'stock',
    'summary': 'This module allow you return product, refund amount, or repair product.',
    'version': '15.0.1.0.0',
    'license': 'OPL-1',
    'description': """This module allow you return product, refund amount, or repair product.""",
    'depends': ['sale', 'delivery', 'account', 'portal', 'purchase'],
    'author': 'Fortutech IMS Pvt. Ltd.',
    'website': 'https://www.fortutechims.com',
    'data': [
        'security/ir.model.access.csv',
        'views/fims_rom_view.xml',
        'datas/data.xml',
        'report/rom_report.xml',
        'report/rom_report_template.xml',
    ],
    "price": 49.0,
    "currency": "EUR",
    "installable": True,
    "application": True,
    "auto_install": False,
    "images": ['static/description/banner.png'],
}
