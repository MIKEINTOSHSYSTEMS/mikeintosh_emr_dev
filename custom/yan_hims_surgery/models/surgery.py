# coding=utf-8
from odoo import api, fields, models, _
from odoo.exceptions import UserError


class YANSurgeryTemplate(models.Model):
    _name = "hms.surgery.template"
    _description = "Surgery Template"

    name= fields.Char(string='Surgery Code', 
        help="Procedure Code, for example ICD-10-PCS Code 7-character string")
    surgery_name= fields.Char (string='Surgery Name')
    diseases_id = fields.Many2one ('hms.diseases', ondelete='restrict', string='Disease', help="Reason for the surgery.")
    dietplan_id = fields.Many2one('hms.dietplan', ondelete='set null', string='Diet Plan')
    surgery_product_id = fields.Many2one('product.product', ondelete='cascade',
        string= "Product", required=True)
    diagnosis = fields.Text(string="Diagnosis")
    clinincal_history = fields.Text(string="Clinical History")
    examination = fields.Text(string="Examination")
    investigation = fields.Text(string="Investigation")
    adv_on_dis = fields.Text(string="Advice on Discharge")
    notes = fields.Text(string='Operative Notes')
    classification = fields.Selection ([
        ('o','Optional'),
        ('r','Required'),
        ('u','Urgent')], string='Surgery Classification', index=True)
    extra_info = fields.Text (string='Extra Info')
    special_precautions = fields.Text(string="Special Precautions")
    consumable_line_ids = fields.One2many('hms.consumable.line', 'surgery_template_id', string='Consumable Line', help="List of items that are consumed during the surgery.")
    medicament_line_ids = fields.One2many('medicament.line', 'surgery_template_id', string='Medicament Line', help="Define the medicines to be taken after the surgery")
    company_id = fields.Many2one('res.company', ondelete='restrict', 
        string='Hospital', default=lambda self: self.env.company)


class YANSurgery(models.Model):
    _name = "hms.surgery"
    _description = "Surgery"
    _inherit = ['mail.thread', 'mail.activity.mixin', 'yan.hms.mixin']
    _order = "id desc"

    @api.model
    def _default_prechecklist(self):
        vals = []
        prechecklists = self.env['pre.operative.check.list.template'].search([])
        for prechecklist in prechecklists:
            vals.append((0,0,{
                'name': prechecklist.name,
                'remark': prechecklist.remark,
            }))
        return vals

    @api.depends('pre_operative_checklist_ids','pre_operative_checklist_ids.is_done')
    def _compute_checklist_done(self):
        for rec in self:
            if rec.pre_operative_checklist_ids:
                done_checklist = rec.pre_operative_checklist_ids.filtered(lambda s: s.is_done)
                rec.pre_operative_checklist_done = (len(done_checklist)* 100)/len(rec.pre_operative_checklist_ids)
            else:
                rec.pre_operative_checklist_done = 0

    @api.depends('patient_id')
    def _get_patient_age(self):
        for rec in self:
            if rec.patient_id:
                rec.age = rec.patient_id.age

    def _yan_rec_count(self):
        for rec in self:
            rec.invoice_count = len(self.invoice_ids)

    STATES = {'cancel': [('readonly', True)], 'done': [('readonly', True)]}

    name = fields.Char(string='Surgery Number', copy=False, readonly=True)
    state = fields.Selection([
        ('draft', 'Draft'),
        ('confirm', 'Confirmed'),
        ('cancel', 'Cancelled'),
        ('done', 'Done'),], string='Status', default='draft', states=STATES)
    surgery_name= fields.Char (string='Surgery Name', states=STATES)
    diseases_id = fields.Many2one ('hms.diseases', ondelete='restrict', 
        string='Disease', help="Reason for the surgery.", states=STATES)
    dietplan_id = fields.Many2one('hms.dietplan', ondelete='set null', 
        string='Diet Plan', states=STATES)
    surgery_product_id = fields.Many2one('product.product', ondelete='cascade',
        string= "Surgery Product", required=True, states=STATES)
    surgery_template_id = fields.Many2one('hms.surgery.template', ondelete='restrict',
        string= "Surgery Template", states=STATES)
    patient_id = fields.Many2one('hms.patient', ondelete="restrict", string='Patient', states=STATES)
    diagnosis = fields.Text(string="Diagnosis", states=STATES)
    clinincal_history = fields.Text(string="Clinical History", states=STATES)
    examination = fields.Text(string="Examination", states=STATES)
    investigation = fields.Text(string="Investigation", states=STATES)
    adv_on_dis = fields.Text(string="Advice on Discharge", states=STATES)
    notes = fields.Text(string='Operative Notes', states=STATES)
    classification = fields.Selection ([
            ('o','Optional'),
            ('r','Required'),
            ('u','Urgent')
        ], string='Surgery Classification', index=True, states=STATES)
    age = fields.Char(string='Patient age',
        help='Patient age at the moment of the surgery. Can be estimative',compute='_get_patient_age' ,states=STATES ,store=True)
    extra_info = fields.Text (string='Extra Info', states=STATES)
    special_precautions = fields.Text(string="Special Precautions", states=STATES)
    consumable_line_ids = fields.One2many('hms.consumable.line', 'surgery_id', string='Consumable Line', help="List of items that are consumed during the surgery.", states=STATES)
    medicament_line_ids = fields.One2many('medicament.line', 'surgery_id', string='Medicament Line', help="Define the medicines to be taken after the surgery", states=STATES)

    #Hospitalization Surgery
    start_date = fields.Datetime(string='Surgery Date', states=STATES)
    end_date = fields.Datetime(string='End Date', states=STATES)
    anesthetist_id = fields.Many2one('hms.physician', string='Anesthetist', ondelete="set null", 
        help='Anesthetist data of the patient', states=STATES)
    anesthesia_id = fields.Many2one('hms.anesthesia', ondelete="set null", 
        string="Anesthesia", states=STATES)
    primary_physician_id = fields.Many2one('hms.physician', ondelete="restrict", 
        string='Main Surgeon', states=STATES)
    primary_physician_ids = fields.Many2many('hms.physician','hosp_pri_doc_rel','hosp_id','doc_id',
        string='Primary Surgeons', states=STATES)
    assisting_surgeon_ids = fields.Many2many('hms.physician','hosp_doc_rel','hosp_id','doc_id',
        string='Assisting Surgeons', states=STATES)
    scrub_nurse_id = fields.Many2one('res.users', ondelete="set null", 
        string='Scrub Nurse', states=STATES)
    pre_operative_checklist_ids = fields.One2many('pre.operative.check.list', 'surgery_id', 
        string='Pre-Operative Checklist', default=lambda self: self._default_prechecklist(), states=STATES)
    pre_operative_checklist_done = fields.Float('Pre-Operative Checklist Done', compute='_compute_checklist_done', store=True)
    notes = fields.Text(string='Operative Notes', states=STATES)
    post_instruction = fields.Text(string='Instructions', states=STATES)

    special_precautions = fields.Text(string="Special Precautions", states=STATES)
    company_id = fields.Many2one('res.company', ondelete='restrict', 
        string='Hospital', default=lambda self: self.env.company)
    invoice_id = fields.Many2one('account.move', string='Invoice', copy=False)
    treatment_id = fields.Many2one('hms.treatment', string='Treatment', copy=False)
    department_id = fields.Many2one('hr.department', ondelete='restrict', 
        domain=[('patient_department', '=', True)], string='Department', tracking=True, states=STATES)
    appointment_id = fields.Many2one('hms.appointment', string='Appointment', copy=False)
    invoice_ids = fields.One2many('account.move', 'surgery_id', string='Invoices')
    invoice_count = fields.Integer(compute='_yan_rec_count', string='# Invoices')

    @api.onchange('surgery_template_id')
    def onchange_surgery_id(self):
        medicament_lines = []
        consumable_lines = []
        Consumable = self.env['hms.consumable.line']
        MedicamentLine = self.env['medicament.line']
        if self.surgery_template_id:
            self.surgery_name = self.surgery_template_id.surgery_name
            self.diseases_id = self.surgery_template_id.diseases_id and self.surgery_template_id.diseases_id.id
            self.surgery_product_id = self.surgery_template_id.surgery_product_id and self.surgery_template_id.surgery_product_id.id
            self.diagnosis = self.surgery_template_id.diagnosis
            self.clinincal_history = self.surgery_template_id.clinincal_history
            self.examination = self.surgery_template_id.examination
            self.investigation = self.surgery_template_id.investigation
            self.adv_on_dis = self.surgery_template_id.adv_on_dis
            self.notes = self.surgery_template_id.notes
            self.classification = self.surgery_template_id.classification

            for line in self.surgery_template_id.consumable_line_ids:
                self.consumable_line_ids += Consumable.new({
                    'product_id': line.product_id.id,
                    'product_uom_id': line.product_uom_id and line.product_uom_id.id or False,
                    'qty': line.qty,
                    'lot_id': line.lot_id and line.lot_id.id or False,
                })

            for line in self.surgery_template_id.medicament_line_ids:
                self.medicament_line_ids += MedicamentLine.new({
                    'product_id': line.product_id.id,
                    'common_dosage_id': line.common_dosage_id and line.common_dosage_id.id or False,
                    'dose': line.dose,
                    'active_component_ids': [(6, 0, [x.id for x in line.active_component_ids])],
                    'form_id' : line.form_id.id,
                    'qty': line.qty,
                    'days': line.days,
                    'instruction': line.instruction,
                })

    @api.model_create_multi
    def create(self, vals_list):
        for values in vals_list:
            values['name'] = self.env['ir.sequence'].next_by_code('hms.surgery') or 'Surgery#'
        return super().create(vals_list)

    def action_confirm(self):
        self.state = 'confirm'

    def action_done(self):
        self.state = 'done'
        self.consume_surgery_material()

    def action_cancel(self):
        self.state = 'cancel'

    def action_draft(self):
        self.state = 'draft'

    def yan_get_consume_locations(self):
        if not self.company_id.yan_surgery_usage_location_id:
            raise UserError(_('Please define a location where the consumables will be used in settings.'))
        if not self.company_id.yan_surgery_stock_location_id:
            raise UserError(_('Please define a surgery location from where the consumables will be taken.'))
        source_location_id  = self.company_id.yan_surgery_stock_location_id.id
        dest_location_id  = self.company_id.yan_surgery_usage_location_id.id
        return source_location_id, dest_location_id

    def consume_surgery_material(self):
        for rec in self:
            source_location_id, dest_location_id = rec.yan_get_consume_locations()
            for line in rec.consumable_line_ids.filtered(lambda s: not s.move_id):
                if line.product_id.is_kit_product:
                    move_ids = []
                    for kit_line in line.product_id.yan_kit_line_ids:
                        if kit_line.product_id.tracking!='none':
                            raise UserError("In Consumable lines Kit product with component having lot/serial tracking is not allowed. Please remove such kit product from consumable lines.")
                        move = self.consume_material(source_location_id, dest_location_id,
                            {'product': kit_line.product_id, 'qty': kit_line.product_qty * line.qty})
                        move.surgery_id = rec.id
                        move_ids.append(move.id)
                    #Set move_id on line also to avoid issue
                    line.move_id = move.id
                    line.move_ids = [(6,0,move_ids)]
                else:
                    move = self.consume_material(source_location_id, dest_location_id,
                        {'product': line.product_id, 'qty': line.qty, 'lot_id': line.lot_id and line.lot_id.id or False,})
                    move.surgery_id = rec.id
                    line.move_id = move.id

    def get_surgery_invoice_data(self):
        product_data = [{
            'name': _("Surgery Charges"),
        }]
        for surgery in self:
            if surgery.surgery_product_id:
                #Line for Surgery Charge
                product_data.append({
                    'product_id': surgery.surgery_product_id,
                    'quantity': 1,
                })

            #Line for Surgery Consumables
            for surgery_consumable in surgery.consumable_line_ids:
                product_data.append({
                    'product_id': surgery_consumable.product_id,
                    'quantity': surgery_consumable.qty,
                    'lot_id': surgery_consumable.lot_id and surgery_consumable.lot_id.id or False,
                })
        return product_data

    def action_create_invoice(self):
        product_data = self.get_surgery_invoice_data()
        inv_data = {
            'physician_id': self.primary_physician_id and self.primary_physician_id.id or False,
        }
        yan_context = {'commission_partner_ids':self.primary_physician_id.partner_id.id}
        invoice_id = self.with_context(yan_context).yan_create_invoice(partner=self.patient_id.partner_id, patient=self.patient_id, product_data=product_data, inv_data=inv_data)
        invoice_id.write({
            'surgery_id': self.id,
        })
        self.invoice_id = invoice_id.id
        return invoice_id

    def action_prescription(self):
        action = self.env["ir.actions.actions"]._for_xml_id("yan_hims_tasks.act_open_hms_prescription_order_view")
        action['domain'] = [('surgery_id', '=', self.id)]
        action['context'] = {
                'default_patient_id': self.patient_id.id,
                'default_diseases_ids': [(6,0,[self.diseases_id.id])],
                'default_surgery_id': self.id}
        return action

    def view_invoice(self):
        invoices = self.env['account.move'].search([('surgery_id', '=', self.id)])
        action = self.yan_action_view_invoice(invoices)
        return action

    def button_pres_request(self):
        action = self.env["ir.actions.actions"]._for_xml_id("yan_hims_tasks.act_open_hms_prescription_order_view")        
        action['domain'] = [('surgery_id', '=', self.id)]
        action['views'] = [(self.env.ref('yan_hims_tasks.view_hms_prescription_order_form').id, 'form')]
        PrescriptionLine = self.env['prescription.line']
        medicament_lines = []

        for line in self.medicament_line_ids:
            medicament_lines.append((0,0,{
                'product_id': line.product_id.id,
                'common_dosage_id': line.common_dosage_id and line.common_dosage_id.id or False,
                'dose': line.dose,
                'active_component_ids': [(6, 0, [x.id for x in line.active_component_ids])],
                'form_id' : line.form_id.id,
                'qty_per_day': line.qty,
                'days': line.days,
                'short_comment': line.instruction,
            }))

        action['context'] = {
                'default_patient_id': self.patient_id.id,
                'default_diseases_ids': [(6,0,[self.diseases_id.id])],
                'default_treatment_id': self.treatment_id and self.treatment_id.id or False,
                'default_surgery_id': self.id,
                'default_prescription_line_ids': medicament_lines}
        return action
