# -*- coding: utf-8 -*-

from odoo import models, fields
from . import json_field


class Product(models.Model):
    _inherit = 'product.product'

    catalogue_id = fields.Many2one(string='Catalogue', comodel_name='catalogue.template')
    product_parameters = json_field.JsonField(string='Json Product Params')
    image_urls = fields.Text(string='Image Urls', help="Comma separated list of image urls")
    description = fields.Text(string='Description')
    dimensions = json_field.JsonField(string='Dimensions')
    attribute_ids = fields.Many2many(string='Attributes', comodel_name='attribute.value.data')
    brand = fields.Char(string='Brand')
    condition_type = fields.Selection(string='Condition Type', selection=[('new', 'New'), ('used', 'Used')])
    # price = fields.Float(string='Price')
    user_id = fields.Many2one(string='User', comodel_name='res.users')
    sku_id = fields.Char(string='SKU')


class ProductCategory(models.Model):
    _inherit = 'product.category'

    bulk_upload_excel_upload = fields.Binary(string='Bulk-Upload Excel')
    product_template_category_id = fields.Many2one(string='Product Template Category',
                                                   comodel_name='product.template.category')


class ProductTemplate(models.Model):
    _inherit = 'product.template'

    template_category_id = fields.Many2one(string='Category', comodel_name='product.template.category')
    sku_id = fields.Char(string='SKU')
