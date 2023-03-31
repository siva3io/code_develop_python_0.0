# -*- coding: utf-8 -*-
###############################################################################
#
# Fortutech IMS Pvt. Ltd.
# Copyright (C) 2016-TODAY Fortutech IMS Pvt. Ltd.(<http://www.fortutechims.com>).
#
###############################################################################
from odoo import fields, models, api, _
from odoo.exceptions import AccessError, UserError


class FimsRom(models.Model):
    _name = "fims.rom"
    _description = "ROM"
    _inherit = ['mail.thread', 'portal.mixin']
    _order = "number desc"
    _rec_name = 'number'

    @api.onchange('sale_id')
    def onchange_sale_id(self):
        if self.sale_id:
            self.user_id = self.sale_id.user_id.id
            self.picking_id = False

    @api.onchange('picking_id')
    def onchange_picking_id(self):
        res = {}
        if self.picking_id:
            lines = []
            for move in self.picking_id.move_lines:
                return_move_ids = self.env['stock.move'].search([('origin_returned_move_id', '=', move.id)])
                returned_qty = sum(return_move_ids.mapped('product_uom_qty'))
                if move.product_uom_qty - returned_qty > 0:
                    lines.append((0, 0,
                                  {'product_id': move.product_id.id, 'return_qty': move.product_uom_qty - returned_qty,
                                   'move_id': move.id}))

            self.rom_product_line_ids = lines
            if self.picking_id.move_lines:
                location = self.picking_id.move_lines[0].location_id
                self.location_id = location.id

                domain = {'location_id': [('id', 'in', [location.id])]}
                res['domain'] = domain

        return res

    def _get_refund_invoices(self):
        for obj in self:
            if obj.refund_invoice_ids:
                obj.is_refund_invoices = True
            else:
                obj.is_refund_invoices = False

    number = fields.Char(string="Number")
    sale_id = fields.Many2one('sale.order', string="Sale Order", copy=False, required=False)
    purchase_id = fields.Many2one('purchase.order', string="Purchase Order", copy=False, required=False)
    grn_number = fields.Many2one(comodel_name='stock.picking', string='Grn_number', required=False)
    sku_id = fields.Many2one(comodel_name='product.product', string='Sku_id', required=False)
    ordered_quantity = fields.Char(string='Ordered Quantity', required=False)
    received_quantity = fields.Char(string='Received Quantity', required=False)
    accepted_quantity = fields.Char(string='Accepted Quantity', required=False)
    delivery_id = fields.Many2one('stock.picking', string="Delivery Order", copy=False)
    replaced_sale_id = fields.Many2one('sale.order', string="Replaced Sale Order", copy=False)
    company_id = fields.Many2one('res.company', related="sale_id.company_id", string="Company")
    picking_id = fields.Many2one('stock.picking', string="Picking", copy=False)
    partner_id = fields.Many2one('res.partner', related="sale_id.partner_id", string="Partner")
    email = fields.Char('Email', related="sale_id.partner_id.email", readonly=False, store_true=True)
    phone = fields.Char('Phone', related="sale_id.partner_id.phone", readonly=False, store_true=True)
    user_id = fields.Many2one('res.users', string="Sales Person")
    date = fields.Date("Date", default=fields.Date.context_today)
    state = fields.Selection([('new', 'New'), ('in_progress', 'In Progress'),
                              ('done', 'Done'), ('rejected', 'Rejected')], 'State', default="new", tracking=True)
    location_id = fields.Many2one('stock.location', string="Return Location", domain=[('usage', '=', 'internal')])
    description = fields.Text('Description', copy=False)

    return_picking_id = fields.Many2one('stock.picking', string='Return Delivery Order', copy=False)
    asn_id = fields.Many2one('asn.asn', string='asn_id', copy=False)
    grn_id = fields.Many2one('stock.picking', string='grn_id', copy=False)
    out_picking_ids = fields.Many2many('stock.picking', string='Out Delivery Order', copy=False)
    rom_product_line_ids = fields.One2many("rom.product.lines", "rom_id", string="Return Line")
    rom_repair_line_ids = fields.One2many("rom.repair.lines", "rom_id", string="Repair Line")
    refund_invoice_ids = fields.Many2many('account.move', string='Refund Invoices', copy=False)
    is_refund_invoices = fields.Boolean(compute=_get_refund_invoices, copy=False)
    grn_number = fields.Many2one(comodel_name='stock.picking', string='Grn_number', required=False)



    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            vals['number'] = self.env['ir.sequence'].sudo().next_by_code('fims.rom.seq')
        res = super(FimsRom, self).create(vals_list)
        return res

    def unlink(self):
        for obj in self:
            if obj.state != 'new':
                raise UserError(_("You can not delete processed ROM."))
        return super(FimsRom, self).unlink()

    def set_new(self):
        self.state = 'new'

    def approve_rom(self):
        #         rom_ids = self.search([('picking_id', '=', self.picking_id.id), ('id', '!=', self.id), ('state', 'not in', ['new', 'rejected'])])
        #         if rom_ids:
        #             raise UserError(_("%s Delivery order is already processed." % (self.picking_id.name)))

        for line in self.rom_product_line_ids:
            if not line.action_type:
                raise UserError(_("Please set Action in all ROM lines."))
        self.create_back_order()
        self.state = 'in_progress'
        return True

    def process_rom(self):
        if self.return_picking_id.state != 'done':
            raise UserError("Please validate Return Delivery.")
        replace_line = []
        refund_line = []
        repair_line = []
        delivery_line = []

        for line in self.rom_product_line_ids:
            if line.return_qty == 0.0:
                continue
            if line.action_type == 'repair':
                repair_line.append(line)
                if not self.rom_repair_line_ids and not self._context.get('from_wizard'):
                    context = dict(self.env.context or {})
                    context['from_wizard'] = True
                    views = [(self.env.ref('fims_return_order_management.view_fims_rom_wizard').id, 'form')]
                    return {
                        'name': "Repair Products",
                        'view_type': 'form',
                        'view_mode': 'form',
                        'res_model': 'fims.rom',
                        'type': 'ir.actions.act_window',
                        'context': context,
                        'views': views,
                        'view_id': False,
                        'target': 'new',
                        'res_id': self.id,
                    }

            if line.action_type == 'refund':
                refund_line.append(line)
            if line.action_type == 'replace':
                if not line.replace_product_id or line.replace_quantity <= 0.0:
                    raise UserError(
                        _("Please set Replace Product and quantity in ROM Lines which action type is Replace."))
                if line.manage_invoice:
                    replace_line.append(line)
                else:
                    delivery_line.append(line)

        if repair_line:
            self.create_delivery_order(repair_line)
        if refund_line:
            self.create_refund_invoice(refund_line)
        if replace_line:
            self.create_sale_order(replace_line)
            self.create_refund_invoice(replace_line)
        if delivery_line:
            self.create_replace_delivery(delivery_line)

        self.state = 'done'
        return True

    def reject_rom(self):
        if self.return_picking_id:
            self.return_picking_id.action_cancel()
        self.state = 'rejected'
        return True

    def create_back_order(self):
        vals = {
            'picking_id': self.picking_id.id,
            'location_id': self.location_id.id
        }
        return_wizard = self.env['stock.return.picking'].with_context(active_id=self.picking_id.id).sudo().create(vals)
        lines = []
        return_wizard.product_return_moves.unlink()
        for l in self.rom_product_line_ids:
            if l.return_qty == 0.0:
                continue
            move_id = self.env['stock.move'].sudo().search(
                [('product_id', '=', l.product_id.id), ('sale_line_id', '=', l.sudo().move_id.sale_line_id.id),
                 ('picking_id', '=', self.picking_id.id)])
            r_line = self.env['stock.return.picking.line'].create(
                {'product_id': l.product_id.id, 'quantity': l.return_qty, 'wizard_id': return_wizard.id,
                 'move_id': move_id.id})
            lines.append(r_line.id)

        new_picking_id, pick_type_id = return_wizard._create_returns()
        self.return_picking_id = new_picking_id

        return True

    def create_delivery_order(self, repair_line):
        vals = {
            'picking_id': self.return_picking_id.id,
            'location_id': self.location_id.id
        }
        return_wizard = self.env['stock.return.picking'].with_context(active_id=self.return_picking_id.id).create(vals)
        lines = []
        return_wizard.product_return_moves.unlink()
        for l in repair_line:
            move_id = self.env['stock.move'].search(
                [('product_id', '=', l.product_id.id), ('sale_line_id', '=', l.move_id.sale_line_id.id),
                 ('picking_id', '=', self.return_picking_id.id)])
            r_line = self.env['stock.return.picking.line'].create(
                {'product_id': l.product_id.id, 'quantity': l.return_qty, 'wizard_id': return_wizard.id,
                 'move_id': move_id.id})
            lines.append(r_line.id)

        new_picking_id, pick_type_id = return_wizard._create_returns()
        self.out_picking_ids = [(4, new_picking_id)]
        if self.rom_repair_line_ids:
            self.create_invoice_for_repair()

        return True

    def create_replace_delivery(self, delivery_line):
        move_lines = []
        for line in delivery_line:
            move_vals = {'product_id': line.replace_product_id.id,
                         'product_uom_qty': line.replace_quantity,
                         'product_uom': line.replace_product_id.uom_id.id,
                         'location_id': self.picking_id.location_id.id,
                         'location_dest_id': self.picking_id.location_dest_id.id,
                         'name': line.replace_product_id.name,
                         'company_id': self.picking_id.company_id.id,
                         'state': 'draft'}
            move_lines.append((0, 0, move_vals))

        do_vals = {'partner_id': self.partner_id.id,
                   'origin': self.number,
                   'location_id': self.picking_id.location_id.id,
                   'location_dest_id': self.picking_id.location_dest_id.id,
                   'move_ids_without_package': move_lines,
                   'picking_type_id': self.picking_id.picking_type_id.id}

        delivery_order = self.env['stock.picking'].create(do_vals)

        self.out_picking_ids = [(4, delivery_order.id)]
        delivery_order.action_assign()

    def create_refund_invoice(self, refund_line):
        invoice_ids = {}
        flag = False
        refund_data = {}
        for line in refund_line:
            if line.id not in refund_data:
                refund_data.update({line.id: {'quantity': line.received_qty, 'inv_line_ids': []}})
            for invoice_line in line.move_id.sale_line_id.invoice_lines:
                if invoice_line.move_id.move_type != 'out_invoice' or invoice_line.move_id.state not in ['posted']:
                    continue
                flag = True
                if refund_data.get(line.id).get('refund_qty', 0.0) < refund_data.get(line.id).get('quantity', 0.0):
                    if refund_data.get(line.id).get('refund_qty', 0.0) + invoice_line.quantity < refund_data.get(
                            line.id).get('quantity', 0.0):
                        refund_qty = invoice_line.quantity
                        #                         refund_data.get(line.id).update({'refund_qty':refund_data.get(line.id).get('refund_qty',0.0)+invoice_line.quantity})
                        refund_data.get(line.id).update({'refund_qty': line.return_qty})
                    else:
                        refund_qty = refund_data.get(line.id).get('quantity', 0) - refund_data.get(line.id).get(
                            'refund_qty', 0.0)
                        #                         refund_data.get(line.id).update({'refund_qty':refund_data.get(line.id).get('quantity', 0.0)})
                        refund_data.get(line.id).update({'refund_qty': line.return_qty})
                    refund_data.get(line.id).get('inv_line_ids').append(
                        [invoice_line, refund_qty, invoice_line.move_id])

                    if invoice_ids.get(invoice_line.move_id.id):
                        invoice_ids.get(invoice_line.move_id.id).append(
                            {invoice_line.product_id.id: refund_qty, 'price': line.move_id.sale_line_id.price_unit})
                    else:
                        invoice_ids.update({invoice_line.move_id.id: [
                            {invoice_line.product_id.id: refund_qty, 'price': line.move_id.sale_line_id.price_unit}]})

        if not flag:
            raise UserError(_("Please check for related Sale order, if there is Invoice Paid or Validated.!"))

        list_ids = []
        existing_refund_inv = False
        for inv in self.refund_invoice_ids:
            if inv.state == 'draft':
                existing_refund_inv = inv

        for invoice_id, refund in invoice_ids.items():
            invoice_obj = self.env['account.move'].browse(invoice_id)
            inv_line = []
            for data in refund_data:
                for line in refund_data.get(data).get('inv_line_ids'):
                    line_vals = {
                        'product_id': line[0].product_id.id,
                        'name': line[0].product_id.name,
                        'account_id': line[0].product_id.categ_id.property_account_income_categ_id.id,
                        'price_unit': line[0].price_unit,
                        'quantity': refund_data.get(data).get('refund_qty'),
                        'product_uom_id': line[0].product_id.uom_id.id,
                        'tax_ids': [(6, 0, line[0].tax_ids.ids)],
                    }
                    inv_line.append((0, 0, line_vals))

            if not existing_refund_inv:
                for move in invoice_obj:
                    move_reversal = self.env['account.move.reversal'].create({'refund_method': 'refund',
                                                                              'date': fields.Date.today(),
                                                                              'journal_id': move.journal_id.id})
                    default_values = move_reversal._prepare_default_reversal(move)
                    default_values.update({
                        'move_type': 'out_refund',
                        'partner_id': move.partner_id.id
                    })
                    default_values['invoice_line_ids'] = inv_line
                    refund_invoice = self.env['account.move'].create(default_values)
            else:
                existing_refund_inv.write({'invoice_line_ids': inv_line})
                refund_invoice = existing_refund_inv

            list_ids.append(refund_invoice)

        if list_ids:
            for inv in list_ids:
                if inv not in self.refund_invoice_ids:
                    self.refund_invoice_ids = [(4, inv.id)]

    def create_invoice_for_repair(self):
        # journal_id = self.env['account.move'].default_get(['journal_id'])['journal_id']
        # if not journal_id:
        #     raise UserError(_('Please define an accounting sales journal for this company.'))
        invoice_vals = {
            'invoice_origin': self.number,
            'move_type': 'out_invoice',
            'partner_id': self.sale_id.partner_invoice_id.id,
            'partner_shipping_id': self.sale_id.partner_shipping_id.id,
            # 'journal_id': journal_id,
            'currency_id': self.sale_id.pricelist_id.currency_id.id,
            'invoice_payment_term_id': self.sale_id.payment_term_id.id,
            'fiscal_position_id': self.sale_id.fiscal_position_id.id or self.sale_id.partner_invoice_id.property_account_position_id.id,
            'company_id': self.sale_id.company_id.id,
            'user_id': self.sale_id.user_id and self.sale_id.user_id.id,
            'team_id': self.sale_id.team_id.id,
            'transaction_ids': [(6, 0, self.sale_id.transaction_ids.ids)],
        }
        onchanges = {
            '_onchange_partner_id': ['invoice_payment_term_id', 'fiscal_position_id', 'partner_bank_id'],
            '_onchange_journal_id': ['currency_id'],
        }
        for onchange_method, changed_fields in onchanges.items():
            if any(f not in invoice_vals for f in changed_fields):
                invoice = self.env['account.move'].new(invoice_vals)
                getattr(invoice, onchange_method)()
                for field in changed_fields:
                    if field not in invoice_vals and invoice[field]:
                        invoice_vals[field] = invoice._fields[field].convert_to_write(invoice[field], invoice)

        # prepare invoice line
        inv_lines = []
        for repair_line in self.rom_repair_line_ids:
            line_vals = {
                'product_id': repair_line.product_id and repair_line.product_id.id or False,
                'name': repair_line.name,
                'account_id': repair_line.product_id.categ_id.property_account_income_categ_id.id,
                'price_unit': repair_line.price_unit,
                'quantity': repair_line.quantity,
                'product_uom_id': repair_line.uom_id.id,
                'tax_ids': [(6, 0, repair_line.tax_ids.ids)],
                'analytic_account_id': self.sale_id.analytic_account_id.id,
            }
            inv_lines.append((0, 0, line_vals))
        invoice_vals['invoice_line_ids'] = inv_lines
        move_id = self.env['account.move'].create(invoice_vals)
        self.refund_invoice_ids = [(4, move_id.id)]

    def create_sale_order(self, replace_line):
        replaced_sale_id = self.sale_id.copy({'client_order_ref': self.number, 'order_line': False})
        replaced_sale_id.order_line
        for line in replace_line:
            vals = {
                'order_id': replaced_sale_id.id,
                'product_id': line.replace_product_id.id
            }
            new_vals = self.env['sale.order.line'].new(vals)
            new_vals.product_id_change()
            new_vals = self.env['sale.order.line']._convert_to_write({name: new_vals[name] for name in new_vals._cache})
            new_vals.update({'product_uom_qty': line.replace_quantity})
            self.env['sale.order.line'].create(new_vals)

        self.replaced_sale_id = replaced_sale_id.id

    def get_return_picking(self):
        if self.return_picking_id:
            return {'name': "Return Delivery",
                    'view_type': 'form',
                    'view_mode': 'form',
                    'res_model': 'stock.picking',
                    'type': 'ir.actions.act_window',
                    'res_id': self.return_picking_id.id}
        else:
            raise UserError(_("There is not related Return Delivery.!"))

    def get_deliver_picking(self):
        if self.out_picking_ids:
            views = [(self.env.ref('stock.vpicktree').id, 'tree'), (self.env.ref('stock.view_picking_form').id, 'form')]
            return {'name': "Delivery Order",
                    'view_type': 'form',
                    'view_mode': 'tree,from',
                    'res_model': 'stock.picking',
                    'type': 'ir.actions.act_window',
                    'view_id': False,
                    'views': views,
                    'domain': [('id', 'in', self.out_picking_ids.ids)]}
        else:
            raise UserError(_("There is not related Delivery Orders.!"))

    def get_replace_sale_order(self):
        if self.replaced_sale_id:
            return {'name': "Replaces Sale Order",
                    'view_type': 'form',
                    'view_mode': 'form',
                    'res_model': 'sale.order',
                    'type': 'ir.actions.act_window',
                    'res_id': self.replaced_sale_id.id}
        else:
            raise UserError(_("There is not related Replaced Sale order.!"))

    def get_refund_invoices(self):
        if self.refund_invoice_ids:
            views = [(self.env.ref('account.view_invoice_tree').id, 'tree'),
                     (self.env.ref('account.view_move_form').id, 'form')]
            return {
                'name': _('Invoices'),
                'view_type': 'form',
                'view_mode': 'tree,from',
                'res_model': 'account.move',
                'view_id': False,
                'views': views,
                'type': 'ir.actions.act_window',
                'domain': [('id', 'in', self.refund_invoice_ids.ids)],
            }
        else:
            raise UserError(_("There is not Refund Invoices.!"))


class RomProductLines(models.Model):
    _name = "rom.product.lines"

    def _get_deliver_quantity(self):
        for obj in self:
            if obj.rom_id.picking_id:
                obj.delivered_qty = obj.move_id.sudo().quantity_done

    def _get_received_quantity(self):
        for obj in self:
            if obj.rom_id.picking_id:
                obj.received_qty = False
                move_line = self.env['stock.move'].search([('picking_id', '=', obj.rom_id.return_picking_id.id),
                                                           ('sale_line_id', '=', obj.move_id.sale_line_id.id)], limit=1)
                obj.received_qty = move_line.quantity_done

    product_id = fields.Many2one('product.product', string="Product")
    delivered_qty = fields.Float('Original Delivered Qty', compute=_get_deliver_quantity)
    return_qty = fields.Float('Return Qty')
    received_qty = fields.Float('Received Qty', compute=_get_received_quantity)
    replace_quantity = fields.Float("Replace Quantity", copy=False)
    rom_id = fields.Many2one('fims.rom')
    action_type = fields.Selection([('refund', 'Refund'), ('replace', 'Replace'), ('repair', 'Repair')], "Action")
    move_id = fields.Many2one('stock.move')
    replace_product_id = fields.Many2one('product.product', "Replace Product")
    manage_invoice = fields.Boolean('Manage Invoice ?')

    def unlink(self):
        for obj in self:
            if obj.rom_id and obj.rom_id.state != 'new':
                raise UserError(_("You can not delete processed ROM Line."))
        return super(RomProductLines, self).unlink()


class RomRepairLines(models.Model):
    _name = "rom.repair.lines"

    rom_id = fields.Many2one('fims.rom')
    product_id = fields.Many2one('product.product', string="Product")
    name = fields.Char('Description')
    quantity = fields.Float('Quantity')
    uom_id = fields.Many2one('uom.uom', "Unit of Measure")
    price_unit = fields.Float('Price')
    tax_ids = fields.Many2many('account.tax', string="Taxes")

    @api.onchange('product_id')
    def product_id_change(self):
        if not self.product_id:
            return {'domain': {'uom_id': []}}
        else:
            self.uom_id = self.product_id.uom_id.id
            self.price_unit = self.product_id.lst_price
            self.tax_ids = self.product_id.taxes_id or False
            self.name = self.product_id.name
            domain = {'uom_id': [('category_id', '=', self.product_id.uom_id.category_id.id)]}
            return {'domain': domain}


class Scraps(models.Model):
    _inherit = "stock.scrap"

    purchase_id = fields.Many2one(comodel_name='purchase.order', string="purchase Order Ids", copy=False)
    picking_id = fields.Many2one(comodel_name='stock.picking', string="internal Transfer Ids", copy=False)
    asn_id = fields.Many2one(comodel_name='asn.asn', string='Asn_ids', required=False)
    grn_number = fields.Many2one(comodel_name='stock.picking', string='grn_number', required=False)
    ordered_units = fields.Integer(string='ordered_units', required=False)
    received_units = fields.Integer(string='received_units', required=False)
    price = fields.Many2one(comodel_name='product.product', string='Price', required=False)
    reason = fields.Char(string='reason', required=False)
