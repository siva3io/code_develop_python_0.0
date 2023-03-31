# -*- coding: utf-8 -*-

from odoo import models, fields


class ProductTemplate(models.Model):
    _inherit = "product.template"

    validation_info = fields.Selection(string='Validation Info', selection=[('valid', 'Valid'), ('invalid', 'Invalid')],
                                       default='invalid')
    product_condition = fields.Selection(string='Product Condition',
                                         selection=[('new', 'New'), ('old', 'Old'), ('refurbished', 'Refurbished')],
                                         default='new')
    detailed_type = fields.Selection(selection_add=[('pack', 'Packaging')], ondelete={'pack': 'set default'})
    type = fields.Selection(selection_add=[('pack', 'Packaging')])
    # Parent SKU ID; Need to add and must be unique
    parent_default_code = fields.Char(string='Parent Default Code')
    status = fields.Boolean(string='Status', default=True)

    # Vendor & Pricing Details
    product_mrp = fields.Float(string='Product MRP')
    product_tax = fields.Float(string='Product Tax')
    tax_in_price = fields.Boolean(string='Tax in Price')
    ship_in_price = fields.Boolean(string='Ship in Price')

    product_packaging_line_ids = fields.One2many(comodel_name='product.package', inverse_name='product_template_id',
                                                 string='Packaging Lines')

    shipping_partner_ids = fields.Many2many(string='Shipping Partners', comodel_name='product.shipping.partner')

    package_length = fields.Float(string='Package Length')
    package_width = fields.Float(string='Package Width')
    package_height = fields.Float(string='Package Height')
    package_weight = fields.Float(string='Package Weight')
    package_volume = fields.Float(string='Package Volume')

    def product_template_read(self):
        pass


class ProductPackage(models.Model):
    _name = "product.package"

    active = fields.Boolean(name='Active', default=True)
    package_material = fields.Many2one(string='Package Material', comodel_name='product.product')
    pkg_qty = fields.Float(string='Package Quantity')
    product_template_id = fields.Many2one(comodel_name='product.template', string='Product Template')
    product_id = fields.Many2one(comodel_name='product.product', string='Product')


class ProductShippingPartner(models.Model):
    _name = 'product.shipping.partner'
    _description = 'Product Shipping Partner'

    name = fields.Many2one('res.partner', 'Shipping Partner', ondelete='cascade', required=True,
                           help="Shipping Partner")
    active = fields.Boolean(name='Active', default=True)
    pack_lead_time = fields.Integer(name='Pack Lead Time', help="Lead time for packing in days")
    location_covered = fields.Char(name='Location Covered', help="Location covered by this partner")
    shipping_lead_time = fields.Integer(name='Shipping Lead Time', help="Lead time for shipping in days")


class ProductSupplierinfo(models.Model):
    _inherit = "product.supplierinfo"

    vendor_sku_id = fields.Char(string='Vendor SKU ID')
    shipping_type = fields.Selection(string='Shipping Type', selection=[('pickup', 'Pickup'), ('delivery', 'Delivery')],
                                     default='pickup')
    credit_period = fields.Integer(string='Credit Period')
    payment_method = fields.Selection(string='Payment Method',
                                      selection=[('cash', 'Cash'), ('credit', 'Credit'), ('online', 'Online')],
                                      default='online')


class ProductProduct(models.Model):
    _inherit = "product.product"

    package_length = fields.Float(string='Package Length')
    package_width = fields.Float(string='Package Width')
    package_height = fields.Float(string='Package Height')
    package_weight = fields.Float(string='Package Weight')
    package_volume = fields.Float(string='Package Volume')
    package_note = fields.Text(string='Special Note')
    variant_mrp = fields.Float(string='Product MRP')

    product_condition = fields.Selection(string='Product Condition',
                                         selection=[('new', 'New'), ('old', 'Old'), ('refurbished', 'Refurbished')],
                                         default='new')
    product_packaging_line_ids = fields.Many2many(string='Package Materials', comodel_name='product.package',
                                                  relation='product_package_materials_rel',
                                                  column1='product_id', column2='package_material_id')
    product_length = fields.Float(string='Product Length')
    product_breadth = fields.Float(string='Product Breadth')
    product_height = fields.Float(string='Product Height')
    product_weight = fields.Float(string='Product Weight')
    std_product_type = fields.Selection(string='Standard Product Type', selection=[('gtin', 'GTIN'), ('upc', 'UPC'),
                                                                                   ('ean', 'EAN'), ('isbn', 'ISBN')],
                                        default='gtin')
    std_product_code = fields.Char(string='Standard Product Code')
