# -*- coding: utf-8 -*-

from odoo import fields, models, api, _
from odoo.exceptions import ValidationError


class YANDocumntViewerMixin(models.AbstractModel):
    _name = "yan.documnt.view.mixin"
    _description = "Document Viewer Mixin"

    def _get_document_preview_url(self):
        base_url = self.env["ir.config_parameter"].sudo().get_param("web.base.url")
        for rec in self:
            rec.document_preview_url = base_url + "/my/yan/image/%s/%s" % (self._name,rec.id)

    document_preview_url = fields.Char(compute=_get_document_preview_url, string="Document Preview Link")

    def yan_action_attachments_preview(self):
        ''' Open the website page with the preview results view '''
        attachments = self.env['ir.attachment'].search([
            ('id', 'in', self.ids),
            ('mimetype', 'in', ['image/jpeg','image/jpg','image/png','image/gif']),
        ])
        if len(attachments)==0:
            raise ValidationError(_("There are no documents to Preview. Please Add it in chatter."))

        self.ensure_one()
        return {
            'type': 'ir.actions.act_url',
            'name': "Preview",
            'target': 'new',
            'url': self.document_preview_url
        }

