# -*- coding: utf-8 -*-

from odoo import http, fields, _
from odoo.http import request
from odoo.tools import DEFAULT_SERVER_DATETIME_FORMAT
from odoo.exceptions import AccessError, MissingError
from odoo.addons.portal.controllers.portal import CustomerPortal, pager as portal_pager, get_records_pager
from odoo import fields as odoo_fields, http, tools, _, SUPERUSER_ID
import base64

class YANHms(http.Controller):

    @http.route(['/validate/patientlaboratorytest/<labresult_unique_code>'], type='http', auth="public", website=True, sitemap=False)
    def labresult_details(self, labresult_unique_code, **post):
        if labresult_unique_code:
            labresult = request.env['patient.laboratory.test'].sudo().search([('unique_code','=',labresult_unique_code)], limit=1)
            if labresult:
                return request.render("yan_laboratory.yan_labresult_details", {'labresult': labresult})
        return request.render("yan_hims_tasks.yan_no_details")


class HMSPortal(CustomerPortal):

    def _prepare_home_portal_values(self, counters):
        values = super()._prepare_home_portal_values(counters)
        LaboratoryTest = request.env['patient.laboratory.test']
        if 'lab_result_count' in counters:
            values['lab_result_count'] = LaboratoryTest.search_count([]) \
                if LaboratoryTest.check_access_rights('read', raise_exception=False) else 0

        LabRequest = request.env['yan.laboratory.request']
        if 'lab_request_count' in counters:
            values['lab_request_count'] = LabRequest.search_count([]) \
                if LabRequest.check_access_rights('read', raise_exception=False) else 0
        return values

    #Lab Result
    @http.route(['/my/lab_results', '/my/lab_results/page/<int:page>'], type='http', auth="user", website=True, sitemap=False)
    def my_lab_results(self, page=1, sortby=None, **kw):
        values = self._prepare_portal_layout_values()
        LaboratoryTest = request.env['patient.laboratory.test']

        if not sortby:
            sortby = 'date'

        sortings = {
            'date': {'label': _('Newest'), 'order': 'date_analysis desc'},
            'name': {'label': _('Name'), 'order': 'name'},
        }

        order = sortings.get(sortby, sortings['date'])['order']
        count = LaboratoryTest.search_count([])
 
        pager = portal_pager(
            url="/my/lab_results",
            url_args={},
            total=count,
            page=page,
            step=self._items_per_page
        )
        # content according to pager and archive selected

        lab_results = LaboratoryTest.search([],
            order=order, limit=self._items_per_page, offset=pager['offset'])

        values.update({
            'sortings': sortings,
            'sortby': sortby,
            'lab_results': lab_results,
            'page_name': 'lab_result',
            'default_url': '/my/lab_results',
            'searchbar_sortings': sortings,
            'pager': pager
        })
        return request.render("yan_laboratory.lab_results", values)

    @http.route(['/my/lab_results/<int:result_id>'], type='http', auth="user", website=True, sitemap=False)
    def my_lab_test_result(self, result_id=None, access_token=None, **kw):
        try:
            order_sudo = self._document_check_access('patient.laboratory.test', result_id, access_token=access_token)
        except (AccessError, MissingError):
            return request.redirect('/my')

        if order_sudo.attachment_ids:
            for att in order_sudo.attachment_ids:
                att._yan_portal_ensure_token()

        return request.render("yan_laboratory.my_lab_test_result", {'lab_result': order_sudo})

    #Lab Request
    @http.route(['/my/lab_requests', '/my/lab_requests/page/<int:page>'], type='http', auth="user", website=True, sitemap=False)
    def my_lab_requests(self, page=1, sortby=None, **kw):
        values = self._prepare_portal_layout_values()
        LabRequest = request.env['yan.laboratory.request']
        if not sortby:
            sortby = 'date'

        sortings = {
            'date': {'label': _('Newest'), 'order': 'date desc'},
            'name': {'label': _('Name'), 'order': 'name'},
        }

        order = sortings.get(sortby, sortings['date'])['order']
        count = LabRequest.search_count([])

        pager = portal_pager(
            url="/my/lab_requests",
            url_args={},
            total=count,
            page=page,
            step=self._items_per_page
        )
        # content according to pager and archive selected
        lab_requests = LabRequest.search([],
            order=order, limit=self._items_per_page, offset=pager['offset'])

        values.update({
            'sortings': sortings,
            'sortby': sortby,
            'lab_requests': lab_requests,
            'page_name': 'lab_request',
            'default_url': '/my/lab_requests',
            'searchbar_sortings': sortings,
            'pager': pager
        })
        return request.render("yan_laboratory.lab_requests", values)

    @http.route(['/my/lab_requests/<int:request_id>'], type='http', auth="user", website=True, sitemap=False)
    def my_lab_test_request(self, request_id=None, access_token=None, **kw):
        try:
            order_sudo = self._document_check_access('yan.laboratory.request', request_id, access_token=access_token)
        except (AccessError, MissingError):
            return request.redirect('/my')

        return request.render("yan_laboratory.my_lab_test_request", {'lab_request': order_sudo})

