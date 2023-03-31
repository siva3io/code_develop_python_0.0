# -*- coding: utf-8 -*-
import traceback
from odoo.http import Controller, route, request, Response


class SmallProductApi(Controller):

    @route(['/api/v1/product-template/search/<string:query>',
            '/api/v1/product-template/search'], type='json', auth="user", cors="*")
    def api_v1_product_template_search(self, query=""):
        data = []
        try:
            domain = [('name', 'ilike', query)]
            product_ids = request.env['product.template'].search(domain, limit=100)
            data = [[rec.id, rec.name] for rec in product_ids]
        except Exception as e:
            traceback.print_exc()
        finally:
            return data

    @route('/api/v1/product-template/delete/<int:product_id>', type='json', auth="user", cors="*")
    def api_v1_product_template_delete(self, product_id):
        data = []
        try:
            if product_id:
                request.env['product.template'].browse(product_id).write({'active': False})
                data = True
        except Exception as e:
            traceback.print_exc()
        finally:
            return data

    @route('/api/v1/product-variant/delete/<int:product_id>', type='json', auth="user", cors="*")
    def api_v1_product_variant_delete(self, product_id):
        data = []
        try:
            if product_id:
                request.env['product.product'].browse(product_id).write({'active': False})
                data = True
        except Exception as e:
            traceback.print_exc()
        finally:
            return data

    @route(['/api/v1/product-variant/search/<string:query>',
            '/api/v1/product-variant/search'], type='json', auth="user", cors="*")
    def api_v1_product_variant_search(self, query=""):
        data = []
        try:
            product_ids = request.env['product.product'].name_search(query)
            data = product_ids
        except Exception as e:
            traceback.print_exc()
        finally:
            return data

    @route(['/api/v1/product-packaging/search/<string:query>',
            '/api/v1/product-packaging/search'], type='json', auth="user", cors="*")
    def api_v1_product_packaging_search(self, query=""):
        data = []
        try:
            args = [('detailed_type', '=', 'pack')]
            product_ids = request.env['product.product'].name_search(query, args=args)
            data = product_ids
        except Exception as e:
            traceback.print_exc()
        finally:
            return data

    @route(['/api/v1/product-attribute/search/<string:query>',
            '/api/v1/product-attribute/search'], type='json', auth="user", cors="*")
    def api_v1_product_attribute_search(self, query=""):
        data = []
        try:
            attribute_ids = request.env['product.attribute'].name_search(query)
            data = attribute_ids
        except Exception as e:
            traceback.print_exc()
        finally:
            return data

    @route('/api/v1/product-attribute/search/create', type='json', auth="user", cors="*")
    def api_v1_product_attribute_search_create(self, name):
        data = []
        try:
            if name:
                data = request.env['product.attribute'].name_create(name)
        except Exception as e:
            traceback.print_exc()
        finally:
            return data

    @route(['/api/v1/product-attribute-value/search/<int:attr_id>/<string:query>',
            '/api/v1/product-attribute-value/search/<int:attr_id>'], type='json', auth="user", cors="*")
    def api_v1_product_attribute_value_search(self, attr_id, query=""):
        data = []
        try:
            domain = [('attribute_id', '=', attr_id)]
            attribute_value_ids = request.env['product.attribute.value'].name_search(name=query, args=domain)
            data = attribute_value_ids
        except Exception as e:
            traceback.print_exc()
        finally:
            return data

    @route('/api/v1/product-attribute-value/search/create', type='json', auth="user", cors="*")
    def api_v1_product_attribute_value_search_create(self, name, attr_id=0):
        data = []
        try:
            if name and attr_id:
                attr_value_id = request.env['product.attribute.value'].create(
                    {'name': name, 'attribute_id': attr_id})
                data = attr_value_id.name_get()[0]
        except Exception as e:
            traceback.print_exc()
        finally:
            return data

    @route(['/api/v1/product-pricelist/search/<string:query>',
            '/api/v1/product-pricelist/search'], type='json', auth="user", cors="*")
    def api_product_pricelist_search(self, query=""):
        data = []
        try:
            product_pricelist_ids = request.env['product.pricelist'].name_search(query)
            data = product_pricelist_ids
        except Exception as e:
            traceback.print_exc()
        finally:
            return data

    @route(['/api/v1/product-category/search/<string:query>',
            '/api/v1/product-category/search/<int:parent_id>',
            '/api/v1/product-category/search/<int:parent_id>/<string:query>',
            '/api/v1/product-category/search'], type='json', auth="user", cors="*")
    def api_v1_product_category_search(self, parent_id=0, query=""):
        data = []
        try:
            if parent_id:
                domain = [('parent_id', '=', parent_id)]
            else:
                domain = [('parent_id', '=', False)]
            product_category_ids = request.env['product.category'].name_search(query, args=domain)
            data = product_category_ids
        except Exception as e:
            traceback.print_exc()
        finally:
            return data

    @route(['/api/v1/product-category/search/create/<string:name>',
            '/api/v1/product-category/search/<int:parent_id>/create/<string:name>'],
           type='json', auth="user", cors="*")
    def api_v1_product_category_search_create(self, name, parent_id=0):
        data = []
        try:
            if parent_id:
                category_name = \
                    request.env['product.category'].create({'name': name, 'parent_id': parent_id}).name_get()[
                        0]
            else:
                category_name = request.env['product.category'].name_create(name)
            data = category_name
        except Exception as e:
            traceback.print_exc()
        finally:
            return data

    @route(['/api/v1/product-brand/search/<string:query>',
            '/api/v1/product-brand/search'], type='json', auth="user", cors="*")
    def api_v1_product_brand_search(self, query=""):
        data = []
        try:
            product_brand_ids = request.env['product.brand'].name_search(query)
            data = product_brand_ids
        except Exception as e:
            traceback.print_exc()
        finally:
            return data

    @route('/api/v1/product-brand/search/create', type='json', auth="user", cors="*")
    def api_v1_product_brand_search_create(self, name):
        data = []
        try:
            if name:
                data = request.env['product.brand'].name_create(name)
        except Exception as e:
            traceback.print_exc()
        finally:
            return data

    @route(['/api/v1/stock-route/search/<string:query>',
            '/api/v1/stock-route/search'], type='json', auth="user", cors="*")
    def api_v1_stock_route_search(self, query=""):
        data = []
        try:
            domain = [('company_id', '=', request.env.user.company_id.id)]
            stock_route_ids = request.env['stock.location.route'].name_search(query, args=domain)
            data = stock_route_ids
        except Exception as e:
            traceback.print_exc()
        finally:
            return data

    @route(['/api/v1/vendor/search/<string:query>',
            '/api/v1/vendor/search'], type='json', auth="user", cors="*")
    def api_v1_vendor_search(self, query=""):
        data = []
        try:
            # ToDo: Add condition for vendor
            domain = [('name', 'ilike', query)]
            vendor_ids = request.env['res.partner'].search(domain, limit=100)
            data = vendor_ids.name_get()
        except Exception as e:
            traceback.print_exc()
        finally:
            return data

    @route(['/api/v1/shipping/partner/search/<string:query>',
            '/api/v1/shipping/partner/search'], type='json', auth="user", cors="*")
    def api_v1_shipping_partner_search(self, query=""):
        data = []
        try:
            partner_ids = request.env['product.shipping.partner'].name_search(query)
            data = partner_ids
        except Exception as e:
            traceback.print_exc()
        finally:
            return data

    @route('/api/v1/shipping/partner/view/<int:partner_id>', type='json', auth="user", cors="*")
    def api_v1_shipping_partner_view(self, partner_id, **kwargs):
        data = []
        try:
            partner_id = request.env['product.shipping.partner'].browse(partner_id)
            data.append({
                'id': partner_id.id,
                'name': partner_id.name.name,
                'pack_lead_time': partner_id.pack_lead_time,
                'location_covered': partner_id.location_covered,
                'shipping_lead_time': partner_id.shipping_lead_time,
            })
        except Exception as e:
            traceback.print_exc()
        finally:
            return data

    @route('/api/v1/product-template/favorite/', type='json', auth="user", cors="*")
    def api_v1_product_template_favorite(self, product_id, priority="0"):
        data = []
        try:
            if product_id:
                product_template_id = request.env['product.template'].browse(int(product_id))
                if product_template_id:
                    product_template_id.write({'priority': priority})
                    data = True if priority == "1" else False
        except Exception as e:
            traceback.print_exc()
        finally:
            return data

    @route(['/api/v1/currency/search/<string:query>',
            '/api/v1/currency/search/'], type='json', auth="user", cors="*")
    def api_v1_currency_search(self, query=""):
        data = []
        try:
            currency_ids = request.env['res.currency'].name_search(query)
            data = currency_ids
        except Exception as e:
            traceback.print_exc()
        finally:
            return data
