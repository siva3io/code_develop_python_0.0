# -*- coding: utf-8 -*-
from odoo import http


class SalesOrders(http.Controller):
    @http.route('/api/v1/sales_orders', auth='user', type='json', csrf=False, cors="*")
    def sales_orders(self, limit=20, offset=0, order='', domain=None, **kwargs):
        fields = []
        if kwargs.get('search_query'):
            fields = [('name', 'ilike', kwargs['search_query'])]
        sales_orders = http.request.env['sale.order'].search(fields or domain, limit=limit, offset=offset, order=order)
        if sales_orders:
            data = []
            for sales_order in sales_orders:
                data.append({
                    "sales_order_id": sales_order.id,
                    "sales_order_name": sales_order.display_name,
                    "sales_order_creation_date": sales_order.create_date,
                    "sales_order_customer_name": sales_order.partner_id.name,
                    "sales_order_user_name": sales_order.user_id.name,
                    "sales_order_company_name": sales_order.company_id.name,
                    "sales_order_total_amount": sales_order.amount_total,
                    "sales_order_status": sales_order.state,
                })
            return data
        else:
            return []

    @http.route('/api/v1/sales_orders/<int:sales_order_id>', auth='user', type='json', csrf=False, cors="*")
    def sales_order_view(self, sales_order_id):
        sales_order = http.request.env['sale.order'].search([("id", "=", sales_order_id)])
        if sales_order:
            data = []
            for order_line in sales_order.order_line:
                data.append({
                    "order_line_id": order_line.id,
                    "vendor_id": order_line.vendor_id.id,
                    "vendor_name": order_line.vendor_id.name,
                    "product_id": order_line.product_id.id,
                    "product_name": order_line.display_name,
                    "product_description": order_line.product_id.name,
                    "product_quantity": order_line.product_uom_qty,
                    "product_unitprice": order_line.price_unit,
                    "product_taxes": order_line.price_tax,
                    "discount_type": order_line.discount_type,
                    "product_total": order_line.price_total,
                })

            sales_order = {
                "sales_order_id": sales_order.id,
                "sales_order_name": sales_order.display_name,
                "gst_treatment": sales_order.l10n_in_gst_treatment,
                "quotation_template": sales_order.sale_order_template_id.name,
                "order_date": sales_order.date_order,
                "expiry_date": sales_order.validity_date,
                "payment_terms_id": sales_order.payment_term_id.id,
                "payment_terms": sales_order.payment_term_id.name,
                "customer_details": [{"customer_id": customer.id, "customer": customer.name,
                                      "customer_address": customer.contact_address}
                                     for customer in sales_order.partner_id],
                "product_details": data,
                "sales_order_total_amount": sales_order.amount_total,
            }
            return sales_order
        else:
            return []

    @http.route('/api/v1/sales_orders/create', auth='user', type='json', csrf=False, cors="*")
    def sales_order(self, **request_data):
        if http.request.jsonrequest:
            if len(request_data) == 0:
                return {"response": "No Data Available"}
            else:
                order_lines = request_data.get('order_line')
                request_data.pop('order_line')
                sales_orders = http.request.env['sale.order'].create(request_data)
                if order_lines:
                    for sales_order_line in order_lines:
                        sub_total = sales_order_line.get('product_uom_qty') * sales_order_line.get('price_unit')
                        if sales_order_line.get('discount_type') == 'percentage':
                            sub_total = sub_total - ((sales_order_line.get('discount_amount') / sub_total) * 100)
                        else:
                            sub_total = sub_total - sales_order_line.get('discount_amount')
                        sales_order_line['order_id'] = sales_orders.id
                        sales_order_line['price_subtotal'] = sub_total
                        sales_order_lines = http.request.env['sale.order.line'].create(sales_order_line)
                response = {'status': True, 'sales_order_id': sales_orders.id,
                            'sales_order_lines_id': sales_order_lines.id}
                return response

    @http.route('/api/v1/sales_orders/search/<string:query>', auth='user', type='json', csrf=False, cors="*")
    def sales_orders_search(self, query=""):
        domain = [('name', 'ilike', query)]
        sales_orders_search = http.request.env['sale.order'].search(domain)
        if sales_orders_search:
            response = []
            for sales_order in sales_orders_search:
                response.append({
                    'id': sales_order.id,
                    'name': sales_order.name
                })
            return response

    @http.route('/api/v1/sales_orders/<int:sale_id>/delete', auth='user', type='json', csrf=False, cors='*')
    def delete_sales_order(self, sale_id, **kwargs):
        sales_orders = http.request.env['sale.order'].search([('id', '=', sale_id)])
        if sales_orders:
            if sales_orders.state == "sent":
                return {"success": False,
                        "status": "You cannot delete a sent quotation or a confirmed sales order",
                        "sales_order_id": sales_orders.id}
            else:
                for order_line in sales_orders.order_line:
                    order_line.unlink()
                sales_orders.unlink()
                return {"success": True,
                        "status": "Sales Order was deleted",
                        "deleted_sale_id": sales_orders.id}

        else:
            return {"status": "No record was found"}

    @http.route('/api/v1/sales_orders/<int:sale_order_id>/edit', auth='user', type='json', csrf=False, cors='*')
    def sales_orders_edit(self, sale_order_id, **kwargs):
        order_lines = kwargs.get('order_line')
        kwargs.pop('order_line')
        sales_orders = http.request.env['sale.order'].search([('id', '=', sale_order_id)])
        sales_orders.write(kwargs)
        if order_lines:
            order_line_ids = []
            for sale_order_line in order_lines:
                sale_order_line['order_id'] = sales_orders.id
                sales_order_lines = http.request.env['sale.order.line'].search(
                    [('id', '=', sale_order_line.get('id'))])
                if sale_order_line.get('id'):
                    sales_order_lines.write(sale_order_line)
                    order_line_ids.append(sales_order_lines.id)
                else:
                    sales_line_create = sales_order_lines.create(sale_order_line)
                    order_line_ids.append(sales_line_create.id)
        sales_orders.write({"order_line": order_line_ids})
        return {'success': True, 'status': 'Updated', 'updated_sales_order_id': sales_orders.id}


    # @http.route('/api/v1/sales_orders/<int:sale_order_id>/edit', auth='public', type='json', csrf=False, cors='*')
    # def sales_orders_edit(self, sale_order_id, **kwargs):
    #     order_lines = kwargs.get('order_line')
    #     kwargs.pop('order_line')
    #     sales_orders = http.request.env['sale.order'].sudo().search([('id', '=', sale_order_id)])
    #     if sales_orders:
    #         sales_orders.write(kwargs)
    #     if order_lines:
    #         for sales_order_line in order_lines:
    #             for sale_order_line in sales_orders.order_line:
    #                 is_record_updated_or_created = False
    #                 if sales_order_line['id']:
    #                     if sale_order_line['id']:
    #                         if sales_order_line['id'] == sale_order_line['id']:
    #                             order_line_update = http.request.env['sale.order.line'].sudo().search([
    #                                 ('id', '=', sales_order_line['id'])])
    #                             if order_line_update:
    #                                 order_line_update.write(sales_order_line)
    #                                 is_record_updated_or_created = True
    #                                 break
    #                         else:
    #                             order_line_update = http.request.env['sale.order.line'].sudo().search([
    #                                 ('id', '=', sale_order_line['id'])])
    #                             if order_line_update:
    #                                 order_line_update.unlink()
    #                                 is_record_updated_or_created = True
    #                                 break
    #                 else:
    #                     sales_order_line['order_id'] = sales_orders.id
    #                     order_line_update = http.request.env['sale.order.line'].sudo().create(sales_order_line)
    #                     is_record_updated_or_created = True
    #                     break
    #
    #         return {"success": True,
    #                 "status": "Sales Order was Updated",
    #                 "updated_sales_order_id": sales_orders.id}


    # @http.route('/api/v1/sales_orders/<int:sale_order_id>/edit', auth='public', type='json', csrf=False, cors='*')
    # def sales_orders_edit(self, sale_order_id, **kwargs):
    #     order_lines = kwargs.get('order_line')
    #     kwargs.pop('order_line')
    #     sales_orders = http.request.env['sale.order'].sudo().search([('id', '=', sale_order_id)])
    #     sales_orders.write(kwargs)
    #     if order_lines:
    #         order_line_ids = []
    #         for sale_order_line in order_lines:
    #             for sales_order_line in sales_orders.order_line:
    #                 if sale_order_line['id']:
    #                     sale_order_line['order_id'] = sales_orders.id
    #                     sales_order_lines = http.request.env['sale.order.line'].sudo().search(
    #                         [('id', '=', sale_order_line.get('id'))])
    #                     if sale_order_line['id'] == sales_order_line['id']:
    #                         sales_order_lines.write(sale_order_line)
    #                         break
    #                     else:
    #                         sales_order_lines.unlink()
    #                         break
    #                 else:
    #                     sales_order_lines = http.request.env['sale.order.line'].sudo().create(sale_order_line)
    #                     break
    #         return {'success': True, 'status': 'Updated', 'updated_sales_order_id': sales_orders.id}