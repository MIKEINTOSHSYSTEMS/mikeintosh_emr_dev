# -*- coding: utf-8 -*-

from odoo import _, api, fields, models
from odoo.tools import email_split, format_datetime
from odoo.exceptions import UserError
import json


def extract_email(email):
    """ extract the email address from a user-friendly email address """
    addresses = email_split(email)
    return addresses[0] if addresses else ''


class Patient(models.Model):
    _inherit = 'hms.patient'

    @api.depends('inverse_family_member_ids','inverse_family_member_ids.patient_id')
    def yan_get_family_partners(self):
        for rec in self:
            family_partner_ids = rec.inverse_family_member_ids.mapped('patient_id.partner_id').ids
            rec.yan_family_partner_ids = [(6,0,family_partner_ids)]

    def _yan_get_patient_portal_line_graph(self):
        for rec in self:
            records = self.env['yan.patient.evaluation'].search([('patient_id','=',rec.id)], order="date", limit=100)
            labels = []
            weight_data = []
            height_data = []
            temp_data = []
            hr_data = []
            rr_data = []
            systolic_bp_data = []
            diastolic_bp_data = []
            spo2_data = []
            rbs_data = []
            for record in records:
                formated_date = format_datetime(self.env, record.date, tz=(self.env.user.tz or "UTC"))
                labels.append(formated_date)
                weight_data.append(record['weight'])
                height_data.append(record['height'])
                temp_data.append(record['temp'])
                hr_data.append(record['hr'])
                rr_data.append(record['rr'])
                systolic_bp_data.append(record['systolic_bp'])
                diastolic_bp_data.append(record['diastolic_bp'])
                spo2_data.append(record['spo2'])
                rbs_data.append(record['rbs'])

            chart_data = {
                'labels': labels,
                'datasets': [{
                    'label': 'Weight Chart',
                    'data': weight_data,
                    'fill': False,
                    'borderColor': 'rgb(75, 192, 192)',
                    'tension': 0.1
                },
                {
                    'label': 'Height Chart',
                    'data': height_data,
                    'fill': False,
                    'borderColor': 'rgb(92, 184, 92)',
                    'tension': 0.1
                },
                {
                    'label': 'Temprature Chart',
                    'data': temp_data,
                    'fill': False,
                    'borderColor': 'rgb(98, 0, 255)',
                    'tension': 0.1
                },
                {
                    'label': 'Heart Rate Chart',
                    'data': hr_data,
                    'fill': False,
                    'borderColor': 'rgb(240, 173, 78)',
                    'tension': 0.1
                },
                {
                    'label': 'RR Chart',
                    'data': rr_data,
                    'fill': False,
                    'borderColor': 'rgb(11, 151, 177)',
                    'tension': 0.1
                },
                {
                    'label': 'Systolic BP Chart',
                    'data': systolic_bp_data,
                    'fill': False,
                    'borderColor': 'rgb(162, 142, 194)',
                    'tension': 0.1
                },
                {
                    'label': 'Diastolic BP Chart',
                    'data': diastolic_bp_data,
                    'fill': False,
                    'borderColor': 'rgb(145, 77, 254)',
                    'tension': 0.1
                },
                {
                    'label': 'SpO2 Chart',
                    'data': spo2_data,
                    'fill': False,
                    'borderColor': 'rgb(158, 250, 193)',
                    'tension': 0.1
                },
                {
                    'label': 'RBS Chart',
                    'data': rbs_data,
                    'fill': False,
                    'borderColor': 'rgb(217, 83, 79)',
                    'tension': 0.1
                }]
            }
            rec.patient_portal_line_graph = json.dumps(chart_data)

    inverse_family_member_ids = fields.One2many('yan.family.member', 'related_patient_id', string='Related Family')
    yan_family_partner_ids = fields.Many2many('res.partner', compute="yan_get_family_partners", store=True, string="Family Partners")
    patient_portal_line_graph = fields.Text(compute='_yan_get_patient_portal_line_graph')

    @api.model_create_multi
    def create(self, vals_list):
        res = super().create(vals_list)
        for record in res:
            company_id = record.company_id or self.env.user.sudo().company_id
            if company_id.create_auto_users and record.email and not record.user_ids:
                record.sudo().create_patient_related_user()
        return res
 
    def create_patient_related_user(self):
        for record in self:
            company_id = record.company_id or self.env.user.sudo().company_id
            if not record.email:
                raise UserError(_('Please define valid email for the Patient'))
            group_portal = self.env.ref('base.group_portal')
            group_portal = group_portal  or False
            user = record.user_ids[0] if record.user_ids else None
            # update partner email, if a new one was introduced
            # add portal group to relative user of selected partners
            user_portal = None
            # create a user if necessary, and make sure it is in the portal group
            if not user:
                user_portal = record.sudo().with_context(company_id=company_id)._create_user()
            else:
                user_portal = user
            if group_portal not in user_portal.groups_id:
                user_portal.write({'active': True, 'groups_id': [(4, group_portal.id)]})
                # prepare for the signup process
                record.partner_id.signup_prepare()

            #YAN NOTE: incase of sigup from website it takes portal user. 
            #And no need to send invitation when user it self is doing signup
            if not self.env.context.get('website_id'):
                record.sudo().send_invitaion_email()

    def _create_user(self):
        company_id = self.env.context.get('company_id')
        email = extract_email(self.email)
        ext_user = self.env['res.users'].sudo().search([('email','=',email)], limit=1)
        if ext_user:
            raise UserError(_('Patient/User already registered with given email address.'))

        return self.env['res.users'].with_context(no_reset_password=True)._create_user_from_template({
            'email': email,
            'login': email,
            'partner_id': self.partner_id.id,
            'company_id': company_id.id,
            'company_ids': [(6, 0, [company_id.id])],
        })

    def send_invitaion_email(self):
        for record in self:
            if not self.env.user.email:
                raise UserError(_('You must have an email address in your User Preferences to send emails.'))

            user = record.user_ids[0] if record.user_ids else None
            if not user:
                raise UserError(_('Patient have no related user in system! Please create one first.'))

            user.mapped('partner_id').sudo().signup_prepare(signup_type="reset", expiration=False)

            template = self.env.ref('yan_hims_portal.set_password_email')

            if not user.email:
                raise UserError(_("Cannot send email: user %s has no email address.") % user.name)
            template.sudo().with_context(lang=user.lang).send_mail(user.id, force_send=True, raise_exception=False)
