# -*- coding: utf-8 -*-
from odoo import models, fields


class ProductTemplateCategoryChannel(models.Model):
    _name = 'product.template.category.channel'
    _description = 'Product Template Category Channel'

    name = fields.Char(string='Name')
    active = fields.Boolean(string='Active', default=False)
    reviewed = fields.Boolean(string='Reviewed', default=False)
    parent_category_id = fields.Many2one(string='Parent Category', comodel_name='product.template.category.channel')
    child_category_ids = fields.One2many(string='Child Categories', comodel_name='product.template.category.channel',
                                         inverse_name='parent_category_id')
    category_id = fields.Many2one(string='Eunimart Category', comodel_name='product.template.category')
    channel_id = fields.Many2one(string='Channel', comodel_name='marketplace')
    actual_category_path = fields.Char(string='Actual Category Path')
    description = fields.Text(string='Description')
    actual_id = fields.Integer(string='Actual Id')
