# -*- coding: utf-8 -*-

from odoo import api, fields, models, _
from odoo.exceptions import UserError
import uuid


class PatientLabTest(models.Model):
    _name = "patient.radiology.test"
    _inherit = ['mail.thread', 'mail.activity.mixin', 'yan.hms.mixin', 'portal.mixin', 'yan.documnt.mixin', 'yan.qrcode.mixin', 'yan.documnt.view.mixin']
    _description = "Patient Radiology Test"
    _order = 'date_analysis desc, id desc'

    @api.model
    def _get_disclaimer(self):
        return self.env.user.sudo().company_id.yan_radiology_disclaimer or ''

    STATES = {'cancel': [('readonly', True)], 'done': [('readonly', True)]}

    name = fields.Char(string='Test ID', help="Radiology result ID", readonly="1",copy=False, index=True, tracking=True)
    test_id = fields.Many2one('yan.radiology.test', string='Test', required=True, ondelete='restrict', states=STATES, tracking=True)
    patient_id = fields.Many2one('hms.patient', string='Patient', required=True, ondelete='restrict', states=STATES, tracking=True)
    user_id = fields.Many2one('res.users',string='Radiology User', default=lambda self: self.env.user, states=STATES)
    physician_id = fields.Many2one('hms.physician',string='Prescribing Doctor', help="Doctor who requested the test", ondelete='restrict', states=STATES)
    radiology_physician_id = fields.Many2one('hms.physician',string='Radiology Doctor', help="Doctor who Approved the test", ondelete='restrict', states=STATES)

    diagnosis = fields.Text(string='Diagnosis', states=STATES)
    date_requested = fields.Datetime(string='Request Date', states=STATES)
    date_analysis = fields.Datetime(string='Test Date', default=fields.Datetime.now, states=STATES)
    radiology_request_id = fields.Many2one('yan.radiology.request', string='Test Request', ondelete='restrict', states=STATES)
    #yanv16: cehck and remove
    #radiology_id = fields.Many2one('yan.radiology', related="radiology_request_id.radiology_id", string='Radiology', readonly=True, store=True)
    report = fields.Text(string='Test Report', states=STATES)
    note = fields.Text(string='Extra Info', states=STATES)
    company_id = fields.Many2one('res.company', ondelete='restrict', 
        string='Company', default=lambda self: self.env.company, states=STATES)
    state = fields.Selection([
        ('draft','Draft'),
        ('done','Done'),
        ('cancel','Cancel'),
    ], string='Status',readonly=True, default='draft', tracking=True)
    consumable_line_ids = fields.One2many('hms.consumable.line', 'patient_radiology_test_id',
        string='Consumable Line', states=STATES)
    disclaimer = fields.Text("Disclaimer", states=STATES, default=_get_disclaimer)
    parent_test_id = fields.Many2one('patient.radiology.test', string='Parent Test', ondelete='cascade', copy=False)
    child_test_ids = fields.One2many('patient.radiology.test', 'parent_test_id', string='Child Tests', copy=False)

    #Just to make object selectable in selction field this is required: Waiting Screen
    yan_show_in_wc = fields.Boolean(default=True)

    _sql_constraints = [
        ('name_company_uniq', 'unique (name,company_id)', 'Test Name must be unique per company !')
    ]

    def _track_subtype(self, init_values):
        self.ensure_one()
        if 'state' in init_values and self.state == 'done':
            return self.env.ref('yan_radiology.mt_radiology_test_done')
        return super(PatientLabTest, self)._track_subtype(init_values)

    def name_get(self):
        result = []
        for rec in self:
            name = rec.name or '-'
            if rec.test_id:
                name += ' [' + rec.test_id.name + ']'
            result.append((rec.id, name))
        return result

    def _subscribe_physician(self):
        done_subtype = self.env.ref('yan_radiology.mt_radiology_test_done').id
        comment_subtype = self.env.ref('mail.mt_comment').id
        for rec in self:
            if rec.physician_id.partner_id and rec.physician_id.partner_id.id not in rec.message_partner_ids.ids:
                rec.message_subscribe(partner_ids=[rec.physician_id.partner_id.id], subtype_ids=[done_subtype,comment_subtype])

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            vals['name'] = self.env['ir.sequence'].next_by_code('patient.radiology.test')
        res = super().create(vals_list)
        for record in res:
            record.unique_code = uuid.uuid4()
            record._subscribe_physician()
        return res

    def write(self, values):
        if 'physician_id' in values:
            self._subscribe_physician()
        return super(PatientLabTest, self).write(values)

    def unlink(self):
        for rec in self:
            if rec.state not in ['draft']:
                raise UserError(_("Radiology Test can be delete only in Draft state."))
        return super(PatientLabTest, self).unlink()

    @api.onchange('radiology_request_id')
    def onchange_radiology_request_id(self):
        if self.radiology_request_id and self.radiology_request_id.date:
            self.date_requested = self.radiology_request_id.date

    def action_radiology_test_send(self):
        '''
        This function opens a window to compose an email, with the template message loaded by default
        '''
        self.ensure_one()
        template_id = self.env['ir.model.data']._xmlid_to_res_id('yan_radiology.yan_radiology_test_email', raise_if_not_found=False)

        ctx = {
            'default_model': 'patient.radiology.test',
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

    @api.onchange('test_id')
    def on_change_test(self):
        test_lines = []
        if self.test_id:
            gender = self.patient_id.gender

    def action_done(self):
        if not self.diagnosis:
            raise UserError(_("Please update diagnosis first on result."))
        self.consume_radiology_material()
        self.state = 'done'

    def action_cancel(self):
        self.state = 'cancel'

    def action_draft(self):
        self.state = 'draft'

    def yan_get_consume_locations(self):
        if not self.company_id.yan_radiology_usage_location_id:
            raise UserError(_('Please define a location where the consumables will be used during the Radiology test in company.'))
        if not self.company_id.yan_radiology_stock_location_id:
            raise UserError(_('Please define a Radiology location from where the consumables will be taken.'))

        dest_location_id  = self.company_id.yan_radiology_usage_location_id.id
        source_location_id  = self.company_id.yan_radiology_stock_location_id.id
        return source_location_id, dest_location_id

    def consume_radiology_material(self):
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
                        move.radiology_test_id = rec.id
                        move_ids.append(move.id)
                    #Set move_id on line also to avoid issue
                    line.move_id = move.id
                    line.move_ids = [(6,0,move_ids)]
                else:
                    move = self.consume_material(source_location_id, dest_location_id,
                        {'product': line.product_id, 'qty': line.qty, 'lot_id': line.lot_id and line.lot_id.id or False,})
                    move.radiology_test_id = rec.id
                    line.move_id = move.id

    def _compute_access_url(self):
        super(PatientLabTest, self)._compute_access_url()
        for rec in self:
            rec.access_url = '/my/radiology_results/%s' % (rec.id)
