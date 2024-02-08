# -*- coding: utf-8 -*-

from odoo import api, fields, models, _
from odoo.tools import DEFAULT_SERVER_DATE_FORMAT
from odoo.exceptions import UserError
from dateutil.relativedelta import relativedelta
from datetime import datetime

from random import randint

import base64
from io import BytesIO

import odoo.modules as addons
loaded_modules = addons.module.loaded


class YANQrcodeMixin(models.AbstractModel):
    _name = "yan.qrcode.mixin"
    _description = "QrCode Mixin"

    unique_code = fields.Char("Unique UID")
    qr_image = fields.Binary("QR Code", compute='yan_generate_qrcode')

    def yan_generate_qrcode(self):
        base_url = self.env['ir.config_parameter'].sudo().get_param('web.base.url')
        for rec in self:
            import qrcode
            model_name = (rec._name).replace('.','')
            url = base_url + '/validate/%s/%s' % (model_name,rec.unique_code)
            data = BytesIO()
            qrcode.make(url.encode(), box_size=4).save(data, optimise=True, format='PNG')
            qrcode = base64.b64encode(data.getvalue()).decode()
            rec.qr_image = qrcode


class YANHmsMixin(models.AbstractModel):
    _name = "yan.hms.mixin"
    _description = "HMS Mixin"

    def yan_prepare_invocie_data(self, partner, patient, product_data, inv_data):
        fiscal_position_id = self.env['account.fiscal.position']._get_fiscal_position(partner)
        data = {
            'partner_id': partner.id,
            'patient_id': patient and patient.id,
            'move_type': inv_data.get('move_type','out_invoice'),
            'ref': self.name,
            'invoice_origin': self.name,
            'currency_id': self.env.user.company_id.currency_id.id,
            'invoice_line_ids': self.yan_get_invoice_lines(product_data, partner, inv_data, fiscal_position_id),
            'physician_id': inv_data.get('physician_id',False),
            'hospital_invoice_type': inv_data.get('hospital_invoice_type',False),
            'fiscal_position_id': fiscal_position_id,
        }
        if inv_data.get('ref_physician_id',False):
            data['ref_physician_id'] = inv_data.get('ref_physician_id',False)
        if inv_data.get('appointment_id',False):
            data['appointment_id'] = inv_data.get('appointment_id',False)
        if "yan_hms_commission" in loaded_modules and self.env.context.get('commission_partner_ids',False):
            data['commission_partner_ids'] = [(6, 0, [self.env.context.get('commission_partner_ids')])]
        return data

    @api.model
    def yan_create_invoice(self, partner, patient=False, product_data=[], inv_data={}):
        inv_data = self.yan_prepare_invocie_data(partner, patient, product_data, inv_data)
        invoice = self.env['account.move'].create(inv_data)
        invoice._onchange_partner_id()
        for line in invoice.invoice_line_ids:
            line._get_computed_taxes()
        return invoice

    @api.model
    def yan_get_invoice_lines(self, product_data, partner, inv_data, fiscal_position_id):
        lines = []
        for data in product_data:
            product = data.get('product_id')
            quantity = data.get('quantity',1.0)
            uom_id = data.get('product_uom_id')

            if product:
                yan_pricelist_id = self.env.context.get('yan_pricelist_id')

                if not data.get('price_unit'):
                    price = product._yan_get_partner_price(quantity, uom_id, partner)
                else:
                    price = data.get('price_unit', product.list_price)

                if inv_data.get('move_type','out_invoice') in ['out_invoice','out_refund']:
                    tax_ids = product.taxes_id
                else:
                    tax_ids = product.supplier_taxes_id

                if tax_ids:
                    if fiscal_position_id:
                        tax_ids = fiscal_position_id.map_tax(tax_ids._origin)
                    tax_ids = [(6, 0, tax_ids.ids)]

                lines.append((0, 0, {
                    'name': data.get('name',product.get_product_multiline_description_sale()),
                    'product_id': product.id,
                    'price_unit': price,
                    'quantity': quantity,
                    'discount': data.get('discount',0.0),
                    'product_uom_id': uom_id,
                    'tax_ids': tax_ids,
                    'display_type': 'product',
                }))
            else:
                lines.append((0, 0, {
                    'name': data.get('name'),
                    'display_type': data.get('display_type', 'line_section'),
                }))
                
        return lines

    @api.model
    def yan_create_invoice_line(self, product_data, invoice):
        product = product_data.get('product_id')
        MoveLine = self.env['account.move.line']
        quantity = product_data.get('quantity',1.0)
        uom_id = product_data.get('product_uom_id')
        if product:
            if not product_data.get('price_unit'):
                price = product._yan_get_partner_price(quantity, uom_id, invoice.partner_id)
            else:
                price = product_data.get('price_unit', product.list_price)

            if invoice.move_type in ['out_invoice','out_refund']:
                tax_ids = product.taxes_id
            else:
                tax_ids = product.supplier_taxes_id

            if tax_ids:
                if invoice.fiscal_position_id:
                    tax_ids = invoice.fiscal_position_id.map_tax(tax_ids._origin)
                tax_ids = [(6, 0, tax_ids.ids)]

            account_id = product.property_account_income_id or product.categ_id.property_account_income_categ_id
            line = MoveLine.with_context(check_move_validity=False).create({
                'move_id': invoice.id,
                'name': product_data.get('name',product.get_product_multiline_description_sale()),
                'product_id': product.id,
                'account_id': account_id.id,
                'price_unit': price,
                'quantity': quantity,
                'discount': product_data.get('discount',0.0),
                'product_uom_id': uom_id,
                'tax_ids': tax_ids,
                'display_type': 'product',
            })
        else:
            line = MoveLine.with_context(check_move_validity=False).create({
                'move_id': invoice.id,
                'name': product_data.get('name'),
                'display_type': 'line_section',
            })
            
        return line

    def yan_action_view_invoice(self, invoices):
        action = self.env["ir.actions.actions"]._for_xml_id("account.action_move_out_invoice_type")
        if len(invoices) > 1:
            action['domain'] = [('id', 'in', invoices.ids)]
        elif len(invoices) == 1:
            action['views'] = [(self.env.ref('account.view_move_form').id, 'form')]
            action['res_id'] = invoices.id
        elif self.env.context.get('yan_open_blank_list'):
            #Allow to open invoices
            action['domain'] = [('id', 'in', invoices.ids)]
        else:
            action = {'type': 'ir.actions.act_window_close'}

        context = {
            'default_move_type': 'out_invoice',
        }
        action['context'] = context
        return action

    @api.model
    def assign_given_lots(self, move, lot_id, lot_qty):
        MoveLine = self.env['stock.move.line'].sudo()
        move_line_id = MoveLine.search([('move_id', '=', move.id),('lot_id','=',False)],limit=1)
        if move_line_id:
            move_line_id.lot_id = lot_id
            move_line_id.qty_done = lot_qty

    def consume_material(self, source_location_id, dest_location_id, product_data):
        product = product_data['product']
        move = self.env['stock.move'].sudo().create({
            'name' : product.name,
            'product_id': product.id,
            'product_uom': product.uom_id.id,
            'product_uom_qty': product_data.get('qty',1.0),
            'date': product_data.get('date',fields.datetime.now()),
            'location_id': source_location_id,
            'location_dest_id': dest_location_id,
            'state': 'draft',
            'origin': self.name,
            'quantity_done': product_data.get('qty',1.0),
        })
        move._action_confirm()
        move._action_assign()
        if product_data.get('lot_id', False):
            lot_id = product_data.get('lot_id')
            lot_qty = product_data.get('qty',1.0)
            self.sudo().assign_given_lots(move, lot_id, lot_qty)
        if move.state == 'assigned':
            move._action_done()
        return move

    def yan_apply_invoice_exemption(self):
        for rec in self:
            rec.invoice_exempt = False if rec.invoice_exempt else True


class YANDocumntMixin(models.AbstractModel):
    _name = "yan.documnt.mixin"
    _description = "Document Mixin"

    def _yan_get_attachemnts(self):
        attachments = self.env['ir.attachment'].search([
            ('res_model', '=', self._name),
            ('res_id', '=', self.id)])
        return attachments 

    def _yan_attachemnt_count(self):
        for rec in self:
            attachments = rec._yan_get_attachemnts()
            rec.attach_count = len(attachments)
            rec.attachment_ids = [(6,0,attachments.ids)]

    attach_count = fields.Integer(compute="_yan_attachemnt_count", readonly=True, string="Documents")
    attachment_ids = fields.Many2many('ir.attachment', 'attachment_yan_hms_rel', 'record_id', 'attachment_id', compute="_yan_attachemnt_count", string="Attachments")

    def action_view_attachments(self):
        self.ensure_one()
        action = self.env["ir.actions.actions"]._for_xml_id("base.action_attachment")
        action['domain'] = [('id', 'in', self.attachment_ids.ids)]
        action['context'] = {
                'default_res_model': self._name,
                'default_res_id': self.id,
                'default_is_document': True}
        return action


class YANAppointmentConsumable(models.Model):
    _name = "hms.consumable.line"
    _description = "List of Consumables"

    @api.depends('price_unit','qty')
    def yan_get_total_price(self):
        for rec in self:
            rec.subtotal = rec.qty * rec.price_unit

    name = fields.Char(string='Name',default=lambda self: self.product_id.name)
    product_id = fields.Many2one('product.product', ondelete="restrict", string='Products/Services')
    product_uom_category_id = fields.Many2one('uom.category', related='product_id.uom_id.category_id')
    product_uom_id = fields.Many2one('uom.uom', string='Unit of Measure', help='Amount of medication (eg, 250 mg) per dose', domain="[('category_id', '=', product_uom_category_id)]")
    qty = fields.Float(string='Quantity', default=1.0)
    tracking = fields.Selection(related='product_id.tracking', store=True)
    lot_id = fields.Many2one('stock.lot', string='Lot/Serial Number', 
        domain="[('product_id', '=', product_id),('product_qty','>',0),'|',('expiration_date','=',False),('expiration_date', '>', context_today().strftime('%Y-%m-%d'))]")
    price_unit = fields.Float(related='product_id.list_price', string='Unit Price', readonly=True)
    subtotal = fields.Float(compute=yan_get_total_price, string='Subtotal', readonly=True, store=True)
    move_id = fields.Many2one('stock.move', string='Stock Move')
    physician_id = fields.Many2one('hms.physician', string='Physician')
    department_id = fields.Many2one('hr.department', string='Department')
    patient_id = fields.Many2one('hms.patient', string='Patient')
    date = fields.Date("Date", default=fields.Date.context_today)
    note = fields.Char("Note")
    invoice_id = fields.Many2one('account.move', string='Invoice', copy=False)

    @api.onchange('product_id')
    def onchange_product(self):
        if self.product_id:
            self.product_uom_id = self.product_id.uom_id.id

class YANPatientTag(models.Model):
    _name = "hms.patient.tag"
    _description = "YAN Patient Tag"

    def _get_default_color(self):
        return randint(1, 11)

    name = fields.Char(string="Name")
    color = fields.Integer('Color', default=_get_default_color)


class YANTherapeuticEffect(models.Model):
    _name = "hms.therapeutic.effect"
    _description = "YAN Therapeutic Effect"


    code = fields.Char(string="Code")
    name = fields.Char(string="Name", required=True)
