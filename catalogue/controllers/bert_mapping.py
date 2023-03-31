# -*- coding: utf-8 -*-
import logging
import re
import numpy as np
from odoo.http import route, Controller, request
# from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity

_logger = logging.getLogger(__name__)
"""
channel_data = [{
            "name":"",
            "marketplace_display_name":"",
            "type":"",
            "attribute_description":"",
            "attribute_validation_regex":"",
            "allowed_values_list":"",
            "is_mandatory":""
        }]
        
Fields to include while creating:
line_id, code, active, marketplace_id, product_template_category_id, mapped_field,cosine_similarity 
"""


# MODEL_NAME = 'bert-base-nli-mean-tokens'
# MODEL = SentenceTransformer(MODEL_NAME)


class CatalogueBertMapping(Controller):
    @staticmethod
    def get_code(field):
        field = field.lower()
        return re.sub('[^0-9a-zA-Z]+', '_', field)

    @staticmethod
    def get_reference_template_attribute(reference_subcategory_id):
        reference_channel_attributes = request.env(su=True)['catalogue.template.lines'].search_read(
            [('product_template_category_id', '=', reference_subcategory_id)],
            fields=['id', 'name', 'possible_keywords'])
        base_template_dict = dict()
        for channel_attribute in reference_channel_attributes:
            if channel_attribute['possible_keywords']:
                channel_attribute['possible_keywords'] += str("," + channel_attribute['name'])
            else:
                channel_attribute['possible_keywords'] = channel_attribute['name']
            for keywords in channel_attribute['possible_keywords'].split(","):
                base_template_dict[str(keywords)] = []
                base_template_dict[str(keywords)].append(channel_attribute['id'])
                base_template_dict[str(keywords)].append(channel_attribute['name'])
                base_template_dict[str(keywords)].append(channel_attribute['possible_keywords'])
                base_template_dict[str(keywords)].append(reference_subcategory_id)
        return base_template_dict

    @staticmethod
    def create_catalogue_template_line(field_name, possible_keywords, subcategory_id):
        new_catalogue_template_line_data = {
            "name": field_name,
            "code": CatalogueBertMapping.get_code(field_name),
            "active": True,
            "possible_keywords": possible_keywords,
            "product_template_category_id": subcategory_id
        }
        new_catalogue_template_line = request.env['catalogue.template.lines'].sudo().create(
            new_catalogue_template_line_data)
        return new_catalogue_template_line.id

    @route('/api/v1/catalogue/category/create', auth='public', type="json", csrf=False, cors="*")
    def create_category(self, category_name, marketplace_id):
        # TODO: create category only if marketplace_id is valid
        # TODO: check if the category is not already there in the given marketplace
        category_data = {
            'name': category_name,
            'marketplace_id': marketplace_id,
            'active': False
        }
        new_category = request.env['product.template.category'].sudo().create(category_data)
        response = {'success': True, 'message': 'Category created', 'ID': new_category.id}
        return response

    @route('/api/v1/catalogue/base_template_dict', auth='public', type="json", csrf=False, cors="*")
    def get_base_template_dict(self, subcategory_id, reference_subcategory_id):
        base_template_dict = self.get_reference_template_attribute(reference_subcategory_id)
        if base_template_dict == {}:
            return [{'success': False, 'message': 'Given reference_subcategory_id has no fields'}]
        if subcategory_id != reference_subcategory_id:
            same_sub_category_dict = self.get_reference_template_attribute(subcategory_id)
            for field_data in same_sub_category_dict:
                base_template_dict[field_data] = same_sub_category_dict[field_data]

        return base_template_dict

    @route('/api/v1/catalogue/template_line/marketplace/create', auth='public', type="json", csrf=False, cors="*")
    def create_marketplace_template_line(
            self, subcategory_id, channel_id, channel_data,
            reference_subcategory_id, base_template_dict, sentence_embeddings_base,
            sentence_embeddings_channel):
        # TODO: Proper foreign key check
        # TODO: Flow if the given subcategory_id and channel_id has fields
        base_template_dict_keys = list(base_template_dict.keys())
        # sentence_embeddings_base = MODEL.encode(base_template_dict_keys).tolist()
        # request_channel_template_data = [a_data["name"] for a_data in channel_data]
        # sentence_embeddings_channel = MODEL.encode(request_channel_template_data).tolist()
        channel_data_response = list()
        created_base_template_data = {}
        for data_index in range(len(channel_data)):
            # TODO: Check if all fields are there and no extra fields also
            cosine_similarity_arr = cosine_similarity(
                [sentence_embeddings_channel[data_index]],
                sentence_embeddings_base[:]
            )
            cosine_similarity_dict = dict(zip(cosine_similarity_arr[0], base_template_dict_keys))
            cosine_similarity_arr = np.sort(cosine_similarity_arr[0])[::-1]
            most_similar_data = cosine_similarity_arr[0]
            mapped_field = base_template_dict[cosine_similarity_dict[most_similar_data]]
            if most_similar_data >= 0.9:
                if subcategory_id != mapped_field[3]:
                    if mapped_field[1] in created_base_template_data:
                        channel_data[data_index]['line_id'] = created_base_template_data[mapped_field[1]]
                    else:
                        channel_data[data_index]['line_id'] = self.create_catalogue_template_line(mapped_field[1],
                                                                                                  mapped_field[2],
                                                                                                  subcategory_id)
                        created_base_template_data[mapped_field[1]] = channel_data[data_index]['line_id']
                else:
                    channel_data[data_index]['line_id'] = mapped_field[0]
            else:
                # create new master field
                channel_data[data_index]['line_id'] = self.create_catalogue_template_line(
                    channel_data[data_index]['name'], channel_data[data_index]['name'], subcategory_id)

            channel_data[data_index]['code'] = self.get_code(channel_data[data_index]['name'])
            channel_data[data_index]['active'] = True
            channel_data[data_index]['marketplace_id'] = channel_id
            channel_data[data_index]['product_template_category_id'] = subcategory_id
            channel_data[data_index]['mapped_field'] = mapped_field[1]
            channel_data[data_index]['cosine_similarity'] = most_similar_data
            new_channel_template_line_data = request.env['catalogue.template.line.marketplace'].sudo().create(
                channel_data[data_index])
            response = {'success': True, 'message': 'Channel Field created', 'Data': new_channel_template_line_data}
            channel_data_response.append(response)
        return channel_data_response

    @route('/api/v1/catalogue/template_line/field/update', auth='public', type="json", csrf=False, cors="*")
    def update_master_template_line_data(self, subcategory_id):
        template_lines = request.env(su=True)['catalogue.template.lines'].search(
            [('product_template_category_id', '=', subcategory_id)],
        )
        channel_data_response = []
        for a_index in range(len(template_lines)):
            write_channel_data = {
                'type': template_lines[a_index].type,
                'is_mandatory': template_lines[a_index].is_mandatory
            }
            for index in range(len(template_lines[a_index].marketplace_line_ids)):
                if write_channel_data['type'] != 'selection':
                    write_channel_data['type'] = template_lines[a_index].marketplace_line_ids[index].type

                if not write_channel_data['is_mandatory']:
                    write_channel_data['is_mandatory'] = template_lines[a_index].marketplace_line_ids[
                        index].is_mandatory
            update_channel_data = request.env['catalogue.template.lines'].sudo().search(
                [('id', '=', template_lines[a_index].id)]).write(
                write_channel_data)
            response = {'success': update_channel_data, 'message': 'Channel Field Updated'}
            channel_data_response.append(response)
        return channel_data_response

    @route('/api/v1/catalogue/template_line/allowed_values', auth='public', type="json", csrf=False, cors="*")
    def get_template_line_data_allowed_values(self, subcategory_id):
        template_lines = request.env(su=True)['catalogue.template.lines'].search(
            [('product_template_category_id', '=', subcategory_id)],
        )
        allowed_values_data = {}
        for a_index in range(len(template_lines)):
            channel_line_allowed_values = {}
            for index in range(len(template_lines[a_index].marketplace_line_ids)):
                if template_lines[a_index].marketplace_line_ids[index].allowed_values_list:
                    channel_line_allowed_values[template_lines[a_index].marketplace_line_ids[index].id] = [str(
                        template_lines[a_index].marketplace_line_ids[index].allowed_values_list).split(",")]
            if channel_line_allowed_values:
                allowed_values_data[template_lines[a_index].id] = channel_line_allowed_values

        return allowed_values_data

    @route('/api/v1/catalogue/template_line/allowed_values/update', auth='public', type="json", csrf=False, cors="*")
    def update_allowed_values_data(self, all_allowed_values):
        allowed_values_update_response = []
        for master_field_index in all_allowed_values:
            base_allowed_values = all_allowed_values[master_field_index][0]
            channel_line_allowed_values = all_allowed_values[master_field_index][1]
            base_allowed_values_dict = {str(a_value): str(a_value) for a_value in base_allowed_values}
            for channel_line_id in channel_line_allowed_values:
                allowed_value_dict = channel_line_allowed_values[channel_line_id][1]
                for a_value in base_allowed_values:
                    if a_value not in allowed_value_dict:
                        allowed_value_dict[a_value] = ""
                update_allowed_value_data = {
                    'allowed_values': allowed_value_dict
                }
                update_channel_template_line_data = request.env['catalogue.template.line.marketplace'].sudo().search(
                    [('id', '=', channel_line_id)]).write(
                    update_allowed_value_data)
            write_channel_data = {'allowed_values': base_allowed_values_dict}
            update_channel_data = request.env['catalogue.template.lines'].sudo().search(
                [('id', '=', master_field_index)]).write(
                write_channel_data)
            response = {'success': update_channel_data, 'message': 'Channel Field Updated'}
            allowed_values_update_response.append(response)
        return allowed_values_update_response

    @route('/api/v1/catalogue/template_line/allowed_values/autocorrect', auth='public', type="json", csrf=False,
           cors="*")
    def autocorrect_allowed_values_data(self):
        all_channel_fields = request.env(su=True)['catalogue.template.line.marketplace'].search(
            [('allowed_values_list', '=', False), ('allowed_values', '!=', False)])
        auto_correct_allowed_values_response = []
        for channel_fields in all_channel_fields:
            # updating allowed value of eunimart field as False
            write_channel_data = {'allowed_values': False}
            update_channel_data = request.env['catalogue.template.lines'].sudo().search(
                [('id', '=', int(channel_fields.line_id))]).write(
                write_channel_data)
            auto_correct_allowed_values_response.append(
                {'success': update_channel_data, 'message': 'Channel Field Updated'})
            for channel_line_id in channel_fields.line_id.marketplace_line_ids:
                update_allowed_value_data = {
                    'allowed_values': False
                }
                update_channel_template_line_data = request.env[
                    'catalogue.template.line.marketplace'].sudo().search(
                    [('id', '=', int(channel_line_id))]).write(
                    update_allowed_value_data)
                auto_correct_allowed_values_response.append(
                    {'success': update_channel_template_line_data, 'message': 'Channel Field Updated'})
        return auto_correct_allowed_values_response

    @route('/api/v1/catalogue/template_line/possible_keywords/update', auth='public', type="json", csrf=False, cors="*")
    def update_possible_keywords(self, subcategory_id):
        template_lines = request.env(su=True)['catalogue.template.lines'].search(
            [('product_template_category_id', '=', subcategory_id)],
        )
        channel_data_response = []
        for a_index in range(len(template_lines)):
            possible_keywords = []
            if template_lines[a_index].possible_keywords:
                for a_keyword in template_lines[a_index].possible_keywords.split(","):
                    if a_keyword not in possible_keywords:
                        possible_keywords.append(a_keyword)

            for index in range(len(template_lines[a_index].marketplace_line_ids)):
                field_name = str(template_lines[a_index].marketplace_line_ids[index].name).strip()
                field_code = str(template_lines[a_index].marketplace_line_ids[index].code).strip()
                field_marketplace_display_name = str(
                    template_lines[a_index].marketplace_line_ids[index].marketplace_display_name).strip()
                if field_name not in possible_keywords:
                    possible_keywords.append(field_name)

                if field_code not in possible_keywords:
                    possible_keywords.append(field_code)

                if field_marketplace_display_name not in possible_keywords:
                    possible_keywords.append(field_marketplace_display_name)

            write_channel_data = {
                'possible_keywords': str(','.join([str(elem).strip() for elem in possible_keywords]))
            }
            update_channel_data = request.env['catalogue.template.lines'].sudo().search(
                [('id', '=', template_lines[a_index].id)]).write(
                write_channel_data)
            response = {'success': update_channel_data, 'message': 'Channel Field Update status'}
            channel_data_response.append(response)

        return channel_data_response

    @route('/api/v1/catalogue/template_line/allowed_vals/import', auth='public', type="json", csrf=False, cors="*")
    def api_import_allowed_values(self, template_line_id, allowed_list):
        template_line_id = request.env(su=True)['catalogue.template.lines'].search([('id', '=', template_line_id)])
        allowed_dict = {d: d for d in str(allowed_list).split(",")}
        if allowed_dict:
            template_line_id.allowed_values = allowed_dict
        return "Successfully update"
