from odoo import fields, models

class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    privy_api_key = fields.Char(
        string='Privy API Key',
        config_parameter='privy.api_key',
        help="Kunci API resmi dari akun dashboard Privy perusahaan Anda."
    )
    privy_environment = fields.Selection([
        ('sandbox', 'Sandbox (Testing)'),
        ('production', 'Production (Live)')
    ], string='Privy Environment', default='sandbox', config_parameter='privy.environment')

    privy_min_amount = fields.Monetary(
        string='Minimum Threshold Nilai Dokumen',
        config_parameter='privy.min_amount',
        currency_field='currency_id',
        help="Batas minimum nominal transaksi. Dokumen di bawah nilai ini akan diblokir dari penggunaan TTE Privy untuk menghemat kuota."
    )
    currency_id = fields.Many2one(
        'res.currency', 
        string='Mata Uang', 
        default=lambda self: self.env.company.currency_id
    )
