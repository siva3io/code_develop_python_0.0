# -*- coding: utf-8 -*-

from odoo import models, fields, api
from . import json_field


class CatalogueTemplateLineMarketplace(models.Model):
    _name = 'catalogue.template.line.marketplace'
    _description = 'Catalogue Template Line Marketplace'

    name = fields.Char(string='Name')
    marketplace_display_name = fields.Char(string='Marketplace Display Name')
    line_id = fields.Many2one(string='Line', comodel_name='catalogue.template.lines')
    type = fields.Selection(string='Type',
                            selection=[('boolean', 'Boolean'), ('integer', 'Integer'), ('float', 'Float'),
                                       ('char', 'Char'), ('selection', 'Selection'), ('html', 'Html'),
                                       ('datetime', 'Datetime'), ('text', 'Text/Json')], default='char')
    code = fields.Char(string='Code')
    attribute_description = fields.Text(string='Attribute Description')
    attribute_validation_regex = fields.Char(string='Attribute Validation RegEx')
    mapped_field = fields.Char(string='Mapped Field')
    cosine_similarity = fields.Float(string='Cosine Similarity')
    product_template_category_id = fields.Many2one(string='Category', comodel_name='product.template.category')
    allowed_values = json_field.JsonField(string='Allowed Values', help="All allowed values in json format")
    allowed_values_list = fields.Char(string='Allowed Values List')
    possible_keywords = fields.Char(string='Possible Keywords')
    sequence = fields.Integer(string='Sequence')
    is_channel_specific = fields.Boolean(string='Channel Specific')
    is_searchable = fields.Boolean(string='Searchable')
    is_predictable = fields.Boolean(string='Predictable')
    algo_code = fields.Char(string='Algo Code')
    python_code = fields.Text(string='Python Code')
    domain = fields.Char(string='Domain', default='[]')
    marketplace_id = fields.Many2one(string='Marketplace', comodel_name='marketplace')
    marketplace_code = fields.Char(string='Marketplace Code')
    json_code = json_field.JsonField(string='Json Code')
    active = fields.Boolean(string='Active')
    is_mandatory = fields.Boolean(string='Mandatory')
    mandatory_type = fields.Selection(string='Mandatory Type',
                            selection=[('mandatory_critical', 'Mandatory Critical'), ('mandatory_informational', 'Mandatory Informational'), ('optional_informational', 'Optional Informational'), ('none','None')], default='none')
    json_identifier = fields.Char(string='Json Identifier')
    use_parent_json_identifier = fields.Boolean(string='Use Parent Json Identifier')
    
    @api.model
    def _cron_sync_mandatory_type_line_id(self):
        for rec in self:
            rec.line_id.mandatory_type = rec.mandatory_type
