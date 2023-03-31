# -*- coding: utf-8 -*-
from odoo import models, fields, api


class ProductTemplateCategory(models.Model):
    _name = 'product.template.category'
    _description = 'Product Template Category'

    name = fields.Char(string='Name')
    active = fields.Boolean(string='Active', default=False)
    code = fields.Char(string='Code')
    reviewed = fields.Boolean(string='Reviewed', default=False)
    parent_category_id = fields.Many2one(string='Parent Category', comodel_name='product.template.category')
    child_category_ids = fields.One2many(string='Child Categories', comodel_name='product.template.category',
                                         inverse_name='parent_category_id')
    channel_category_ids = fields.One2many(string='Channel Categories',
                                           comodel_name='product.template.category.channel',
                                           inverse_name='category_id')
    marketplace_id = fields.Many2one(string='Marketplace', comodel_name='marketplace')
    product_category_ids = fields.One2many(string='Product Category', comodel_name='product.category',
                                           inverse_name='product_template_category_id')
    description = fields.Text(string='Description')
    actual_id = fields.Integer(string='Actual Id')
    # stats = fields.TBD(string='Stats')
