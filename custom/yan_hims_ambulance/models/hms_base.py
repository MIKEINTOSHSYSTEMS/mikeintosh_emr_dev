# -*- coding: utf-8 -*-

from odoo import api, fields, models, _


class ResPartner(models.Model):
    _inherit = 'res.partner'

    def _ambulance_drive_count(self):
        for rec in self: 
            rec.yan_ambulance_drive_count = len(rec.sudo().yan_ambulance_drive_ids.ids)

    is_driver = fields.Boolean('Is Driver')
    yan_ambulance_drive_ids = fields.One2many('yan.ambulance.service', 'driver_id', 'Ambulance Drives')
    yan_ambulance_drive_count = fields.Integer(compute="_ambulance_drive_count", string='#Ambulance Drives')

    def view_yan_ambulance_drive(self):
        action = self.env["ir.actions.actions"]._for_xml_id("yan_hims_ambulance.action_yan_ambulance_service")
        action['domain'] = [('driver_id', '=', self.id)]
        action['context'] = {'default_driver_id': self.id}
        return action


class HMSPatient(models.Model):
    _inherit = 'hms.patient'

    def _ambulance_service_count(self):
        for rec in self: 
            rec.yan_ambulance_service_count = len(rec.yan_ambulance_service_ids.ids)

    yan_ambulance_service_ids = fields.One2many('yan.ambulance.service','patient_id', 'Ambulance Services')
    yan_ambulance_service_count = fields.Integer(compute="_ambulance_service_count", string='#Ambulance Services', groups="yan_hims_ambulance.group_ambulance_service_user")

    def view_yan_ambulance_service(self):
        action = self.env["ir.actions.actions"]._for_xml_id("yan_hims_ambulance.action_yan_ambulance_service")
        action['domain'] = [('patient_id', '=', self.id)]
        action['context'] = {'default_patient_id': self.id}
        return action


class ProductTemplate(models.Model):
    _inherit = 'product.template'

    hospital_product_type = fields.Selection(selection_add=[('ambulance','Ambulance')])


class FleetVehicle(models.Model):
    _inherit = 'fleet.vehicle'

    service_product_id = fields.Many2one('product.product', 
        domain=[('type','=','service')], string='Ambulance Invoicing Product', 
        ondelete='restrict', help='Ambulance Invoicing Product')
    user_id = fields.Many2one('res.users',  string='Doctor/Nurse', ondelete='restrict')

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4: