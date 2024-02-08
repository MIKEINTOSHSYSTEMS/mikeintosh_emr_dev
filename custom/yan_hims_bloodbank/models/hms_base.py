# -*- coding: utf-8 -*-

from odoo import api, fields, models, _


class ResPartner(models.Model):
    _inherit = 'res.partner'

    @api.depends('yan_blood_requisition_ids','yan_blood_issuance_count')
    def _blood_count(self):
        for rec in self: 
            rec.yan_blood_requisition_count = len(rec.sudo().yan_blood_requisition_ids.ids)
            rec.yan_blood_issuance_count = len(rec.sudo().yan_blood_issuance_ids.ids)

    yan_blood_requisition_ids = fields.One2many('yan.blood.requisition','partner_id', 'Blood Requisitions')
    yan_blood_issuance_ids = fields.One2many('yan.blood.issuance','partner_id', 'Blood Donations')
    yan_blood_requisition_count = fields.Integer(compute="_blood_count", readonly=True, string="#Blood Donations", store=True)
    yan_blood_issuance_count = fields.Integer(compute="_blood_count", readonly=True, string="#Blood Requisitions", store=True)

    def view_yan_blood_requisition(self):
        action = self.env["ir.actions.actions"]._for_xml_id("yan_hims_bloodbank.action_yan_blood_requisition")
        action['domain'] = [('partner_id', '=', self.id)]
        action['context'] = {'default_partner_id': self.id}
        return action

    def view_yan_blood_issuance(self):
        action = self.env["ir.actions.actions"]._for_xml_id("yan_hims_bloodbank.action_yan_blood_issuance")
        action['domain'] = [('partner_id', '=', self.id)]
        action['context'] = {'default_partner_id': self.id}
        return action


class HMSPatient(models.Model):
    _inherit = 'hms.patient'

    def view_yan_blood_requisition(self):
        action = self.env["ir.actions.actions"]._for_xml_id("yan_hims_bloodbank.action_yan_blood_requisition")
        action['domain'] = [('patient_id', '=', self.id)]
        action['context'] = {'default_patient_id': self.id}
        return action

    def view_yan_blood_issuance(self):
        action = self.env["ir.actions.actions"]._for_xml_id("yan_hims_bloodbank.action_yan_blood_issuance")
        action['domain'] = [('patient_id', '=', self.id)]
        action['context'] = {'default_patient_id': self.id}
        return action


class ProductTemplate(models.Model):
    _inherit = 'product.template'

    hospital_product_type = fields.Selection(selection_add=[('blood','Blood Bank')])


class StockProductionLot(models.Model):
    _inherit = 'stock.lot'

    @api.depends('product_id')
    def _get_blood_product(self):
        for rec in self:
            rec.is_blood_product = True if rec.product_id.hospital_product_type=='blood' else False

    is_blood_product = fields.Boolean(compute="_get_blood_product", store=True, string='Is Blood Product')
    requisition_id = fields.Many2one('yan.blood.requisition', ondelete='cascade', string='Blood Requisition')
    issuance_id = fields.Many2one('yan.blood.issuance', ondelete='cascade', string='Blood Issuance')
    receiver_partner_id = fields.Many2one('res.partner', ondelete='cascade', string='Receiver')
    donor_partner_id = fields.Many2one('res.partner', ondelete='cascade', string='Donor')
    blood_group = fields.Selection(related="requisition_id.blood_group", store=True, string='Blood Group')

    @api.onchange('issuance_id')
    def onchange_issuance_id(self):
        if self.issuance_id:
            self.receiver_partner_id = self.issuance_id.partner_id.id
        else:
            self.receiver_partner_id = False

    @api.onchange('requisition_id')
    def onchange_requisition_id(self):
        if self.requisition_id:
            self.donor_partner_id = self.requisition_id.partner_id.id
        else:
            self.donor_partner_id = False


class StockMove(models.Model):
    _inherit = "stock.move"

    issuance_id = fields.Many2one('yan.blood.issuance', string="Blood Issuance", ondelete="restrict")

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4: