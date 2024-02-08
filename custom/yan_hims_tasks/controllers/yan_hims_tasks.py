# -*- coding: utf-8 -*-

from odoo import http, fields, _
from odoo.http import request
from odoo import fields as odoo_fields, http, tools, _, SUPERUSER_ID

class YANHms(http.Controller):

    @http.route(['/validate/prescriptionorder/<prescription_unique_code>'], type='http', auth="public", website=True, sitemap=False)
    def prescription_details(self, prescription_unique_code, **post):
        if prescription_unique_code:
            prescription = request.env['prescription.order'].sudo().search([('unique_code','=',prescription_unique_code)], limit=1)
            if prescription:
                return request.render("yan_hims_tasks.yan_prescription_details", {'prescription': prescription})
        return request.render("yan_hims_tasks.yan_no_details")

