# -*- coding: utf-8 -*-
# Part of AlmightyCS. See LICENSE file for full copyright and licensing details.

from werkzeug import urls

from odoo import api, fields, models, _


class PaymentLinkWizard(models.TransientModel):
    _inherit = 'payment.link.wizard'

    def _get_payment_provider_available(self, res_model, res_id, **kwargs):
        """ Select and return the providers matching the criteria.

        :param str res_model: active model
        :param int res_id: id of 'active_model' record
        :return: The compatible providers
        :rtype: recordset of `payment.provider`
        """
        if res_model == 'hms.appointment':
            kwargs['yan_appointment_id'] = res_id
        return super()._get_payment_provider_available(**kwargs)

    def _get_additional_link_values(self):
        """ Override of `payment` to add `yan_appointment_id` to the payment link values.

        The other values related to the appointment from _get_default_payment_link_values.

        Note: self.ensure_one()

        :return: The additional payment link values.
        :rtype: dict
        """
        res = super()._get_additional_link_values()
        if self.res_model != 'hms.appointment':
            return res

        # Order-related fields are retrieved in the controller
        return {
            'yan_appointment_id': self.res_id,
        }
