# -*- coding: utf-8 -*-

from odoo import models, fields, api


class CatalogueTemplateSection(models.Model):
    _name = 'catalogue.template.section'
    _description = 'Catalogue Template Section'

    name = fields.Char(string='Name', required=True)
    sequence = fields.Integer(string='Sequence')
    product_template_category_id = fields.Many2one('product.template.category', string='Product Template Category')
    catalogue_template_lines_ids = fields.One2many('catalogue.template.lines', 'catalogue_template_section_id',
                                                   string='Catalogue Template Lines')
    catalogue_template_id = fields.Many2one('catalogue.template', string='Catalogue Template')
    active = fields.Boolean(string='Active', default=True)
    description = fields.Text(string='Description')
