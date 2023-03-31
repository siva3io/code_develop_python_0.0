# -*- coding: utf-8 -*-

from odoo import models, fields, api
from datetime import datetime


class PurchaseModule(models.Model):
    _inherit = 'purchase.order.line'

    discount_type = fields.Selection(string='Discount', selection=[('percentage', 'Percentage'), ('flat', 'Flat')])
    discount = fields.Integer(string='Discount Amount')


class PurchaseOrderModel(models.Model):
    _inherit = 'purchase.order'

    sale_id = fields.Many2one(comodel_name='sale.order', string='Sale_id', required=False)
    external_notes = fields.Text(string='External notes', required=False)
    date_planned = fields.Datetime(string='Scheduled Date', required=True, index=True, oldname='minimum_planned_date',
                                   compute=False, default=datetime.now())

#     name = fields.Char()
#     value = fields.Integer()
#     value2 = fields.Float(compute="_value_pc", store=True)
#     description = fields.Text()
#
#     @api.depends('value')
#     def _value_pc(self):
#         for record in self:
#             record.value2 = float(record.value) / 100
