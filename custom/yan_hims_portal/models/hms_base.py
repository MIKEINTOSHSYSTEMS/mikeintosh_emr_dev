# -*- coding: utf-8 -*-
from odoo import api, fields, models


class HmsAppointment(models.Model):
    _name = "hms.appointment"
    _inherit = ['portal.mixin', 'hms.appointment']

    def _compute_access_url(self):
        super(HmsAppointment, self)._compute_access_url()
        for record in self:
            record.access_url = '/my/appointments/%s' % (record.id)

    def yan_preview_record(self):
        self.ensure_one()
        return {
            'type': 'ir.actions.act_url',
            'target': 'self',
            'url': self.get_portal_url(),
        }


class PrescriptionOrder(models.Model):
    _name = "prescription.order"
    _inherit = ['portal.mixin', 'prescription.order']

    def _compute_access_url(self):
        super(PrescriptionOrder, self)._compute_access_url()
        for record in self:
            record.access_url = '/my/prescriptions/%s' % (record.id)

    def yan_preview_record(self):
        self.ensure_one()
        return {
            'type': 'ir.actions.act_url',
            'target': 'self',
            'url': self.get_portal_url(),
        }


class YanPatientEvaluation(models.Model):
    _name = "yan.patient.evaluation"
    _inherit = ['portal.mixin', 'yan.patient.evaluation']

    def _compute_access_url(self):
        super(YanPatientEvaluation, self)._compute_access_url()
        for record in self:
            record.access_url = '/my/evaluations/%s' % (record.id)

    def yan_preview_record(self):
        self.ensure_one()
        return {
            'type': 'ir.actions.act_url',
            'target': 'self',
            'url': self.get_portal_url(),
        }
