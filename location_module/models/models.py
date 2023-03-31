# -*- coding: utf-8 -*-

from odoo import models, fields, api


class LocationModule(models.Model):
    _inherit = 'stock.location'
    # _name = 'location_module.location_module'
    # _description = 'location_module.location_module'

    landmark = fields.Text(string='Landmark', required=False)
    latitude = fields.Float(string='Latitude', required=False)
    longitude = fields.Float(string='Longitude', required=False)
    external_id = fields.Integer(string='External ID', required=False)
    external_url = fields.Text(string='External URL', required=False)
    external_salt = fields.Text(string='External Salt', required=False)
    incharge_name = fields.Text(string='Incharge Name', required=False)


#     name = fields.Char()
#     value = fields.Integer()
#     value2 = fields.Float(compute="_value_pc", store=True)
#     description = fields.Text()
#
#     @api.depends('value')
#     def _value_pc(self):
#         for record in self:
#             record.value2 = float(record.value) / 100
