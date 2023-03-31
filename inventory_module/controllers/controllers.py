from odoo import http


class Inventory(http.Controller):

    @http.route('/api/v1/inventory/<string:query>', auth="public", type="json", csrf=False, cors='*')
    def get_locations(self, query, **kw):
        if query == 'locations':
            fields = [
                "id",
                "is_outdated",
                "tracking",
                "inventory_quantity_set",
                "location_id",
                "product_id",
                "product_categ_id",
                "lot_id",
                "package_id",
                "owner_id",
                "available_quantity",
                "quantity",
                "product_uom_id",
                "accounting_date",
                "inventory_quantity",
                "inventory_diff_quantity",
                "inventory_date",
                "user_id",
                "company_id"
            ]
            groupby = ["location_id"]
            quantity_group = http.request.env['stock.quant'].sudo().read_group([], fields=fields, groupby=groupby, lazy=False)
            data = []
            if quantity_group:
                for quant in quantity_group:
                    location_view = http.request.env['stock.location'].sudo().browse(quant.get('location_id')[0])
                    data.append({
                        "inventory_quantity": quant.get('inventory_quantity'),
                        'location_name': location_view.name,
                        'location_type': location_view.usage,
                        'location_id': location_view.location_id.id,
                        'parent_location': location_view.location_id.complete_name,
                        'address': location_view.company_id.street,
                        'latitude': location_view.posy,
                        'zip': location_view.company_id.zip,
                        'longitude': location_view.posx,
                        'state': location_view.company_id.state_id.display_name,
                        'country': location_view.company_id.country_id.name
                    })
                return data
        elif query == 'products':
            fields = [
                "id",
                "is_outdated",
                "tracking",
                "inventory_quantity_set",
                "location_id",
                "product_id",
                "product_categ_id",
                "lot_id",
                "package_id",
                "owner_id",
                "available_quantity",
                "quantity",
                "product_uom_id",
                "accounting_date",
                "inventory_quantity",
                "inventory_diff_quantity",
                "inventory_date",
                "user_id",
                "company_id"
            ]
            groupby = ["product_id"]
            quantity_group = http.request.env['stock.quant'].sudo().read_group([], fields=fields, groupby=groupby, lazy=False)
            data = []
            if quantity_group:
                for quant in quantity_group:
                    product_view = http.request.env['product.product'].sudo().browse(quant.get('product_id')[0])
                    data.append({
                        "total_quantity": quant.get('inventory_quantity'),
                        'product_name': product_view.name,
                        'sku_id': product_view.default_code,
                        'category': product_view.categ_id.name
                    })
                return data
        else:
            data = {"response": "No Data Found"}
            return data

    @http.route('/api/v1/inventory/analytics', auth="public", type="json", csrf=False, cors='*')
    def get_locations_reports(self, **request_data):
        date_filter_start = request_data.get('date_start')
        date_filter_end = request_data.get('date_end')
        location_type = request_data.get('location_type')
        fields = ["__count", "quantity:sum", "reserved_quantity:sum", "inventory_quantity:sum"]
        domain = ["&",["location_id.usage","=",location_type],"&",["in_date",">=",date_filter_start],["in_date","<=",date_filter_end]]
        groupby = ["in_date:day", "location_id"]
        quantity_group = http.request.env['stock.quant'].sudo().read_group(domain=domain, fields=fields, groupby=groupby,
                                                                           lazy=False)
        print(quantity_group)
        data = []
        if quantity_group:
            for quant in quantity_group:
                data.append({
                    "day": quant.get('in_date:day'),
                    "location_id": quant.get('location_id'),
                    "quantity": quant.get('quantity'),
                    "reserved_quantity": quant.get('reserved_quantity'),
                    # "available_quantity": quant.get('available_quantity'),
                    "inventory_quantity": quant.get('inventory_quantity'),
                    "count": quant.get('__count'),
                })
            return data
        else:
            data = {"response": "No Data Found"}
            return data

