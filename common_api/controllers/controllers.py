# -*- coding: utf-8 -*-
import traceback
from odoo.http import route, request, Controller, Response


class CommonApi(Controller):
    @route(['/api/v1/country/search/<string:query>',
            '/api/v1/country/search/<int:state_id>',
            '/api/v1/country/search'], type='json', auth="public", cors="*")
    def api_country_search(self, state_id=0, query=""):
        data = []
        try:
            if state_id:
                country_id = request.env(su=True)['res.country.state'].browse(state_id)
                data = country_id.country_id.name_get()
            else:
                country_ids = request.env(su=True)['res.country'].name_search(query)
                data = country_ids
        except Exception as e:
            traceback.print_exc()
        finally:
            return data

    @route(['/api/v1/state/search/<int:country_id>/<string:query>',
            '/api/v1/state/search/<int:country_id>',
            '/api/v1/state/search/<string:query>',
            '/api/v1/state/search'], type='json', auth="public", cors="*")
    def api_state_search(self, country_id=0, query=""):
        data = []
        try:
            domain = []
            if country_id:
                domain = [('country_id', '=', country_id)]
            state_ids = request.env(su=True)['res.country.state'].name_search(query, args=domain)
            data = state_ids
        except Exception as e:
            traceback.print_exc()
        finally:
            return data

    @route(['/api/v1/partner/search/<string:query>',
            '/api/v1/partner/search'], type='json', auth="public", cors="*")
    def api_partner_search(self, query=""):
        data = []
        try:
            # domain = [("is_company", "=", True)]
            domain = [('name', 'ilike', query)]
            partner_ids = request.env(su=True)['res.partner'].search(domain, limit=100)
            data = partner_ids.name_get()
        except Exception as e:
            traceback.print_exc()
        finally:
            return data

    @route(['/api/v1/partner-title/search/<string:query>',
            '/api/v1/partner-title/search'], type='json', auth="public", cors="*")
    def api_partner_title_search(self, query=""):
        data = []
        try:
            partner_title_ids = request.env(su=True)['res.partner.title'].name_search(query)
            data = partner_title_ids
        except Exception as e:
            traceback.print_exc()
        finally:
            return data

    @route(['/api/v1/partner-category/search/<string:query>',
            '/api/v1/partner-category/search'], type='json', auth="public", cors="*")
    def api_partner_category_search(self, query=""):
        data = []
        try:
            partner_category_ids = request.env(su=True)['res.partner.category'].name_search(query)
            data = partner_category_ids
        except Exception as e:
            traceback.print_exc()
        finally:
            return data

    @route(['/api/v1/user/search/<string:query>',
            '/api/v1/user/search'], type='json', auth="public", cors="*")
    def api_user_search(self, query=""):
        data = []
        try:
            user_ids = request.env(su=True)['res.users'].name_search(query)
            data = user_ids
        except Exception as e:
            traceback.print_exc()
        finally:
            return data

    @route(['/api/v1/crm-team/search/<string:query>',
            '/api/v1/crm-team/search/'], type='json', auth="public", cors="*")
    def api_crm_team_search(self, query=""):
        data = []
        try:
            crm_team_ids = request.env(su=True)['crm.team'].name_search(query)
            data = crm_team_ids
        except Exception as e:
            traceback.print_exc()
        finally:
            return data

    @route(['/api/v1/payment-term/search/<string:query>',
            '/api/v1/payment-term/search'], type='json', auth="public", cors="*")
    def api_payment_term_search(self, query=""):
        data = []
        try:
            payment_term_ids = request.env(su=True)['account.payment.term'].name_search(query)
            data = payment_term_ids
        except Exception as e:
            traceback.print_exc()
        finally:
            return data

    @route(['/api/v1/payment-method/search/<string:query>',
            '/api/v1/payment-method/search'], type='json', auth="public", cors="*")
    def api_payment_method_search(self, query=""):
        data = []
        try:
            payment_method_ids = request.env(su=True)['account.payment.method'].name_search(query)
            data = payment_method_ids
        except Exception as e:
            traceback.print_exc()
        finally:
            return data

    @route(['/api/v1/fiscal-position/search/<string:query>',
            '/api/v1/fiscal-position/search'], type='json', auth="public", cors="*")
    def api_fiscal_position_search(self, query=""):
        data = []
        try:
            fiscal_position_ids = request.env(su=True)['account.fiscal.position'].name_search(query)
            data = fiscal_position_ids
        except Exception as e:
            traceback.print_exc()
        finally:
            return data

    @route(['/api/v1/currency/search/<string:query>',
            '/api/v1/currency/search'], type='json', auth="public", cors="*")
    def api_currency_search(self, query=""):
        data = []
        try:
            res_currency_ids = request.env(su=True)['res.currency'].name_search(query)
            data = res_currency_ids
        except Exception as e:
            traceback.print_exc()
        finally:
            return data

    @route(['/api/v1/stock-location/search/<string:query>',
            '/api/v1/stock-location/search'], type='json', auth="public", cors="*")
    def api_stock_location_search(self, query=""):
        data = []
        try:
            stock_location_ids = request.env(su=True)['stock.location'].name_search(query)
            data = stock_location_ids
        except Exception as e:
            traceback.print_exc()
        finally:
            return data

    @route(['/api/v1/bank/search/<string:query>',
            '/api/v1/bank/search'], type='json', auth="public", cors="*")
    def api_bank_search(self, query=""):
        data = []
        try:
            res_bank_ids = request.env(su=True)['res.bank'].name_search(query)
            data = res_bank_ids
        except Exception as e:
            traceback.print_exc()
        finally:
            return data
