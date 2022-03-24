# -*- coding: utf-8 -*-
from odoo import models, fields, api
class AccountMove( models.Model):
    _inherit = 'account.move'
    control_number = fields.Char(string='Numero de control', required=True, default='00')
    
    withholdings_counter = fields.Integer(string='counter', compute='_compute_withholding_counter') 
    
    @api.model
    def _compute_withholding_counter(self):
        for record in self:
            count = self.env['tax.withholding_voucher_vendor'].search_count([('related_invoice', '=', record.id)])
            record.withholdings_counter = count
            


    def open_model_test(self):
        print("dnfvjhv   nsfd nm fdnb nme njndfsm dnf nmf  nmdf nm nm  nmds nm fdn dfnm nmjd ndvn nd nmdnj sk mxcnjdfm ndf  nmd nc mdfnm fds d, kndf  kmnmn nmdf njd  ")