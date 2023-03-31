# -*- coding: utf-8 -*-
from odoo import http
from odoo.http import request


class DOGRNITManagementModule(http.Controller):
    @http.route('/api/v1/grn', auth='user', type='json', csrf=False, cors="*")
    def grn_list(self, limit=20, offset=0, order='', domain=None, **kwargs):
        data = []
        if kwargs.get('purchase_id'):
            data = [("purchase_id", "in", kwargs["purchase_id"])]
        elif kwargs.get('picking_id'):
            data = [("id", "in", kwargs["picking_id"])]
        elif kwargs.get('asn_id'):
            data = [("asn_ids", "in", kwargs["asn_id"])]
        elif kwargs.get('returns_id'):
            data = [("returns_ids", "in", kwargs["returns_id"])]
        elif kwargs.get("location_ids"):
            data = [("location_id", "in", kwargs.get("location_ids"))]
        elif kwargs.get('search_query'):
            data = [('name', 'ilike', kwargs.get('search_query'))]

        grn_list = http.request.env['stock.picking'].search(data or domain, limit=limit, offset=offset,
                                                                   order=order)
        if grn_list:
            data = []
            for grn in grn_list:
                data.append({
                    "grn_id": grn.id,
                    "asn_number": grn.asn_ids.asn_number,
                    "grn_number": grn.name,
                    "state": grn.state,
                    "validity_date": grn.scheduled_date,
                    "ordered_quantity": grn.requested_quantity.display_name,
                    "grn_delivered_location": {
                        "id": grn.location_id.id,
                        "name": grn.location_id.name,
                        "parent_location_name": grn.location_id.location_id.name,
                        "phone": grn.location_id.location_id.company_id.phone,
                        "email": grn.location_id.location_id.company_id.email,
                        "gst": grn.location_id.location_id.company_id.vat,
                        "address": str(grn.location_id.company_id.street)
                                   + ',' + str(grn.location_id.company_id.street2)
                                   + ',' + str(grn.location_id.company_id.city)
                                   + ',' + str(grn.location_id.company_id.state_id.name)
                                   + ',' + str(grn.location_id.company_id.country_id.name)
                                   + ',' + str(grn.location_id.company_id.zip),
                    },
                    "grn_destination_location": {
                        "id": grn.location_dest_id.id,
                        "name": grn.location_dest_id.name,
                        "parent_location_name": grn.location_dest_id.location_id.name,
                        "phone": grn.location_dest_id.location_id.company_id.phone,
                        "email": grn.location_dest_id.location_id.company_id.email,
                        "gst": grn.location_dest_id.location_id.company_id.vat,
                        "address": str(grn.location_dest_id.company_id.street)
                                   + ',' + str(grn.location_dest_id.company_id.street2)
                                   + ',' + str(grn.location_dest_id.company_id.city)
                                   + ',' + str(grn.location_dest_id.company_id.state_id.name)
                                   + ',' + str(grn.location_dest_id.company_id.country_id.name)
                                   + ',' + str(grn.location_dest_id.company_id.zip),
                    },
                    "grn_sender_location": {
                        "id": grn.partner_id.id,
                        "name": grn.partner_id.name,
                        "phone": grn.partner_id.phone,
                        "email": grn.partner_id.email,
                        "gst": grn.partner_id.vat,
                        "address": str(grn.partner_id.street)
                                   + ',' + str(grn.partner_id.street2)
                                   + ',' + str(grn.partner_id.city)
                                   + ',' + str(grn.partner_id.state_id.name)
                                   + ',' + str(grn.partner_id.country_id.name)
                                   + ',' + str(grn.partner_id.zip),
                    },
                    "create_date": grn.create_date,
                })
            return data
        else:
            return []

    @http.route('/api/v1/grn/<int:grn_id>', auth='user', type='json', csrf=False, cors="*")
    def grn_view(self, grn_id):
        grn_obj = http.request.env['stock.picking'].browse(grn_id)
        if grn_obj:
            data = []
            for grn_line in grn_obj.move_ids_without_package:
                data.append({
                    "grn_line_id": grn_line.id,
                    "product_id": grn_line.product_id.id,
                    "product_name": grn_line.product_id.name,
                    "uom_qty": grn_line.product_uom_qty,
                    "qty_done": grn_line.quantity_done,
                    "batch_number": grn_line.lot_ids.name,

                })
            grn = {
                "grn_id": grn_obj.id,
                "asn_number": grn_obj.asn_ids.asn_number,
                "grn_number": grn_obj.name,
                "grn_delivered_location": {
                    "id": grn_obj.location_id.id,
                    "name": grn_obj.location_id.name,
                    "parent_location_name": grn_obj.location_id.location_id.name,
                    "phone": grn_obj.location_id.location_id.company_id.phone,
                    "email": grn_obj.location_id.location_id.company_id.email,
                    "gst": grn_obj.location_id.location_id.company_id.vat,
                    "address": str(grn_obj.location_id.company_id.street)
                               + ',' + str(grn_obj.location_id.company_id.street2)
                               + ',' + str(grn_obj.location_id.company_id.city)
                               + ',' + str(grn_obj.location_id.company_id.state_id.name)
                               + ',' + str(grn_obj.location_id.company_id.country_id.name)
                               + ',' + str(grn_obj.location_id.company_id.zip),
                },
                "grn_destination_location": {
                    "id": grn_obj.location_dest_id.id,
                    "name": grn_obj.location_dest_id.name,
                    "parent_location_name": grn_obj.location_dest_id.location_id.name,
                    "phone": grn_obj.location_dest_id.location_id.company_id.phone,
                    "email": grn_obj.location_dest_id.location_id.company_id.email,
                    "gst": grn_obj.location_dest_id.location_id.company_id.vat,
                    "address": str(grn_obj.location_dest_id.company_id.street)
                               + ',' + str(grn_obj.location_dest_id.company_id.street2)
                               + ',' + str(grn_obj.location_dest_id.company_id.city)
                               + ',' + str(grn_obj.location_dest_id.company_id.state_id.name)
                               + ',' + str(grn_obj.location_dest_id.company_id.country_id.name)
                               + ',' + str(grn_obj.location_dest_id.company_id.zip),
                },
                "grn_sender_location": {
                    "id": grn_obj.partner_id.id,
                    "name": grn_obj.partner_id.name,
                    "phone": grn_obj.partner_id.phone,
                    "email": grn_obj.partner_id.email,
                    "gst": grn_obj.partner_id.vat,
                    "address": str(grn_obj.partner_id.street)
                               + ',' + str(grn_obj.partner_id.street2)
                               + ',' + str(grn_obj.partner_id.city)
                               + ',' + str(grn_obj.partner_id.state_id.name)
                               + ',' + str(grn_obj.partner_id.country_id.name)
                               + ',' + str(grn_obj.partner_id.zip),
                },
                "create_date": grn_obj.create_date,
                "validate_date": grn_obj.create_date,
                "sale_id": grn_obj.sale_id.id,
                "purchase_id": grn_obj.purchase_id.id,
                "asn_id": grn_obj.asn_ids.id,
                "returns_ids": grn_obj.returns_ids.id,
                "ordered_quantity": grn_obj.requested_quantity.display_name,
                "grn_products": data
            }

            return grn
        return {"result": "No records found"}

    @http.route('/api/v1/grn/create', auth='user', type='json', csrf=False, cors="*")
    def grn_create(self, **request_data):
        if http.request.jsonrequest:
            if request_data.get('purchase_id'):
                purchase_obj = http.request.env['purchase.order'].browse(request_data.get('purchase_id'))
                data = purchase_obj.button_confirm()
                print(data)
                if data:
                    print(purchase_obj.id)
                    grn_obj = http.request.env['stock.picking'].search_read(
                        [('purchase_id', '=', purchase_obj.id)],
                        limit=1)
                    return {'status': True, 'grn': grn_obj}
                else:
                    return {'status': False, 'error': 'Something went wrong'}
            elif request_data.get('asn_ids'):
                grn_lines = request_data.get('grn_lines')
                request_data.pop('grn_lines')
                picking_type = http.request.env['stock.picking.type'].search([('name', 'ilike', 'grn')],
                                                                                    limit=1)
                request_data['picking_type_id'] = picking_type.id
                grn_obj = http.request.env['stock.picking'].create(request_data)
                if grn_lines:
                    line_ids = []
                    for grn_line in grn_lines:
                        grn_line['picking_id'] = grn_obj.id
                        grn_line['product_uom'] = 1
                        grn_line_obj = http.request.env['stock.move'].create(grn_line)
                        line_ids.append(grn_line_obj.id)
                    grn_obj.write({'move_ids_without_package': line_ids})
                return {'status': True, 'grn_id': grn_obj.id, 'grn_line_id': grn_line_obj.id}
            else:
                return {'status': False, 'error': 'No purchase id passed'}

    @http.route('/api/v1/delivery_orders', auth='user', type='json', csrf=False, cors="*")
    def do_list(self, limit=20, offset=0, order='', **kwargs):
        domain = []
        if kwargs.get('sale_ids'):
            domain = [("sale_id", 'in', kwargs['sale_ids'])]
        elif kwargs.get("location_ids"):
            domain = [("location_id", "in", kwargs.get("location_ids"))]
        elif kwargs.get('search_query'):
            domain = [('name', 'ilike', kwargs['search_query'])]

        delivery_orders = http.request.env['stock.picking'].search(domain, limit=limit, offset=offset,
                                                                          order=order)
        if delivery_orders:
            data = []
            for delivery_order in delivery_orders:
                products = []
                for do_line in delivery_order.move_ids_without_package:
                    products.append({
                        "product_id": do_line.product_id.id,
                        "product_name": do_line.product_id.name,
                        "uom_qty": do_line.product_uom_qty,
                        "qty_done": do_line.quantity_done,
                        "product_price": do_line.price_unit
                    })
                data.append({
                    "delivery_order_id": delivery_order.id,
                    "delivery_order_name": delivery_order.name,
                    "delivery_location": delivery_order.location_id.name,
                    "sender_location": delivery_order.partner_id.name,
                    "sales_order_id": delivery_order.sale_id.id,
                    "purchase_order_id": delivery_order.purchase_id.id,
                    "state": delivery_order.state,
                    "product_details": products
                })
            return data
        else:
            return []

    @http.route('/api/v1/delivery_orders/<int:do_id>', auth='user', type='json', csrf=False, cors="*")
    def do_view(self, do_id):
        do_obj = http.request.env['stock.picking'].search([("id","=",do_id)])
        if do_obj:
            data = []
            for do_line in do_obj.move_ids_without_package:
                data.append({
                    "product_id": do_line.product_id.id,
                    "product_name": do_line.product_id.name,
                    "uom_qty": do_line.product_uom_qty,
                    "qty_done": do_line.quantity_done,
                    "batch_number": do_line.lot_ids.name,
                    "description": do_line.product_id.description_picking,
                    "date": do_line.date
                })
            delivery_order = {
                "delivery_order_id": do_obj.id,
                "delivery_order_partner_id": do_obj.partner_id.id,
                "order_date": do_obj.scheduled_date,
                "delivery_date": do_obj.date_done,
                "channel": do_obj.channel,
                "delivery_order_name": do_obj.name,
                "sender_location": do_obj.partner_id.name,
                "reason": do_obj.reason,
                "user_id": do_obj.create_uid.id,
                "delivery_location": {
                    "id": do_obj.location_id.id,
                    "name": do_obj.location_id.name,
                    "address": do_obj.location_id.company_id.street,
                    "country": do_obj.location_id.company_id.country_id.name,
                    "state": do_obj.location_id.company_id.state_id.name,
                    "city": do_obj.location_id.company_id.city,
                    "zip": do_obj.location_id.company_id.zip,
                    "email": do_obj.location_id.company_id.email,
                    "phone": do_obj.location_id.company_id.phone,
                    "location_incharge": do_obj.location_id.company_id.name
                },
                "sales_order_id": do_obj.sale_id.id,
                "asn_id": do_obj.asn_ids.id,
                "grn_id": do_obj.grn_ids.id,
                "purchase_order_id": do_obj.purchase_id.id,
                "state": do_obj.state,
                "ordered_quantity": do_obj.requested_quantity.requested_quantity,
                "return_quantity": do_obj.return_quantity.return_qty,
                "received_quantity": do_obj.grn_ids.move_ids_without_package.quantity_done,
                "accepted_quantity": do_obj.grn_ids.move_ids_without_package.quantity_done - do_obj.return_quantity.return_qty,
                "do_products": data
            }
            return delivery_order
        return {"result": "No records found"}

    @http.route('/api/v1/delivery_orders/create', auth='user', type='json', csrf=False, cors="*")
    def do_create(self, **request_data):
        if http.request.jsonrequest:
            if request_data.get('sale_id'):
                sale_obj = http.request.env['sale.order'].browse(request_data.get('sale_id'))
                data = sale_obj.action_confirm()
                print(data)
                if data:
                    print(sale_obj.id)
                    do_obj = http.request.env['stock.picking'].search_read([('sale_id', '=', sale_obj.id)],
                                                                                  limit=1)
                    return {'status': True, 'do': do_obj}
                else:
                    return {'status': False, 'error': 'Something went wrong'}
            elif request_data.get('asn_ids'):
                grn_lines = request_data.get('grn_lines')
                request_data.pop('grn_lines')
                picking_type = http.request.env['stock.picking.type'].search([('name', 'ilike', 'grn')],
                                                                                    limit=1)
                request_data['picking_type_id'] = picking_type.id
                grn_obj = http.request.env['stock.picking'].create(request_data)
                if grn_lines:
                    line_ids = []
                    for grn_line in grn_lines:
                        grn_line['picking_id'] = grn_obj.id
                        grn_line['product_uom'] = 1
                        grn_line_obj = http.request.env['stock.move'].create(grn_line)
                        line_ids.append(grn_line_obj.id)
                    grn_obj.write({'move_ids_without_package': line_ids})
                return {'status': True, 'grn_id': grn_obj.id}
            else:
                return {'status': False, 'error': 'No sale id passed'}

    @http.route('/api/v1/internal_transfers', auth='user', type='json', csrf=False, cors="*")
    def it_list(self, limit=20, offset=0, domain=None, order='', **kwargs):
        data = []
        if kwargs.get('search_query'):
            data = [('name', 'ilike', kwargs.get('search_query'))]
        internal_transfers = http.request.env['stock.picking'].search(domain or data, limit=limit, offset=offset,
                                                                             order=order)
        if internal_transfers:
            data = []
            for internal_transfer in internal_transfers:
                data.append({
                    "internal_transfer_id": internal_transfer.id,
                    "internal_transfer_name": internal_transfer.name,
                    "delivery_location": internal_transfer.location_id.name,
                    "sender_location": internal_transfer.partner_id.name,
                    "state": internal_transfer.state,
                })
            return data
        else:
            return []

    @http.route('/api/v1/internal_transfers/<int:do_id>', auth='user', type='json', csrf=False, cors="*")
    def it_view(self, do_id):
        it_obj = http.request.env['stock.picking'].browse(do_id)
        if it_obj:
            data = []
            for it_line in it_obj.move_ids_without_package:
                data.append({
                    "id": it_line.id,
                    "product_id": it_line.product_id.id,
                    "name": it_line.product_id.name,
                    "product_uom_qty": it_line.product_uom_qty,
                    "quantity_done": it_line.quantity_done,
                    "lot_ids": it_line.lot_ids.name,
                    "description_picking": it_line.description_picking,
                    "date": it_line.date,
                    "product_uom": it_line.product_uom.name,
                    "date_deadline": it_line.date_deadline,
                    "location_id": it_line.location_id.id,
                    "location_dest_id": it_line.location_dest_id.id
                })
            internal_transfer = {
                "internal_transfer_id": it_obj.id,
                "internal_transfer_name": it_obj.name,
                "created_date": it_obj.create_date,
                "start_date": it_obj.date,
                "validity_date": it_obj.date_done,
                "cost": it_obj.carrier_price,
                "ist_delivered_location": {
                    "id": it_obj.location_id.id,
                    "name": it_obj.location_id.name,
                    "parent_location_name": it_obj.location_id.location_id.name,
                    "phone": it_obj.location_id.location_id.company_id.phone,
                    "email": it_obj.location_id.location_id.company_id.email,
                    "gst": it_obj.location_id.location_id.company_id.vat,
                    "address": str(it_obj.location_id.company_id.street)
                               + ',' + str(it_obj.location_id.company_id.street2)
                               + ',' + str(it_obj.location_id.company_id.city)
                               + ',' + str(it_obj.location_id.company_id.state_id.name)
                               + ',' + str(it_obj.location_id.company_id.country_id.name)
                               + ',' + str(it_obj.location_id.company_id.zip),
                },
                "ist_destination_location": {
                    "id": it_obj.location_dest_id.id,
                    "name": it_obj.location_dest_id.name,
                    "parent_location_name": it_obj.location_dest_id.location_id.name,
                    "phone": it_obj.location_dest_id.location_id.company_id.phone,
                    "email": it_obj.location_dest_id.location_id.company_id.email,
                    "gst": it_obj.location_dest_id.location_id.company_id.vat,
                    "address": str(it_obj.location_dest_id.company_id.street)
                               + ',' + str(it_obj.location_dest_id.company_id.street2)
                               + ',' + str(it_obj.location_dest_id.company_id.city)
                               + ',' + str(it_obj.location_dest_id.company_id.state_id.name)
                               + ',' + str(it_obj.location_dest_id.company_id.country_id.name)
                               + ',' + str(it_obj.location_dest_id.company_id.zip),
                },
                "ist_sender_location": {
                    "id": it_obj.partner_id.id,
                    "name": it_obj.partner_id.name,
                    "phone": it_obj.partner_id.phone,
                    "email": it_obj.partner_id.email,
                    "gst": it_obj.partner_id.vat,
                    "address": str(it_obj.partner_id.street)
                               + ',' + str(it_obj.partner_id.street2)
                               + ',' + str(it_obj.partner_id.city)
                               + ',' + str(it_obj.partner_id.state_id.name)
                               + ',' + str(it_obj.partner_id.country_id.name)
                               + ',' + str(it_obj.partner_id.zip),
                },
                "notes": it_obj.note,
                "delivery_location": it_obj.location_id.name,
                "sender_location": it_obj.partner_id.name,
                "state": it_obj.state,
                "move_type": it_obj.move_type,
                "carrier_id": it_obj.carrier_id.name,
                "user_id": it_obj.user_id.name,
                "group_id": it_obj.group_id.name,
                "carrier_tracking": it_obj.carrier_tracking_ref,
                "it_products": data
            }

            return internal_transfer
        return {"result": "No records found"}

    @http.route('/api/v1/internal_transfers/create', auth='user', type='json', csrf=False, cors="*")
    def internal_transfers_create(self, **request_data):
        if http.request.jsonrequest:
            if request_data.get('location_id'):
                it_lines = request_data.get('it_lines')
                request_data.pop('it_lines')
                picking_type = http.request.env['stock.picking.type'].search(
                    [('name', 'ilike', 'Internal Transfers')],
                    limit=1)
                request_data['picking_type_id'] = picking_type.id
                it_obj = http.request.env['stock.picking'].create(request_data)
                if it_lines:
                    line_ids = []
                    for it_line in it_lines:
                        it_line['picking_id'] = it_obj.id
                        it_line['product_uom'] = 1
                        it_line_obj = http.request.env['stock.move'].create(it_line)
                        line_ids.append(it_line_obj.id)
                    it_obj.write({'move_ids_without_package': line_ids})
                return {'status': True, 'internal_transfer_id': it_obj.id}
            else:
                return {'status': False, 'error': 'No location id passed'}

    @http.route('/api/v1/internal_transfers/<int:id>/delete', auth='user', type='json', csrf=False, cors="*")
    def internal_transfers_delete(self, id):
        internal_transfers_delete = http.request.env['stock.picking'].search([('id', '=', id)])
        if internal_transfers_delete:
            if internal_transfers_delete.state == "draft":
                for it_ids in internal_transfers_delete.move_ids_without_package:
                    it_ids.unlink()
                internal_transfers_delete.unlink()
                return {"Status": "Deleted", "Deleted id": internal_transfers_delete.id}
            else:
                return {"status": "Order can't be delete as it's status is not in draft",
                        "id": internal_transfers_delete.id}
        else:
            return {"status": "Data Not Found"}

    # @http.route('/api/v1/grn/<int:grn_id>/edit', auth='public', type='json', csrf=False, cors="*")
    # def grn_edit(self, grn_id, **kwargs):
    #     if kwargs.get('asn_ids'):
    #         grn_line_items = kwargs.get('grn_lines')
    #         kwargs.pop('grn_lines')
    #         grn_update = http.request.env['stock.picking'].sudo().search([("id", "=", grn_id)])
    #         grn_update.write(kwargs)
    #
    #         if grn_line_items:
    #             grn_line_ids = []
    #             for grn_line in grn_line_items:
    #                 grn_line['picking_id'] = grn_update.id
    #                 grn_line['product_uom'] = 1
    #                 if grn_line.get('id'):
    #                     grn_lines_update = http.request.env['stock.move'].sudo().search([("id", "=",
    #                                                                                       grn_line.get('id'))])
    #                     grn_lines_update.write(grn_line)
    #                     grn_line_ids.append(grn_lines_update.id)
    #                 else:
    #                     grn_lines_update = http.request.env['stock.move'].sudo().create(grn_line)
    #                     grn_line_ids.append(grn_lines_update.id)
    #         grn_update.write({"grn_lines": grn_line_ids})
    #         return {"success": True, "status": "Updated", "grn": grn_update.id}

    @http.route('/api/v1/grn/<int:grn_id>/edit', auth='user', type='json', csrf=False, cors="*")
    def grn_edit(self, grn_id, **kwargs):
        if kwargs.get('asn_ids'):
            grn_line_items = kwargs.get('grn_lines')
            kwargs.pop('grn_lines')
            grn_update = http.request.env['stock.picking'].search([("id", "=", grn_id)])
            if grn_update:
                grn_update.write(kwargs)
            if grn_line_items:
                for grn_line in grn_line_items:
                    grn_line['picking_id'] = grn_update.id
                    grn_line['product_uom'] = 1
                    if grn_line.get('id'):
                        grn_lines_update = http.request.env['stock.move'].search([("id", "=",
                                                                                          grn_line.get('id'))])
                        if grn_lines_update:
                            grn_lines_update.write(grn_line)
                    else:
                        grn_lines_update = http.request.env['stock.move'].create(grn_line)
            return {"success": True,
                    "status": "Updated",
                    "grn": grn_update.id}

    @http.route('/api/v1/grn/<int:grn_id>/delete', auth='user', type='json', csrf=False, cors="*")
    def grn_delete(self, grn_id):
        grn_delete = http.request.env['stock.picking'].search([("id", "=", grn_id)])
        if grn_delete:
            if grn_delete.state == "draft":
                for line_ids in grn_delete.move_lines:
                    line_ids.unlink()
                grn_delete.unlink()
                return {"status": "grn deleted", "result": grn_delete.id}
            else:
                return {"status": "order can't be deleted because its status is not in draft ", "result": grn_delete.id}
        else:
            return {"status": "no data found for delete"}