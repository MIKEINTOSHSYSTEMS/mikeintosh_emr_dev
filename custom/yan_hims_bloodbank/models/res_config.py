# -*- coding: utf-8 -*-
# Part of AlmightyCS See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models


class ResCompany(models.Model):
    _inherit = "res.company"

    yan_blood_requisition_invoicing = fields.Boolean("Allow Blood Requisition Invoicing", default=False)
    yan_blood_issuance_invoicing = fields.Boolean("Allow Blood Issuance Invoicing", default=False)
    yan_blood_usage_location_id = fields.Many2one('stock.location', 
        string='Usage Location for Blood.')
    yan_blood_stock_location_id = fields.Many2one('stock.location', 
        string='Stock Location for Blood')
    yan_blood_requisition_product_id = fields.Many2one('product.product', 
        domain=[('type','=','service')],
        string='Blood Requisition Invoice Product', 
        ondelete='restrict', help='Blood Requisition Invoice Product')
    yan_blood_issuance_product_id = fields.Many2one('product.product', 
        domain=[('type','=','service')],
        string='Blood Issuance Invoice Product', 
        ondelete='restrict', help='Blood Issuance Invoice Product')


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    yan_blood_requisition_invoicing = fields.Boolean("Allow Blood Requisition Invoicing", related='company_id.yan_blood_requisition_invoicing', readonly=False)
    yan_blood_issuance_invoicing = fields.Boolean("Allow Blood Issuance Invoicing", related='company_id.yan_blood_issuance_invoicing', readonly=False)
    yan_blood_usage_location_id = fields.Many2one('stock.location', 
        related='company_id.yan_blood_usage_location_id',
        domain=[('usage','=','customer')],
        string='Usage Location for Blood', readonly=False)
    yan_blood_stock_location_id = fields.Many2one('stock.location', 
        related='company_id.yan_blood_stock_location_id',
        domain=[('usage','=','internal')],
        string='Stock Location for Blood', readonly=False)

    yan_blood_requisition_product_id = fields.Many2one('product.product', related='company_id.yan_blood_requisition_product_id', readonly=False,
        domain=[('type','=','service')],
        string='Blood Requisition Invoice Product', 
        ondelete='restrict', help='Blood Requisition Invoice Product')
    yan_blood_issuance_product_id = fields.Many2one('product.product', related='company_id.yan_blood_issuance_product_id', readonly=False,
        domain=[('type','=','service')],
        string='Blood Issuance Invoice Product', 
        ondelete='restrict', help='Blood Issuance Invoice Product')