# -*- coding: utf-8 -*-

from odoo import api, fields, models, http, _
from odoo.http import route, request
from odoo.addons.portal.controllers.portal import CustomerPortal, pager as portal_pager, get_records_pager
from odoo.addons.website.controllers.main import Website
from datetime import timedelta


class HMSWebsite(Website):

    #Appointment Booking
    def create_booking_data(self):
        user = request.env['res.users'].sudo().browse(request.uid)
        values = {
            'error': {},
            'error_message': []
        }

        department_ids = request.env['hr.department'].sudo().search([('patient_department','=',True),('allowed_online_booking','=',True)])
        physician_ids = request.env['hms.physician'].sudo().search([('allowed_online_booking','=',True)])

        values.update({
            'slots': [],
            'slot_lines': [],
            'partner': user.partner_id,
            'department_ids': department_ids,
            'physician_ids': physician_ids,
            'appointment_tz': False,
            'allow_department_selection': True if department_ids else False,
            'allow_physician_selection': True if physician_ids else False,
        })
        return values

    def user_booking_data(self, post):
        values = {
            'error': {},
            'error_message': []
        }
        physician_id = post.get('physician_id')
        department_id = post.get('department_id')
        appoitment_by = post.get('appoitment_by','physician')
        physician = department = ''
        allow_home_appointment = False
        
        if physician_id:
            physician = request.env['hms.physician'].sudo().search([('id','=',int(physician_id))])
            allow_home_appointment = physician.allow_home_appointment
        if department_id:
            department = request.env['hr.department'].sudo().search([('id','=',int(department_id))])
            allow_home_appointment = department.allow_home_appointment
        if appoitment_by=='physician':
            department = ''
        if appoitment_by=='department':
            physician = ''

        slot_data = request.env['hms.appointment'].get_slot_data(physician_id, department_id)
        user = request.env['res.users'].sudo().browse(request.uid)
        last_date = fields.Date.today() + timedelta(days=user.company_id.allowed_booking_online_days)
        disable_dates = request.env['hms.appointment'].get_disabled_dates(physician_id, department_id)

        schedule_slot_id = False
        schedule_slot_name = schedule_slot_date = ''
        if post.get('schedule_slot_id'):
            slot_line = request.env['appointment.schedule.slot.lines'].browse(int(post.get('schedule_slot_id')))
            schedule_slot_name = slot_line.name
            schedule_slot_date = slot_line.slot_id.slot_date
            schedule_slot_id = slot_line.id

        values.update({
            'terms_page_link': user.company_id.yan_appointment_tc,
            'allow_video_call': user.company_id.yan_allowed_video_consultation,
            'department_id': department_id,
            'department': department,
            'physician_id': physician_id,
            'physician': physician,
            'partner': user.partner_id,
            'slots_data': slot_data,
            'schedule_slot_id': schedule_slot_id,
            'schedule_slot_name': schedule_slot_name,
            'schedule_slot_date': schedule_slot_date,
            'allow_home_appointment': allow_home_appointment,
            'last_date': last_date,
            'disable_dates': disable_dates,
        })
        return values

    @http.route(['/create/appointment'], type='http', auth='public', website=True, sitemap=True)
    def create_appointment(self, redirect=None, **post):
        values = self.create_booking_data()
        values.update({
            'redirect': redirect,
        })
        return request.render("yan_hims_online_appointment.appointment_details", values)

    @http.route(['/get/appointment/data'], type='http', auth='public', website=True, sitemap=False)
    def create_appointment_data(self, redirect=None, **post):
        appoitment_by = post.get('appoitment_by','physician')
        if appoitment_by=='physician' and 'department_id' in post:
            post.pop('department_id')
        if appoitment_by=='department' and 'physician_id' in post:
            post.pop('physician_id')
        values = self.user_booking_data(post)
        return request.render("yan_hims_online_appointment.appointment_slot_details", values)

    @http.route(['/get/appointment/personaldata'], type='http', auth='public', website=True, sitemap=False)
    def appointment_personal_data(self, redirect=None, **post):
        values = self.user_booking_data(post)
        return request.render("yan_hims_online_appointment.appointment_personal_details", values)

    @http.route(['/save/appointment'], type='http', auth='user', website=True, sitemap=False)
    def save_appointment(self, redirect=None, **post):
        env = request.env
        partner = env['res.users'].browse(request.uid).partner_id
        app_obj = env['hms.appointment'].sudo()
        res_patient = env['hms.patient'].sudo()
        slot_line = env['appointment.schedule.slot.lines']
        user = env.user.sudo()
        values = {
            'error': {},
            'error_message': [],
            'partner': partner,
        }

        patient = res_patient.search([('partner_id', '=', partner.id)],limit=1)
        error, error_message = self.validate_application_details(patient, post)
        if error_message:
            values = self.user_booking_data(post)
            values.update({
                'redirect': redirect,
            })
            values.update({'error': error, 'error_message': error_message})
            return request.render("yan_hims_online_appointment.appointment_slot_details", values)

        if post:
            slot = slot_line.browse(int(post.get('schedule_slot_id')))
            if slot.from_slot < fields.Datetime.now():
                values = self.user_booking_data(post)
                values.update({'error_message':['Appointment date is past please enter valid.']})
                return request.render("yan_hims_online_appointment.appointment_slot_details", values)

            if slot.rem_limit <= 0:
                values = self.user_booking_data(post)
                values.update({'error_message':['Appointment slot is already booked please select other slot.']})
                return request.render("yan_hims_online_appointment.appointment_slot_details", values)

            diff = slot.to_slot - slot.from_slot
            planned_duration = (diff.days * 24) + (diff.seconds/3600)

            post.update({
                'schedule_slot_id': slot.id,
                'booked_online':True,
                'patient_id': patient.id,
                'date': slot.from_slot,
                'planned_duration': planned_duration,
                'date_to': slot.to_slot,
                'schedule_date': slot.slot_id.slot_date,
            })

            if slot.physician_id:
                post.update({
                    'physician_id': slot.physician_id.id,
                })

            if post.get('location'):
                post.update({
                    'outside_appointment': True,
                })

            post.pop('name', '')
            post.pop('slot_date', '')
            post.pop('physician_name', '')
            post.pop('department_name', '')
            #POP Accept T&C field. if needed can be stored also.
            post.pop('yan_appointment_tc', '')

            # Create Appointment
            app_id = app_obj.sudo().create(post)

            if user.sudo().company_id.allowed_booking_payment:
                app_id.sudo().with_context(yan_online_transaction=True).onchange_physician()

                context = {'active_id': app_id.id, 'active_model': 'hms.appointment'}
                payment_link_wiz = request.env['payment.link.wizard'].sudo().with_context(context).create({})
                #if fee is 0 validate appointment
                if payment_link_wiz.amount==0:
                    app_id.sudo().with_context(yan_online_transaction=True).appointment_confirm()
                    return request.render("yan_hims_online_appointment.appointment_thank_you", {'appointment': app_id})

                return request.redirect(payment_link_wiz.link)

            return request.render("yan_hims_online_appointment.appointment_thank_you", {'appointment': app_id})

        return request.redirect('/my/account')

    def validate_application_details(self, patient, data):
        error = dict()
        error_message = []
        mandatory_fields = ['schedule_slot_id']

        #If no patient 
        if not patient:
            error_message.append(_('No patient is linked with user. Please Contact Administration for further support.'))

        if not data.get('schedule_slot_id'):
            error_message.append(_('Please Select Available Appointment Slot Properly.'))

        # Mandatory Field Validation
        for field_name in mandatory_fields:
            if not data.get(field_name):
                error[field_name] = 'missing'

        # error message for empty required fields
        if [err for err in error.values() if err == 'missing']:
            error_message.append(_('Some required fields are empty.'))

        return error, error_message


class YanCustomerPortal(CustomerPortal):

    def _get_custom_rendering_context_values(self, **kwargs):
        """ Return a dict of additional rendering context values.

        :param dict kwargs: Optional data. This parameter is not used here
        :return: The dict of additional rendering context values
        :rtype: dict
        """
        res = super(YanCustomerPortal, self)._get_custom_rendering_context_values(**kwargs)
        if kwargs.get('yan_appointment_id'):
            res['yan_appointment_id'] = kwargs.get('yan_appointment_id')
        return res

    def _create_transaction(
        self, payment_option_id, reference_prefix, amount, currency_id, partner_id, flow,
        tokenization_requested, landing_route, is_validation=False, invoice_id=None, yan_appointment_id=None,
        custom_create_values=None, **kwargs
    ):
        res = super(YanCustomerPortal, self)._create_transaction(payment_option_id, reference_prefix, amount, currency_id, partner_id, flow,
        tokenization_requested, landing_route, is_validation=is_validation, invoice_id=invoice_id,
        custom_create_values=custom_create_values, **kwargs)
        if yan_appointment_id:
            res.yan_appointment_id = yan_appointment_id
        return res
