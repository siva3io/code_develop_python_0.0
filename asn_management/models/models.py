# -*- coding: utf-8 -*-

from odoo import models, fields, api


class ASNModule(models.Model):
    _name = 'asn.asn'
    _description = 'asn management'

    name = fields.Char(string='Asn_name', required=False)
    asn_number = fields.Char(string='Asn_number', required=False)
    validity_date = fields.Datetime(string='Validity Date', required=False)
    estimated_delivery_date = fields.Datetime(string='Estimated delivery Date', required=False)
    drop_location_id = fields.Many2one(comodel_name='stock.location', string='Drop_location_id', required=False)
    pickup_location_id = fields.Many2one(comodel_name='stock.location', string='Pickup_location_id', required=False)
    picking_id = fields.Many2one(comodel_name='stock.picking', string='Picking_id', required=False)
    purchase_id = fields.Many2one(comodel_name='purchase.order', string='Purchase_id', required=False)
    line_ids = fields.One2many(comodel_name='asn.asn.line', inverse_name='asn_id', string='Line_ids', required=False)
    state = fields.Selection(string='Status', selection=[('draft', 'Draft'), ('sent', 'Sent')])
    location_id = fields.Many2one(comodel_name='stock.location', string='location_id', required=False)


class ASNLineModule(models.Model):
    _name = 'asn.asn.line'
    _description = 'asn line management'

    name = fields.Char(string='Name', required=False)
    product_id = fields.Many2one(comodel_name='product.product', string='product_id', required=True)
    asn_id = fields.Many2one(comodel_name='asn.asn', string='Asn_id', required=False)
    requested_quantity = fields.Integer(string='Requested Quantity', required=False)
    received_quantity = fields.Integer(string='Received Quantity', required=False)
    returned_quantity = fields.Integer(string='Returned Quantity', required=False)
    scrap_quantity = fields.Integer(string='Scrap Quantity', required=False)
    remaining_quantity = fields.Integer(string='Remaining Quantity', required=False)


#     name = fields.Char()
#     value = fields.Integer()
#     value2 = fields.Float(compute="_value_pc", store=True)
#     description = fields.Text()
#
#     @api.depends('value')
#     def _value_pc(self):
#         for record in self:
#             record.value2 = float(record.value) / 100
