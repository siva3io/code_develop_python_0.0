# -*- coding: utf-8 -*-

from odoo.http import route, request, Controller, Response
import logging
import traceback

_logger = logging.getLogger(__name__)


class ContactApi(Controller):

    @staticmethod
    def contact_sanity_check(data):
        if data.get('address'):
            data['child_ids'] = []
            for rec in data['address']:
                data['child_ids'].append((0, 0, {
                    "location_name": rec.get('location_name'),
                    "type": rec.get('type'),
                    "street": rec.get('street'),
                    "street2": rec.get('street2'),
                    "street3": rec.get('street3'),
                    "landmark": rec.get('landmark'),
                    "zip": rec.get('zip'),
                    "country_id": int(rec.get('country_id')) if rec.get('country_id') else "",
                    "state_id": int(rec.get('state_id')) if rec.get('state_id') else "",
                    "city": rec.get('city'),
                    "gstin_number": rec.get('gstin_number'),
                    "name": rec.get('name'),
                    "phone": rec.get('phone'),
                }))
            # state_id, country_id, parent_id, category_id
        if "address" in data:
            data.pop('address')
        if data.get('category_id'):
            data['category_id'] = [(6, 0, list(map(int, data.get('category_id'))))]
        if data.get('parent_id'):
            data['parent_id'] = int(data.get('parent_id'))
        return data

    @route('/api/v1/contact/view', type='json', auth="user", cors="*")
    def api_v1_contact_view(self, view='list', limit=20, offset=0, domain=None, order='', **kw):
        data = []
        try:
            partner_ids = request.env['res.partner'].search(domain or [], limit=limit, offset=offset,
                                                                     order=order)
            if partner_ids:
                if view == 'grid':
                    for rec in partner_ids:
                        fields = ['id', 'image_1024', 'name', 'category_id', 'phone', 'email']
                        data = partner_ids.read(fields)
                        data.append({
                            'id': rec.id,
                            'image': rec.image_1024,
                            'name': rec.name,
                            'businessType': rec.category_id.mapped('display_name'),
                            'phone': rec.phone,
                            'email': rec.email
                        })
                else:
                    for rec in partner_ids:
                        data.append({
                            'id': rec.id,
                            'image': rec.avatar_128,
                            'name': rec.name,
                            'contactType': rec.company_type,
                            'businessType': rec.category_id.mapped('display_name'),
                            'company': rec.company_name,
                            'jobTitle': rec.function,
                            'email': rec.email,
                            'phone': rec.phone
                        })
                    # mobile = request.env(su=True)['res.company'].browse(1).mobile
                    # if mobile:
                    #     data = [data]
            else:
                pass  # ToDo: Add response
        except Exception as e:
            traceback.print_exc()
            pass  # ToDo: Add response
        finally:
            # ToDo: read about make_response
            return data

    @route('/api/v1/contact/create', type='json', auth="user", cors="*")
    def api_v1_contact_create(self, **kw):
        data = []
        try:
            _logger.info(f"=====Body======{kw}")
            if kw.get('name'):
                kw = ContactApi.contact_sanity_check(kw)
                partner_id = request.env['res.partner'].create(kw)
                # is_address is for storing partner as address
                partner_id.write({'is_address': False})
                if partner_id:
                    data = partner_id.api_contact_read()
                    pass  # ToDo: Add response
            else:
                data = {'error': 'Mandatory Parameter Missing'}
        except Exception as e:
            data = {'error': 'Something went wrong'}
            traceback.print_exc()
        finally:
            return data

    @route('/api/v1/address/create', type='json', auth="user", cors="*")
    def api_v1_address_create(self, **kw):
        data = []
        try:
            if kw.get('name'):
                address_id = request.env['res.partner'].create(kw)
                if address_id:
                    data = address_id.api_address_read()
                    pass  # ToDo: Add response
            else:
                pass  # ToDo: Add response
        except Exception as e:
            traceback.print_exc()
        finally:
            return data

    @route('/api/v1/address/read/<int:rec_id>', type='json', auth="user", cors="*")
    def api_v1_address_read(self, rec_id):
        data = []
        try:
            partner_id = request.env['res.partner'].browse(rec_id)
            if partner_id:
                data = partner_id.api_address_read()
            else:
                pass  # ToDo: Add response
        except Exception as e:
            traceback.print_exc()
        finally:
            return data

    @route('/api/v1/contact/read/<int:rec_id>', type='json', auth="user", cors="*")
    def api_v1_contact_read(self, rec_id):
        data = []
        try:
            partner_id = request.env['res.partner'].browse(rec_id)
            if partner_id:
                data = partner_id.api_contact_read()
            else:
                pass  # ToDo: Add response
        except Exception as e:
            traceback.print_exc()
        finally:
            return data

    @route('/api/v1/related/contact/read/<int:rec_id>', type='json', auth="user", cors="*")
    def api_v1_related_contact_read(self, rec_id):
        data = []
        try:
            partner_id = request.env['res.partner'].browse(rec_id)
            if partner_id:
                data = {
                    "parent_id": partner_id.parent_id.api_rel_contact_read(),
                    "child_ids": partner_id.child_ids.api_rel_contact_read()
                }
            else:
                pass  # ToDo: Add response
        except Exception as e:
            traceback.print_exc()
        finally:
            return data

    @route('/api/v1/address/write/<int:rec_id>', type='json', auth="user", cors="*")
    def api_v1_address_update(self, rec_id, **kw):
        data = []
        try:
            partner_id = request.env['res.partner'].browse(rec_id)
            if partner_id:
                partner_id.write(kw)
                data = partner_id.api_address_read()
            else:
                pass  # ToDo: Add response
        except Exception as e:
            traceback.print_exc()
        finally:
            return data

    @route('/api/v1/contact/write/<int:rec_id>', type='json', auth="user", cors="*")
    def api_v1_contact_update(self, rec_id, **kw):
        data = []
        try:
            if kw.get('address'):
                kw.pop('address')
            if kw.get('category_id'):
                kw['category_id'] = [(6, 0, kw['category_id'])]
            partner_id = request.env['res.partner'].browse(rec_id)
            if partner_id:
                partner_id.write(kw)
                data = partner_id.api_contact_read()
            else:
                pass  # ToDo: Add response
        except Exception as e:
            traceback.print_exc()
        finally:
            return data

    @route(['/api/v1/contact/delete/<int:rec_id>',
            '/api/v1/address/delete/<int:rec_id>'], type='json', auth="user", cors="*")
    def api_v1_partner_delete(self, rec_id):
        data = []
        try:
            partner_id = request.env['res.partner'].browse(rec_id)
            if partner_id.active:
                partner_id.write({'active': False})
                data = True
            else:
                data = True
                pass  # ToDo: Add response
        except Exception as e:
            traceback.print_exc()
        finally:
            return data
