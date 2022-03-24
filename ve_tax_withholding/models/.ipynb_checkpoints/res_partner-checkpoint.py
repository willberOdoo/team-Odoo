# -*- coding: utf-8 -*- 

from odoo import models, fields, api 
#retencion de ISLR para tipo de persona
class ResPartner(models.Model):
    
    _inherit = 'res.partner' 
    
    partner_type_custom = fields.Selection([('PNR','PNR: Persona Natural Residente '),
                                            ('PNNR','PNNR: Persona Natural No Residente'), 
                                            ('PJD','PJD: Persona Juridica Dominciliada'), 
                                            ('PJDN','PJDN: Persona Juridica No Domicialda'), 
                                            ('PJNCD','PJNCD: Persona Juridica No Costituida Domicilada')],
                                           string='Retención ISLR Tipo de persona', store=True, ) 
    #permite cargar el tipo de impuesto 
    type_tax = fields.Many2one( string = '% Retencion IVA', comodel_name = 'account.tax')
    
    
            
    

            
    