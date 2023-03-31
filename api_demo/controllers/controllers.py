from odoo import http, fields
from odoo.http import request
from odoo.tools.safe_eval import safe_eval
from odoo.addons.catalogue.controllers.controllers import Catalogue as main_controller


class ApiDemoController(main_controller):

    @http.route(['/demo', ], type='http', auth="public", website=False)
    def render_demo_form(self):
        # if request.env.user.has_group('abc.abc'):
        #     return request.render('http_routing.403')
        return self.render_form()

    def render_form(self):
        data = {
            'category': self.catalogue_category(),
            'marketplace': self.catalogue_marketplace()
        }
        return request.render("api_demo.demo_form", data)

    # @http.route(['/demo/products/<int:category_id>/<int:marketplace_id>', ], type='http', auth="public", website=False)
    # def render_demo_products(self, category_id, marketplace_id):
    #     data = self.catalogue_category_data(category_id, marketplace_id)
    #     return self.render_products(data)
    #
    # def render_products(self, data):
    #     return request.render("api_demo.demo_products", data)
