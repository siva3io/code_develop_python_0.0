# -*- coding: utf-8 -*-
import logging
from odoo.http import route, Controller, request

_logger = logging.getLogger(__name__)


class Catalogue(Controller):

    @staticmethod
    def modify_request_channel_attributes(attributes):
        new_attributes = dict()
        for attr in attributes:
            new_attributes[attr["name"]] = attr.get("value", "")
        return new_attributes

    @route('/catalogue/categories', auth='public', type="json", csrf=False, cors="*")
    def catalogue_category_list(self, **kw):
        categories = request.env(su=True)['product.template.category'].search([('parent_category_id', '=', False)])
        if categories:
            data = []
            for category in categories:
                if category.reviewed:
                    data.append({
                        "category_id": category.id,
                        "category_name": category.name,
                        "category_code": category.code
                    })
            return data

    @route('/catalogue/subcategories', auth='public', type="json", csrf=False, cors="*")
    def catalogue_subcategory_list(self, category_id, **kw):
        category = request.env(su=True)['product.template.category'].search([('id', '=', category_id)])
        if category:
            data = []
            for subcategory in category.child_category_ids:
                if subcategory.reviewed:
                    data.append({
                        "subcategory_id": subcategory.id,
                        "subcategory_name": subcategory.name,
                        "subcategory_code": subcategory.code
                    })
            return data

    @route('/catalogue/channels', auth='public', type="json", csrf=False, cors="*")
    def catalogue_marketplace(self, **kw):
        master_template = {
            "id": 0,
            "name": "Eunimart",
            "sequence": 1,
            "channel_type": "platform"
        }
        marketplace_ids = request.env(su=True)['marketplace'].search_read([],
                                                                          fields=['name', 'sequence', 'channel_type'])
        if marketplace_ids:
            marketplace = marketplace_ids
            marketplace = [master_template] + marketplace
            return marketplace

    @route('/catalogue/subcategory/channels/fields', auth='public', type="json", csrf=False, cors="*")
    def catalogue_subcategory_template_fields(self, subcategory_id, channel_id_list):

        all_channel_fields = []
        for channel_id in channel_id_list:
            if channel_id == 0:
                channel_fields = request.env(su=True)['catalogue.template.lines'].search_read(
                    [('product_template_category_id', '=', subcategory_id)],
                    fields=['id', 'name', 'code', 'type', 'allowed_values', 'attribute_description',
                            'attribute_validation_regex', 'json_code',
                            'is_mandatory', 'is_predictable'])

            else:
                channel_fields = request.env(su=True)['catalogue.template.line.marketplace'].search_read(
                    [('product_template_category_id', '=', subcategory_id),
                     ('marketplace_id.id', '=', channel_id)],
                    fields=['id', 'name', 'code', 'marketplace_display_name', 'type', 'allowed_values',
                            'attribute_description', 'attribute_validation_regex', 'json_code',
                            'is_mandatory', 'is_predictable'])

            for channel_field in channel_fields:
                if channel_id == 0:
                    channel_field['display_name'] = channel_field['name']
                else:
                    channel_field['display_name'] = channel_field['marketplace_display_name']

                channel_field['name'] = channel_field.pop('code')
                if not channel_field['allowed_values']:
                    channel_field['allowed_values'] = {}

                if channel_field['is_predictable'] and channel_field['json_code']:
                    channel_field['source'] = 'data_science'
                    channel_field['prediction_route_endpoint'] = '/catalogue/predict'
                    channel_field['prediction_params'] = dict(channel_field['json_code']).get('prediction_params', [])
                else:
                    channel_field['is_predictable'] = False
                    channel_field['source'] = 'backend'
                    channel_field['prediction_route_endpoint'] = ""
                    channel_field['prediction_params'] = []

                del channel_field['json_code']

            all_channel_fields.append({
                "channel_id": channel_id,
                "channel_attribute_version": 1,
                "channel_attributes": channel_fields
            })

        return all_channel_fields

    @route('/catalogue/template/attribute_mapping', auth='public', type="json", csrf=False, cors="*")
    def catalogue_subcategory_mapped_template_fields(self, subcategory_id, request_channel_id, response_channel_id_list,
                                                     request_channel_attributes):

        all_channel_mapped_fields = []
        for channel_id in response_channel_id_list:
            prefilled_values_dict = {}
            channel_fields = []
            if channel_id == 0:
                channel_field_lines = request.env(su=True)['catalogue.template.lines'].search(
                    [('product_template_category_id', '=', subcategory_id)])

            else:
                channel_field_lines = request.env(su=True)['catalogue.template.line.marketplace'].search(
                    [('product_template_category_id', '=', subcategory_id),
                     ('marketplace_id.id', '=', channel_id)],
                )

            channel_field = {}
            for field_line in channel_field_lines:
                channel_field['python_code'] = ""
                channel_field["id"] = field_line.id
                channel_field["name"] = field_line.code
                channel_field['display_name'] = field_line.name
                if channel_id == 0:
                    channel_field['display_name'] = field_line.name
                else:
                    channel_field['display_name'] = field_line.marketplace_display_name
                channel_field['attribute_description'] = field_line.attribute_description
                channel_field['attribute_validation_regex'] = field_line.attribute_validation_regex
                if field_line.is_predictable and field_line.json_code:
                    channel_field['source'] = 'data_science'
                    channel_field['is_predictable'] = field_line.is_predictable
                    channel_field['prediction_route_endpoint'] = '/catalogue/predict'
                    channel_field['prediction_params'] = dict(field_line.json_code).get('prediction_params', [])
                    channel_field['python_code'] = str(field_line.python_code)
                else:
                    channel_field['source'] = 'backend'
                    channel_field['is_predictable'] = False
                    channel_field['prediction_route_endpoint'] = ""
                    channel_field['prediction_params'] = []

                channel_field['type'] = field_line.type
                if field_line.allowed_values:
                    channel_field['allowed_values'] = field_line.allowed_values
                else:
                    channel_field['allowed_values'] = {}
                channel_field['is_mandatory'] = field_line.is_mandatory
                channel_field['is_prefilled'] = False
                channel_field['prefilled_value'] = ""
                if channel_id == request_channel_id:
                    channel_field['prefilled_value'] = str(request_channel_attributes.get(field_line.code, ""))
                elif request_channel_id == 0:
                    channel_field['prefilled_value'] = str(request_channel_attributes.get(field_line.line_id.code, ""))
                    if channel_field['allowed_values'] != {}:
                        channel_field['prefilled_value'] = str(channel_field['allowed_values'].get(
                            channel_field['prefilled_value'], channel_field['prefilled_value']))

                elif channel_id == 0:
                    for index in range(len(field_line.marketplace_line_ids)):
                        if field_line.marketplace_line_ids[index].marketplace_id.id == request_channel_id:
                            channel_field['prefilled_value'] = str(request_channel_attributes.get(
                                field_line.marketplace_line_ids[index].code, ""))
                else:
                    for index in range(len(field_line.line_id.marketplace_line_ids)):
                        if field_line.line_id.marketplace_line_ids[index].marketplace_id.id == request_channel_id:
                            channel_field['prefilled_value'] = str(request_channel_attributes.get(
                                field_line.line_id.marketplace_line_ids[index].code, ""))

                if channel_field['prefilled_value'] != "":
                    channel_field['is_prefilled'] = True
                    if field_line.algo_code:
                        input_variable = channel_field["name"] + " ='" + channel_field['prefilled_value'] + "'\n"
                        exec(str(input_variable + field_line.algo_code).strip(), globals())
                    prefilled_values_dict[channel_field["name"]] = channel_field['prefilled_value']
                channel_fields.append(channel_field)
                channel_field = {}

            for channel_field in channel_fields:
                if ~(channel_field['is_prefilled']) and channel_field['is_predictable']:
                    python_code_variables = ""
                    for a_param in channel_field['prediction_params']:
                        param_value = ""
                        """if a_param['channel_id'] == request_channel_id:
                            param_value = request_channel_attributes.get(a_param['name'], "")
                        elif a_param['channel_id'] == channel_id:
                            param_value = channel_fields.get(a_param['name'], "")"""
                        param_value = prefilled_values_dict.get(a_param['name'], "")
                        if param_value:
                            param_value = param_value.replace("'", "")
                            python_code_variables += str(a_param['name'])
                            python_code_variables += "='"
                            python_code_variables += str(param_value)
                            python_code_variables += "'\n"
                        else:
                            python_code_variables = ""
                            break

                    if python_code_variables:
                        python_code_variables += "allowed_values"
                        python_code_variables += "="
                        python_code_variables += str(list(channel_field['allowed_values'].values()))
                        python_code_variables += "\n"
                        try:
                            exec(str(python_code_variables + str(channel_field['python_code'])).strip(), globals())
                            channel_field['is_prefilled'] = True
                            channel_field['prefilled_value'] = field_result
                        except Exception as e:
                            _logger.info('=== Exception Case ===', e)
                        channel_field['is_prefilled'] = True
                        channel_field['prefilled_value'] = field_result
                        if channel_field['prefilled_value'] and channel_id == request_channel_id:
                            request_channel_attributes[channel_field['name']] = channel_field['prefilled_value']

                del channel_field['python_code']
            all_channel_mapped_fields.append({
                "channel_id": channel_id,
                "channel_attribute_version": 1,
                "channel_attributes": channel_fields
            })

        return all_channel_mapped_fields

    @route('/catalogue/predict', auth='public', type="json", csrf=False, cors="*")
    def catalogue_predict_value(self, channel_id, attribute_name, attribute_id, **kw):

        if channel_id == 0:
            template_field_line = request.env(su=True)['catalogue.template.lines'].search([('id', '=', attribute_id)])
        else:
            template_field_line = request.env(su=True)['catalogue.template.line.marketplace'].search(
                [('id', '=', attribute_id)])

        python_code_variables = ""
        for field in dict(template_field_line.json_code).get('prediction_params', []):
            python_code_variables += field.get('name', "")
            python_code_variables += "='"
            python_code_variables += str(kw.get(field.get('name', "")))
            python_code_variables += "'\n"
        python_code_variables += "allowed_values"
        python_code_variables += "="
        python_code_variables += str(list(dict(template_field_line.allowed_values).keys()))
        python_code_variables += "\n"

        exec(str(python_code_variables + template_field_line.python_code).strip(), globals())
        prediction_result = {
            "attribute_name": attribute_name,
            "attribute_value": field_result
        }

        return prediction_result

    @route('/v2/catalogue/subcategory/available_channels', auth='public', type="json", csrf=False, cors="*")
    def catalogue_subcategory_channels(self, subcategory_id):
        channels = self.catalogue_marketplace()
        channel_id_list = [a_channel["id"] for a_channel in channels]

        template_fields = self.v2_catalogue_subcategory_template_fields(subcategory_id, channel_id_list)
        available_channel_list = []
        for a_template_field in template_fields:
            if a_template_field["channel_attributes"]:
                available_channel_list.append(a_template_field["channel_id"])

        return available_channel_list

    """
    @route('/catalogue/category/data/<int:a_category_id>', auth='public', type="json", csrf=False, cors="*")
    def catalogue_category_data(self, a_category_id):
        o_category_id = request.env(su=True)['product.template.category'].search_read(
            [('actual_id', '=', a_category_id)], fields=['id'])
        if o_category_id:
            # ctm_lines = request.env(su=True)['catalogue.template.lines'].search_read(
            #     [('product_template_category_id', '=', o_category_id[0]['id'])],
            #     fields=['name', 'code', 'allowed_values', 'type', 'is_mandatory', 'catalogue_template_section_id'])
            results = request.env(su=True)['catalogue.template.lines'].read_group(
                [('product_template_category_id', '=', o_category_id[0]['id'])],
                ['catalogue_template_section_id'], 'catalogue_template_section_id')
            groups = request.env(su=True)['catalogue.template.section'].browse(
                [result['catalogue_template_section_id'][0] for result in results])
            ctm_lines = []
            for rec in groups:
                ctm_lines.append({
                    "id": rec.id,
                    "name": rec.name,
                    "fields": [{"id": r.id,
                                "name": r.name,
                                "code": r.code,
                                "allowed_values": r.allowed_values,
                                "type": r.type} for r in rec.catalogue_template_lines_ids]
                })
            return ctm_lines

    @route('/catalogue/category/marketplace_data/<int:a_category_id>/<int:a_marketplace_id>', auth='public',
           type="json", csrf=False, cors="*")
    def catalogue_marketplace_category_data(self, a_category_id, a_marketplace_id):
        o_category_id = request.env(su=True)['product.template.category'].search_read(
            [('id', '=', a_category_id)], limit=1)
        if o_category_id:
            marketplace_field_data = request.env(su=True)['catalogue.template.line.marketplace'].search_read(
                [('product_template_category_id', '=', o_category_id[0]['id']),
                 ('marketplace_id.id', '=', a_marketplace_id)],
                fields=['id', 'name', 'code', 'allowed_values', 'type'])
            return marketplace_field_data

    @route('/catalogue/store/product', auth='public', type="json", csrf=False, cors="*")
    def catalogue_store_product(self, **kw):
        response = {}
        try:
            values = {key: kw.get(key) for key in ('productName', 'jsonData', 'category')}
            catalogue_id = False
            if values['category']:
                catalogue_id = request.env(su=True)['catalogue.template'].search_read(
                    [('category_id', '=', int(values['category']))], fields=['name'])
                # category_ids = request.env(su=True)['product.template.category'].search_read(
                #     [('id', '=', int(values['category']))], fields=['name'])
            if values['jsonData']:
                val = {
                    'type': "product",
                    'name': values['productName'],
                    'catalogue_id': False if not catalogue_id else catalogue_id[0]['id'],
                    'product_parameters': values['jsonData'],
                }
                product = request.env['product.product'].create(val)
                if product:
                    response['success'] = True
                    response['message'] = 'Product created successfully'
                    response['id'] = product.id
        except Exception as e:
            _logger.info('=== Exception Case ===')
            response = {"ResponseCode": 500, "ResponseMessage": "Something went Wrong", "data": {'error': e}}
        finally:
            return response

    @route('/api/v1/products/<int:pro_temp_id>', auth='public', type="json", csrf=False, cors="*")
    def api_v1_products_data(self, pro_temp_id):
        product_template_id = request.env(su=True)['product.template'].browse(pro_temp_id)
        response = {"ResponseCode": 400, "ResponseMessage": "Product Not Available"}
        if product_template_id:
            response = []
            for product in product_template_id.product_variant_ids:
                response.append({
                    "id": product.id,
                    "is_archive": not product.active,
                    "product_name": product.name,
                    "product_images": product.image_urls.split(",") if product.image_urls else False,
                    "product_desc": product.description,
                    "dimensions": product.dimensions,
                    "attribute_ids": product.attribute_ids.ids,
                    "brand": product.brand,
                    "condition_type": product.condition_type,
                    "price": product.price,
                    "title": product.display_name,
                    "account_id": product.user_id.id,
                    "product_template_id": product_template_id.id,
                    "sku_id": "582165SKU",
                    "product_ids": [product_template_id.id],
                    "template_name": product_template_id.name,
                    "category_id": product_template_id.template_category_id.id,
                    "shipping_partner_ids": product_template_id.shipping_partner_ids.ids,
                    "vendor_ids": product.variant_seller_ids.ids,
                    "category_name": product_template_id.template_category_id.name,
                    "category_desc": product_template_id.template_category_id.description,
                    "parent_category_id": product_template_id.template_category_id.parent_category_id.id,
                    "parent_cat_name": product_template_id.template_category_id.parent_category_id.name,
                    "shipping_array": [
                        {
                            "id": ship.id,
                            "is_archive": not ship.active,
                            "name": ship.name.name,
                            "pack_lead_time": ship.pack_lead_time,
                            "shipping_lead_time": ship.shipping_lead_time,
                        } for ship in product_template_id.shipping_partner_ids],
                    "vendors_array": [
                        {
                            "id": seller.id,
                            "is_archive": False,
                            "name": seller.name.name,
                            "supply_lead_time": seller.delay,
                            "cost": seller.price,
                        } for seller in product.variant_seller_ids],
                    "variants_array": [
                        {
                            "id": attr.id,
                            "is_archive": not attr.active,
                            "value_name": attr.name,
                            "account_ids": attr.user_id.id,
                            "at_cat_tem_id": attr.att_cat_data_id.att_category_template_id.id,
                            "att_parent_name": attr.att_val_template_id.name
                        } for attr in product.attribute_ids],
                })
        return response
        """

    @route('/v2/catalogue/subcategory/channels/fields', auth='public', type="json", csrf=False, cors="*")
    def v2_catalogue_subcategory_template_fields(self, subcategory_id, channel_id_list):
        all_channel_fields = []
        for channel_id in channel_id_list:
            if channel_id == 0:
                channel_fields = request.env(su=True)['catalogue.template.lines'].search_read(
                    [('product_template_category_id', '=', subcategory_id)],
                    fields=['id', 'name', 'code', 'type', 'allowed_values', 'attribute_description',
                            'attribute_validation_regex', 'json_code',
                            'is_mandatory', 'is_predictable'])
            else:
                channel_fields = request.env(su=True)['catalogue.template.line.marketplace'].search_read(
                    [('product_template_category_id', '=', subcategory_id),
                     ('marketplace_id.id', '=', channel_id)],
                    fields=['id', 'name', 'code', 'marketplace_display_name', 'type', 'allowed_values',
                            'attribute_description', 'attribute_validation_regex', 'json_code',
                            'is_mandatory', 'is_predictable'])
            for channel_field in channel_fields:
                if channel_id == 0:
                    channel_field['display_name'] = channel_field['name']
                else:
                    channel_field['display_name'] = channel_field['marketplace_display_name']
                channel_field['name'] = channel_field.pop('code')
                allowed_vals = []
                if channel_field['allowed_values']:
                    for val in channel_field['allowed_values']:
                        if channel_field['allowed_values'][val]:
                            allowed_vals.append(str(channel_field['allowed_values'][val]))
                channel_field['allowed_values'] = allowed_vals
                if channel_field['is_predictable'] and channel_field['json_code']:
                    channel_field['source'] = 'data_science'
                    channel_field['prediction_route_endpoint'] = '/catalogue/predict'
                    channel_field['prediction_params'] = dict(channel_field['json_code']).get('prediction_params', [])
                else:
                    channel_field['is_predictable'] = False
                    channel_field['source'] = 'backend'
                    channel_field['prediction_route_endpoint'] = ""
                    channel_field['prediction_params'] = []
                    channel_field['value'] = ""
                del channel_field['json_code']
            all_channel_fields.append({
                "channel_id": channel_id,
                "channel_attribute_version": 1,
                "channel_attributes": channel_fields
            })
        return all_channel_fields

    @route('/v2/catalogue/template/attribute_mapping', auth='public', type="json", csrf=False, cors="*")
    def v2_catalogue_subcategory_mapped_template_fields(self, subcategory_id, request_channel_id,
                                                        response_channel_id_list,
                                                        request_channel_attributes):
        all_channel_mapped_fields = []
        for channel_id in response_channel_id_list:
            prefilled_values_dict = {}
            channel_fields = []
            if channel_id == 0:
                channel_field_lines = request.env(su=True)['catalogue.template.lines'].search(
                    [('product_template_category_id', '=', subcategory_id)])
            else:
                channel_field_lines = request.env(su=True)['catalogue.template.line.marketplace'].search(
                    [('product_template_category_id', '=', subcategory_id),
                     ('marketplace_id.id', '=', channel_id)],
                )
            channel_field = {}
            for field_line in channel_field_lines:
                channel_field["python_code"] = ""
                channel_field["id"] = field_line.id
                channel_field["name"] = field_line.code
                channel_field['display_name'] = field_line.name
                if channel_id == 0:
                    channel_field['display_name'] = field_line.name
                else:
                    channel_field['display_name'] = field_line.marketplace_display_name
                channel_field['attribute_description'] = field_line.attribute_description
                channel_field['attribute_validation_regex'] = field_line.attribute_validation_regex
                if field_line.is_predictable and field_line.json_code:
                    channel_field['source'] = 'data_science'
                    channel_field['is_predictable'] = field_line.is_predictable
                    channel_field['prediction_route_endpoint'] = '/catalogue/predict'
                    channel_field['prediction_params'] = dict(field_line.json_code).get('prediction_params', [])
                    channel_field["python_code"] = str(field_line.python_code)
                else:
                    channel_field['source'] = 'backend'
                    channel_field['is_predictable'] = False
                    channel_field['prediction_route_endpoint'] = ""
                    channel_field['prediction_params'] = []
                channel_field['type'] = field_line.type
                allowed_vals = []
                if field_line.allowed_values:
                    for val in field_line.allowed_values:
                        if field_line.allowed_values[val]:
                            allowed_vals.append(str(field_line.allowed_values[val]))
                channel_field['allowed_values'] = allowed_vals
                channel_field['is_mandatory'] = field_line.is_mandatory
                channel_field['mandatory_type'] = field_line.mandatory_type
                channel_field['is_prefilled'] = False
                channel_field['value'] = ""
                if channel_id == request_channel_id:
                    channel_field['value'] = str(request_channel_attributes.get(field_line.code, ""))
                elif request_channel_id == 0:
                    channel_field['value'] = str(request_channel_attributes.get(field_line.line_id.code, ""))
                elif channel_id == 0:
                    for index in range(len(field_line.marketplace_line_ids)):
                        if field_line.marketplace_line_ids[index].marketplace_id.id == request_channel_id:
                            if channel_field['value']:
                                # if value is already set not to modify the value
                                _logger.info('=== Mapped Value ===', channel_field['value'])
                                continue
                            channel_field['value'] = str(request_channel_attributes.get(
                                field_line.marketplace_line_ids[index].code, ""))
                else:
                    for index in range(len(field_line.line_id.marketplace_line_ids)):
                        if field_line.line_id.marketplace_line_ids[index].marketplace_id.id == request_channel_id:
                            if channel_field['value']:
                                # if value is already set not to modify the value
                                _logger.info('=== Mapped Value ===', channel_field['value'])
                                continue
                            channel_field['value'] = str(request_channel_attributes.get(
                                field_line.line_id.marketplace_line_ids[index].code, ""))
                if channel_field['value']:
                    channel_field['is_prefilled'] = True
                    if field_line.allowed_values:
                        channel_field['value'] = str(dict(field_line.allowed_values).get(
                            channel_field['value'], channel_field['value']))
                    if field_line.algo_code:
                        input_variable = channel_field["name"] + " ='" + channel_field['value'] + "'\n"
                        exec(str(input_variable + field_line.algo_code).strip(), globals())
                    prefilled_values_dict[channel_field["name"]] = channel_field['value']
                channel_fields.append(channel_field)
                channel_field = {}
            for channel_field in channel_fields:
                if ~(channel_field['is_prefilled']) and channel_field['is_predictable']:
                    python_code_variables = ""
                    for a_param in channel_field['prediction_params']:
                        param_value = ""
                        param_value = prefilled_values_dict.get(a_param['name'], "")
                        if param_value:
                            param_value = param_value.replace("'", "")
                            python_code_variables += str(a_param['name'])
                            python_code_variables += "='"
                            python_code_variables += str(param_value)
                            python_code_variables += "'\n"
                        else:
                            python_code_variables = ""
                            break

                    if python_code_variables:
                        python_code_variables += "allowed_values"
                        python_code_variables += "="
                        python_code_variables += str(channel_field['allowed_values'])
                        python_code_variables += "\n"
                        try:
                            exec(str(python_code_variables + str(channel_field['python_code'])).strip(), globals())
                            channel_field['is_prefilled'] = True
                            channel_field['value'] = field_result
                        except Exception as e:
                            _logger.info('=== Exception Case ===', e)

                        if channel_field['value'] and channel_id == request_channel_id:
                            request_channel_attributes[channel_field['name']] = channel_field['value']
                del channel_field['python_code']
            all_channel_mapped_fields.append({
                "channel_id": channel_id,
                "channel_attribute_version": 1,
                "channel_attributes": channel_fields
            })

        return all_channel_mapped_fields
