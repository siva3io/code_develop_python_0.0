# -*- coding: utf-8 -*-
from odoo import http
from odoo.http import request


class ASNManagementModule(http.Controller):
    @http.route('/api/v1/asn', auth='user', type='json', csrf=False, cors="*")
    def asn_list(self, limit=20, offset=0, order='', domain=None, **request_data):
        data = []
        if request_data.get("purchase_ids"):
            data = [("purchase_id", "in", request_data.get("purchase_ids"))]
        elif request_data.get("internal_transfer_ids"):
            data = [("picking_id", "in", request_data.get("internal_transfer_ids"))]
        elif request_data.get("location_ids"):
            data = [("location_id", "in", request_data.get("location_ids"))]
        elif request_data.get("search_query"):
            data = [('name', 'ilike', request_data.get("search_query"))]
        asn_list = http.request.env['asn.asn'].search(data or domain, limit=limit,
                                                             offset=offset, order=order)
        data = []
        if asn_list:
            for asn in asn_list:
                data.append({
                    "asn_id": asn.id,
                    "asn_number": asn.asn_number,
                    "drop_location": {
                        "id": asn.drop_location_id.id,
                        "name": asn.drop_location_id.name
                    },
                    "pickup_location": {
                        "id": asn.pickup_location_id.id,
                        "name": asn.pickup_location_id.name
                    },
                    "asn_status": asn.state,
                })
            return data
        else:
            return data

    

    @http.route('/api/v1/asn/create', auth='user', type='json', csrf=False, cors="*")
    def asn_create(self, **request_data):
        if http.request.jsonrequest:
            asn_lines = request_data.get('asn_lines')
            request_data.pop('asn_lines')
            record_ids = http.request.env['asn.asn'].search([], order='id desc', limit=1)
            last_id = int(record_ids.id)
            request_data['name'] = "ASN0" + str((last_id + 1))
            request_data['asn_number'] = request_data['name']
            asn_obj = request.env['asn.asn'].create(request_data)
            if asn_lines:
                data = []
                for asn_line in asn_lines:
                    print(asn_obj.id)
                    asn_line['asn_id'] = asn_obj.id
                    asn_lines_response = http.request.env['asn.asn.line'].create(asn_line)
                    data.append(asn_lines_response.id)
            response = {'status': True, 'asn_id': asn_obj.id, 'line_ids': data}
            return response

    @http.route('/api/v1/asn/search/<string:query>', auth='user', type='json', csrf=False, cors="*")
    def asn_search(self, query=""):
        domain = [('name', 'ilike', query)]
        asn_search = http.request.env['asn.asn'].search(domain)
        if asn_search:
            response = []
            for asn in asn_search:
                response.append({
                    'id': asn.id,
                    'name': asn.name
                })
            return response

    @http.route('/api/v1/asn/<int:asn_id>/edit', auth='user', type='json', csrf=False, cors="*")
    def asn_edit(self, asn_id, **kw):
        asn_line_ids = kw.get('asn_lines')
        kw.pop('asn_lines')
        asn_update = http.request.env['asn.asn'].search([('id', '=', asn_id)])
        asn_update.write(kw)
        if asn_line_ids:
            for line_id in asn_line_ids:
                line_id['asn_id'] = asn_update.id
                asn_line_id = http.request.env['asn.asn.line'].search(
                    [('id', '=', line_id.get('id'))])
                if line_id.get('id'):
                    asn_line_id.write(line_id)
                else:
                    asn_line_id.create(line_id)
        return {'status': True, 'Success': 'Updated', 'result': asn_update.id}

    @http.route('/api/v1/asn/<int:id>/delete', auth='user', type='json', csrf=False, cors="*")
    def asn_delete(self, id):
        asn_delete = http.request.env['asn.asn'].search([('id', '=', id)])
        if asn_delete:
            for asn_line_ids in asn_delete.line_ids:
                asn_line_ids.unlink()
            asn_delete.unlink()
            return {"Status": "Deleted", "Deleted id": asn_delete.id}
        else:
            return {"status": "Data Not Found"}
