# -*- coding: utf-8 -*-

from odoo import api, fields, models, _
from odoo.exceptions import UserError


class YanLaboratoryRequest(models.Model):
    _inherit = 'yan.laboratory.request'
    
    STATES = {'requested': [('readonly', True)], 'accepted': [('readonly', True)], 'in_progress': [('readonly', True)], 'cancel': [('readonly', True)], 'done': [('readonly', True)]}

    appointment_id = fields.Many2one('hms.appointment', string='Appointment', ondelete='restrict', states=STATES)
    treatment_id = fields.Many2one('hms.treatment', string='Treatment', ondelete='restrict', states=STATES)

    def prepare_test_result_data(self, line, patient):
        res = super(YanLaboratoryRequest, self).prepare_test_result_data(line, patient)
        res['appointment_id'] = self.appointment_id and self.appointment_id.id or False
        return res

