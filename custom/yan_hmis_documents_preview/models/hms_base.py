# -*- coding: utf-8 -*-

from odoo import fields, models, api, _
from odoo.exceptions import ValidationError


class YanHmsDocuments(models.Model):
    _name = "ir.attachment"
    _inherit = ['ir.attachment', 'yan.documnt.view.mixin']


class YanHmsPatient(models.Model):
    _name = "hms.patient"
    _inherit = ['hms.patient', 'yan.documnt.view.mixin']


class YanHmsTreatment(models.Model):
    _name = "hms.treatment"
    _inherit = ['hms.treatment', 'yan.documnt.view.mixin']


class YanPatientProcedure(models.Model):
    _name = "yan.patient.procedure"
    _inherit = ['yan.patient.procedure', 'yan.documnt.view.mixin']


class YanHmsAppointment(models.Model):
    _name = "hms.appointment"
    _inherit = ['hms.appointment', 'yan.documnt.view.mixin']
