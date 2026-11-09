import base64
import requests
import logging
from odoo import models, fields, api
from odoo.exceptions import UserError, ValidationError

_logger = logging.getLogger(__name__)

class AccountMove(models.Model):
    _inherit = 'account.move'

    use_privy_signature = fields.Boolean(
        string='Gunakan TTE Privy', 
        default=False,
        tracking=True,
        help="Centang untuk mengaktifkan tanda tangan elektronik Privy."
    )
    privy_doc_token = fields.Char(string='Privy Document Token', readonly=True, copy=False)
    privy_status = fields.Selection([
        ('draft', 'Belum Dikirim'),
        ('sent', 'Menunggu Tanda Tangan'),
        ('signed', 'Selesai (Signed)'),
        ('rejected', 'Ditolak')
    ], string='Status Privy', default='draft', tracking=True, copy=False)
    
    privy_signer_ids = fields.One2many(
        'privy.document.signer', 
        'res_id', 
        string='Daftar Penandatangan Privy',
        domain=lambda self: [('res_model', '=', self._name)]
    )

    @api.constrains('use_privy_signature', 'amount_total')
    def _check_privy_threshold(self):
        for move in self:
            if move.use_privy_signature and move.move_type in ('out_invoice', 'out_refund'):
                min_amount_param = self.env['ir.config_parameter'].sudo().get_param('privy.min_amount', 0.0)
                min_amount = float(min_amount_param) if min_amount_param else 0.0
                
                if min_amount > 0 and move.amount_total < min_amount:
                    raise ValidationError(
                        f"Penggunaan TTE Privy ditolak!\n"
                        f"Nilai tagihan saat ini ({move.amount_total:,.2f}) berada di bawah "
                        f"batas minimum ketentuan perusahaan ({min_amount:,.2f}) untuk menghemat kuota."
                    )

    def action_send_to_privy(self):
        self.ensure_one()
        if not self.use_privy_signature:
            raise UserError("Fitur Privy tidak diaktifkan untuk dokumen ini.")
        
        if self.privy_status == 'signed':
            raise ValidationError("Dokumen ini sudah bertanda tangan elektronik sah.")

        get_param = self.env['ir.config_parameter'].sudo().get_param
        api_key = get_param('privy.api_key')
        environment = get_param('privy.environment', 'sandbox')
        
        if not api_key:
            raise UserError("API Key Privy belum dikonfigurasi di menu Settings.")

        base_url = "https://app-uat.privy.id/api/v1" if environment == 'sandbox' else "https://api.privy.id/api/v1"
        
        pdf_content, _ = self.env['ir.actions.report']._render_qweb_pdf('account.action_report_invoice', self.ids)
        
        headers = {
            'Authorization': f'Bearer {api_key}',
            'Accept': 'application/json'
        }
        
        files = {
            'document': (f'{self.name.replace("/", "_")}.pdf', pdf_content, 'application/pdf')
        }
        
        signers_payload = []
        for signer in self.privy_signer_ids:
            signers_payload.append({
                'email': signer.email,
                'phone': signer.phone,
                'role': signer.role_type,
                'sequence': signer.sequence
            })

        data = {
            'recipient_email': self.partner_id.email or '',
            'recipient_phone': self.partner_id.phone or self.partner_id.mobile or '',
            'title': f'Tagihan {self.name}'
        }

        try:
            response = requests.post(f"{base_url}/documents/upload", headers=headers, files=files, data=data, timeout=30)
            response_data = response.json()
            
            if response.status_code in [200, 201]:
                doc_token = response_data.get('data', {}).get('document_token') or response_data.get('token') or "PRV-TOKEN-SIMULATED"

                self.write({
                    'privy_status': 'sent',
                    'privy_doc_token': doc_token
                })

                return {
                    'type': 'ir.actions.client',
                    'tag': 'display_notification',
                    'params': {
                        'title': 'Berhasil Terkirim',
                        'message': 'Dokumen berhasil dikirim ke server Privy.',
                        'type': 'success',
                        'sticky': False,
                    }
                }
            else:
                raise UserError(f"Gagal mengirim ke Privy ({response.status_code}): {response.text}")
                
        except requests.exceptions.RequestException as e:
            raise UserError(f"Koneksi ke server Privy gagal: {str(e)}")

    def action_download_signed_document(self):
        self.ensure_one()
        if self.privy_status != 'signed' or not self.privy_doc_token:
            raise UserError("Dokumen belum selesai ditandatangani atau token tidak ditemukan.")

        get_param = self.env['ir.config_parameter'].sudo().get_param
        api_key = get_param('privy.api_key')
        environment = get_param('privy.environment', 'sandbox')
        
        base_url = "https://app-uat.privy.id/api/v1" if environment == 'sandbox' else "https://api.privy.id/api/v1"
        
        headers = {
            'Authorization': f'Bearer {api_key}',
            'Accept': 'application/json'
        }

        download_url = f"{base_url}/documents/{self.privy_doc_token}/download"
        
        try:
            response = requests.get(download_url, headers=headers, timeout=30)
            if response.status_code == 200:
                pdf_binary = response.content
                
                self.env['ir.attachment'].create({
                    'name': f"Signed_Privy_{self.name.replace('/', '_')}.pdf",
                    'type': 'binary',
                    'datas': base64.b64encode(pdf_binary),
                    'res_model': self._name,
                    'res_id': self.id,
                    'mimetype': 'application/pdf',
                })
                
                return {
                    'type': 'ir.actions.client',
                    'tag': 'display_notification',
                    'params': {
                        'title': 'Berhasil',
                        'message': 'Dokumen bertanda tangan Privy berhasil diunduh dan dilampirkan.',
                        'type': 'success',
                        'sticky': False,
                    }
                }
            else:
                raise UserError(f"Gagal mengunduh dari Privy. Respon server: {response.text}")
        except Exception as e:
            raise UserError(f"Terjadi kesalahan koneksi ke API Privy: {str(e)}")

    def action_auto_send_to_privy(self):
        for move in self:
            if move.use_privy_signature and move.privy_status == 'draft' and move.move_type == 'out_invoice':
                try:
                    move.action_send_to_privy()
                except Exception as e:
                    _logger.error(f"Auto-send Privy error for Invoice {move.name}: {str(e)}")
