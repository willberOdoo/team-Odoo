# -*- coding: utf-8 -*-
from odoo import models, fields, api
class AccountMove( models.Model):
    _inherit = 'account.move'
    control_number = fields.Char(string='Numero de control', required=True, store=True, default='00') 
    
    subjects = fields.Many2one( string = 'Concepto Retención ISLR', comodel_name='tax.withholding_subject', required = True) 
    