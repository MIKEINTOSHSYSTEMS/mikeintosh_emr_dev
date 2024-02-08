# -*- coding: utf-8 -*-

from odoo import api, fields, models

class YanMedicineExpiry(models.TransientModel):
    _name = "yan.medicine.expiry"
    _description = "Yan Medicine Expiry"

    date_from = fields.Date(string='Date From')
    date_to = fields.Date(string='Date To')
    user_id = fields.Many2one('res.users', string='User', default=lambda self: self.env.user.id)
    location_ids = fields.Many2many('stock.location', string='Locations')

    def get_medicine_data(self):
        medicine_data = []
        domain = [('location_id.usage','=', 'internal'),('lot_id','!=',False)]

        if self.date_from:
            domain += [('removal_date','>=', self.date_from)]
        if self.date_to:
            domain += [('removal_date','<=', self.date_to)]
        if self.location_ids:
            domain += [('location_id','child_of', self.location_ids.ids)]

        madi_data = self.env['stock.quant'].search(domain)

        for medicine in madi_data:
            medicine_data.append({
                'name': medicine.lot_id.name,
                'product_id': medicine.product_id.name,
                'quantity': medicine.inventory_quantity_auto_apply,
                'expiration_date': medicine.removal_date,
                'location': medicine.location_id.name,
            })
        return medicine_data

    def print_pdf_report(self):
        return self.env.ref('yan_pharmacy.yan_medicine_expiry_report_action').report_action(self)

    def action_view_medicine_expiry(self):
        action = self.env["ir.actions.actions"]._for_xml_id("stock.dashboard_open_quants")
        action['views'] = [(self.env.ref('stock.view_stock_quant_tree_editable').id, 'tree')]
        domain = [('location_id.usage','=', 'internal'),('lot_id','!=',False)]
        if self.date_from:
            domain += [('removal_date','>=', self.date_from)]
        if self.date_to:
            domain += [('removal_date','<=', self.date_to)]
        if self.location_ids:
            domain += [('location_id','child_of', self.location_ids.ids)]
        action['domain'] = domain
        return action