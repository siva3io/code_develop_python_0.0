# -*- coding: utf-8 -*-

from odoo import models, fields


class CatalogueTemplate(models.Model):
    _name = 'catalogue.template'
    _description = 'Catalogue Template'

    name = fields.Char(string='Name')
    active = fields.Boolean(string='Active')
    product_ids = fields.One2many(string='Products', comodel_name='product.product', inverse_name='catalogue_id')
    line_ids = fields.One2many(string='Lines', comodel_name='catalogue.template.lines', inverse_name='catalogue_id')
    # data_ids = fields.One2many(string='Data', comodel_name='catalogue.template.data', inverse_name='catalogue_id')
    marketplace_ids = fields.One2many(string='Marketplaces', comodel_name='catalogue.template.marketplace',
                                      inverse_name='catalogue_id')
    category_id = fields.Many2one(string='Category', comodel_name='product.template.category')
