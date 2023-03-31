from odoo import http


class ScrapOrders(http.Controller):

    @http.route('/api/v1/scrap_orders/<int:id>', auth="user", type="json", csrf=False, cors='*')
    def get_scrap_detail_view(self, id, **kw):
        scrap_details = http.request.env['stock.scrap'].search([('id', '=', id)])
        if scrap_details:
            data = {
                'name': scrap_details.display_name,
                'scrap_qty': scrap_details.scrap_qty,
                'origin': scrap_details.origin,
                'date_done': scrap_details.date_done,
                'location_id': scrap_details.location_id.display_name,
                'scrap_location_id': scrap_details.scrap_location_id.display_name,
                'picking': scrap_details.picking_id.display_name,
                'company_id': scrap_details.company_id.display_name,
                'grn_number': scrap_details.grn_number.display_name,
                'ordered_units': scrap_details.ordered_units,
                'received_units': scrap_details.received_units,
                'state': scrap_details.state
                }
            return data
        else:
            response = {'status': 'no data found'}
            return response

    @http.route('/api/v1/scrap_orders', auth="user", type="json", csrf=False, cors='*')
    def get_scrap_orders(self, limit=20, offset=0, order="", domain=None, **kwargs):
        data = []
        if kwargs.get('purchase_ids'):
            data = [("purchase_id", "in", kwargs["purchase_ids"])]
        elif kwargs.get('picking_ids'):
            data = [("picking_id", "in", kwargs["picking_ids"])]
        elif kwargs.get('asn_ids'):
            data = [("asn_id", "in", kwargs["asn_ids"])]
        elif kwargs.get('grn_ids'):
            data = [("picking_id", "in", kwargs["grn_ids"])]
        elif kwargs.get("search_query"):
            data = [('name', 'ilike', kwargs.get("search_query"))]
        scrap_orders = http.request.env['stock.scrap'].search(data or domain, limit=limit, offset=offset,
                                                                     order=order)
        if scrap_orders:
            data = []
            for scraps in scrap_orders:
                data.append({
                    'id': scraps.id,
                    'sku_id': scraps.product_id.default_code,
                    'reference': scraps.name,
                    'date': scraps.create_date,
                    'product': scraps.product_id.display_name,
                    'location_id': scraps.location_id.display_name,
                    'scrap_location_id': scraps.scrap_location_id.display_name,
                    'quantity': scraps.scrap_qty,
                    'product_uom_id': scraps.product_uom_id.display_name,
                    'company': scraps.company_id.display_name,
                    'grn_number': scraps.grn_number.display_name,
                    'ordered_quantity': scraps.ordered_units,
                    'scrap_quantity': scraps.scrap_qty,
                    'status': scraps.state,
                    'reason': scraps.reason
                })
            return data
        else:
            response = {"status": "No Data Available"}
            return response

    @http.route('/api/v1/scrap_orders/create', auth='user', type='json', csrf=False, cors= '*')
    def scrap_orders_create(self, **kw):
        if http.request.jsonrequest:
            if len(kw) == 0:
                response = {"status": "No Data found for creation of Scrap Order"}
                return response
            else:
                kw['product_uom_id'] = 1
                scrap_create = http.request.env["stock.scrap"].create(kw)
                response = {"status":"scrap order created", "id": scrap_create.id}
                return response

    @http.route('/api/v1/scrap_orders/<int:scrap_id>/edit', auth="user", type="json", csrf=False, cors='*')
    def scrap_orders_update(self, scrap_id, **kw):
        if http.request.jsonrequest:
            if len(kw) == 0:
                response = {"status": "No Data found for update of Scrap Order"}
                return response
            scrap_update = http.request.env['stock.scrap'].search([('id', '=', scrap_id)])
        if scrap_update:
            scrap_update.write(kw)
            response = {'status': 'scrap order updated', 'result': scrap_update.id}
            return response

    @http.route('/api/v1/scrap_orders/<int:scrap_id>/delete', auth='user', type='json', csrf=False, cors='*')
    def scrap_orders_delete(self, scrap_id):
        scrap_delete = http.request.env['stock.scrap'].search([('id', '=', scrap_id)])
        if scrap_delete:
            response = {'status': 'You cannot delete a scrap which is done', 'result': scrap_delete.id}
            return response
        else:
            response = {"status": "no data found to delete"}
            return response
