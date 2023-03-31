# -*- coding: utf-8 -*-
from odoo import http
from odoo.http import request


class ProductsController(http.Controller):
    @http.route('/api/v1/product/create', auth='public', type='json', csrf=False, cors="*")
    def product_create(self, **req):
        if request.jsonrequest:
            print("req", req)
            if req['name']:
                vals = {
                    'name': req['name'],
                    'detailed_type': req['detailed_type'],
                    'purchase_ok': req['purchase_ok'],
                    'sale_ok': req['sale_ok'],
                    'description': req['description'],
                    'list_price': req['list_price'],
                    'standard_price': req['standard_price'],
                    'weight': req['weight'],
                    # 'sku_id ': req['sku_id'],
                    # 'image_1920': req['image_1920'],
                    # 'categ_id': req['categ_id'],
                    # 'shipping_partner_ids': req['shipping_partner_ids'],
                    # 'taxes_id': req['taxes_id'],
                }
                new_product = request.env['product.template'].sudo().create(vals)
                print("New Product Is", new_product)
                args = {'success': True, 'message': 'Success', 'ID': new_product.id}
        return args

    @http.route('/api/v1/product/view/<string:view_type>', auth='public', type='json', csrf=False, cors="*")
    def product_view(self, view_type):
        product_ids = http.request.env['product.template'].sudo().search([])
        if product_ids:
            response = []
            if view_type == 'list':
                for product in product_ids:
                    response.append({
                        "product_id": product.id,
                        "product_image": product.image_128,
                        "product_name": product.name,
                        # "sku_id": product.sku_id,
                        "category": product.categ_id.parent_id.name,
                        "description": product.description,
                        "cost_price": product.standard_price
                    })
            elif view_type == 'grid':
                for product in product_ids:
                    response.append({
                        "product_id": product.id,
                        "product_image": product.image_256,
                        "product_name": product.name,
                        # "sku_id": product.sku_id,
                        "category": product.categ_id.parent_id.name,
                        "sub_category": product.categ_id.name
                    })
            return response

# @http.route('/create_product/<int:pro_id>', auth='public', type='json')
# def create_product(self, pro_id):
#     product = http.request.env['product.template'].sudo().browse(pro_id)
#     if product:
#         data = {
#             "Product Title": product.name,
#             "Type": product.detailed_type,
#             "Can be Purchase": product.purchase_ok,
#             "Can be sold": product.sale_ok,
#             "SKU ID": product.sku_id
#         }
#         return data

# @http.route('/upload_image/<int:pro_id>', auth='public', type='json')
# def default_image(self, pro_id):
#     product = http.request.env['product.template'].sudo().browse(pro_id)
#     if product:
#         data = {
#             "product_image": product.image_1920
#         }
#         return data

# @http.route('/category_details/<int:pro_id>', auth='public', type='json')
# def category_details(self, pro_id):
#     product = http.request.env['product.template'].sudo().browse(pro_id)
#     if product:
#         data = {
#             "Category": [{"parent id": i.parent_id} for i in product.categ_id],
#             "Leaf level category": [{"name": i.name} for i in product.categ_id],
#             "Description": product.description
#         }
#         return data

# @http.route('/create_variant/<int:pro_id>', auth='public', type='json')
# def product_variants(self, pro_id):
#     product = http.request.env['product.attribute'].sudo().browse(pro_id)
#     if product:
#         data = {
#             "variant_attribute": product.name,
#             "variant_value": product.value_ids
#         }
#         return data

# @http.route('/cost_details/<int:pro_id>', auth='public', type='json')
# def product_cost(self, pro_id):
#     product = http.request.env['product.template'].sudo().browse(pro_id)
#     if product:
#         data = {
#             "Sell Price": product.list_price,
#             "Shipping Partners": product.shipping_partner_ids,
#             "Taxes": product.taxes_id,
#             "Cost price": product.standard_price
#         }
#         return data

# @http.route('/packing_details/<int:pro_id>', auth='public', type='json')
# def product_package(self, pro_id):
#     product = http.request.env['product.shipping.partner'].sudo().browse(pro_id)
#     if product:
#         data = {
#             # Shipping Partners": product.shipping_partner_ids,"
#             # "Weight": product.weight,
#             "Shipping Partner": product.name,
#             "Packing Lead time": product.pack_lead_time,
#             "Shipping Lead time": product.shipping_lead_time
#         }
#         return data

# @http.route('/upload_variant_image/<int:pro_id>', auth='public', type='json')
# def product_variant(self, pro_id):
#     product = http.request.env['product.product'].sudo().browse(pro_id)
#     if product:
#         data = {
#             "Upload image": product.image_1920
#         }
#         return data

# @http.route('/grid_view', auth='public', type='json')
# def product_grid_view(self):
#     product_grid = http.request.env['product.template'].sudo().search([])
#     if product_grid:
#         response = []
#         for product in product_grid:
#             response.append({
#                 "Product Image": product.image_128,
#                 "Product Name": product.name,
#                 "SKU ID": product.sku_id,
#                 "Category": [{"parent_id": i.parent_id} for i in product.categ_id],
#                 "Sub Category": [{"name": i.name} for i in product.categ_id]
#             })
#         return response

# @http.route('/list_view', auth='public', type='json')
# def product_list_view(self):
#     product_list = http.request.env['product.template'].sudo().search([])
#     if product_list:
#         response = []
#         for product in product_list:
#             response.append({
#                 # "Product Image": product.image_128,
#                 "Product Name": product.name,
#                 "Category": [{"name": i.name} for i in product.categ_id],
#                 "SKU ID": product.sku_id,
#                 "Description": product.description,
#                 "Cost price": product.standard_price
#             })
#         return response

# @http.route('/products_module/products_module/objects', auth='public')
# def list(self, **kw):
#     return http.request.render('products_module.listing', {
#         'root': '/products_module/products_module',
#         'objects': http.request.env['products_module.products_module'].search([]),
#     })

#     @http.route('/products_module/products_module/objects/<model("products_module.products_module"):obj>', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('products_module.object', {
#             'object': obj
#         })
