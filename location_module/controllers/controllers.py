# -*- coding: utf-8 -*-
from odoo import http


class LocationModule(http.Controller):
    @http.route('/api/v1/locations', auth='user', type='json', csrf=False, cors="*")
    def location_list(self, limit=20, offset=0, order='',  domain=[], **request_data):
        data = []
        if request_data.get("search_query"):
            data = [('name', 'ilike', request_data.get("search_query"))]
        location_list = http.request.env['stock.location'].search(data or domain, limit=limit,
                                                            offset=offset, order=order)

        if location_list:
            response = []
            for location in location_list:
                response.append({
                    'id': location.id,
                    'name': location.name,
                    'address': location.company_id.street,
                    'type': location.usage,
                    'zip': location.company_id.zip,
                    'contact': location.company_id.phone,
                })
            return response
        else:
            return []

    @http.route('/api/v1/locations/<int:location_id>', auth='user', type='json', csrf=False, cors="*")
    def location_view(self, location_id):
        location_view = http.request.env['stock.location'].browse(location_id)
        if location_view:
            response = {
                'id': location_view.id,
                'location_name': location_view.name,
                'location_type': location_view.usage,
                'location_id': location_view.location_id.id,
                'parent_location': location_view.location_id.complete_name,
                'address1': location_view.company_id.street,
                'address2': location_view.company_id.street2,
                'latitude': location_view.latitude,
                'zip': location_view.company_id.zip,
                'longitude': location_view.longitude,
                'state': location_view.company_id.state_id.display_name,
                'country': location_view.company_id.country_id.name,
                'external_id': location_view.external_id
            }
            return response

    @http.route('/api/v1/locations/search/<string:query>', auth='user', type='json', csrf=False, cors="*")
    def location_search(self, query=""):
        domain = [('name', 'ilike', query)]
        location_search = http.request.env['stock.location'].search(domain)
        if location_search:
            response = []
            for location in location_search:
                response.append({
                    'id': location.id,
                    'name': location.name,
                    'address': location.company_id.street,
                    'type': location.usage,
                    'zip': location.company_id.zip,
                    'contact': location.company_id.phone,
                })
            return response

    @http.route('/api/v1/locations/create', auth='user', type='json', csrf=False, cors="*")
    def location_create(self, **request_data):
        if http.request.jsonrequest:
            company_address = request_data.get('company_address')
            request_data.pop('company_address')
            company_address_obj = http.request.env['res.company'].create(company_address)
            request_data['company_id'] = company_address_obj.id
            location = http.request.env['stock.location'].create(request_data)
            response = {'status': True, 'location_id': location.id, "company":company_address_obj.id}
            return response

    @http.route('/api/v1/locations/country/search/<string:query>', auth='user', type='json', csrf=False, cors="*")
    def country_search(self, query=""):
        domain = [('name', 'ilike', query)]
        country_search = http.request.env['res.country'].search(domain)
        if country_search:
            response = []
            for country in country_search:
                response.append({
                    'id': country.id,
                    'name': country.name
                })
            return response

    @http.route('/api/v1/locations/state/<int:country_id>', auth='user', type='json', csrf=False, cors="*")
    def state_search(self, country_id):
        domain = [('id', 'ilike', country_id)]
        state_search = http.request.env['res.country.state'].search(domain)
        if state_search:
            response = []
            for state in state_search:
                response.append({
                    'id': state.id,
                    'name': state.name
                })
            return response

    @http.route('/api/v1/locations/<int:id>/edit', type="json", cors='*', auth='user', csrf=False)
    def locations_edit(self, id, **kw):
        location = http.request.env['stock.location'].search([("id", "=", id)])
        if location:
            obj = kw.pop("company_address")
            location.write(kw)
            if obj:
                company_address = http.request.env['res.company'].search([("id", "=", location.company_id.id)])
                company_address.write(obj)
            return {"status": "Updated", "updated": "True", "result": location.id}
        else:
            return {"status": "No Data Found"}

    @http.route('/api/v1/locations/<int:id>/delete', type="json", cors='*', auth='user', csrf=False)
    def location_delete(self, id, **kw):
        location_delete = http.request.env['stock.location'].search([("id", "=", id)])
        if location_delete:
            location_delete.unlink()
            return {"status": "Deleted", "Deleted id": location_delete.id}
        else:
            return {"status": "no data found to delete"}





#   @http.route('/location_module/location_module/objects', auth='public')
#     def list(self, **kw):
#         return http.request.render('location_module.listing', {
#             'root': '/location_module/location_module',
#             'objects': http.request.env['location_module.location_module'].search([]),
#         })

#   @http.route('/location_module/location_module/objects/<model("location_module.location_module"):obj>', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('location_module.object', {
#             'object': obj
#         })
