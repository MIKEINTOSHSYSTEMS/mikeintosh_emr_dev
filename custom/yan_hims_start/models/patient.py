# -*- coding: utf-8 -*-

from odoo import api, fields, models, _
from odoo.exceptions import UserError, ValidationError
from datetime import datetime


class YANPatient(models.Model):
    _name = 'hms.patient'
    _description = 'Patient'
    _inherit = ['mail.thread', 'mail.activity.mixin', 'yan.hms.mixin', 'yan.documnt.mixin']
    _inherits = {
        'res.partner': 'partner_id',
    }
    _rec_names_search = ['name', 'code']

    def _rec_count(self):
        Invoice = self.env['account.move']
        for rec in self:
            rec.invoice_count = Invoice.sudo().search_count([('partner_id', '=', rec.partner_id.id)])

    partner_id = fields.Many2one('res.partner', required=True, ondelete='restrict', auto_join=True,
                                 string='Related Partner', help='Partner-related data of the Patient')
    # registered_as = fields.Selection([
    #     ('patient', 'Patient'),
    #     ('care giver', 'Care Giver'),
    #     ('family member', 'Family Member')], string='Register as', required=True)
    gov_code = fields.Char(string='Government Identity', copy=False, tracking=True)
    marital_status = fields.Selection([
        ('single', 'Single'),
        ('married', 'Married'),
        ('divorced', 'Divorced'),
        ('separated', 'Separated'),
        ('widowed', 'Widowed')], string='Marital Status', default="single")
    spouse_name = fields.Char("Spouse's Name")
    spouse_edu = fields.Char("Spouse's Education")
    spouse_business = fields.Char("Spouse's Business")
    education = fields.Char("Patient Education")
    is_corpo_tieup = fields.Boolean(string='Corporate Tie-Up',
                                    help="If not checked, these Corporate Tie-Up Group will not be visible at all.")
    corpo_company_id = fields.Many2one('res.partner', string='Corporate Company',
                                       domain="[('is_company', '=', True),('customer_rank', '>', 0)]",
                                       ondelete='restrict')
    emp_code = fields.Char(string='Employee Code')
    user_id = fields.Many2one('res.users', string='Related User', ondelete='cascade',
                              help='User-related data of the patient')
    primary_physician_id = fields.Many2one('hms.physician', 'Primary Care Doctor')
    yan_tag_ids = fields.Many2many('hms.patient.tag', 'patient_tag_hms_rel', 'tag_id', 'patient_tag_id',
                                   string="HMS Tags")

    yan_region = fields.Selection([
        ('addis Ababa', 'Addis Ababa'),
        ('afar', 'Afar'),
        ('amhara', 'Amhara'),
        ('benishangul-Gumuz', 'Benishangul-Gumuz'),
        ('dire Dawa', 'Dire Dawa'),
        ('gambela', 'Gambela'),
        ('harari', 'Harari'),
        ('oromia', 'Oromia'),
        ('sidama', 'Sidama'),
        ('somali', 'Somali'),
        ('south West', 'South West'),
        ('southern', 'Southern'),
        ('tigray', 'Tigray')], string='Region', default="addis Ababa")
    zone = fields.Char("Zone")
    subcity = fields.Selection([
        ('addis Ketema', 'Addis Ketema'),
        ('akaky Kaliti', 'Akaky Kaliti'),
        ('arada', 'Arada'),
        ('bole', 'Bole'),
        ('gullele', 'Gullele'),
        ('kirkos', 'Kirkos'),
        ('kolfe Keranio', 'Kolfe Keranio'),
        ('lemi Kura', 'Lemi Kura'),
        ('lideta', 'Lideta'),
        ('nifas Silk-Lafto', 'Nifas Silk-Lafto'),
        ('yeka', 'Yeka')], string='Subcity')
    woreda = fields.Char("Woreda")
    house_number = fields.Char("House Number")

    invoice_count = fields.Integer(compute='_rec_count', string='# Invoices')
    occupation = fields.Char("Occupation")
    religion = fields.Char("Religion")
    nationality_id = fields.Many2one("res.country", string="Nationality")
    passport = fields.Char("Passport Number")
    active = fields.Boolean(string="Active", default=True)
    location_url = fields.Text()

    emergency_contact_relation = fields.Selection([
        ('spouse', 'Spouse'),
        ('sibling', 'Sibling'),
        ('relative', 'Relative'),
        ('friend', 'Friend'),
        ('norelation', 'No Relation')], string='Contact relation')
    emergency_contact_name = fields.Char("Contact's Name")
    emergency_contact_phone = fields.Char("Contact's Phone")

    _sql_constraints = [
        ('mobile', 'unique(mobile)', 'Mobile number already exists!')]

    @api.constrains('mobile')
    def _check_mobile(self):
        for rec in self:
            domain = [('mobile', '=', rec.mobile)]
            count = self.sudo().search_count(domain)
            if count > 1:
                raise ValidationError(_("The mobile No should be unique"))

    _sql_constraints = [
        ('email', 'unique(email)', 'Email already exists!')]

    @api.constrains('email')
    def _check_mobile(self):
        for rec in self:
            domain = [('email', '=', rec.email)]
            count = self.sudo().search_count(domain)
            if count > 1:
                raise ValidationError(_("The email should be unique"))

    def check_gov_code(self, gov_code):
        patient = self.search([('gov_code', '=', gov_code)], limit=1)
        if patient:
            raise ValidationError(_('Patient already exists with Government Identity: %s.') % (gov_code))

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get('code', '/') == '/':
                vals['code'] = self.env['ir.sequence'].next_by_code('hms.patient') or ''
            company_id = vals.get('company_id')
            if company_id:
                company_id = self.env['res.company'].sudo().search([('id', '=', company_id)], limit=1)
            else:
                company_id = self.env.user.company_id
            if company_id.unique_gov_code and vals.get('gov_code'):
                self.check_gov_code(vals.get('gov_code'))
            vals['customer_rank'] = True
        return super().create(vals_list)

    def write(self, values):
        company_id = self.sudo().company_id or self.env.user.sudo().company_id
        if company_id.unique_gov_code and values.get('gov_code'):
            self.check_gov_code(values.get('gov_code'))
        return super(YANPatient, self).write(values)

    def view_invoices(self):
        invoices = self.env['account.move'].search([('partner_id', '=', self.partner_id.id)])
        action = self.with_context(yan_open_blank_list=True).yan_action_view_invoice(invoices)
        action['context'].update({
            'default_partner_id': self.partner_id.id,
            'default_patient_id': self.id,
        })
        return action

    @api.model
    def send_birthday_email(self):
        wish_template_id = self.env.ref('yan_hims_start.email_template_birthday_wish', raise_if_not_found=False)
        user_cmp_template = self.env.user.company_id.birthday_mail_template_id
        today = datetime.now()
        today_month_day = '%-' + today.strftime('%m') + '-' + today.strftime('%d')
        patient_ids = self.search([('birthday', 'like', today_month_day)])
        for patient_id in patient_ids:
            if patient_id.email:
                wish_temp = patient_id.company_id.birthday_mail_template_id or user_cmp_template or wish_template_id
                wish_temp.sudo().send_mail(patient_id.id, force_send=True)

    def name_get(self):
        result = []
        for rec in self:
            name = rec.name
            if rec.title and rec.title.shortcut:
                name = (rec.title.shortcut or '') + ' ' + (rec.name or '')
            result.append((rec.id, name))
        return result

    @api.onchange('mobile')
    def _onchange_mobile_warning(self):
        if not self.mobile:
            return
        mobile = self.mobile
        message = ''
        domain = [('mobile', '=', self.mobile)]
        if self._origin and self._origin.id:
            domain += [('id', '!=', self._origin.id)]
        patients = self.sudo().search(domain)
        for patient in patients:
            message += _(
                '\nThe Mobile number is already registered with another Patient: %s, Government Identity:%s, DOB: %s.') % (
                       patient.name, patient.gov_code, patient.birthday)
        if message:
            message += _('\n\n Are you sure you want to create a new Patient?')
            return {
                'warning': {
                    'title': _("Warning for Mobile Duplication"),
                    'message': message,
                }
            }
