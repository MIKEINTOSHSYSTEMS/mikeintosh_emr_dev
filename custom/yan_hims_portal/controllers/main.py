# -*- coding: utf-8 -*-

from odoo import http, fields, _
from odoo.http import request
from odoo.tools import DEFAULT_SERVER_DATETIME_FORMAT
from odoo.addons.portal.controllers.portal import CustomerPortal, pager as portal_pager, get_records_pager
from odoo.exceptions import AccessError, MissingError


class HMSPortal(CustomerPortal):

    def _prepare_portal_layout_values(self):
        values = super()._prepare_portal_layout_values()
        values.update({
            'patient_id': request.env.user.yan_patient_id,
        })
        return values

    def _prepare_home_portal_values(self, counters):
        values = super()._prepare_home_portal_values(counters)
        Appointment = request.env['hms.appointment']
        Prescription = request.env['prescription.order']
        Evaluation = request.env['yan.patient.evaluation']
        if 'appointment_count' in counters:
            values['appointment_count'] = Appointment.search_count([]) \
                if Appointment.check_access_rights('read', raise_exception=False) else 0
        if 'prescription_count' in counters:
            values['prescription_count'] = Prescription.search_count([]) \
                if Prescription.check_access_rights('read', raise_exception=False) else 0
        if 'evaluation_count' in counters:
            values['evaluation_count'] = Evaluation.search_count([]) \
                if Evaluation.check_access_rights('read', raise_exception=False) else 0
        return values

    @http.route(['/my/appointments', '/my/appointments/page/<int:page>'], type='http', auth="user", website=True, sitemap=False)
    def my_appointments(self, page=1, sortby=None, **kw):
        values = self._prepare_portal_layout_values()
        Appointment = request.env['hms.appointment']
        if not sortby:
            sortby = 'date'

        sortings = {
            'date': {'label': _('Newest'), 'order': 'create_date desc'},
            'name': {'label': _('Name'), 'order': 'name'},
        }

        order = sortings.get(sortby, sortings['date'])['order']
        count = Appointment.search_count([])
 
        pager = portal_pager(
            url="/my/appointments",
            url_args={},
            total=count,
            page=page,
            step=self._items_per_page
        )
        # content according to pager and archive selected
        partner = request.env.user.partner_id.commercial_partner_id
        appointments = Appointment.search([],
            order=order, limit=self._items_per_page, offset=pager['offset'])

        values.update({
            'sortings': sortings,
            'sortby': sortby,
            'appointments': appointments,
            'page_name': 'appointment',
            'default_url': '/my/appointments',
            'searchbar_sortings': sortings,
            'pager': pager
        })
        return request.render("yan_hims_portal.my_appointments", values)

    @http.route(['/my/appointments/<int:appointment_id>'], type='http', auth="public", website=True, sitemap=False)
    def my_appointments_appointment(self, appointment_id=None, access_token=None, **kw):
        try:
            record_sudo = self._document_check_access('hms.appointment', appointment_id, access_token=access_token)
        except (AccessError, MissingError):
            return request.redirect('/my')
        return request.render("yan_hims_portal.my_appointments_appointment", {'appointment': record_sudo})

    #Prescriptions
    @http.route(['/my/prescriptions', '/my/prescriptions/page/<int:page>'], type='http', auth="user", website=True, sitemap=False)
    def my_prescriptions(self, page=1, sortby=None, **kw):
        values = self._prepare_portal_layout_values()
        Prescription = request.env['prescription.order']
        if not sortby:
            sortby = 'date'

        sortings = {
            'date': {'label': _('Newest'), 'order': 'create_date desc'},
            'name': {'label': _('Name'), 'order': 'name'},
        }

        order = sortings.get(sortby, sortings['date'])['order']
        count = Prescription.search_count([])
 
        pager = portal_pager(
            url="/my/prescriptions",
            url_args={},
            total=count,
            page=page,
            step=self._items_per_page
        )
        # content according to pager and archive selected
        partner = request.env.user.partner_id.commercial_partner_id
        prescriptions = request.env['prescription.order'].search([],
            order=order, limit=self._items_per_page, offset=pager['offset'])

        values.update({
            'sortings': sortings,
            'sortby': sortby,
            'prescriptions': prescriptions,
            'page_name': 'prescription',
            'default_url': '/my/prescriptions',
            'searchbar_sortings': sortings,
            'pager': pager
        })
        return request.render("yan_hims_portal.my_prescriptions", values)

    @http.route(['/my/prescriptions/<int:prescription_id>'], type='http', auth="public", website=True, sitemap=False)
    def my_appointments_prescription(self, prescription_id=None, access_token=None, **kw):
        try:
            record_sudo = self._document_check_access('prescription.order', prescription_id, access_token=access_token)
        except (AccessError, MissingError):
            return request.redirect('/my')
        return request.render("yan_hims_portal.my_prescriptions_prescription", {'prescription': record_sudo})

    def details_form_validate(self, data):
        error, error_message = super(HMSPortal, self).details_form_validate(data)
        # prevent VAT/name change if invoices | Prescription exist
        partner = request.env['res.users'].browse(request.uid).partner_id
        has_prescription = request.env['prescription.order'].search([], limit=1)
        if has_prescription:
            if 'name' in data and (data['name'] or False) != (partner.name or False):
                error['name'] = 'error'
                error_message.append(_('Changing your name is not allowed once Prescriptions have been issued for your account. Please contact us directly for this operation.'))
        return error, error_message

    @http.route(['/yan/cancel/<int:appointment_id>/appointment'], type='http', auth="user", website=True, sitemap=False)
    def cancel_appointment(self, appointment_id,**kw):
        try:
            record_sudo = self._document_check_access('hms.appointment', appointment_id)
        except (AccessError, MissingError):
            return request.redirect('/my')

        record_sudo.write({
            'cancel_reason': kw.get('cancel_reason')
        })
        record_sudo.appointment_cancel()

        return request.redirect('/my/appointments')
 
    #Evaluations
    @http.route(['/my/evaluations', '/my/evaluations/page/<int:page>'], type='http', auth="user", website=True, sitemap=False)
    def my_evaluations(self, page=1, sortby=None, **kw):
        values = self._prepare_portal_layout_values()
        Evaluation = request.env['yan.patient.evaluation']
        if not sortby:
            sortby = 'date'

        sortings = {
            'date': {'label': _('Newest'), 'order': 'date desc'},
            'name': {'label': _('Name'), 'order': 'name'},
        }

        order = sortings.get(sortby, sortings['date'])['order']
        count = Evaluation.search_count([])
 
        pager = portal_pager(
            url="/my/evaluations",
            url_args={},
            total=count,
            page=page,
            step=self._items_per_page
        )
        # content according to pager and archive selected
        partner = request.env.user.partner_id.commercial_partner_id
        evaluations = Evaluation.search([],
            order=order, limit=self._items_per_page, offset=pager['offset'])

        values.update({
            'sortings': sortings,
            'sortby': sortby,
            'evaluations': evaluations,
            'page_name': 'evaluation',
            'default_url': '/my/evaluations',
            'searchbar_sortings': sortings,
            'pager': pager
        })
        return request.render("yan_hims_portal.my_evaluations", values)

    @http.route(['/my/evaluations/<int:evaluation_id>'], type='http', auth="public", website=True, sitemap=False)
    def my_evaluation(self, evaluation_id=None, access_token=None, **kw):
        try:
            record_sudo = self._document_check_access('yan.patient.evaluation', evaluation_id, access_token=access_token)
        except (AccessError, MissingError):
            return request.redirect('/my')
        return request.render("yan_hims_portal.my_evaluation", {'evaluation': record_sudo})

    @http.route(['/my/evaluations/create'], type='http', auth="user", website=True, sitemap=False)
    def my_evaluation_create(self, **kw):
        partner = request.env.user.partner_id.commercial_partner_id
        patient_id = request.env['hms.patient'].sudo().search([('partner_id','=', partner.id)], limit=1)
        values = {
            'patient_id': patient_id,
        }
        return request.render("yan_hims_portal.create_evaluation", values)

    @http.route(['/my/evaluations/charts'], type='http', auth="user", website=True, sitemap=False)
    def my_evaluation_charts(self, **kw):
        partner = request.env.user.partner_id.commercial_partner_id
        patient_id = request.env['hms.patient'].sudo().search([('partner_id','=', partner.id)], limit=1)
        values = {
            'patient_id': patient_id,
        }
        return request.render("yan_hims_portal.my_evaluation_charts", values)

    def get_values_from_form(self, kwargs):
        data = {
            'name': kwargs.get('name'),
            'email': kwargs.get('email'),
            'mobile': kwargs.get('mobile'),
            'street': kwargs.get('street'),
            'city': kwargs.get('city'),
            'zip': kwargs.get('zip'),
            'gov_code': kwargs.get('gov_code'),
            'state_id': kwargs.get('state_id') and int(kwargs.get('state_id')) or False,
            'country_id': kwargs.get('country_id') and int(kwargs.get('country_id')) or False,
            'gender': kwargs.get('gender'),
            'birthday': kwargs.get('birthday'),
        }
        return data

    def get_default_form_data(self):
        countries = request.env['res.country'].sudo().search([])
        states = request.env['res.country.state'].sudo().search([])
        relations = request.env['yan.family.relation'].sudo().search([])
        patient_id = request.env['hms.patient'].sudo()
        return {
            'countries': countries, 
            'states': states, 
            'relations': relations, 
            'error': {},
            'record': patient_id,
        }

    @http.route(['/my/family/new'], type='http', auth="user", website=True, sitemap=False)
    def family_member_new_form(self, redirect=None, **kw):
        values = self.get_default_form_data()
        values.update({'relation_id': 0, 'redirect': redirect})
        return request.render("yan_hims_portal.create_family_member", values)

    @http.route('/yan/hms/family/create', type="http", auth="user", website=True, csrf=True, sitemap=False)
    def create_family_member(self, **kwargs):
        data = self.get_values_from_form(kwargs)
        new_patient = request.env['hms.patient'].sudo().create(data)
        request.env['yan.family.member'].sudo().create({
            'patient_id': request.env.user.yan_patient_id.id,
            'related_patient_id': new_patient.id,
            'relation_id': int(kwargs.get('relation_id')),
        })
        if kwargs.get('redirect'):
            return request.redirect(kwargs.get('redirect'))
        return request.redirect('/my')

    @http.route(['/my/family/update/<int:family_memebr_id>'], type='http', auth="user", website=True, sitemap=False)
    def family_member_update_form(self, family_memebr_id, redirect=None, **kw):
        values = self.get_default_form_data()
        family_memebr = request.env['yan.family.member'].sudo().search([('id','=',family_memebr_id)])
        patient_id = family_memebr.related_patient_id
        values.update({
            'record': patient_id,
            'relation_id': family_memebr.relation_id and family_memebr.relation_id.id or 0,
            'family_memebr': family_memebr.id,
            'redirect': redirect,
        })
        return request.render("yan_hims_portal.update_family_member", values)

    @http.route('/yan/hms/family/update', type="http", auth="user", website=True, csrf=True, sitemap=False)
    def update_family_member(self, **kwargs):
        patient = request.env['hms.patient'].sudo().search([('id','=',kwargs.get('patient_id'))])
        data = self.get_values_from_form(kwargs)
        patient.write(data)
        family_memebr = request.env['yan.family.member'].sudo().search([('id','=',kwargs.get('family_memebr'))])
        if family_memebr:
            family_memebr.relation_id = int(kwargs.get('relation_id'))
        if kwargs.get('redirect'):
            return request.redirect(kwargs.get('redirect'))
        return request.redirect('/my')
