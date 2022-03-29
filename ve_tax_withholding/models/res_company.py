# -*- coding: utf-8 -*- 

from odoo import models, fields, api 
#factor para calcular la retencion ISLR
class ResCompany(models.Model):
    _inherit = 'res.company'
    
    factor = fields.Float(string = 'Factor Fiscal', store=True  )
