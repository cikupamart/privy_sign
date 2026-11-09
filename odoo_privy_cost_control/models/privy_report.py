from odoo import models, fields

class PrivyUsageReport(models.Model):
    _name = 'privy.usage.report'
    _description = 'Rekapitulasi Penggunaan Kuota Privy'
    _auto = False
    _order = 'date desc'

    name = fields.Char(string='Nomor Dokumen', readonly=True)
    partner_id = fields.Many2one('res.partner', string='Partner / Klien', readonly=True)
    user_id = fields.Many2one('res.users', string='Sales / Responsible', readonly=True)
    company_id = fields.Many2one('res.company', string='Perusahaan', readonly=True)
    date = fields.Date(string='Tanggal Dokumen', readonly=True)
    amount_total = fields.Monetary(string='Nilai Transaksi', currency_field='currency_id', readonly=True)
    currency_id = fields.Many2one('res.currency', string='Mata Uang', readonly=True)
    
    document_type = fields.Selection([
        ('invoice', 'Customer Invoice'),
        ('sale', 'Sales Order'),
        ('purchase', 'Purchase Order')
    ], string='Tipe Dokumen', readonly=True)
    
    privy_status = fields.Selection([
        ('draft', 'Belum Dikirim'),
        ('sent', 'Menunggu Tanda Tangan'),
        ('signed', 'Selesai (Signed)'),
        ('rejected', 'Ditolak')
    ], string='Status Privy', readonly=True)

    def init(self):
        self.env.cr.execute("""
            CREATE OR REPLACE VIEW privy_usage_report AS (
                SELECT 
                    id AS id,
                    name AS name,
                    partner_id AS partner_id,
                    invoice_user_id AS user_id,
                    company_id AS company_id,
                    invoice_date AS date,
                    amount_total AS amount_total,
                    currency_id AS currency_id,
                    'invoice' AS document_type,
                    privy_status AS privy_status
                FROM account_move
                WHERE use_privy_signature = TRUE AND move_type IN ('out_invoice', 'out_refund')
                
                UNION ALL
                
                SELECT 
                    id + 1000000 AS id,
                    name AS name,
                    partner_id AS partner_id,
                    user_id AS user_id,
                    company_id AS company_id,
                    date_order::date AS date,
                    amount_total AS amount_total,
                    currency_id AS currency_id,
                    'sale' AS document_type,
                    privy_status AS privy_status
                FROM sale_order
                WHERE use_privy_signature = TRUE
                
                UNION ALL
                
                SELECT 
                    id + 2000000 AS id,
                    name AS name,
                    partner_id AS partner_id,
                    user_id AS user_id,
                    company_id AS company_id,
                    date_order::date AS date,
                    amount_total AS amount_total,
                    currency_id AS currency_id,
                    'purchase' AS document_type,
                    privy_status AS privy_status
                FROM purchase_order
                WHERE use_privy_signature = TRUE
            )
""")
