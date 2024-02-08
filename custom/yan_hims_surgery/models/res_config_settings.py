# -*- encoding: utf-8 -*-
from odoo import api, fields, models,_


class ResCompany(models.Model):
    _inherit = "res.company"

    yan_surgery_usage_location_id = fields.Many2one('stock.location', 
        string='Surgery Usage Location for Consumed Products')
    yan_surgery_stock_location_id = fields.Many2one('stock.location', 
        string='Surgery Stock Location for Consumed Products')


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    yan_surgery_usage_location_id = fields.Many2one('stock.location', 
        related='company_id.yan_surgery_usage_location_id',
        domain=[('usage','=','customer')],
        string='Surgery Usage Location for Consumed Products', 
        ondelete='cascade', help='Usage Location for Consumed Products in Surgery', readonly=False)
    yan_surgery_stock_location_id = fields.Many2one('stock.location', 
        related='company_id.yan_surgery_stock_location_id',
        domain=[('usage','=','internal')],
        string='Surgery Stock Location for Consumed Products', 
        ondelete='cascade', help='Stock Location for Consumed Products in Surgery', readonly=False)

    