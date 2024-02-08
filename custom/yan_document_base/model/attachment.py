# -*- coding: utf-8 -*-

from odoo import api, fields, models, _
from odoo.exceptions import AccessError, ValidationError, MissingError, UserError
from collections import defaultdict


class Attachment(models.Model):
    _inherit = "ir.attachment"

    is_document = fields.Boolean("Is Document")
    directory_id = fields.Many2one('document.directory', string='Directory', ondelete='restrict')
    description = fields.Text(string='Description')
    tag_ids = fields.Many2many('yan.document.tag', 'yan_attachment_document_tag_rel', 'document_id', 'tag_id', 
        string='Tags', help="Classify and analyze your Document")

    #yan: Allow to read Documents. Only by passs to read is_document is added as if condition.
    @api.model
    def check(self, mode, values=None):
        """ Restricts the access to an ir.attachment, according to referred mode """
        if self.env.is_superuser():
            return True
        # Always require an internal user (aka, employee) to access to an attachment
        if not (self.env.is_admin() or self.env.user._is_internal()):
            raise AccessError(_("Sorry, you are not allowed to access this document."))
        # collect the records to check (by model)
        model_ids = defaultdict(set)            # {model_name: set(ids)}
        if self:
            self.env['ir.attachment'].flush_model(['res_model', 'res_id', 'create_uid', 'public', 'res_field'])
            self._cr.execute('SELECT res_model, res_id, create_uid, public, res_field, is_document FROM ir_attachment WHERE id IN %s', [tuple(self.ids)])
            for res_model, res_id, create_uid, public, res_field, is_document in self._cr.fetchall():
                if public and mode == 'read':
                    continue
                if is_document:
                    continue
                if not self.env.is_system() and (res_field or (not res_id and create_uid != self.env.uid)):
                    raise AccessError(_("Sorry, you are not allowed to access this document."))
                if not (res_model and res_id):
                    continue
                model_ids[res_model].add(res_id)
        if values and values.get('res_model') and values.get('res_id'):
            model_ids[values['res_model']].add(values['res_id'])

        # check access rights on the records
        for res_model, res_ids in model_ids.items():
            # ignore attachments that are not attached to a resource anymore
            # when checking access rights (resource was deleted but attachment
            # was not)
            if res_model not in self.env:
                continue
            if res_model == 'res.users' and len(res_ids) == 1 and self.env.uid == list(res_ids)[0]:
                # by default a user cannot write on itself, despite the list of writeable fields
                # e.g. in the case of a user inserting an image into his image signature
                # we need to bypass this check which would needlessly throw us away
                continue
            records = self.env[res_model].browse(res_ids).exists()
            # For related models, check if we can write to the model, as unlinking
            # and creating attachments can be seen as an update to the model
            access_mode = 'write' if mode in ('create', 'unlink') else mode
            records.check_access_rights(access_mode)
            records.check_access_rule(access_mode)

