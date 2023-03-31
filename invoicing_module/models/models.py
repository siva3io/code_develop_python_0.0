# -*- coding: utf-8 -*-

from odoo import models, fields, api


class InvoicingModule(models.Model):
    _inherit = 'account.move'

    return_order_id = fields.Many2one(comodel_name="fims.rom", string="return_order_id", required=False)
    sale_id = fields.Many2one(comodel_name="sale.order", string="return_order_id", required=False)


class InvoicingLineModule(models.Model):
    _inherit = 'account.move.line'

    discount_type = fields.Selection(string='Discount', selection=[('percentage', 'Percentage'), ('flat', 'Flat')])
    discount = fields.Integer(string='Discount Amount')

#     name = fields.Char()
#     value = fields.Integer()
#     value2 = fields.Float(compute="_value_pc", store=True)
#     description = fields.Text()
#
#     @api.depends('value')
#     def _value_pc(self):
#         for record in self:
#             record.value2 = float(record.value) / 100
