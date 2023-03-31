# -*- coding: utf-8 -*-

from odoo import models, fields, api


class GRNModule(models.Model):
    _inherit = 'stock.picking'

    asn_ids = fields.Many2one(comodel_name='asn.asn', string='Asn_ids', required=False)
    channel = fields.Char(string='Channel', required=False)
    date = fields.Datetime(string='Date', required=False)
    reason = fields.Text(string='Reason', required=False)
    returns_ids = fields.Many2one(comodel_name='fims.rom', string='Return ids', required=False)
    # picking_ids = fields.Many2one(comodel_name='stock.picking', string="Internal Stock Transfer", required=False
    grn_ids = fields.Many2one(comodel_name='stock.picking', string='GRN ids', required=False)
    requested_quantity = fields.Many2one(comodel_name='asn.asn.line', string='ordered_quantity', required=False)
    return_quantity = fields.Many2one(comodel_name='rom.product.lines', string='return_quantity', required=False)
    validity_date = fields.Datetime(comodel_name='asn.asn', string='Validity Date', required=False)
