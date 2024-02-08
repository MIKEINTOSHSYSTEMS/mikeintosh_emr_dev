# -*- coding: utf-8 -*-

from odoo import api, fields, models, _


class YANAppointment(models.Model):
    _inherit='hms.appointment'

    def _radiology_rec_count(self):
        for rec in self:
            rec.radiology_request_count = len(rec.radiology_request_ids)
            rec.radiology_test_count = len(rec.radiology_test_ids)

    def _yan_get_attachemnts(self):
        attachments = super(YANAppointment, self)._yan_get_attachemnts()
        attachments += self.radiology_test_ids.mapped('attachment_ids')
        return attachments

    radiology_test_ids = fields.One2many('patient.radiology.test', 'appointment_id', string='Radiology Tests')
    radiology_request_ids = fields.One2many('yan.radiology.request', 'appointment_id', string='Radiology Requests')
    radiology_request_count = fields.Integer(compute='_radiology_rec_count', string='# Radiology Requests')
    radiology_test_count = fields.Integer(compute='_radiology_rec_count', string='# Radiology Tests')

    def action_radiology_request(self):
        action = self.env["ir.actions.actions"]._for_xml_id("yan_radiology.hms_action_radiology_request")
        action['context'] = {'default_patient_id': self.patient_id.id, 'default_physician_id': self.physician_id.id, 'default_appointment_id': self.id}
        action['views'] = [(self.env.ref('yan_radiology.patient_radiology_test_request_form').id, 'form')]
        return action

    def action_view_radiology_requests(self):
        action = self.env["ir.actions.actions"]._for_xml_id("yan_radiology.hms_action_radiology_request")
        action['domain'] = [('id','in',self.radiology_request_ids.ids)]
        action['context'] = {'default_patient_id': self.patient_id.id, 'default_hospitalization_id': self.id}
        return action

    def action_view_radiology_results(self):
        action = self.env["ir.actions.actions"]._for_xml_id("yan_radiology.action_radiology_result")
        action['domain'] = [('id','in',self.radiology_test_ids.ids)]
        action['context'] = {'default_patient_id': self.patient_id.id, 'default_physician_id': self.physician_id.id, 'default_appointment_id': self.id}
        return action


class Treatment(models.Model):
    _inherit = "hms.treatment"

    def _radiology_rec_count(self):
        for rec in self:
            rec.radiology_request_count = len(rec.radiology_request_ids)
            rec.radiology_test_count = len(rec.radiology_test_ids)

    radiology_request_ids = fields.One2many('yan.radiology.request', 'treatment_id', string='Radiology Requests')
    radiology_test_ids = fields.One2many('patient.radiology.test', 'treatment_id', string='Radiology Tests')
    radiology_test_count = fields.Integer(compute='_radiology_rec_count', string='# Radiology Tests')
    radiology_request_count = fields.Integer(compute='_radiology_rec_count', string='# Radiology Requests')

    def action_radiology_request(self):
        action = self.env["ir.actions.actions"]._for_xml_id("yan_radiology.hms_action_radiology_request")
        action['context'] = {'default_patient_id': self.patient_id.id, 'default_treatment_id': self.id}
        action['views'] = [(self.env.ref('yan_radiology.patient_radiology_test_request_form').id, 'form')]
        return action

    def action_radiology_requests(self):
        action = self.env["ir.actions.actions"]._for_xml_id("yan_radiology.hms_action_radiology_request")
        action['domain'] = [('id','in',self.radiology_request_ids.ids)]
        action['context'] = {'default_patient_id': self.patient_id.id, 'default_treatment_id': self.id}
        return action

    def action_view_test_results(self):
        action = self.env["ir.actions.actions"]._for_xml_id("yan_radiology.action_radiology_result")
        action['domain'] = [('id','in',self.radiology_test_ids.ids)]
        action['context'] = {'default_patient_id': self.patient_id.id, 'default_treatment_id': self.id}
        return action

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4: