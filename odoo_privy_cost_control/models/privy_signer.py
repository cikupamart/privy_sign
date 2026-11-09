from odoo import models, fields

class PrivyDocumentSigner(models.Model):
    _name = 'privy.document.signer'
    _description = 'Daftar Penandatangan Dokumen Privy'
    _order = 'sequence asc'

    sequence = fields.Integer(string='Urutan', default=1)
    res_model = fields.Char(string='Model Dokumen', required=True)
    res_id = fields.Integer(string='ID Dokumen', required=True)
    
    partner_id = fields.Many2one('res.partner', string='Kontak Penandatangan', required=True)
    name = fields.Char(string='Nama Lengkap', related='partner_id.name', readonly=True)
    email = fields.Char(string='Email Privy', related='partner_id.email', readonly=True)
    phone = fields.Char(string='Nomor Telepon', related='partner_id.phone', readonly=True)
    
    role_type = fields.Selection([
        ('internal', 'Pihak Internal (Perusahaan)'),
        ('external', 'Pihak Eksternal (Klien/Vendor)')
    ], string='Peran', default='external', required=True)
    
    signer_status = fields.Selection([
        ('pending', 'Menunggu'),
        ('signed', 'Sudah Ditandatangani'),
        ('rejected', 'Ditolak')
    ], string='Status Tanda Tangan', default='pending', readonly=True)
