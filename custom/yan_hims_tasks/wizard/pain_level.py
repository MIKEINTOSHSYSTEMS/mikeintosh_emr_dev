# coding: utf-8

from odoo import models, api, fields

class YanPainLevel(models.TransientModel):
    _name = 'yan.pain.level'
    _description = "Pain Level Diagram"

    name = fields.Char()