# -*- coding: utf-8 -*-

from odoo import api, fields, models, _
from odoo.exceptions import UserError


class PatientRadiologyTest(models.Model):
    _inherit = "patient.radiology.test"

    STATES = {'cancel': [('readonly', True)], 'done': [('readonly', True)]}

    appointment_id = fields.Many2one('hms.appointment', string='Appointment', ondelete='restrict', states=STATES)
    treatment_id = fields.Many2one('hms.treatment', string='Treatment', ondelete='restrict', states=STATES)

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4: