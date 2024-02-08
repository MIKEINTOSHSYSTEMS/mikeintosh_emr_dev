# -*- coding: utf-8 -*-

from odoo import api, fields, models, _
from odoo.exceptions import UserError
from datetime import date, datetime, timedelta


class YANTreatment(models.Model):
    _name = 'hms.treatment'
    _description = "Treatment"
    _inherit = ['mail.thread', 'mail.activity.mixin', 'yan.hms.mixin', 'yan.documnt.mixin']

    @api.depends('medical_alert_ids')
    def _get_alert_count(self):
        for rec in self:
            rec.alert_count = len(rec.medical_alert_ids)

    @api.model
    def _get_service_id(self):
        registration_product = False
        if self.env.user.company_id.treatment_registration_product_id:
            registration_product = self.env.user.company_id.treatment_registration_product_id.id
        return registration_product

    def _rec_count(self):
        for rec in self:
            rec.appointment_count = len(rec.appointment_ids)
            rec.patient_procedure_count = len(rec.patient_procedure_ids)

    READONLY_STATES = {'cancel': [('readonly', True)], 'done': [('readonly', True)]}

    name = fields.Char(string='Name', readonly=True, index=True, copy=False, tracking=True)
    subject = fields.Char(string='Subject', tracking=True, states=READONLY_STATES)
    patient_id = fields.Many2one('hms.patient', 'Patient', required=True, index=True, states=READONLY_STATES, tracking=True)
    department_id = fields.Many2one('hr.department', ondelete='restrict', string='Department',
        domain=[('patient_department', '=', True)], states=READONLY_STATES, tracking=True)
    image_128 = fields.Binary(related='patient_id.image_128', string='Image', readonly=True)
    date = fields.Datetime(string='Date of Diagnosis', default=fields.Datetime.now, states=READONLY_STATES)
    healed_date = fields.Date(string='Healed Date', states=READONLY_STATES)
    end_date = fields.Date(string='End Date',help='End of treatment date', states=READONLY_STATES)
    diagnosis_id = fields.Many2one('hms.diseases',string='Diagnosis', states=READONLY_STATES)
    physician_id = fields.Many2one('hms.physician', ondelete='restrict', string='Physician',
        help='Physician who treated or diagnosed the patient', states=READONLY_STATES, tracking=True)
    attending_physician_ids = fields.Many2many('hms.physician','hosp_treat_doc_rel','treat_id','doc_id', string='Primary Doctors',
        states=READONLY_STATES)
    prescription_line_ids = fields.One2many('prescription.line', 'treatment_id', 'Prescription',
        states=READONLY_STATES)
    finding = fields.Text(string="Findings", states=READONLY_STATES)
    appointment_ids = fields.One2many('hms.appointment', 'treatment_id', string='Appointments',
        states=READONLY_STATES)
    appointment_count = fields.Integer(compute='_rec_count', string='# Appointments')
    state = fields.Selection([
            ('draft', 'Draft'),
            ('running', 'Running'),
            ('done', 'Completed'),
            ('cancel', 'Cancelled'),
        ], string='Status',default='draft', required=True, copy=False, states=READONLY_STATES, tracking=True)
    description = fields.Char(string='Treatment Description', states=READONLY_STATES)

    is_allergy = fields.Boolean(string='Allergic Disease', states=READONLY_STATES)
    pregnancy_warning = fields.Boolean(string='Pregnancy warning', states=READONLY_STATES)
    lactation = fields.Boolean('Lactation', states=READONLY_STATES)
    disease_severity = fields.Selection([
            ('mild', 'Mild'),
            ('moderate', 'Moderate'),
            ('severe', 'Severe'),
        ], string='Severity',index=True, states=READONLY_STATES)
    disease_status = fields.Selection([
            ('acute', 'Acute'),
            ('chronic', 'Chronic'),
            ('unchanged', 'Unchanged'),
            ('healed', 'Healed'),
            ('improving', 'Improving'),
            ('worsening', 'Worsening'),
        ], string='Status of the disease',index=True, states=READONLY_STATES)
    is_infectious = fields.Boolean(string='Infectious Disease', states=READONLY_STATES, 
        help='Check if the patient has an infectious transmissible disease')
    allergy_type = fields.Selection([
            ('da', 'Drug Allergy'),
            ('fa', 'Food Allergy'),
            ('ma', 'Misc Allergy'),
            ('mc', 'Misc Contraindication'),
        ], string='Allergy type',index=True, states=READONLY_STATES)
    age = fields.Char(string='Age when diagnosed', states=READONLY_STATES,
        help='Patient age at the moment of the diagnosis. Can be estimative')
    patient_disease_id = fields.Many2one('hms.patient.disease', string='Patient Disease', states=READONLY_STATES)
    invoice_id = fields.Many2one('account.move',string='Invoice', ondelete='restrict', copy=False)
    company_id = fields.Many2one('res.company', ondelete='restrict', states=READONLY_STATES, 
        string='Hospital',default=lambda self: self.env.company)
    medical_alert_ids = fields.Many2many('yan.medical.alert', 'treatment_medical_alert_rel','treatment_id', 'alert_id',
        string='Medical Alerts', related="patient_id.medical_alert_ids")
    alert_count = fields.Integer(compute='_get_alert_count', default=0)
    registration_product_id = fields.Many2one('product.product', default=_get_service_id, string="Registration Service")
    department_type = fields.Selection(related='department_id.department_type', string="Treatment Department", store=True)

    patient_procedure_ids = fields.One2many('yan.patient.procedure', 'treatment_id', 'Patient Procedures')
    patient_procedure_count = fields.Integer(compute='_rec_count', string='# Patient Procedures')
    procedure_group_id = fields.Many2one('procedure.group', ondelete="set null", string='Procedure Group', states=READONLY_STATES)

    @api.model
    def default_get(self, fields):
        res = super(YANTreatment, self).default_get(fields)
        if self._context.get('yan_department_type'):
            department = self.env['hr.department'].search([('department_type','=',self._context.get('yan_department_type'))], limit=1)
            if department:
                res['department_id'] = department.id
        return res

    def action_view_patient_procedures(self):
        action = self.env["ir.actions.actions"]._for_xml_id("yan_hims_tasks.action_yan_patient_procedure")
        action['domain'] = [('id', 'in', self.patient_procedure_ids.ids)]
        action['context'] = {'default_patient_id': self.patient_id.id, 'default_treatment_id': self.id, 'default_department_id': self.department_id.id}
        return action

    @api.onchange('department_id')
    def onchange_department(self):
        if self.department_id:
            self.department_type = self.department_id.department_type

    def get_line_data(self, line):
        base_date = fields.Date.today()
        return {
            'product_id': line.product_id.id,
            'patient_id': self.patient_id.id,
            'date': fields.datetime.now() + timedelta(days=line.days_to_add),
            'date_stop': fields.datetime.now() + timedelta(days=line.days_to_add) + timedelta(hours=line.product_id.procedure_time)
        }

    @api.onchange('procedure_group_id')
    def onchange_procedure_group(self):
        patient_procedure_ids = []
        if self.procedure_group_id:
            for line in self.procedure_group_id.line_ids:
                patient_procedure_ids.append((0,0,self.get_line_data(line)))
            self.patient_procedure_ids = patient_procedure_ids

    @api.model_create_multi
    def create(self, vals_list):
        for values in vals_list:
            if values.get('name', 'New Treatment') == 'New Treatment':
                values['name'] = self.env['ir.sequence'].next_by_code('hms.treatment') or 'New Treatment'
        return super().create(vals_list)

    def unlink(self):
        for data in self:
            if data.state in ['done']:
                raise UserError(('You can not delete record in done state'))
        return super(YANTreatment, self).unlink()

    def treatment_draft(self):
        self.state = 'draft'

    @api.onchange('patient_id')
    def onchange_patient_id(self):
        self.age = self.patient_id.age

    def treatment_running(self):
        patient_disease_id = self.env['hms.patient.disease'].create({
            'patient_id': self.patient_id.id,
            'treatment_id': self.id,
            'disease_id': self.diagnosis_id.id,
            'age': self.age,
            'diagnosed_date': self.date,
            'healed_date': self.healed_date,
            'allergy_type': self.allergy_type,
            'is_infectious': self.is_infectious,
            'status': self.disease_status,
            'disease_severity': self.disease_severity,
            'lactation': self.lactation,
            'pregnancy_warning': self.pregnancy_warning,
            'is_allergy': self.is_allergy,
            'description': self.description,
        })
        self.patient_disease_id = patient_disease_id.id
        self.state = 'running'

    def treatment_done(self):
        self.state = 'done'

    def treatment_cancel(self):
        self.state = 'cancel'

    def action_appointment(self):
        action = self.env["ir.actions.actions"]._for_xml_id("yan_hims_tasks.action_appointment")
        action['domain'] = [('treatment_id','=',self.id)]
        action['context'] = { 
            'default_treatment_id': self.id, 
            'default_patient_id': self.patient_id.id, 
            'default_physician_id': self.physician_id.id,
            'default_department_id': self.department_id and self.department_id.id or False}
        return action

    def create_invoice(self):
        product_id = self.registration_product_id or self.env.user.company_id.treatment_registration_product_id
        yan_context = {'commission_partner_ids':self.physician_id.partner_id.id}
        if not product_id:
            raise UserError(_("Please Configure Registration Product in Configuration first."))
        invoice = self.with_context(yan_context).yan_create_invoice(partner=self.patient_id.partner_id, patient=self.patient_id, product_data=[{'product_id': product_id}], inv_data={'hospital_invoice_type': 'treatment'})
        self.invoice_id = invoice.id

    def action_create_procedure_invoice(self):
        procedure_ids = self.patient_procedure_ids.filtered(lambda proc: not proc.invoice_id)
        if not procedure_ids:
            raise UserError(_("There is no Procedure to Invoice or all are already Invoiced."))

        product_data = []
        for procedure in procedure_ids:
            product_data.append({
                'product_id': procedure.product_id,
                'price_unit': procedure.price_unit,
            })
        inv_data = {
            'physician_id': self.physician_id and self.physician_id.id or False,
        }
        invoice = self.yan_create_invoice(partner=self.patient_id.partner_id, patient=self.patient_id, product_data=product_data, inv_data=inv_data)
        procedure_ids.write({'invoice_id': invoice.id})

    def view_invoice(self):
        invoices = self.invoice_id + self.patient_procedure_ids.mapped('invoice_id')
        action = self.yan_action_view_invoice(invoices)
        action['context'].update({
            'default_partner_id': self.patient_id.partner_id.id,
            'default_patient_id': self.id,
        })
        return action

    