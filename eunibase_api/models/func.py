# -*- coding: utf-8 -*-

# from odoo.tools import func


def get_many2many_dict(record):
    return [{'id': rec.id, 'name': rec.display_name} for rec in record]


def get_many2one_dict(record):
    return {
        'id': record.id,
        'name': record.display_name,
    }
