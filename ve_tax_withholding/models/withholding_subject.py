# -*- coding: utf-8 -*-
from odoo import models, fields, api

class WithholdingSubject( models.Model):
    _name = 'tax.withholding_subject'
    _description = 'Subject of Withholding Voucher'

    name = fields.Char( string = 'Concepto de la Retención', required = True)
    code = fields.Char( string = 'Código', required = True)
    notes = fields.Text( string = 'Notas internas')
    active = fields.Boolean( string = 'Active', default = True)
    partner_type_custom = fields.Selection([('PNR',' PNR: Persona Natural Residente '),
                                            ('PNNR','PNNR: Persona Natural No Residente'), 
                                            ('PJD',' PJD: Persona Juridica Dominciliada'), 
                                            ('PJDN','PJDN: Persona Juridica No Domicialda'), 
                                            ('PJNCD','PJNCD: Persona Juridica No Costituida Domicilada')],
                                           string='Retención ISLR Tipo de persona', store=True, )
    