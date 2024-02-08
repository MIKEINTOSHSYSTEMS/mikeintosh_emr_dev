# -*- coding: utf-8 -*-

from odoo import api, fields, models, _


class YANAppointment(models.Model):
    _inherit='hms.appointment'

    def _rec_count(self):
        for rec in self:
            rec.request_count = len(rec.lab_request_ids)
            rec.test_count = len(rec.test_ids)

    def _yan_get_attachemnts(self):
        attachments = super(YANAppointment, self)._yan_get_attachemnts()
        attachments += self.test_ids.mapped('attachment_ids')
        return attachments

    test_ids = fields.One2many('patient.laboratory.test', 'appointment_id', string='Lab Tests')
    lab_request_ids = fields.One2many('yan.laboratory.request', 'appointment_id', string='Lab Requests')
    request_count = fields.Integer(compute='_rec_count', string='# Lab Requests')
    test_count = fields.Integer(compute='_rec_count', string='# Lab Tests')

    def action_lab_request(self):
        action = self.env["ir.actions.actions"]._for_xml_id("yan_laboratory.hms_action_lab_test_request")
        action['context'] = {'default_patient_id': self.patient_id.id, 'default_physician_id': self.physician_id.id, 'default_appointment_id': self.id}
        action['views'] = [(self.env.ref('yan_laboratory.patient_laboratory_test_request_form').id, 'form')]
        return action

    def action_view_test_results(self):
        action = self.env["ir.actions.actions"]._for_xml_id("yan_laboratory.action_lab_result")
        action['domain'] = [('id','in',self.test_ids.ids)]
        action['context'] = {'default_patient_id': self.patient_id.id, 'default_physician_id': self.physician_id.id, 'default_appointment_id': self.id}
        return action

    def action_view_lab_request(self):
        action = self.env["ir.actions.actions"]._for_xml_id("yan_laboratory.hms_action_lab_test_request")
        action['domain'] = [('id','in',self.lab_request_ids.ids)]
        action['context'] = {'default_patient_id': self.patient_id.id, 'default_physician_id': self.physician_id.id, 'default_appointment_id': self.id}
        return action


class Treatment(models.Model):
    _inherit = "hms.treatment"

    def _lab_rec_count(self):
        for rec in self:
            rec.request_count = len(rec.request_ids)
            rec.test_count = len(rec.test_ids)

    request_ids = fields.One2many('yan.laboratory.request', 'treatment_id', string='Lab Requests')
    test_ids = fields.One2many('patient.laboratory.test', 'treatment_id', string='Tests')
    request_count = fields.Integer(compute='_lab_rec_count', string='# Lab Requests')
    test_count = fields.Integer(compute='_lab_rec_count', string='# Lab Tests')

    def action_lab_request(self):
        action = self.env["ir.actions.actions"]._for_xml_id("yan_laboratory.hms_action_lab_test_request")
        action['context'] = {'default_patient_id': self.patient_id.id, 'default_treatment_id': self.id}
        action['views'] = [(self.env.ref('yan_laboratory.patient_laboratory_test_request_form').id, 'form')]
        return action

    def action_lab_requests(self):
        action = self.env["ir.actions.actions"]._for_xml_id("yan_laboratory.hms_action_lab_test_request")
        action['domain'] = [('id','in',self.request_ids.ids)]
        action['context'] = {'default_patient_id': self.patient_id.id, 'default_treatment_id': self.id}
        return action

    def action_view_test_results(self):
        action = self.env["ir.actions.actions"]._for_xml_id("yan_laboratory.action_lab_result")
        action['domain'] = [('id','in',self.test_ids.ids)]
        action['context'] = {'default_patient_id': self.patient_id.id, 'default_treatment_id': self.id}
        return action
