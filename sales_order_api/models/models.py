# -*- coding: utf-8 -*-

from odoo import models, fields, api


class SalesOrderModule(models.Model):
    _inherit = 'sale.order.line'

    vendor_id = fields.Many2one(comodel_name='res.partner', string='Vendor_id', required=False)
    discount_type = fields.Selection(string='Discount', selection=[('percentage', 'percentage'), ('flat', 'Flat')])
    discount_amount = fields.Integer(string='Discount Amount')
    # id = fields.Integer(comodel_name='sale.order.line', string='Order_line_id', required=False)
