# -*- coding: utf-8 -*-

from odoo import api, fields, models, _
from odoo.exceptions import UserError


class PhysicianSpecialty(models.Model):
    _name = 'physician.specialty'
    _description = "Physician Specialty"

    code = fields.Char(string='Code')
    name = fields.Char(string='Specialty', required=True, translate=True)

    _sql_constraints = [
        ('name_uniq', 'UNIQUE(name)', 'Name must be unique!'),
    ]


class PhysicianDegree(models.Model):
    _name = 'physician.degree'
    _description = "Physician Degree"

    name = fields.Char(string='Degree')

    _sql_constraints = [
        ('name_uniq', 'UNIQUE(name)', 'Name must be unique!'),
    ]


class Physician(models.Model):
    _name = 'hms.physician'
    _description = "Physician"
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _inherits = {'res.users': 'user_id'}

    user_id = fields.Many2one('res.users',string='Related User', required=True,
        ondelete='cascade', help='User-related data of the physician')
    code = fields.Char(string='Physician Code', default='/', tracking=True)
    degree_ids = fields.Many2many('physician.degree', 'physician_rel_education', 'physician_ids','degree_ids', string='Degree')
    specialty_id = fields.Many2one('physician.specialty', ondelete='set null', string='Specialty', help='Specialty Code', tracking=True)
    medical_license = fields.Char(string='Medical License', tracking=True)

    yan_region = fields.Selection([
        ('addis Ababa', 'Addis Ababa'),
        ('afar', 'Afar'),
        ('amhara', 'Amhara'),
        ('benishangul-Gumuz', 'Benishangul-Gumuz'),
        ('dire Dawa', 'Dire Dawa'),
        ('gambela', 'Gambela'),
        ('harari', 'Harari'),
        ('oromia', 'Oromia'),
        ('sidama', 'Sidama'),
        ('somali', 'Somali'),
        ('south West', 'South West'),
        ('southern', 'Southern'),
        ('tigray', 'Tigray')], string='Region', default="addis Ababa")
    zone = fields.Char("Zone")
    subcity = fields.Selection([
        ('addis Ketema', 'Addis Ketema'),
        ('akaky Kaliti', 'Akaky Kaliti'),
        ('arada', 'Arada'),
        ('bole', 'Bole'),
        ('gullele', 'Gullele'),
        ('kirkos', 'Kirkos'),
        ('kolfe Keranio', 'Kolfe Keranio'),
        ('lemi Kura', 'Lemi Kura'),
        ('lideta', 'Lideta'),
        ('nifas Silk-Lafto', 'Nifas Silk-Lafto'),
        ('yeka', 'Yeka')], string='Subcity')
    woreda = fields.Char("Woreda")
    house_number = fields.Char("House Number")

    @api.model_create_multi
    def create(self, vals_list):
        for values in vals_list:
            if values.get('code','/') == '/':
                values['code'] = self.env['ir.sequence'].next_by_code('hms.physician')
            if values.get('email'):
                values['login'] = values.get('email')

            #YAN: It creates issue in physican creation
            if values.get('user_ids'):
                values.pop('user_ids')

        return super(Physician, self).create(vals_list)

#