# -*- coding: utf-8 -*-

from odoo import api, fields, models, _
from odoo.exceptions import UserError
from odoo.tools import DEFAULT_SERVER_DATETIME_FORMAT
from datetime import date, datetime, timedelta
from dateutil.relativedelta import relativedelta


class PatientLabTestLine(models.Model):
    _name = "laboratory.request.line"
    _description = "Test Lines"

    @api.depends('quantity', 'sale_price')
    def _compute_amount(self):
        for line in self:
            line.amount_total = line.quantity * line.sale_price

    @api.depends('test_id')
    def _yan_is_manager(self):
        is_manager = self.env.user.has_group('yan_laboratory.group_hms_lab_manager')
        for rec in self:
            rec.is_manager = is_manager

    test_category_ids = fields.Many2one('yan.laboratory.category.list', string='Test Category')
    test_id = fields.Many2one('yan.lab.test', string='Test', ondelete='cascade', required=True)
    # test_categ = fields.Selection(related='test_id.test_category', string='Test Category',
    #                               ondelete='cascade', required=True)
    # test_category_only = fields.Many2one(related='test_id.test_category', string='Test Category')
    # test_id_filtered = fields.Many2one('yan.lab.test', string='Test Name',
    #                                    domain="[('test_id', '=', test_category_only)]", select=True,
    #                                    ondelete='cascade', required=True)
    yan_tat = fields.Char(related='test_id.yan_tat', string='Turnaround Time', readonly=True)
    instruction = fields.Char(string='Special Instructions')
    request_id = fields.Many2one('yan.laboratory.request', string='Lines', ondelete='cascade')
    sale_price = fields.Float(string='Sale Price')
    company_id = fields.Many2one('res.company', ondelete='restrict',
                                 string='Company', related='request_id.company_id')
    quantity = fields.Integer(string='Quantity', default=1)
    amount_total = fields.Float(compute="_compute_amount", string="Sub Total", store=True)
    parent_line_id = fields.Many2one('laboratory.request.line', string='Parent Line', ondelete='cascade', copy=False)
    patient_lab_ids = fields.Many2many('patient.laboratory.test', 'laboratory_request_line_test_rel', 'req_line_id',
                                       'patient_lab_test_id', 'Lab Tests', ondelete='cascade')
    is_manager = fields.Boolean(compute=_yan_is_manager)

    @api.onchange('test_id')
    def onchange_test(self):
        if self.test_id:
            price = 0.0
            if self.request_id.pricelist_id:
                price = self.request_id.pricelist_id._get_product_price(self.test_id.product_id, 1)
            elif self.request_id.patient_id.property_product_pricelist:
                price = self.request_id.patient_id.property_product_pricelist._get_product_price(
                    self.test_id.product_id, 1)
            else:
                price = self.test_id.product_id.lst_price
            self.sale_price = price

    @api.model_create_multi
    def create(self, vals_list):
        res = super().create(vals_list)
        if not self._context.get('avoid_subsequent_test'):
            for record in res:
                for sub_seq_test in record.test_id.subsequent_test_ids:
                    sub_line = self.with_context(avoid_subsequent_test=True).create({
                        'parent_line_id': record.id,
                        'test_id': sub_seq_test.id,
                        'request_id': record.request_id.id,
                    })
                    sub_line.onchange_test()
        return res


class LaboratoryRequest(models.Model):
    _name = 'yan.laboratory.request'
    _description = 'Laboratory Request'
    _inherit = ['mail.thread', 'mail.activity.mixin', 'yan.hms.mixin']
    _order = 'date desc, id desc'

    @api.depends('line_ids', 'line_ids.amount_total')
    def _get_total_price(self):
        for rec in self:
            rec.total_price = sum(line.amount_total for line in rec.line_ids)

    @api.depends('patient_id', 'patient_id.birthday', 'date')
    def get_patient_age(self):
        for rec in self:
            age = ''
            if rec.patient_id.birthday:
                end_data = rec.date or fields.Datetime.now()
                delta = relativedelta(end_data, rec.patient_id.birthday)
                if delta.years <= 2:
                    age = str(delta.years) + _(" Year") + str(delta.months) + _(" Month ") + str(delta.days) + _(
                        " Days")
                else:
                    age = str(delta.years) + _(" Year")
            rec.patient_age = age

    STATES = {'requested': [('readonly', True)], 'accepted': [('readonly', True)], 'in_progress': [('readonly', True)],
              'cancel': [('readonly', True)], 'done': [('readonly', True)]}

    @api.model
    def _get_default_collection_center_id(self):
        return self.env.user.default_collection_center_id.id if self.env.user.default_collection_center_id else False

    def _yan_rec_count(self):
        for rec in self:
            rec.invoice_count = len(self.invoice_ids)

    name = fields.Char(string='Request Number', readonly=True, index=True, copy=False, tracking=True)
    notes = fields.Text(string='Notes', states=STATES)
    date = fields.Datetime('Date', required=True, default=fields.Datetime.now, states=STATES, tracking=True)
    state = fields.Selection([
        ('draft', 'Draft'),
        ('requested', 'Requested'),
        ('accepted', 'Accepted'),
        ('in_progress', 'In Progress'),
        ('to_invoice', 'To Invoice'),
        ('done', 'Done'),
        ('cancel', 'Cancel'), ],
        string='Status', readonly=True, default='draft', tracking=True)
    patient_id = fields.Many2one('hms.patient', string='Patient', required=True, ondelete='restrict', states=STATES,
                                 tracking=True)
    patient_age = fields.Char(compute="get_patient_age", string='Age', store=True,
                              help="Computed patient age at the moment of the evaluation")
    physician_id = fields.Many2one('hms.physician',
                                   string='Prescribing Doctor', help="Doctor who Request the lab test.",
                                   ondelete='restrict', states=STATES, tracking=True)
    invoice_id = fields.Many2one('account.move', string='Invoice', copy=False, states=STATES)
    lab_bill_id = fields.Many2one('account.move', string='Vendor Bill', copy=False, states=STATES)
    line_ids = fields.One2many('laboratory.request.line', 'request_id',
                               string='Lab Test Line', states=STATES, copy=True)
    invoice_exempt = fields.Boolean(string='Invoice Exemption', readonly=True)
    total_price = fields.Float(compute=_get_total_price, string='Total', store=True)
    info = fields.Text(string='Extra Info', states=STATES)
    critearea_ids = fields.One2many('lab.test.critearea', 'request_id', string='Test Cases', states=STATES)
    company_id = fields.Many2one('res.company', ondelete='restrict',
                                 string='Hospital', default=lambda self: self.env.company, states=STATES)
    pricelist_id = fields.Many2one('product.pricelist', string='Pricelist', check_company=True,
                                   domain="['|', ('company_id', '=', False), ('company_id', '=', company_id)]",
                                   help="If you change the pricelist, related invoice will be affected.")
    payment_state = fields.Selection(related="invoice_id.payment_state", store=True, string="Payment Status")
    sample_ids = fields.One2many('yan.patient.laboratory.sample', 'request_id', string='Test Samples', states=STATES)
    laboratory_group_id = fields.Many2one('laboratory.group', ondelete="set null", string='Test Group', states=STATES)
    yan_laboratory_invoice_policy = fields.Selection(related="company_id.yan_laboratory_invoice_policy")

    LABSTATES = {'cancel': [('readonly', True)], 'done': [('readonly', True)]}

    other_laboratory = fields.Boolean(string='Send to Other Laboratory', states=LABSTATES)
    collection_center_id = fields.Many2one('yan.laboratory', string='Collection Center', states=LABSTATES,
                                           default=_get_default_collection_center_id)
    laboratory_id = fields.Many2one('yan.laboratory', ondelete='restrict', string='Laboratory', states=LABSTATES)

    # Just to make object selectable in selction field this is required: Waiting Screen
    yan_show_in_wc = fields.Boolean(default=True)
    is_group_request = fields.Boolean(states=STATES)
    group_patient_ids = fields.Many2many("hms.patient", "hms_patient_lab_req_rel", "request_id", "patient_id",
                                         string="Other Group Patients", states=STATES)
    patient_test_ids = fields.One2many('patient.laboratory.test', 'request_id', string='Test Results')

    invoice_ids = fields.One2many('account.move', 'request_id', string='Invoices')
    invoice_count = fields.Integer(compute='_yan_rec_count', string='# Invoices')

    def name_get(self):
        result = []
        for rec in self:
            name = rec.name or '-'
            if rec.patient_id:
                name += ' [' + rec.patient_id.name + ']'
            result.append((rec.id, name))
        return result

    @api.onchange('laboratory_group_id')
    def onchange_laboratory_group(self):
        test_line_ids = []
        if self.laboratory_group_id:
            for line in self.laboratory_group_id.line_ids:
                test_line_ids.append((0, 0, {
                    'test_id': line.test_id.id,
                    'instruction': line.instruction,
                    'sale_price': line.sale_price,
                }))
            self.line_ids = test_line_ids

    def unlink(self):
        for rec in self:
            if rec.state not in ['draft']:
                raise UserError(_("Lab Requests can be delete only in Draft state."))
        return super(LaboratoryRequest, self).unlink()

    def button_requested(self):
        if not self.line_ids:
            raise UserError(_('Please add atleast one Laboratory test line before submitting request.'))
        self.name = self.env['ir.sequence'].next_by_code('yan.laboratory.request')
        if self.is_group_request:
            for line in self.line_ids:
                line.quantity = len(self.group_patient_ids) + 1
        self.state = 'requested'

    def prepare_sample_data(self, line, patient):
        res = {
            'sample_type_id': line.test_id.sample_type_id.id,
            'request_id': line.request_id.id,
            'user_id': self.env.user.id,
            'patient_id': patient.id,
            'company_id': line.request_id.sudo().company_id.id,
            'test_ids': [(4, line.test_id.id)]
        }
        return res

    def create_sample(self):
        Sample = self.env['yan.patient.laboratory.sample']
        patients = self.mapped('patient_id') + self.mapped('group_patient_ids')
        for line in self.line_ids:
            if line.test_id.sample_type_id:
                sample_exist = Sample.search(
                    [('request_id', '=', line.request_id.id), ('sample_type_id', '=', line.test_id.sample_type_id.id)])
                if (not sample_exist) or (line.test_id.yan_use_other_test_sample != True):
                    for patient in patients:
                        lab_sample_data = self.prepare_sample_data(line, patient)
                        Sample.create(lab_sample_data)
                    else:
                        sample_exist.test_ids = [(4, line.test_id.id)]

    def button_accept(self):
        company_id = self.sudo().company_id
        if company_id.yan_laboratory_invoice_policy == 'in_advance':
            if not self.invoice_id:
                raise UserError(_('Invoice is not created yet.'))
            elif self.invoice_id and company_id.yan_check_laboratory_payment and self.payment_state not in [
                'in_payment', 'paid']:
                raise UserError(_('Invoice is not Paid yet.'))
        if self.sudo().company_id.yan_auto_create_lab_sample:
            self.create_sample()
        self.state = 'accepted'

    def prepare_test_result_data(self, line, patient):
        parent_test_id = False
        if line.parent_line_id and line.parent_line_id.patient_lab_ids:
            parent_test_ids = line.parent_line_id.patient_lab_ids.filtered(lambda lt: lt.patient_id == patient)
            if parent_test_ids:
                parent_test_id = parent_test_ids[0].id
        res = {
            'patient_id': patient.id,
            'physician_id': self.physician_id and self.physician_id.id,
            'test_id': line.test_id.id,
            'user_id': self.env.user.id,
            'date_analysis': self.date,
            'request_id': self.id,
            'sample_ids': self.sample_ids.filtered(lambda ls: ls.patient_id == patient and ls.test_ids == line.test_id),
            'parent_test_id': parent_test_id,
        }
        return res

    def button_in_progress(self):
        self.state = 'in_progress'
        Critearea = self.env['lab.test.critearea']
        LabTest = self.env['patient.laboratory.test']
        Consumable = self.env['hms.consumable.line']
        gender = self.patient_id.gender

        patients = self.mapped('patient_id') + self.mapped('group_patient_ids')
        for line in self.line_ids:
            for patient in patients:
                lab_test_data = self.prepare_test_result_data(line, patient)
                test_result = LabTest.create(lab_test_data)
                line.patient_lab_ids = [(4, test_result.id)]
                for res_line in line.test_id.critearea_ids:
                    Critearea.create({
                        'patient_lab_id': test_result.id,
                        'name': res_line.name,
                        'normal_range': res_line.normal_range_female if gender == 'female' else res_line.normal_range_male,
                        'lab_uom_id': res_line.lab_uom_id and res_line.lab_uom_id.id or False,
                        'sequence': res_line.sequence,
                        'remark': res_line.remark,
                        'display_type': res_line.display_type,
                    })

                for con_line in line.test_id.consumable_line_ids:
                    Consumable.create({
                        'patient_lab_test_id': test_result.id,
                        'name': con_line.name,
                        'product_id': con_line.product_id and con_line.product_id.id or False,
                        'product_uom_id': con_line.product_uom_id and con_line.product_uom_id.id or False,
                        'qty': con_line.qty,
                        'date': fields.Date.today(),
                    })

    def button_done(self):
        if not self.invoice_id:
            self.state = 'to_invoice'
        else:
            self.state = 'done'

    def button_cancel(self):
        self.state = 'cancel'

    def button_draft(self):
        self.state = 'draft'

    def create_invoice(self):
        if not self.line_ids:
            raise UserError(_("Please add lab Tests first."))

        product_data = []
        for line in self.line_ids:
            product_data.append({
                'product_id': line.test_id.product_id,
                'price_unit': line.sale_price,
                'quantity': line.quantity,
            })
        yan_context = {}
        if self.pricelist_id:
            yan_context.update({'yan_pricelist_id': self.pricelist_id.id})
        if self.physician_id:
            yan_context.update({'commission_partner_ids': self.physician_id.partner_id.id})

        invoice = self.with_context(yan_context).yan_create_invoice(partner=self.patient_id.partner_id,
                                                                    patient=self.patient_id, product_data=product_data,
                                                                    inv_data={'hospital_invoice_type': 'laboratory',
                                                                              'physician_id': self.physician_id and self.physician_id.id or False})
        self.invoice_id = invoice.id
        invoice.request_id = self.id
        if self.state == 'to_invoice':
            self.state = 'done'

    def create_laboratory_bill(self):
        if not self.line_ids:
            raise UserError(_("Please add lab Tests first."))

        product_data = []
        for line in self.line_ids:
            product_data.append({
                'product_id': line.test_id.product_id,
                'price_unit': line.test_id.product_id.standard_price,
            })

        inv_data = {'type': 'in_invoice'}
        bill = self.yan_create_invoice(partner=self.laboratory_id.partner_id, patient=self.patient_id,
                                       product_data=product_data, inv_data=inv_data)
        self.lab_bill_id = bill.id
        bill.request_id = self.id

    def view_invoice(self):
        action = self.yan_action_view_invoice(self.invoice_ids)
        return action

    def action_view_test_results(self):
        action = self.env["ir.actions.actions"]._for_xml_id("yan_laboratory.action_lab_result")
        action['domain'] = [('request_id', '=', self.id)]
        action['context'] = {'default_request_id': self.id, 'default_physician_id': self.physician_id.id}
        return action

    def action_view_lab_samples(self):
        action = self.env["ir.actions.actions"]._for_xml_id("yan_laboratory.action_yan_patient_laboratory_sample")
        action['domain'] = [('request_id', '=', self.id)]
        action['context'] = {'default_request_id': self.id}
        return action

    def action_sendmail(self):
        '''
        This function opens a window to compose an email, with the template message loaded by default
        '''
        self.ensure_one()
        template_id = self.env['ir.model.data']._xmlid_to_res_id('yan_laboratory.yan_lab_req_email',
                                                                 raise_if_not_found=False)
        ctx = {
            'default_model': 'yan.laboratory.request',
            'default_res_id': self.ids[0],
            'default_use_template': bool(template_id),
            'default_template_id': template_id,
            'default_composition_mode': 'comment',
            'force_email': True
        }
        return {
            'type': 'ir.actions.act_window',
            'res_model': 'mail.compose.message',
            'views': [(False, 'form')],
            'view_id': False,
            'target': 'new',
            'context': ctx,
        }

    def _yan_get_report_base_filename(self):
        if not self.patient_test_ids:
            raise UserError(_("There are no linked results to print."))
        return (self.name or 'LabResults').replace('/', '_') + '_LabResults'
