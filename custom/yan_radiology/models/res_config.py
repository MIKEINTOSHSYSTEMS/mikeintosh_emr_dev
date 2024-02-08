# -*- coding: utf-8 -*-

from odoo import api, fields, models, SUPERUSER_ID, _


class ResCompany(models.Model):
    _inherit = "res.company"

    yan_radiology_usage_location_id = fields.Many2one('stock.location', 
        string='Usage Location for Consumed Radiology Test Material.')
    yan_radiology_stock_location_id = fields.Many2one('stock.location', 
        string='Stock Location for Consumed Radiology Test Material')
    yan_radiology_result_qrcode = fields.Boolean(string="Print Authetication QrCode on Radiology Result", default=True)
    yan_radiology_invoice_policy = fields.Selection([('any_time', 'Anytime'), ('in_advance', 'Advance'),
        ('in_end', 'At End')], default="any_time", string="Radiology Invoice Policy", required=True)
    yan_check_radiology_payment = fields.Boolean(string="Check Payment Status before Accepting Radiology Request")
    yan_radiology_disclaimer = fields.Text(string="Radiology Disclaimer")


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    yan_radiology_usage_location_id = fields.Many2one('stock.location', 
        related='company_id.yan_radiology_usage_location_id',
        domain=[('usage','=','customer')],
        string='Usage Location for Consumed Radiology Test Material', readonly=False)
    yan_radiology_stock_location_id = fields.Many2one('stock.location', 
        related='company_id.yan_radiology_stock_location_id',
        domain=[('usage','=','internal')],
        string='Stock Location for Consumed Radiology Test Material', readonly=False)
    yan_radiology_result_qrcode = fields.Boolean(related='company_id.yan_radiology_result_qrcode', string="Print Authetication QrCode on Radiology Result", readonly=False)
    yan_radiology_invoice_policy = fields.Selection(related='company_id.yan_radiology_invoice_policy', string="Radiology Invoice Policy", readonly=False)
    yan_check_radiology_payment = fields.Boolean(related='company_id.yan_check_radiology_payment', string="Check Payment Status before Accepting Radiology Request", readonly=False)
    yan_radiology_disclaimer = fields.Text(related='company_id.yan_radiology_disclaimer', string="Radiology Disclaimer", readonly=False)

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4: