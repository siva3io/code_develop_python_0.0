# -*- coding: utf-8 -*-
import traceback
# from odoo.exceptions import ValidationError
from odoo.http import request, Controller, route


class ProductApi(Controller):
    @staticmethod
    def product_sanity_check(data, name):
        if data.get('parent_categ_id'):
            data.pop('parent_categ_id')
        if data.get('route_ids'):
            data['route_ids'] = [(6, 0, data['route_ids'])]
        if data.get('images'):
            image_ids = []
            data['image_1920'] = data['images'][0]
            for rec in data['images']:
                image_ids.append([0, 0, {
                    "sequence": 10,
                    "name": name,
                    "video_url": False,
                    "image_1920": rec,
                }])
            data.pop('images')
            data['product_template_image_ids'] = image_ids
        return data

    @staticmethod
    def product_variant_sanity_check(data):
        if data.get('attributes'):
            for rec in data.get('attributes'):
                data['attribute_line_ids'] = [0, 0, {
                    "attribute_id": 1,
                    "value_ids": [[6, 0, data['attributes']['val_ids']]]
                }]
        if data.get('images'):
            image_ids = []
            for rec in data['images']:
                image_ids.append([0, 0, {
                    "sequence": 10,
                    "video_url": False,
                    "image_1920": rec,
                }])
            data.pop('images')
            data['product_template_image_ids'] = image_ids
        return data

    @staticmethod
    def product_attribute_sanity_check(attributes):
        data = []
        for rec in attributes:
            if rec.get('attr_id') and rec.get('val_ids'):
                data.append([0, 0, {
                    "attribute_id": rec.get('attr_id'),
                    "value_ids": [[6, 0, rec.get('val_ids')]]
                }])
        return data

    @route('/api/v1/product/view', type='json', auth='user', cors='*')
    def api_v1_product_view(self, view='list', limit=20, offset=0, domain=None, order='', **kw):
        data = {
            'size': 0,
            'records': []
        }
        try:
            if not domain:
                domain = []
            product_ids = request.env['product.template'].search(domain, limit=limit, offset=offset,
                                                                          order=order)
            if product_ids:
                if view == 'list':
                    for rec in product_ids:
                        data['records'].append({
                            'id': rec.id,
                            'image': rec.image_128,
                            'name': rec.name,
                            'default_code': rec.default_code,
                            'parent_category': rec.categ_id.parent_id.name,
                            'category': rec.categ_id.name,
                            'create_date': rec.create_date,
                            'description': rec.description,
                            'standard_price': rec.standard_price,
                            'list_price': rec.list_price,
                            'qty_available': rec.qty_available,
                            'status': rec.status,
                            'validation_info': rec.validation_info
                        })
                else:
                    for rec in product_ids:
                        data['records'].append({
                            'id': rec.id,
                            'image': rec.image_1024,
                            'name': rec.name,
                            'default_code': rec.default_code,
                            'parent_category': rec.categ_id.parent_id.name,
                            'category': rec.categ_id.name
                        })
                if limit and len(data['records']) == limit:
                    size = product_ids.search_count(domain)
                else:
                    size = len(data['records']) + offset
                data['size'] = size
            else:
                pass  # ToDo: Add response
        except Exception as e:
            traceback.print_exc()
        finally:
            return data

    @route('/api/v1/product/create', type='json', auth="user", cors="*")
    def api_v1_product_create(self, **kw):
        data = []
        try:
            if kw.get('id'):
                product_id = request.env['product.template'].browse(int(kw.get('id')))
                kw = ProductApi.product_sanity_check(kw, kw['name'])
                if product_id:
                    product_id.write(kw)
            else:
                if kw.get('name'):
                    kw = ProductApi.product_sanity_check(kw, kw['name'])
                    product_id = request.env['product.template'].create(kw)
                    if product_id:
                        product_id.write({'parent_default_code': product_id.default_code})
                        data = product_id.id
                        pass  # ToDo: Add response
                else:
                    pass  # ToDo: Add response
        except Exception as e:
            traceback.print_exc()
        finally:
            return data

    @route('/api/v1/product/variant/create', type='json', auth="user", cors="*")
    def api_v1_product_variant_create(self, **kw):
        data = []
        try:
            if kw.get('id'):
                pass
                # product_id = request.env(su=True)['product.product'].browse(int(kw.get('id')))
                # kw = ProductApi.product_variant_sanity_check(kw, kw['name'])
                # if product_id:
                #     product_id.write(kw)
            else:
                if kw.get('product_id'):
                    product_id = request.env['product.template'].browse(int(kw.get('product_id')))
                    if product_id:
                        if kw.get('attributes'):
                            # To update the product template with the new variants
                            data = ProductApi.product_attribute_sanity_check(kw.get('attributes'))
                            product_id.write({
                                'attribute_line_ids': data
                            })
                        variant_ids = product_id.product_variant_ids
                        image_ids = product_id.product_template_image_ids
                        img_data = []
                        for image_id in image_ids:
                            img_data.append([0, 0, {
                                'name': image_id.name,
                                'image_1920': image_id.image_1920.decode("utf-8"),
                                'product_tmpl_id': product_id.id
                            }])
                        if variant_ids and img_data:
                            for variant in variant_ids:
                                variant.product_variant_image_ids = img_data
                        # variant_ids[0].attribute_line_ids
                        if kw.get('variants'):
                            for var in kw.get('variants'):
                                pass
                            # ToDo: Add data to variants
                    # product_id = request.env(su=True)['product.product'].create(kw)
                    # if product_id:
                    #     data = product_id.id
                    else:
                        pass  # ToDo: Add response
                else:
                    pass  # ToDo: Add response
        except Exception as e:
            traceback.print_exc()
        finally:
            return data

    @route('/api/v1/product/variants/create', type='json', auth="user", cors="*")
    def api_v1_product_variants_create(self, **kw):
        data = []
        try:
            if kw.get('product_id'):
                product_id = request.env['product.template'].browse(int(kw.get('product_id')))
                if product_id:
                    if kw.get('attributes'):
                        if product_id.product_variant_ids:
                            # product_image = product_id.image_1920
                            product_id.attribute_line_ids.unlink()
                            # product_id.image_1920 = product_image
                            # product_id.product_variant_ids.unlink()
                        # To update the product template with the new variants
                        attribute_data = ProductApi.product_attribute_sanity_check(kw.get('attributes'))
                        if attribute_data:
                            product_id.write({
                                'attribute_line_ids': attribute_data
                            })
                    variant_ids = product_id.product_variant_ids
                    for count, variant in enumerate(variant_ids, start=0):
                        if product_id.parent_default_code:
                            variant.write({
                                'default_code': product_id.parent_default_code + '-' + str(count),
                                'description': product_id.description,
                                'package_length': product_id.package_length,
                                'package_width': product_id.package_width,
                                'package_height': product_id.package_height,
                                'package_weight': product_id.package_weight,
                                'package_volume': product_id.package_volume,
                                'product_packaging_line_ids': product_id.product_packaging_line_ids,
                            })
                        data.append({
                            'id': variant.id,
                            'default_code': variant.default_code,
                            # 'product_template_variant_value_ids': variant.product_template_variant_value_ids.mapped(
                            #     "name"),
                            'product_template_attribute_value_ids': variant.product_template_attribute_value_ids.mapped(
                                "name"),
                            'variant_mrp': variant.variant_mrp if variant.variant_mrp else None,
                            'product_variant_image_ids': [{
                                'id': image.id,
                                'name': image.name,
                                'image_1920': image.image_1920,
                            } for image in variant.product_variant_image_ids],
                        })
                # ToDo: Add data to variants
                # product_id = request.env(su=True)['product.product'].create(kw)
                # if product_id:
                #     data = product_id.id
                else:
                    pass  # ToDo: Add response
            else:
                pass  # ToDo: Add response
        except Exception as e:
            traceback.print_exc()
        finally:
            return data

    @route('/api/v1/product/variants/create/update', type='json', auth="user", cors="*")
    def api_v1_product_variants_create_update(self, **kw):
        data = []
        try:
            if kw.get('variants'):
                for variant in kw.get('variants'):
                    prod_variant = request.env['product.product'].browse(int(variant.get('id')))
                    if prod_variant:
                        prod_variant.write({
                            'variant_mrp': variant.get('variant_mrp'),
                            'default_code': variant.get('default_code'),
                            'product_variant_image_ids': [(0, 0, {'name': prod_variant.name, 'image_1920': image}) for
                                                          image in variant.get('product_variant_image_ids')],
                            'image_1920': variant.get('product_variant_image_ids')[0] if variant.get(
                                'product_variant_image_ids') else False,
                        })
                        data.append({
                            'id': prod_variant.id,
                            'default_code': prod_variant.default_code,
                            'product_template_variant_value_ids': prod_variant.product_template_variant_value_ids.mapped(
                                "name"),
                            'variant_mrp': prod_variant.variant_mrp,
                            'product_variant_image_ids': [{
                                'id': image.id,
                                'name': image.name,
                                'image_1920': image.image_1920,
                            } for image in prod_variant.product_variant_image_ids],
                        })
            else:
                pass  # ToDo: Add response
        except Exception as e:
            traceback.print_exc()
        finally:
            return data

    @route('/api/v1/product/vendor-pack/create', type='json', auth="user", cors="*")
    def api_v1_product_vendor_pack_create(self, **kw):
        data = []
        try:
            if kw.get('id'):
                pass
            else:
                if kw.get('product_id'):
                    product_id = request.env['product.template'].browse(int(kw.get('product_id')))
                    if product_id:
                        product_id.write({
                            'list_price': kw.get('list_price'),
                            'standard_price': kw.get('standard_price'),
                            'product_mrp': kw.get('product_mrp'),
                            'product_tax': kw.get('product_tax'),
                            'tax_in_price': kw.get('tax_in_price'),
                            'ship_in_price': kw.get('ship_in_price'),
                            'seller_ids': [[0, 0, {
                                'name': rec.get('name'),
                                'product_name': rec.get('product_name'),
                                'product_tmpl_id': product_id.id,
                                'vendor_sku_id': rec.get('vendor_sku_id'),
                                'min_qty': rec.get('min_qty'),
                                'shipping_type': rec.get('shipping_type'),
                            }] for rec in kw.get('seller_ids')],
                            'product_packaging_line_ids': [[0, 0, {
                                'package_material': rec.get('package_material'),
                                'pkg_qty': rec.get('pkg_qty'),
                            }] for rec in kw.get('product_packaging_line_ids')],
                            'shipping_partner_ids': [[0, 0, {
                                'name': rec.get('name'),
                                'pack_lead_time': rec.get('pack_lead_time'),
                                'location_covered': rec.get('location_covered'),
                            }] for rec in kw.get('shipping_partner_ids')],
                            'package_length': kw.get('package_length'),
                            'package_width': kw.get('package_width'),
                            'package_height': kw.get('package_height'),
                            'package_weight': kw.get('package_weight'),
                            'package_volume': kw.get('package_volume'),
                        })
                        # Update/Sync data update in Variants
                        for variant_id in product_id.product_variant_ids:
                            variant_id.write({
                                'product_packaging_line_ids': [[0, 0, {
                                    'package_material': rec.get('package_material'),
                                    'pkg_qty': rec.get('pkg_qty'),
                                }] for rec in kw.get('product_packaging_line_ids')],
                                'package_length': kw.get('package_length'),
                                'package_width': kw.get('package_width'),
                                'package_height': kw.get('package_height'),
                                'package_weight': kw.get('package_weight'),
                                'package_volume': kw.get('package_volume'),
                            })
                        data = product_id.id
                    else:
                        pass  # ToDo: Add response
                else:
                    pass  # ToDo: Add response
        except Exception as e:
            traceback.print_exc()
        finally:
            return data

    @route('/api/v1/product/update', type='json', auth="user", cors="*")
    def api_v1_product_update(self, **kw):
        data = []
        try:
            if kw.get('id'):
                kw = ProductApi.product_sanity_check(kw, kw['name'])
                product_id = request.env['product.template'].search([('id', '=', kw['id'])])
                if product_id:
                    product_id.write(kw)
                    data = product_id.id
                else:
                    pass  # ToDo: Add response
            else:
                pass  # ToDo: Add response
        except Exception as e:
            traceback.print_exc()
        finally:
            return data

    @route('/api/v1/product/read/<int:id>', type='json', auth="user", cors="*")
    def api_v1_product_read(self, id):
        data = []
        try:
            product_id = request.env['product.template'].browse(id)
            if product_id:
                data = {
                    'id': product_id.id,
                    'name': product_id.name,
                    'default_code': product_id.default_code,
                    'parent_categ_id': {
                        'id': product_id.categ_id.parent_id.id,
                        'name': product_id.categ_id.parent_id.name,
                    },
                    'categ_id': {
                        'id': product_id.categ_id.id,
                        'name': product_id.categ_id.name,
                    },
                    'product_variant_ids': [{
                        'id': variant.id,
                        'name': variant.name,
                        'image': variant.image_1920,
                        'product_template_variant_value_ids': [{
                            'id': variant_value.id,
                            'attribute_id': {
                                'id': variant_value.attribute_id.id,
                                'name': variant_value.attribute_id.name,
                            },
                            'product_attribute_value_id': {
                                'id': variant_value.product_attribute_value_id.id,
                                'name': variant_value.product_attribute_value_id.name,
                            },
                        } for variant_value in variant.product_template_variant_value_ids],
                        'variant_detail': {
                            'id': variant.id,
                            'name': variant.name,
                            'parent_default_code': variant.product_tmpl_id.default_code,
                            'currency_id': {
                                'id': variant.currency_id.id,
                                'name': variant.currency_id.name,
                            },
                            'barcode': variant.barcode,
                            'default_code': variant.default_code,
                            'detailed_type': variant.detailed_type,
                            'list_price': variant.list_price,
                            'standard_price': variant.standard_price,
                            'std_product_type': variant.std_product_type,
                            'std_product_code': variant.std_product_code,
                            'product_condition': variant.product_condition,
                            'brand_id': {
                                'id': variant.brand_id.id,
                                'name': variant.brand_id.name,
                            },
                            'product_length': variant.product_length,
                            'product_breadth': variant.product_breadth,
                            'product_height': variant.product_height,
                            'product_weight': variant.product_weight,
                            'parent_categ_id': {
                                'id': variant.product_tmpl_id.categ_id.parent_id.id,
                                'name': variant.product_tmpl_id.categ_id.parent_id.name,
                            },
                            'categ_id': {
                                'id': variant.product_tmpl_id.categ_id.id,
                                'name': variant.product_tmpl_id.categ_id.name,
                            },
                            'description': variant.description,
                            'images': [{
                                'id': variant_image.id,
                                'name': variant_image.name,
                                'image_1920': variant_image.image_1920
                            } for variant_image in variant.product_variant_image_ids],
                            'product_packaging_line_ids': [{
                                'id': product_packaging_line.id,
                                'package_material': {
                                    'id': product_packaging_line.package_material.id,
                                    'name': product_packaging_line.package_material.name,
                                },
                                'pkg_qty': product_packaging_line.pkg_qty,
                            } for product_packaging_line in variant.product_packaging_line_ids],
                            'package_length': variant.package_length,
                            'package_width': variant.package_width,
                            'package_height': variant.package_height,
                            'package_weight': variant.package_weight,
                            'package_volume': variant.package_volume,
                            'package_note': variant.package_note,
                            'shipping_partner_ids': [{
                                'id': shipping_partner.id,
                                'name': {
                                    'id': shipping_partner.name.id,
                                    'name': shipping_partner.name.name,
                                },
                                'pack_lead_time': shipping_partner.pack_lead_time,
                                'location_covered': shipping_partner.location_covered,
                                'shipping_lead_time': shipping_partner.shipping_lead_time,
                            } for shipping_partner in variant.shipping_partner_ids],
                            'seller_ids': [{
                                'id': seller.id,
                                'name': {
                                    'id': seller.name.id,
                                    'name': seller.name.name,
                                },
                                'product_name': seller.product_name,
                                'vendor_sku_id': seller.vendor_sku_id,
                                'min_qty': seller.min_qty,
                                'price': seller.price,
                                'shipping_type': seller.shipping_type,
                            } for seller in variant.seller_ids],
                        }
                    } for variant in product_id.product_variant_ids],
                }
            else:
                pass  # ToDo: Add response
        except Exception as e:
            traceback.print_exc()
        finally:
            return data

    @route('/api/v1/vendor/view', type='json', auth="user", cors="*")
    def api_v1_vendor_view(self, limit=20, offset=0, domain=None, order='', **kw):
        data = []
        try:
            # ToDo: Add default domain
            vendor_ids = request.env['res.partner'].search(domain or [], limit=limit, offset=offset,
                                                                    order=order)
            for rec in vendor_ids:
                data.append({
                    'id': rec.id,
                    'image': rec.avatar_128,
                    'name': rec.name,
                    'vendor_id': "",
                    'phone': rec.phone,
                    'email': rec.email,
                    'sales_person': {
                        'id': 100,
                        'name': "Dummy record",
                    }
                })
            else:
                pass  # ToDo: Add response
        except Exception as e:
            traceback.print_exc()
        finally:
            return data

    @route('/api/v1/vendor/pricelist/view', type='json', auth="user", cors="*")
    def api_v1_vendor_pricelist_view(self, limit=20, offset=0, domain=None, order='', **kw):
        data = []
        try:
            vendor_ids = request.env['product.supplierinfo'].search(domain or [], limit=limit,
                                                                             offset=offset, order=order)
            for rec in vendor_ids:
                data.append({
                    'id': rec.id,
                    'name': rec.name.name,
                    'product_name': rec.product_name,
                    'product_code': rec.product_code,
                    'min_qty': rec.min_qty,
                    'delay': rec.delay,
                    'price': rec.price,
                    'currency_id': {
                        "id": rec.currency_id.id,
                        "name": rec.currency_id.name,
                    },
                    'date_start': rec.date_start,
                    'date_end': rec.date_end,
                    'credit_period': rec.credit_period,
                    'payment_method': rec.payment_method
                })
            else:
                pass  # ToDo: Add response
        except Exception as e:
            traceback.print_exc()
        finally:
            return data

    @route('/api/v1/product/variant/update/<int:id>', type='json', auth="user", cors="*")
    def api_v1_product_variant_update(self, id, **kw):
        data = {"status": False, "message": "Something went wrong"}
        try:
            product_id = request.env['product.product'].browse(id)
            if product_id:
                if 'parent_categ_id' in kw:
                    kw.pop('parent_categ_id')
                product_id.write(kw)
                data = {"status": True, "message": "Product variant updated successfully"}
            else:
                pass  # ToDo: Add response
        except Exception as e:
            traceback.print_exc()
            data = {"status": False, "message": str(e)}
        finally:
            return data

    @route('/api/v1/product/variant/image/upload', type='json', auth="user", cors="*")
    def api_v1_product_variant_image_upload(self, **kw):
        data = {}
        try:
            if kw.get('id'):
                product_id = request.env['product.product'].browse(int(kw.get('id')))
                if product_id:
                    product_id.product_variant_image_ids.unlink()
                    product_id.write({
                        'product_variant_image_ids': [(0, 0, {
                            'image_1920': image,
                            'name': product_id.name}) for image in kw.get('images')]
                    })
                    data = [{
                        'id': variant_image.id,
                        'name': variant_image.name,
                        'image_1920': variant_image.image_1920
                    } for variant_image in product_id.product_variant_image_ids]
            else:
                pass  # ToDo: Add response
        except Exception as e:
            traceback.print_exc()
        finally:
            return data

    @route('/api/v1/product-variant/sku/check', type='json', auth="user", cors="*")
    def api_v1_product_variant_sku_check(self, **kw):
        data = {}
        try:
            if kw.get('default_code'):
                domain = [('default_code', '=', kw.get('default_code'))]
                product_id = request.env['product.product'].search(domain, limit=1)
                if product_id:
                    data = True
                else:
                    data = False
            else:
                pass  # ToDo: Add response
        except Exception as e:
            traceback.print_exc()
        finally:
            return data

    @route('/api/v1/product-variant/barcode/check', type='json', auth="user", cors="*")
    def api_v1_product_variant_barcode_check(self, **kw):
        data = {}
        try:
            if kw.get('barcode'):
                domain = [('barcode', '=', kw.get('barcode'))]
                product_id = request.env['product.product'].search(domain, limit=1)
                if product_id:
                    data = True
                else:
                    data = False
            else:
                pass  # ToDo: Add response
        except Exception as e:
            traceback.print_exc()
        finally:
            return data

    @route('/api/v1/product-template/sku/check', type='json', auth="user", cors="*")
    def api_v1_product_template_sku_check(self, **kw):
        data = {}
        try:
            if kw.get('default_code'):
                domain = [('default_code', '=', kw.get('default_code'))]
                product_id = request.env['product.template'].search(domain, limit=1)
                if product_id:
                    data = True
                else:
                    data = False
            else:
                pass  # ToDo: Add response
        except Exception as e:
            traceback.print_exc()
        finally:
            return data

    @route('/api/v1/product-template/mrp/check', type='json', auth="user", cors="*")
    def api_v1_product_template_mrp_check(self, **kw):
        data = False
        try:
            if kw.get('id'):
                if kw.get('variant_mrp'):
                    product_id = request.env['product.template'].browse(int(kw.get('id')))
                    if product_id:
                        mrp = product_id.product_variant_ids.mapped("variant_mrp")
                        min_mrp = min(mrp)
                        if min_mrp != 0 and kw.get('variant_mrp') < min_mrp:
                            data = True
                elif not kw.get('variant_mrp'):
                    data = True
            else:
                pass  # ToDo: Add response
        except Exception as e:
            traceback.print_exc()
        finally:
            return data

    # Reference of request body
    params = {
        "args": [
            {
                "service_type": "manual",
                "attribute_line_ids": [
                    [
                        0,
                        "virtual_711",
                        {
                            "attribute_id": 1,
                            "value_ids": [
                                [
                                    6,
                                    False,
                                    [
                                        1,
                                        2
                                    ]
                                ]
                            ]
                        }
                    ],
                    [
                        0,
                        "virtual_713",
                        {
                            "attribute_id": 2,
                            "value_ids": [
                                [
                                    6,
                                    False,
                                    [
                                        4
                                    ]
                                ]
                            ]
                        }
                    ]
                ],
                "type": "product",
                "is_published": False,
                "image_1920": False,
                "__last_update": False,
                "priority": "0",
                "name": "p1",
                "sale_ok": True,
                "purchase_ok": True,
                "active": True,
                "detailed_type": "product",
                "invoice_policy": "order",
                "expense_policy": "no",
                "uom_id": 1,
                "base_unit_count": 0,
                "base_unit_id": False,
                "uom_po_id": 1,
                "list_price": 1,
                "taxes_id": [
                    [
                        6,
                        False,
                        [
                            76
                        ]
                    ]
                ],
                "standard_price": 0,
                "categ_id": 8,
                "default_code": False,
                "barcode": False,
                "l10n_in_hsn_code": False,
                "l10n_in_hsn_description": False,
                "company_id": False,
                "description": "<p><br></p>",
                "template_category_id": False,
                "sku_id": False,
                "shipping_partner_ids": [
                    [
                        6,
                        False,
                        []
                    ]
                ],
                "accessory_product_ids": [
                    [
                        6,
                        False,
                        []
                    ]
                ],
                "alternative_product_ids": [
                    [
                        6,
                        False,
                        []
                    ]
                ],
                "website_id": False,
                "website_sequence": 10015,
                "public_categ_ids": [
                    [
                        6,
                        False,
                        []
                    ]
                ],
                "website_ribbon_id": False,
                "product_template_image_ids": [
                    [
                        0,
                        "virtual_715",
                        {
                            "sequence": 10,
                            "name": "p1",
                            "video_url": False,
                            "image_1920": "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",
                            "__last_update": False
                        }
                    ],
                    [
                        0,
                        "virtual_721",
                        {
                            "sequence": 10,
                            "name": "p1",
                            "video_url": False,
                            "image_1920": "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",
                            "__last_update": False
                        }
                    ]
                ],
                "description_sale": False,
                "sale_line_warn": "no-message",
                "seller_ids": [],
                "service_to_purchase": False,
                "supplier_taxes_id": [
                    [
                        6,
                        False,
                        [
                            83
                        ]
                    ]
                ],
                "purchase_method": "receive",
                "description_purchase": False,
                "purchase_line_warn": "no-message",
                "route_ids": [
                    [
                        6,
                        False,
                        []
                    ]
                ],
                "responsible_id": 2,
                "weight": 0,
                "volume": 0,
                "sale_delay": 0,
                "tracking": "none",
                "property_stock_production": 15,
                "property_stock_inventory": 14,
                "packaging_ids": [],
                "description_pickingin": False,
                "description_pickingout": False,
                "description_picking": False,
                "property_account_income_id": False,
                "property_account_expense_id": False,
                "property_account_creditor_price_difference": False,
                "message_follower_ids": [],
                "activity_ids": [],
                "message_ids": []
            }
        ],
        "model": "product.template",
        "method": "create",
        "kwargs": {
            "context": {
                "lang": "en_US",
                "tz": "Asia/Calcutta",
                "uid": 2,
                "allowed_company_ids": [
                    1
                ],
                "search_default_consumable": 1,
                "default_detailed_type": "product"
            }
        }
    }


# Edit


ab = {
    "attribute_id": 1,
    "value_ids": [[6, 0, [1, 2]]]
}

ddata = {
    "product_id": 1,
    "attributes": [{
        "attr_id": 1,
        "val_ids": [1, 2]
    }],
    "variants": [{
        "default_code": "Prod_12345",
        "standard_price": 22.50,
        "image": ["546789fghj==", "fghjk89=="]
    }]
}
