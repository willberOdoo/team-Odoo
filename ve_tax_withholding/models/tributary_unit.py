# -*- coding: utf-8 -*- 
import datetime 
from odoo import models, fields, api


class TributaryUnit(models.Model):
    _name = 'tax.tributary_unit'
    _description = 'model for tributary  unit'
    
    unit = fields.Float(string='Valor de la Unidad Tributaria', required = True, store= True)
    factor = fields.Float(string='Factor Fiscal', required = True, store= True)
    minimum = fields.Float(string='Minimo', default= lambda self: self._compute_minimum() , store= True)
    
    gaceta = fields.Char(string='Nro. Gaceta', store= True)
    gaceta_fecha = fields.Date(string='Fecha de la Gaceta', store= True)
    
    @api.onchange('unit', 'factor')
    def _compute_minimum(self):
        for record in self:
            record.minimum = record.unit * record.factor