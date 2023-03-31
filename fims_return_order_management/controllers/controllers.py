from odoo import http


class ReturnOrders(http.Controller):
    # return all the data in return order management
    @http.route('/api/v1/returns', auth='user', type='json', csrf=False, cors='*')
    def get_returns_list(self,limit=20, offset=0, order='', domain=None, **request_data):
        data = []
        if request_data.get("sale_ids"):
            data = [("sale_id", "in", request_data.get("sale_ids"))]
        elif request_data.get("purchase_ids"):
            data = [("purchase_id", "in", request_data.get("purchase_ids"))]
        elif request_data.get("internal_transfer_ids"):
            data = [("grn_id", "in", request_data.get("internal_transfer_ids"))]
        elif request_data.get("grn_ids"):
            data = [("grn_id", "in", request_data.get("grn_ids"))]
        elif request_data.get("asn_ids"):
            data = [("asn_id", "in", request_data.get("asn_ids"))]
        elif request_data.get("search_query"):
            data = [('number', 'ilike', request_data.get("search_query"))]
        products = http.request.env['fims.rom'].search(data or domain, limit=limit,
                                                             offset=offset, order=order)
        data = []
        if products:
            for product in products:
                data.append({
                    'id': product.id,
                    'partner': product.partner_id.display_name,
                    'asn_id': product.asn_id.id,
                    'grn_id': product.grn_id.id,
                    'purchase_id': product.purchase_id.id,
                    'sale_id': product.sale_id.id,
                    'internal_transfer_id': product.return_picking_id.id,
                    'product_name': product.display_name,
                    'sale_order': product.sale_id.display_name,
                    'grn_number': product.grn_number.display_name,
                    'ordered_quantity': product.ordered_quantity,
                    'received_quantity': product.received_quantity,
                    'accepted_quantity': product.accepted_quantity,
                    'reason': product.description,
                    'purchase_order': product.purchase_id.display_name,
                    'delivery_order': product.delivery_id.display_name,
                    'picking': product.picking_id.display_name,
                    'create_date': product.picking_id.create_uid.create_date,
                    'date': product.date,
                    'state': product.state,
                })
            return data
        else:
            return []

    # returns a list of data of products which contains sales order
    @http.route('/api/v1/sales_returns', auth='user', type='json', csrf=False, cors='*')
    def get_sales_returns_list(self, **kw):
        products = http.request.env['fims.rom'].search([])
        objects = []
        if products:
            for product in products:
                if product.sale_id:
                    objects.append({
                        'id': product.id,
                        'partner': product.partner_id.display_name,
                        'sale_order': product.sale_id.display_name,
                        'picking': product.picking_id.display_name,
                        'reason': product.description,
                        # 'ordered_qty': product.sale_id.cart_quantity,
                        'date': product.picking_id.create_uid.create_date,
                        'state': product.state
                    })
            return objects
        else:
            return objects

    # returns list of data which are in delivery orders
    @http.route('/api/v1/delivery_returns', auth='user', type='json', csrf=False, cors="*")
    def delivery_returns_list(self, **kw):
        delivery_returns = http.request.env['fims.rom'].search([])
        data = []
        if delivery_returns:
            for delivery in delivery_returns:
                if delivery.delivery_id:
                    data.append({
                        'delivery_id': delivery.id,
                        'partner': delivery.partner_id.display_name,
                        'sale_order': delivery.sale_id.display_name,
                        'purchase_order': delivery.purchase_id.display_name,
                        'delivery_order': delivery.delivery_id.display_name,
                        'picking': delivery.picking_id.display_name,
                        'date': delivery.date,
                        'state': delivery.state
                    })
            return data
        else:
            return data

    # return list of products which have purchase id
    @http.route('/api/v1/purchase_returns', auth='user', type='json', csrf=False, cors="*")
    def get_purchase_returns_list(self, **kw):
        purchase_returns = http.request.env['fims.rom'].search([])
        data = []
        if purchase_returns:
            for purchase_return in purchase_returns:
                if purchase_return.purchase_id:
                    total = 0
                    for line in purchase_return.purchase_id.order_line:
                        total += line.product_qty
                    data.append({
                        'purchase_return_id': purchase_return.id,
                        'partner': purchase_return.partner_id.display_name,
                        'purchase_order': purchase_return.purchase_id.display_name,
                        'picking': purchase_return.picking_id.display_name,
                        'ordered_qty': total,
                        'date': purchase_return.create_date,
                        'state': purchase_return.state
                    })
            return data
        else:
            response = {'status': "No Data Available"}
            return response

    # return detail data of a single product using the id
    @http.route('/api/v1/returns/<int:id>', auth='user', type='json', csrf=False, cors='*')
    def return_view(self, id, **kw):
        sale_return = http.request.env['fims.rom'].search([("id", "=", id)])
        data =[]
        if sale_return:
            repair_product_data = []
            rom_product_data = []
            for product in sale_return.rom_repair_line_ids:
                repair_product_data.append({
                    'ids': product.id,
                    'id': product.product_id.id,
                    'product_id': product.product_id.display_name,
                    'name': product.display_name,
                    'quantity': product.quantity,
                    'uom_id': product.uom_id.display_name,
                    'price_unit': product.price_unit,
                    'tax_ids': product.tax_ids.display_name
                })
            for product in sale_return.rom_product_line_ids:
                rom_product_data.append({
                    'id': product.id,
                    'product_id': product.product_id.id,
                    'product_name': product.product_id.display_name,
                    'sku_id': product.product_id.default_code,
                    'replace_product_id': product.replace_product_id.display_name,
                    'replace_quantity': product.replace_quantity,
                    'manage_invoice': product.manage_invoice,
                    'delivery_qty': product.delivered_qty,
                    'return_qty': product.return_qty,
                    'received_qty': product.received_qty,
                    'action_type': product.action_type
                })
            data = {
                'state': sale_return.state,
                'number': sale_return.display_name,
                'product_name': sale_return.display_name,
                'sale_order': sale_return.sale_id.display_name,
                'sale_ids': sale_return.sale_id.id,
                'asn_id': sale_return.asn_id.id,
                'grn_id': sale_return.grn_id.id,
                'purchase_id': sale_return.purchase_id.id,
                'internal_transfer_id': sale_return.return_picking_id.id,
                'grn_number': sale_return.grn_number.display_name,
                'ordered_quantity': sale_return.ordered_quantity,
                'received_quantity': sale_return.received_quantity,
                'accepted_quantity': sale_return.accepted_quantity,
                'reason': sale_return.description,
                'purchase_order': sale_return.purchase_id.display_name,
                'sale_id': sale_return.sale_id.display_name,
                'picking_id': sale_return.picking_id.display_name,
                'partner_id': sale_return.partner_id.display_name,
                'date': sale_return.date,
                'email': sale_return.email,
                'phone': sale_return.phone,
                'user_id': sale_return.user_id.display_name,
                'location_id': sale_return.location_id.display_name,
                'repair_product_data': repair_product_data,
                'rom_product_data': rom_product_data,
            }
            return data
        else:
            return data

    # create return_product in return order management using json data
    @http.route('/api/v1/sales_returns/create', auth='user', type='json', csrf=False, cors='*')
    def sales_return_create(self, **request_data):
        if http.request.jsonrequest:
            if len(request_data) == 0:
                response = {"status": "No Data Is Available"}
                return response
            elif request_data.get('sales_order_id'):
                pic_obj = {}
                return_lines = request_data.get('return_lines')
                request_data.pop('return_lines')
                picking_type = http.request.env['stock.picking.type'].search([('name', 'ilike', 'Returns')],
                                                                                         limit=1)
                pic_obj['picking_type_id'] = picking_type.id
                pic_obj['partner_id'] = request_data['partner_id']
                pic_obj['location_dest_id'] = request_data['location_dest_id']
                pic_obj['location_id'] = request_data['location_dest_id']
                pic_obj['scheduled_date'] = request_data['scheduled_date']
                req_obj = http.request.env['stock.picking'].create(pic_obj)
                ret_obj = {}
                ret_obj['picking_id'] = req_obj.id
                ret_obj['sale_id'] = request_data['sales_order_id']
                ret_obj['asn_id'] = request_data['asn_id']
                ret_obj['grn_id'] = request_data['grn_id']
                ret_obj['ordered_quantity'] = request_data['ordered_quantity']
                ret_obj['received_quantity'] = request_data['received_quantity']
                ret_obj['accepted_quantity'] = request_data['accepted_quantity']
                ret_obj['email'] = request_data['email']
                ret_obj['phone'] = request_data['phone']
                ret_obj['description'] = request_data['reason']
                ret_obj['user_id'] = request_data['user_id']
                sale_returns_obj = http.request.env['fims.rom'].create(ret_obj)
                if return_lines:
                    line_ids = []
                    for return_line in return_lines:
                        pic_line = {}
                        pic_line['picking_id'] = req_obj.id
                        pic_line['product_uom'] = 1
                        pic_line['product_id'] = return_line['product_id']
                        pic_line['name'] = return_line['name']
                        pic_line['description_picking'] = return_line['description_picking']
                        pic_line['product_uom_qty'] = return_line['product_uom_qty']
                        pic_line['location_dest_id'] = request_data['location_dest_id']
                        pic_line['location_id'] = request_data['location_dest_id']
                        pic_line_obj = http.request.env['stock.move'].create(pic_line)
                        ret_line = {}
                        ret_line['product_id'] = return_line['product_id']
                        ret_line['rom_id'] = sale_returns_obj.id
                        ret_line['replace_quantity'] = return_line['replace_quantity']
                        ret_line['delivered_qty'] = return_line['delivered_qty']
                        ret_line['return_qty'] = return_line['return_qty']
                        return_line_obj = http.request.env['rom.product.lines'].create(ret_line)
                        line_ids.append(return_line_obj.id)
                    sale_returns_obj.write({'rom_product_line_ids': line_ids})

                return {'status': True, 'return_id': sale_returns_obj.id }
            else:
                return {"status": "No Sales ID passed"}

    # create return_product in return order management using json data
    @http.route('/api/v1/purchase_returns/create', auth='user', type='json', csrf=False, cors='*')
    def purchase_return_create(self, **request_data):
        if http.request.jsonrequest:
            if len(request_data) == 0:
                response = {"status": "No Data Is Available"}
                return response
            elif request_data.get('purchase_order_id'):
                pic_obj = {}
                return_lines = request_data.get('return_lines')
                request_data.pop('return_lines')
                picking_type = http.request.env['stock.picking.type'].search([('name', 'ilike', 'Returns')],
                                                                                    limit=1)
                pic_obj['picking_type_id'] = picking_type.id
                pic_obj['partner_id'] = request_data['partner_id']
                pic_obj['location_dest_id'] = request_data['location_dest_id']
                pic_obj['location_id'] = request_data['location_dest_id']
                pic_obj['scheduled_date'] = request_data['scheduled_date']
                req_obj = http.request.env['stock.picking'].create(pic_obj)
                ret_obj = {}
                ret_obj['picking_id'] = req_obj.id
                ret_obj['purchase_id'] = request_data['purchase_order_id']
                ret_obj['asn_id'] = request_data['asn_id']
                ret_obj['grn_id'] = request_data['grn_id']
                ret_obj['ordered_quantity'] = request_data['ordered_quantity'],
                ret_obj['received_quantity'] = request_data['received_quantity'],
                ret_obj['accepted_quantity'] = request_data['accepted_quantity'],
                ret_obj['email'] = request_data['email']
                ret_obj['phone'] = request_data['phone']
                ret_obj['description'] = request_data['reason']
                ret_obj['user_id'] = request_data['user_id']
                purchase_returns_obj = http.request.env['fims.rom'].create(ret_obj)
                if return_lines:
                    line_ids = []
                    for return_line in return_lines:
                        pic_line = {}
                        pic_line['picking_id'] = req_obj.id
                        pic_line['product_uom'] = 1
                        pic_line['product_id'] = return_line['product_id']
                        pic_line['name'] = return_line['name']
                        pic_line['description_picking'] = return_line['description_picking']
                        pic_line['product_uom_qty'] = return_line['product_uom_qty']
                        pic_line['location_dest_id'] = request_data['location_dest_id']
                        pic_line['location_id'] = request_data['location_dest_id']
                        pic_line_obj = http.request.env['stock.move'].create(pic_line)
                        ret_line = {}
                        ret_line['product_id'] = return_line['product_id']
                        ret_line['rom_id'] = purchase_returns_obj.id
                        ret_line['replace_quantity'] = return_line['replace_quantity']
                        ret_line['delivered_qty'] = return_line['delivered_qty']
                        ret_line['return_qty'] = return_line['return_qty']
                        return_line_obj = http.request.env['rom.product.lines'].create(ret_line)
                        line_ids.append(return_line_obj.id)
                    purchase_returns_obj.write({'rom_product_line_ids': line_ids})

                return {'status': True, 'return_id': purchase_returns_obj.id}
            else:
                return {"status": "No Sales ID passed"}

    @http.route('/api/v1/sales_returns/<int:id>/edit', type='json', auth='user', cors='*', csrf=False)
    def sales_return_edit(self, id, **request_data):
        if http.request.jsonrequest:
            return_edit = http.request.env['fims.rom'].search([("id", "=", id)])
            if return_edit:
                product_obj = []
                rom_product_line_ids = request_data.pop("rom_product_line_ids")
                return_edit.write(request_data)
                for obj in rom_product_line_ids:
                    if obj.get('id'):
                        product_objects = return_edit.rom_product_line_ids.search([("id", "=", obj.get('id'))])
                        product_objects.write(dict(obj))
                        product_obj.append(product_objects.id)
                    elif obj.get("product_id"):
                        obj['rom_id'] = return_edit.id
                        return_line_obj = http.request.env['rom.product.lines'].create(obj)
                        product_obj.append(return_line_obj.id)
                return_edit.write({"rom_product_line_ids": product_obj})
                return {"success": True, "status": "Updated", "result": return_edit.id}

    @http.route('/api/v1/purchase_returns/<int:id>/edit', auth='user', type='json', csrf=False, cors='*')
    def purchase_return_edit(self, id, **request_data):
        if http.request.jsonrequest:
            return_edit = http.request.env['fims.rom'].search([("id", "=", id)])
            if return_edit:
                product_obj = []
                rom_product_line_ids = request_data.pop("rom_product_line_ids")
                return_edit.write(request_data)
                for obj in rom_product_line_ids:
                    if obj.get('id'):
                        product_objects = return_edit.rom_product_line_ids.search([("id", "=", obj.get('id'))])
                        product_objects.write(dict(obj))
                        product_obj.append(product_objects.id)
                    elif obj.get("product_id"):
                        obj['rom_id'] = return_edit.id
                        return_line_obj = http.request.env['rom.product.lines'].create(obj)
                        product_obj.append(return_line_obj.id)
                # if return_edit.state == "new":
                #     for del_obj in return_edit.rom_product_line_ids.ids:
                #         if del_obj not in product_obj:
                #             deleted_obj = return_edit.rom_product_line_ids.search([("id", "=", del_obj)])
                #             deleted_obj.unlink()
                return_edit.write({"rom_product_line_ids": product_obj})
                return {"status": "True", "updated": "True", "result": return_edit.id}
            else:
                return {"status": "Not Updated"}

    @http.route('/api/v1/sales_returns/<int:id>/delete', auth='user', type='json', csrf=False, cors="*")
    def return_delete(self, id, **kw):
        return_delete = http.request.env['fims.rom'].search([('id', '=', id)])
        if return_delete:
            if return_delete.state == "new":
                for line_ids in return_delete.rom_product_line_ids:
                    line_ids.unlink()
                return_delete.unlink()
                return {"status": "Deleted", "Deleted id": return_delete.id}
            else:
                return {"status": "You can not delete processed ROM", "id": return_delete.id}
        else:
            return {"status": "No data found to delete"}
