# -*- encoding: utf-8 -*-
from odoo import api, fields, models,_


class AccountMove(models.Model):
    _inherit = "account.move"

    hospitalization_id = fields.Many2one('yan.hospitalization', ondelete="restrict", string='Hospitalization',
        help="Enter the patient hospitalization code")

 
class Prescription(models.Model):
    _inherit = 'prescription.order'

    STATES = {'cancel': [('readonly', True)], 'prescription': [('readonly', True)]}

    hospitalization_id = fields.Many2one('yan.hospitalization', ondelete="restrict", string='Hospitalization',
        help="Enter the patient hospitalization code", states=STATES)
    ward_id = fields.Many2one('hospital.ward',string='Ward/Room No.', ondelete="restrict",
        states=STATES)
    bed_id = fields.Many2one("hospital.bed",string="Bed No.", ondelete="restrict",
        states=STATES)
    print_in_discharge = fields.Boolean('Print In Discharge')
 

class YANAppointment(models.Model):
    _inherit = 'hms.appointment'

    hospitalization_ids = fields.One2many('yan.hospitalization', 'appointment_id',string='Hospitalizations')

    def action_hospitalization(self):
        action = self.env["ir.actions.actions"]._for_xml_id("yan_hims_ipd.yan_action_form_inpatient")
        action['domain'] = [('appointment_id', '=', self.id)]
        action['context'] = {'default_patient_id': self.patient_id.id, 'default_appointment_id': self.id, 'default_physician_id': self.physician_id.id}
        return action


class YANPatient(models.Model):
    _inherit = "hms.patient"
    
    def _get_hospitalization_count(self):
        for rec in self:
            rec.hospitalization_count = len(rec.hospitalization_ids)

    hospitalization_ids = fields.One2many('yan.hospitalization', 'patient_id',string='Hospitalizations')
    hospitalization_count = fields.Integer(compute='_get_hospitalization_count', string='# Hospitalizations')
    death_register_id = fields.Many2one('patient.death.register', string='Death Register')

    hospitalized = fields.Boolean()
    discharged = fields.Boolean()

    @api.onchange('death_register_id')   
    def onchange_death_register(self):
        if self.death_register_id:
            self.date_of_death = self.death_register_id.date_of_death

    def action_hospitalization(self):
        action = self.env["ir.actions.actions"]._for_xml_id("yan_hims_ipd.yan_action_form_inpatient")
        action['domain'] = [('patient_id', '=', self.id)]
        action['context'] = {'default_patient_id': self.id}
        return action


class StockMove(models.Model):
    _inherit = "stock.move"
    
    hospitalization_id = fields.Many2one('yan.hospitalization', 'Hospitalization')


class YANConsumableLine(models.Model):
    _inherit = "hms.consumable.line"

    hospitalization_id = fields.Many2one('yan.hospitalization', ondelete="restrict", string='Hospitalization')


class YANSurgery(models.Model):
    _inherit = "hms.surgery"

    hospital_ot_id = fields.Many2one('yan.hospital.ot', ondelete="restrict", 
        string='Operation Theater', 
        states={'cancel': [('readonly', True)], 'done': [('readonly', True)]})
    hospitalization_id = fields.Many2one('yan.hospitalization', ondelete="restrict", string='Hospitalization')


class YANMedicamentLine(models.Model):
    _inherit = "medicament.line"
    
    hospitalization_id = fields.Many2one('yan.hospitalization', ondelete="restrict", string='Inpatient')


class product_template(models.Model):
    _inherit = "product.template"

    hospital_product_type = fields.Selection(selection_add=[('bed', 'Bed')])


class YanPatientEvaluation(models.Model):
    _inherit = 'yan.patient.evaluation'

    READONLY_STATES = {'cancel': [('readonly', True)], 'done': [('readonly', True)]}

    hospitalization_id = fields.Many2one('yan.hospitalization', states=READONLY_STATES, string='Hospitalization')


class Physician(models.Model):
    _inherit = "hms.physician"

    def _hos_rec_count(self):
        Hospitalization = self.env['yan.hospitalization']
        for record in self.with_context(active_test=False):
            record.hospitalization_count = Hospitalization.search_count([('physician_id', '=', record.id)])

    hospitalization_count = fields.Integer(compute='_hos_rec_count', string='# Hospitalization')
    ward_round_service_id = fields.Many2one('product.product', domain=[('type','=','service')],
        string='Ward Round Service',  ondelete='cascade', help='Ward Round Product')

    def action_hospitalization(self):
        action = self.env["ir.actions.actions"]._for_xml_id("yan_hims_ipd.yan_action_form_inpatient")
        action['domain'] = [('physician_id','=',self.id)]
        action['context'] = {'default_physician_id': self.id}
        return action