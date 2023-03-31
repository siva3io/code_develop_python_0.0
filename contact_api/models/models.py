# -*- coding: utf-8 -*-

from odoo import models, fields
from odoo.addons.eunibase_api.models import func


class Partner(models.Model):
    _inherit = 'res.partner'

    first_name = fields.Char(string='First Name')
    last_name = fields.Char(string='Last Name')
    # individual_company_name = fields.Char(string='Individual Company Name')
    location_name = fields.Char(string='Location Name')
    street3 = fields.Char(string='Street 3')
    landmark = fields.Char(string='Landmark')
    gstin_number = fields.Char(string='GSTIN Number')
    date_of_birth = fields.Date(string='Date of Birth')
    emergency_contact = fields.Char(string='Emergency Contact')
    additional_information = fields.Text(string='Additional Information')
    custom_field = fields.Char(string='Custom Field')
    custom_field_details = fields.Text(string='Custom Field Details')

    # bank details
    bank_acc_number = fields.Char(string='Bank Account Number')
    bank_name = fields.Char(string='Bank Name')
    upi_id = fields.Char(string='UPI ID')
    bank_account_name = fields.Char(string='Bank Account Name')
    ifsc_code = fields.Char(string='IFSC Code')

    is_address = fields.Boolean(string='Is Address', default=True)
    contact_name = fields.Char(string='Contact Person Name')

    def api_address_read(self):
        return {
            "id": self.id,
            "location_name": self.location_name,
            "type": self.type,
            "street": self.street,
            "street2": self.street2,
            "street3": self.street3,
            "landmark": self.landmark,
            "zip": self.zip,
            "country_id": func.get_many2one_dict(self.country_id),
            "state_id": func.get_many2one_dict(self.state_id),
            "city": self.city,
            "gstin_number": self.gstin_number,
            "name": self.name,
            "phone": self.phone
        }

    def api_contact_read(self):
        return {
            "id": self.id,
            "company_type": self.company_type,
            "first_name": self.first_name,
            "last_name": self.last_name,
            "name": self.name,
            "email": self.email,
            "parent_id": func.get_many2one_dict(self.parent_id),
            "category_id": func.get_many2many_dict(self.category_id),
            "phone": self.phone,
            "image_1920": self.image_1920,
            "address": [rec.api_address_read() for rec in self.child_ids if rec.is_address],
            "bank_acc_number": self.bank_acc_number,
            "bank_name": self.bank_name,
            "upi_id": self.upi_id,
            "bank_account_name": self.bank_account_name,
            "ifsc_code": self.ifsc_code,
            "date_of_birth": self.date_of_birth,
            "emergency_contact": self.emergency_contact,
            "additional_information": self.additional_information,
            "comment": self.comment,
            "custom_field": self.custom_field,
            "website": self.website,
            "custom_field_details": self.custom_field_details
        }

    def api_rel_contact_read(self):
        data = []
        for rec in self:
            data.append({
                'id': rec.id,
                'image': rec.image_1024,
                'name': rec.display_name,
                'businessType': rec.category_id.mapped('display_name'),
                'phone': rec.phone,
                'email': rec.email
            })
        return data
