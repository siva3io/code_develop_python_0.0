# -*- coding: utf-8 -*-

from odoo import models, fields


class AttributeCategoryTemplate(models.Model):
    _name = 'attribute.category.template'
    _description = 'Attribute Category Template'

    name = fields.Char(string='Name', required=True)
    active = fields.Boolean(string='Active', default=True)
    user_ids = fields.Many2many('res.users', string='Users')
    is_global = fields.Boolean(string='Is Global', default=False)


class AttributeCategoryData(models.Model):
    _name = 'attribute.category.data'
    _description = 'Attribute Category Data'

    name = fields.Char(string='Name', required=True)
    active = fields.Boolean(string='Active', default=True)
    att_category_template_id = fields.Many2one('attribute.category.template', string='Attribute Category Template')
    product_template_id = fields.Many2one('product.template', string='Product Template')
    user_ids = fields.Many2many('res.users', string='Users')
    is_global = fields.Boolean(string='Is Global', default=False)


class AttributeValueTemplate(models.Model):
    _name = 'attribute.value.template'
    _description = 'Attribute Value Template'

    name = fields.Char(string='Name', required=True)
    active = fields.Boolean(string='Active', default=True)
    user_ids = fields.Many2many('res.users', string='Users')
    att_category_template_id = fields.Many2one('attribute.category.template', string='Attribute Category Template')


class AttributeValueData(models.Model):
    _name = 'attribute.value.data'
    _description = 'Attribute Value Data'

    name = fields.Char(string='Name', required=True)
    active = fields.Boolean(string='Active', default=True)
    user_id = fields.Many2one('res.users', string='User')
    att_val_template_id = fields.Many2one('attribute.value.template', string='Attribute Value Template')
    att_cat_data_id = fields.Many2one('attribute.category.data', string='Attribute Category Data')

