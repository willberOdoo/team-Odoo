 # -*- coding: utf-8 -*-

from odoo import models, fields, api

class InheritedTaxes(models.Model):
    
    _inherit = 'account.tax'
    
    impuesto = fields.Char(string='Impuestos')