# -*- coding: utf-8 -*-

from odoo import models, fields, api
from . import json_field


class CatalogueTemplateMarketplace(models.Model):
    _name = 'catalogue.template.marketplace'
    _description = 'Catalogue Template Marketplace'

    name = fields.Char(string='Name')
    marketplace_id = fields.Many2one(string='Marketplace', comodel_name='marketplace')
    catalogue_id = fields.Many2one(string='Catalogue', comodel_name='catalogue.template')
    template_json_internal = json_field.JsonField(string='Template Json Internal')
    template_json_external = json_field.JsonField(string='Template Json External')
    data_schema = fields.Text(string='Data_Schema', help='To store the default schema structure.')
