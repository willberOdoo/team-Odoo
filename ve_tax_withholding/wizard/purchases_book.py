# -*- coding: utf-8 -*-
from odoo import models, fields, api
from datetime import datetime

class PurchasesBookWizard( models.TransientModel):
    _name = 'tax.purchases_book_wizard'
    _description = 'Book of every purchase invoice entry by period'
    date_from = fields.Date(string='Fecha desde')
    date_to = fields.Date(string='Fecha hasta') 
    related_invoices = fields.One2many(string='Facturas', comodel_name='tax.purchases_book.lines_wizard', inverse_name='related_book')
    
    company_id = fields.Many2one(string='Compañía', comodel_name='res.company')

    @api.onchange('date_from','date_to')
    def _compute_invoices(self):
        book_lines = []
        invoices = self.env['account.move'].search([('move_type','=','in_invoice'),('invoice_date','>=',self.date_from),('invoice_date','<=',self.date_to)])
        self.clear_related_invoices()
        for bill in invoices:
            debit_credit_notes = self.env['account.move'].search([('move_type','=','in_refund'),('reversed_entry_id', '=', bill.id)])
            taxes_vouchers = self.env['tax.withholding_voucher_vendor'].search([('related_invoice', '=', bill.id)])
            book_lines.append((0,0,{'name':bill.name, 'control_number':bill.control_number, 'total_amount_with_taxes':bill.amount_total, 'tax_amount':bill.amount_tax, 'tax_amount_held':0.0, 'period':bill.invoice_date}) )
            for note in debit_credit_notes:
                book_lines.append((0,0,{'name':note.name, 'control_number':note.control_number, 'total_amount_with_taxes':0.0, 'tax_amount':0.0, 'tax_amount_held':0.0, 'period':note.invoice_date}) )
            for voucher in taxes_vouchers:
                book_lines.append((0,0,{'name':voucher.code, 'control_number':voucher.code, 'total_amount_with_taxes':0.0, 'tax_amount':0.0, 'tax_amount_held':voucher.taxed_amount_held, 'period':voucher.creation_date}) )
        self.related_invoices = book_lines
           
    def clear_related_invoices(self):
        for invoice in self.related_invoices:
            invoice.unlink()

    def action_print_report(self):
        data = {'date_from':self.date_from, 'date_to':self.date_to, 'related_invoices': self.related_invoices.ids}
        return self.env.ref('ve_tax_withholding.action_report_tax_book_report').report_action(self, data)

    def action_generate_xlsx_report(self):
        data = {'date_from':self.date_from, 'date_to':self.date_to, 'related_invoices': self.related_invoices.ids}
        return self.env.ref('ve_tax_withholding.action_report_excel_book').report_action(self, data)

class BookReportExcel(models.AbstractModel):
    _name = 'report.ve_tax_withholding.report_book_excel'
    _description = 'Report Book in Excel'
    _inherit = 'report.report_xlsx.abstract'

    def generate_xlsx_report(self, workbook, data, partners):
        domain = [('move_type','=','in_invoice')]
        dates = []
        months = ['Enero','Febrero','Marzo','Abril','Mayo','Junio','Julio','Agosto','Septiembre','Octubre','Noviembre','Diciembre']
        if data.get('date_from'):
            domain.append(('invoice_date', '>=', data.get('date_from')))
            dates.append(data.get('date_from'))
        if data.get('date_to'):
            domain.append(('invoice_date', '<=', data.get('date_to')))
            dates.append(data.get('date_to'))
        docs = self.env['account.move'].search(domain)
        book_lines = []
        total_base = 0.0
        total_credit = 0.0
        total_tax = 0.0
        total_tax_held = 0.0
        sheet = workbook.add_worksheet('Libro de Compras')
        bold = workbook.add_format({'bold': True, 'align': 'center', 'bg_color': '#fffbed', 'border': True})
        title = workbook.add_format({'bold': True, 'align': 'center', 'font_size': 20, 'bg_color': '#f2eee4', 'border': True})
        header_row_style = workbook.add_format({'bold': True, 'align': 'center', 'border': True})
        book_header = workbook.add_format({'bold': True, 'align': 'center', 'font_size': 10})
        total_base = 0.0 # BASE IMPONIBLE
        total_credit = 0.0 # CREDITO TOTAL
        total_tax = 0.0 # IMPUESTO TOTAL
        total_tax_held = 0.0 # IMPUESTO RETENIDO 
        sheet.merge_range('A1:N1', 'Libro de Compras', title)
        company_information = self.env['res.company'].search([('id','=',1)])
        info = []
        date_f = datetime.strptime(dates[0], '%Y-%m-%d')
        date_t = datetime.strptime(dates[1], '%Y-%m-%d')
        days = date_t.day-(date_f.day)
        period = ''
        if days > 15:
            period = months[date_t.month-1] + ' ' + str(date_t.year)
        else:
            period = 'Desde el ' + str(date_f) + ' hasta el ' + str(date_t)
        for company in company_information:
            info.append({ 'name': company.name, 'rif':company.vat,})
            break
        for obj in info:
            sheet.write(2, 0,   obj['name'], book_header)
            sheet.write(3, 0, obj['rif'], book_header)
            sheet.write(4, 0, period, book_header)
            sheet.write(5, 0, 'De acuerdo al Artículo 76 del Reglamento Ley IVA', book_header)
            break
        for invoice in docs:
            debit_credit_notes = self.env['account.move'].search([('move_type','=','in_refund'),('reversed_entry_id', '=', invoice.id)])
            taxes_vouchers = self.env['tax.withholding_voucher_vendor'].search([('related_invoice', '=', invoice.id)])
            for note in debit_credit_notes:
                book_lines.append({ 'name':note.name, 'period':note.invoice_date, 'rif': note.partner_id.vat, 'customer': note.partner_id.display_name, 'prov_type': 'PJD', 'control_number': 0, 'related_invoice': invoice.name, 'related_debit_note': 0, 'related_credit_note': 0, 'total_amount_with_taxes': note.amount_total, 'untaxed_amount': note.amount_untaxed_signed, 'tax_amount': note.amount_tax, 'tax_amount_held': 0.0, 'advance_payment': 0,})
            if (taxes_vouchers):
                for voucher in taxes_vouchers:
                    book_lines.append({ 'name':invoice.name, 'period':invoice.invoice_date, 'rif': voucher.related_invoice.partner_id.vat, 'customer': voucher.related_invoice.partner_id.display_name, 'prov_type': 'PJD', 'control_number': 0, 'related_invoice': '', 'related_debit_note': 0, 'related_credit_note': 0, 'total_amount_with_taxes': voucher.total_amount, 'untaxed_amount': voucher.untaxed_amount, 'tax_amount': voucher.taxed_amount, 'tax_amount_held': voucher.taxed_amount_held, 'advance_payment': 0,})
            else:
                book_lines.append({ 'name':invoice.name, 'period':invoice.invoice_date, 'rif': invoice.partner_id.vat, 'customer': invoice.partner_id.display_name, 'prov_type': 'PJD', 'control_number': invoice.control_number, 'related_invoice': '', 'related_debit_note': 0, 'related_credit_note': 0, 'total_amount_with_taxes': invoice.amount_total, 'untaxed_amount': invoice.amount_untaxed_signed, 'tax_amount': invoice.amount_tax, 'tax_amount_held': 0.0, 'advance_payment': 0,})
        sorted_book_lines = sorted(book_lines, key=lambda d: d['period'])
        for doc in sorted_book_lines:
            total_base += doc['total_amount_with_taxes']
            total_credit += doc['total_amount_with_taxes']
            total_tax += doc['tax_amount']
            total_tax_held += doc['tax_amount_held']
        sheet.merge_range('K8:O8', 'INTERNAS', header_row_style)
        row = 8
        col = 0
        sheet.set_column(0, 5, 18)
        sheet.write(row, col,   'No Operacion', header_row_style)
        sheet.write(row, col+1, 'Fecha', header_row_style)
        sheet.write(row, col+2, 'RIF', header_row_style)
        sheet.write(row, col+3, 'Nombre o Razon Social.', header_row_style)
        sheet.write(row, col+4, 'Tipo Prov.', header_row_style)
        sheet.write(row, col+5, 'No Documento', header_row_style)
        sheet.write(row, col+6, 'Numero de Control', header_row_style)
        sheet.write(row, col+7, 'No de Factura afectada', header_row_style)
        sheet.write(row, col+8, 'No de Nota de Debito', header_row_style)
        sheet.write(row, col+9, 'No de Nota Credito', header_row_style)
        sheet.write(row, col+10, 'Importe de La factura', header_row_style)
        sheet.write(row, col+11, 'Base Imponible', header_row_style)
        sheet.write(row, col+12, 'Porcentaje de Impuesto', header_row_style)
        sheet.write(row, col+13, 'Total de Impuesto Retenido', header_row_style)
        sheet.write(row, col+14, 'Anticipo de Impuesto', header_row_style)
        row += 1
        operation_number = 1
        for invoice in sorted_book_lines:
            sheet.write(row, col, operation_number)
            sheet.write(row, col+1, invoice['period'].strftime("%m/%d/%Y"))
            sheet.write(row, col+2, invoice['rif'])
            sheet.write(row, col+3, invoice['customer'])
            sheet.write(row, col+4, invoice['prov_type'])
            sheet.write(row, col+5, invoice['name'])
            sheet.write(row, col+6, invoice['control_number'])
            sheet.write(row, col+7, invoice['related_invoice'])
            sheet.write(row, col+8, invoice['related_debit_note'])
            sheet.write(row, col+9, invoice['related_credit_note'])
            sheet.write(row, col+10, invoice['total_amount_with_taxes'])
            sheet.write(row, col+11, invoice['untaxed_amount'])
            sheet.write(row, col+12, invoice['tax_amount'])
            sheet.write(row, col+13, invoice['tax_amount_held'])
            sheet.write(row, col+14, invoice['advance_payment'])
            row += 1
            operation_number += 1
        row += 1
        sheet.write(row , col+2, 'Resumen del Libro de Compra', header_row_style)
        sheet.write(row + 1, col+1, 'TOTAL BASE IMPONIBLE')
        sheet.write(row + 2, col+1, 'TOTAL CREDITO')
        sheet.write(row + 3, col+1, 'TOTAL DE IMPUESTO')
        sheet.write(row + 4, col+1, 'TOTAL IMPUESTO RETENIDO')
        sheet.write(row + 1, col+2, total_base)
        sheet.write(row + 2, col+2, total_credit)
        sheet.write(row + 3, col+2, total_tax)
        sheet.write(row + 4, col+2, total_tax_held)
