# -*- coding: utf-8 -*-

from odoo import models, fields, api
from . import json_field


class CatalogueTemplateLines(models.Model):
    _name = 'catalogue.template.lines'
    _description = 'Catalogue Template Lines'

    name = fields.Char(string='Name')
    catalogue_id = fields.Many2one(string='Catalogue', comodel_name='catalogue.template')
    type = fields.Selection(string='Type',
                            selection=[('boolean', 'Boolean'), ('integer', 'Integer'), ('float', 'Float'),
                                       ('char', 'Char'), ('selection', 'Selection'), ('html', 'Html'),
                                       ('datetime', 'Datetime'), ('text', 'Text/Json')], default='char')
    marketplace_line_ids = fields.One2many(string='Marketplace Lines',
                                           comodel_name='catalogue.template.line.marketplace', inverse_name='line_id')
    code = fields.Char(string='Code')
    active = fields.Boolean(string='Active')
    attribute_description = fields.Text(string='Attribute Description')
    attribute_validation_regex = fields.Char(string='Attribute Validation RegEx')
    catalogue_template_section_id = fields.Many2one(string='Section', comodel_name='catalogue.template.section')
    product_template_category_id = fields.Many2one(string='Product Template Category',
                                                   comodel_name='product.template.category')
    allowed_values = json_field.JsonField(string='Allowed Values', help="All allowed values in json format")
    possible_keywords = fields.Char(string='Possible Keywords')
    is_reviewed = fields.Boolean(string='Reviewed')
    sequence = fields.Integer(string='Sequence')
    is_searchable = fields.Boolean(string='Searchable')
    is_predictable = fields.Boolean(string='Predictable')
    is_mandatory = fields.Boolean(string='Mandatory')
    mandatory_type = fields.Selection(string='Mandatory Type',
                            selection=[('mandatory_critical', 'Mandatory Critical'), ('mandatory_informational', 'Mandatory Informational'), ('optional_informational', 'Optional Informational'), ('none','None')], default='none')
    algo_code = fields.Char(string='Algo Code')
    python_code = fields.Text(string='Python Code')
    domain = fields.Char(string='Domain', default='[]')
    json_code = json_field.JsonField(string='Json Code')
