# -*- coding: utf-8 -*-
from odoo import models, fields, api
from . import json_field


class Marketplace(models.Model):
    _name = 'marketplace'
    _description = 'Marketplace'
    _order = 'sequence'

    name = fields.Char(string='Name')
    code = fields.Char(string='Code')
    sequence = fields.Integer(string='Sequence')
    channel_type = fields.Selection(string='Channel Type',
                                    selection=[('webstore', 'Webstore'), ('marketplace', 'Marketplace'),
                                               ('platform', 'Platform')],
                                    default='marketplace')
    product_template_category_ids = fields.One2many(string='Product Template Category',
                                                    comodel_name='product.template.category',
                                                    inverse_name='marketplace_id')
    data_type = fields.Selection(string='Data Type',
                                 selection=[('xlsx', 'XLSX'), ('csv', 'CSV'), ('json', 'JSON'), ('xml', 'XML')])
    api_endpoint = fields.Char(string='Api Endpoint')
    api_salt = fields.Char(string='Api Salt')
    api_secret = fields.Char(string='Api Secret')
    api_user = fields.Char(string='Api User')
    json_auth = json_field.JsonField(string='Json Auth')
    active = fields.Boolean(string='Active')
    sandbox = fields.Boolean(string='Sandbox')
    sandbox_api_endpoint = fields.Char(string='Sandbox Api Endpoint')
    sandbox_api_salt = fields.Char(string='Sandbox Api Salt')
    sandbox_api_secret = fields.Char(string='Sandbox Api Secret')
    sandbox_api_user = fields.Char(string='Sandbox Api User')
    sandbox_json_auth = json_field.JsonField(string='Sandbox Json Auth')
