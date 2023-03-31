# -*- coding: utf-8 -*-
from odoo import http
from odoo.http import request


class PurchaseModule(http.Controller):
    @http.route('/api/v1/purchase_orders', auth='user', type='json', csrf=False, cors="*")
    def purchase_list(self, limit=20, offset=0, order='', domain=[], **kwargs):
        data = []
        if kwargs.get('sale_ids'):
            data = [("sale_id", "in", kwargs['sale_ids'])]
        elif kwargs.get('search_query'):
            data = [('name', 'ilike', kwargs['search_query'])]
        order_view = http.request.env['purchase.order'].search(data or domain, limit=limit, offset=offset, order=order)
        if order_view:
            response = []
            # if view_type == 'list':
            for order in order_view:
                products = []
                for order_line in order.order_line:
                    products.append({
                        'id': order_line.id,
                        'product_id': order_line.product_id.id,
                        'product_name': order_line.display_name,
                        'unit_price': order_line.price_unit,
                        'product_quantity': order_line.product_qty,
                        'tax': order_line.price_tax,
                        'total': order_line.price_subtotal
                    })
                response.append({
                    'id': order.id,
                    'po_number': order.name,
                    'confirmation_date': order.date_approve,
                    'validity_date': order.date_planned,
                    'vendor_id': order.partner_id.id,
                    'vendor_name': order.partner_id.name,
                    'product_details': products,
                    'vendor_code': order.partner_ref,
                    'po_value': order.amount_total,
                    'state': order.state
                })
            # elif view_type == 'kanban':
            #     for order in order_view:
            #         response.append({
            #             'po_number': order.name,
            #             'vendor_name': order.partner_id.name,
            #             'total': order.amount_total,
            #             'confirmation_date': order.date_approve,
            #             'validity_date': order.date_planned
            #         })
            return response
        else:
            return []

    @http.route('/api/v1/purchase_orders/create', auth='user', type='json', csrf=False, cors="*")
    def purchase_create(self, **request_data):
        if http.request.jsonrequest:
            order_lines = request_data.get('order_line')
            request_data.pop('order_line')
            purchase_order = request.env['purchase.order'].create(request_data)
            if order_lines:
                # record = []
                for purchase_order_line in order_lines:
                    sub_total = purchase_order_line.get('product_qty') * purchase_order_line.get('price_unit')
                    if purchase_order_line.get('discount_type') == 'percentage':
                        sub_total = sub_total - ((purchase_order_line.get('discount') / sub_total) * 100)
                    else:
                        sub_total = sub_total - purchase_order_line.get('discount')
                    print(sub_total)
                    purchase_order_line['order_id'] = purchase_order.id
                    purchase_order_line['price_subtotal'] = sub_total
                    purchase_order_lines = http.request.env['purchase.order.line'].create(purchase_order_line)
                response = {'status': True, 'order_id': purchase_order.id}
                return response

    @http.route('/api/v1/purchase_orders/<int:order_id>', auth='user', type='json', csrf=False, cors="*")
    def purchase_view(self, order_id):
        purchase_orders = http.request.env['purchase.order'].browse(order_id)
        if purchase_orders:
            order_lines = purchase_orders.order_line
            if order_lines:
                data = []
                for order_line in order_lines:
                    data.append({
                        'id': order_line.id,
                        'product_id': order_line.product_id.id,
                        # 'product_sku': order_line.product_id.sku_id,
                        # 'product_sku': order_line.sku_id,
                        'product_name': order_line.display_name,
                        'unit_price': order_line.price_unit,
                        'product_quantity': order_line.product_qty,
                        'tax': order_line.price_tax,
                        'total': order_line.price_subtotal
                    })
                response = {
                    'id': purchase_orders.id,
                    'po_number': purchase_orders.name,
                    'start_date': purchase_orders.date_approve,
                    'validity_date': purchase_orders.date_planned,
                    'sales_order_id': purchase_orders.sale_id.name,
                    'vendor_code': purchase_orders.partner_ref,
                    'vendor_name': purchase_orders.partner_id.name,
                    'company_name': purchase_orders.company_id.name,
                    'registered_address': purchase_orders.company_id.street,
                    'company_gst': purchase_orders.company_id.vat,
                    'company_mobile': purchase_orders.company_id.mobile,
                    'company_email': purchase_orders.company_id.email,
                    'city': purchase_orders.company_id.city,
                    'state_id': purchase_orders.company_id.state_id.name,
                    'zip': purchase_orders.company_id.zip,
                    'country': purchase_orders.company_id.country_id.name,
                    'notes': purchase_orders.notes,
                    'external_notes': purchase_orders.external_notes,
                    'company_logo': purchase_orders.company_id.logo,
                    'phone': purchase_orders.company_id.phone,
                    'purchase_order_line': data,
                    'total_cost': purchase_orders.amount_total,
                    'name': purchase_orders.picking_ids.name,
                    'receive_from': purchase_orders.picking_ids.partner_id.name,
                    'scheduled_date': purchase_orders.picking_ids.scheduled_date,
                    'operation_type': purchase_orders.picking_type_id.name,
                    'destination': purchase_orders.picking_ids.location_dest_id.complete_name,
                    'deadline': purchase_orders.picking_ids.date_deadline,
                    'source': purchase_orders.picking_ids.origin,
                    'owner': purchase_orders.picking_ids.owner_id.name,
                    'carrier_id': purchase_orders.picking_ids.carrier_id.name,
                    'tracking_reference': purchase_orders.picking_ids.carrier_tracking_ref,
                    'weight': purchase_orders.picking_ids.weight,
                    'shipping_weight': purchase_orders.picking_ids.shipping_weight,
                    'user': purchase_orders.picking_ids.user_id.name,
                    'group_id': purchase_orders.group_id.name
                }
                return response

    @http.route('/api/v1/purchase_orders/search/<string:query>', auth='user', type='json', csrf=False, cors="*")
    def purchase_order_search(self, query=""):
        domain = [('name', 'ilike', query)]
        purchase_order_search = http.request.env['purchase.order'].search(domain)
        if purchase_order_search:
            response = []
            for purchase_order in purchase_order_search:
                response.append({
                    'id': purchase_order.id,
                    'name': purchase_order.name
                })
            return response

    @http.route('/api/v1/purchase_orders/<int:purchase_order_id>/edit', auth='user', type='json', csrf=False,
                cors="*")
    def purchase_order_edit(self, purchase_order_id, **kw):
        order_lines = kw.get('order_line')
        kw.pop('order_line')
        purchase_orders = http.request.env['purchase.order'].search([('id', '=', purchase_order_id)])
        purchase_orders.write(kw)
        if order_lines:
            order_line_ids = []
            for purchase_order_line in order_lines:
                purchase_order_line['order_id'] = purchase_orders.id
                purchase_order_lines = http.request.env['purchase.order.line'].search(
                    [('id', '=', purchase_order_line.get('id'))])
                if purchase_order_line.get('id'):
                    purchase_order_lines.write(purchase_order_line)
                    order_line_ids.append(purchase_order_lines.id)
                else:
                    purchase_create = purchase_order_lines.create(purchase_order_line)
                    order_line_ids.append(purchase_create.id)
        purchase_orders.write({"order_line": order_line_ids})
        return {'status': True, 'Success': 'Updated', 'result': purchase_orders.id}

    @http.route('/api/v1/purchase_orders/<int:id>/delete', auth='user', type='json', csrf=False, cors="*")
    def purchase_delete(self, id, **kw):
        purchase_delete = http.request.env['purchase.order'].search([('id', '=', id)])
        if purchase_delete:
            purchase_delete.button_cancel()
            for line_ids in purchase_delete.order_line:
                line_ids.unlink()
            purchase_delete.unlink()
            return {"status": "Deleted", "Deleted id": purchase_delete.id}
        else:
            return {"status": "no data found to delete"}

#     @http.route('/purchase_module/purchase_module/objects', auth='public')
#     def list(self, **kw):
#         return http.request.render('purchase_module.listing', {
#             'root': '/purchase_module/purchase_module',
#             'objects': http.request.env['purchase_module.purchase_module'].search([]),
#         })

#     @http.route('/purchase_module/purchase_module/objects/<model("purchase_module.purchase_module"):obj>', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('purchase_module.object', {
#             'object': obj
#         })
