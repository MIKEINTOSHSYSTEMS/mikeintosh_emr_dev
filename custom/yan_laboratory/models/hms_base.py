# -*- coding: utf-8 -*-

from odoo import api, fields, models, _
import uuid

class AccountInvoice(models.Model):
    _inherit = 'account.move'

    request_id = fields.Many2one('yan.laboratory.request', string='Lab Request', copy=False, ondelete='restrict')
    hospital_invoice_type = fields.Selection(selection_add=[('laboratory', 'Laboratory')])


class StockMove(models.Model):
    _inherit = "stock.move"

    lab_test_id = fields.Many2one('patient.laboratory.test', string="Lab Test", ondelete="restrict")


class YANConsumableLine(models.Model):
    _inherit = "hms.consumable.line"

    patient_lab_test_id = fields.Many2one('patient.laboratory.test', string="Patient Lab Test", ondelete="restrict")
    lab_test_id = fields.Many2one('yan.lab.test', string="Lab Test", ondelete="restrict")


class YANPatient(models.Model):
    _inherit = "hms.patient"

    def _rec_count(self):
        rec = super(YANPatient, self)._rec_count()
        for rec in self:
            rec.request_count = len(rec.request_ids)
            rec.test_count = len(rec.test_ids)

    def _yan_get_attachemnts(self):
        attachments = super(YANPatient, self)._yan_get_attachemnts()
        attachments += self.test_ids.mapped('attachment_ids')
        return attachments

    request_ids = fields.One2many('yan.laboratory.request', 'patient_id', string='Lab Requests')
    test_ids = fields.One2many('patient.laboratory.test', 'patient_id', string='Tests')
    request_count = fields.Integer(compute='_rec_count', string='# Lab Requests')
    test_count = fields.Integer(compute='_rec_count', string='# Lab Tests')

    def action_lab_requests(self):
        action = self.env["ir.actions.actions"]._for_xml_id("yan_laboratory.hms_action_lab_test_request")
        action['domain'] = [('id','in',self.request_ids.ids)]
        action['context'] = {'default_patient_id': self.id}
        return action

    def action_view_lab_test_results(self):
        action = self.env["ir.actions.actions"]._for_xml_id("yan_laboratory.action_lab_result")
        action['domain'] = [('id','in',self.test_ids.ids)]
        action['context'] = {'default_patient_id': self.id}
        return action


class product_template(models.Model):
    _inherit = "product.template"

    hospital_product_type = fields.Selection(selection_add=[('pathology', 'Pathology'), ('laboratory', 'Laboratory')])


class Physician(models.Model):
    _inherit = "hms.physician"

    def _yan_lab_rec_count(self):
        Labrequest = self.env['yan.laboratory.request']
        Labresult = self.env['patient.laboratory.test']
        for record in self.with_context(active_test=False):
            record.lab_request_count = Labrequest.search_count([('physician_id', '=', record.id)])
            record.lab_result_count = Labresult.search_count([('physician_id', '=', record.id)])

    lab_request_count = fields.Integer(compute='_yan_lab_rec_count', string='# Lab Request')
    lab_result_count = fields.Integer(compute='_yan_lab_rec_count', string='# Lab Result')

    def action_lab_request(self):
        action = self.env["ir.actions.actions"]._for_xml_id("yan_laboratory.hms_action_lab_test_request")
        action['domain'] = [('physician_id','=',self.id)]
        action['context'] = {'default_physician_id': self.id}
        return action

    def action_lab_result(self):
        action = self.env["ir.actions.actions"]._for_xml_id("yan_laboratory.action_lab_result")
        action['domain'] = [('physician_id','=',self.id)]
        action['context'] = {'default_physician_id': self.id}
        return action


class ResUsers(models.Model):
    _inherit = "res.users"

    default_collection_center_id = fields.Many2one('yan.laboratory',  string='Collection Center')

    @property
    def SELF_READABLE_FIELDS(self):
        return super().SELF_READABLE_FIELDS + ['default_collection_center_id']

    @property
    def SELF_WRITEABLE_FIELDS(self):
        return super().SELF_WRITEABLE_FIELDS + ['default_collection_center_id']


class IrAttachment(models.Model):
    _inherit = "ir.attachment"

    def _yan_portal_ensure_token(self):
        """ Get the current record access token """
        if not self.access_token:
            # we use a `write` to force the cache clearing otherwise `return self.access_token` will return False
            self.sudo().write({'access_token': str(uuid.uuid4())})
        return self.access_token

