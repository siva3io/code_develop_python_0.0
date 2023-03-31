# -*- coding: utf-8 -*-
import werkzeug
from odoo.http import route, request, Controller


class BaseApi(Controller):
    @route('/api/v1/web/session/authenticate', type='json', auth="none", cors="*")
    def api_web_session_authenticate(self, db, login, password, base_location=None):
        request.session.authenticate(db, login, password)
        return request.env['ir.http'].session_info()
