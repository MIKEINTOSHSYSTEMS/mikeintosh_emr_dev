# -*- coding: utf-8 -*-

from odoo import http
from odoo.http import request
from odoo.tools.translate import _


class YanImageZoom(http.Controller):

    @http.route(['/my/yan/image/<string:model>/<int:record>'], type='http', auth="user", website=True, sitemap=False)
    def yan_image_preview(self, model=False, record=False, **kwargs):
        record = request.env[model].browse([record])
        attachments = request.env['ir.attachment'].search([
            ('id', 'in', record.ids),
            ('mimetype', 'in', ['image/jpeg','image/jpg','image/png','image/gif']),
        ])
        return request.render("yan_documents_preview.yan_image_preview", {'attachments':attachments})

