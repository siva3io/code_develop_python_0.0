# -*- coding: utf-8 -*-
from odoo import http


class InvoicingModule(http.Controller):
    @http.route('/api/v1/invoicing', auth='user', type='json', csrf=False, cors="*")
    def invoicing_list(self, limit=20, offset=0, order='', domain=[], **request_data):
        data = []
        if request_data.get("purchase_ids"):
            data = [("purchase_id", "in", request_data.get("purchase_ids"))]
        elif request_data.get("sale_ids"):
            data = [("sale_id", "in", request_data.get("sale_ids"))]
        elif request_data.get("sales_return_ids"):
            data = [("return_order_id", "in", request_data.get("sales_return_ids"))]
        elif request_data.get("purchase_return_id"):
            data = [("return_order_id", "in", request_data.get("purchase_return_ids"))]
        elif request_data.get("search_query"):
            data = [('name', 'ilike', request_data.get("search_query"))]
        invoicing_list = http.request.env['account.move'].search(data or domain, limit=limit,
                                                                        offset=offset, order=order)
        if invoicing_list:
            response = []
            for invoice in invoicing_list:
                response.append({
                    'id': invoice.id,
                    'invoice_number': invoice.name,
                    'invoice_create_date': invoice.invoice_date,
                    'payment_terms': invoice.invoice_payment_term_id.name,
                    'payee_contact': invoice.team_id.company_id.phone,
                    'payer_contact': invoice.partner_id.phone,
                    'status': invoice.state
                })
            return response
        else:
            return {"status": "No Data Available"}

    @http.route('/api/v1/invoicing/<int:invoice_id>', auth='user', type='json', csrf=False, cors="*")
    def invoicing_view(self, invoice_id):
        invoicing_view = http.request.env['account.move'].browse(invoice_id)
        if invoicing_view:
            data = []
            for order_line in invoicing_view.invoice_line_ids:
                data.append({
                    'id': order_line.id,
                    'product_id': order_line.product_id.id,
                    'product_sku': order_line.product_id.default_code,
                    'product_name': order_line.display_name,
                    'price': order_line.price_unit,
                    'product_quantity': order_line.quantity,
                    'discount_type': order_line.discount_type,
                    'discount': order_line.discount,
                    'tax': order_line.tax_ids.name,
                    'total': order_line.price_subtotal
                })
            response = {
                'id': invoicing_view.id,
                'issue_date': invoicing_view.invoice_date,
                'gst_treatment': invoicing_view.l10n_in_gst_treatment,
                'due_date': invoicing_view.invoice_date_due,
                'image': invoicing_view.partner_id.image_1920,
                'payer_name': invoicing_view.partner_id.name,
                'payer_phone': invoicing_view.partner_id.phone,
                'payer_email': invoicing_view.partner_id.email,
                'payee_name': invoicing_view.team_id.company_id.name,
                'payee_phone': invoicing_view.team_id.company_id.phone,
                'payee_email': invoicing_view.team_id.company_id.email,
                'payee_account_name': invoicing_view.partner_bank_id.acc_holder_name,
                'payee_account_number': invoicing_view.partner_bank_id.acc_number,
                'payee_bank_name': invoicing_view.partner_bank_id.bank_name,
                'payer_account_name': invoicing_view.partner_id.bank_ids.acc_holder_name,
                'payer_account_number': invoicing_view.partner_id.bank_ids.acc_number,
                'payer_bank_name': invoicing_view.partner_id.bank_ids.acc_holder_name,
                'total_amount': invoicing_view.amount_total,
                'term_value': invoicing_view.invoice_payment_term_id.line_ids.value_amount,
                'payment_term_period': invoicing_view.invoice_payment_term_id.line_ids.days,
                'invoicing_order_line': data,
            }
            return response

    @http.route('/api/v1/invoicing/create', auth='user', type='json', csrf=False, cors="*")
    def invoicing_create(self, **request_data):
        if http.request.jsonrequest:
            invoice_lines = request_data.get('invoice_line_ids')
            request_data.pop('invoice_line_ids')
            invoice = http.request.env['account.move'].create(request_data)
            if invoice_lines:
                for line_id in invoice_lines:
                    line_id['move_id'] = invoice.id
                    invoice_line_ids = http.request.env['account.move.line'].create(line_id)
            response = {'status': True, 'invoice_id': invoice.id}
            return response

    @http.route('/api/v1/invoicing/<int:invoice_id>/edit', auth='user', type='json', csrf=False, cors="*")
    def invoicing_edit(self, invoice_id, **request_data):
        line_ids = request_data.get('invoice_line_ids')
        request_data.pop('invoice_line_ids')
        invoicing_edit = http.request.env['account.move'].search([('id', '=', invoice_id)])
        invoicing_edit.write(request_data)
        if line_ids:
            invoice_line_id = []
            for invoice_line in line_ids:
                invoice_line['move_id'] = invoicing_edit.id
                invoice_line_items = http.request.env['account.move.line'].search(
                    [('id', '=', invoice_line.get('id'))])
                if invoice_line.get('id'):
                    invoice_line_items.write(invoice_line)
                    invoice_line_id.append(invoice_line_items.id)
                else:
                    invoice_line_create = invoice_line_items.create(invoice_line)
                    invoice_line_id.append(invoice_line_create.id)
            invoicing_edit.write({"invoice_line_ids": invoice_line_id})
            return {'success': True, 'status': 'Updated', 'updated_invoice_id': invoicing_edit.id}

    @http.route('/api/v1/invoicing/<int:invoicing_id>/delete', auth='user', type='json', csrf=False, cors="*")
    def invoice_delete(self, invoicing_id, **kw):
        invoice_delete = http.request.env['account.move'].search([('id', '=', invoicing_id)])
        if invoice_delete:
            if invoice_delete.state == "sent":
                return {"success": False,
                        "status": "You cannot delete a sent quotation or a confirmed sales order",
                        "invoicing_id": invoice_delete.id}
            else:
                for line_id in invoice_delete.invoice_line_ids:
                    line_id.unlink()
            invoice_delete.unlink()
            return {"status": "Deleted", "Deleted id": invoice_delete.id}
        else:
            return {"status": "no data found to delete"}



#     @http.route('/invoicing_module/invoicing_module/objects', auth='public')
#     def list(self, **kw):
#         return http.request.render('invoicing_module.listing', {
#             'root': '/invoicing_module/invoicing_module',
#             'objects': http.request.env['invoicing_module.invoicing_module'].search([]),
#         })

#     @http.route('/invoicing_module/invoicing_module/objects/<model("invoicing_module.invoicing_module"):obj>', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('invoicing_module.object', {
#             'object': obj
#         })
