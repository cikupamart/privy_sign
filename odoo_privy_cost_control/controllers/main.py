import logging
from odoo import http
from odoo.http import request

_logger = logging.getLogger(__name__)

class PrivyWebhookController(http.Controller):

    @http.route('/privy/webhook/callback', type='json', auth='public', methods=['POST'], csrf=False)
    def privy_webhook_listener(self, **kw):
        data = request.json_request or {}
        _logger.info(f"Privy Webhook Payload diterima: {data}")

        doc_token = data.get('document_token') or data.get('token')
        status = data.get('status')

        if not doc_token or not status:
            return {'status': 'error', 'message': 'Invalid payload: missing token or status'}

        # 1. Cek Invoice
        invoice = request.env['account.move'].sudo().search([('privy_doc_token', '=', doc_token)], limit=1)
        if invoice:
            if status == 'signed':
                invoice.write({'privy_status': 'signed'})
                try: invoice.action_download_signed_document()
                except Exception as e: _logger.error(f"Gagal unduh PDF Invoice: {str(e)}")
            elif status == 'rejected':
                invoice.write({'privy_status': 'rejected'})
            return {'status': 'success', 'message': 'Invoice webhook processed'}

        # 2. Cek Sales Order
        sale_order = request.env['sale.order'].sudo().search([('privy_doc_token', '=', doc_token)], limit=1)
        if sale_order:
            if status == 'signed':
                sale_order.write({'privy_status': 'signed'})
                try: sale_order.action_download_signed_so()
                except Exception as e: _logger.error(f"Gagal unduh PDF Sales Order: {str(e)}")
            elif status == 'rejected':
                sale_order.write({'privy_status': 'rejected'})
            return {'status': 'success', 'message': 'Sales Order webhook processed'}

        # 3. Cek Purchase Order
        purchase_order = request.env['purchase.order'].sudo().search([('privy_doc_token', '=', doc_token)], limit=1)
        if purchase_order:
            if status == 'signed':
                purchase_order.write({'privy_status': 'signed'})
                try: purchase_order.action_download_signed_po()
                except Exception as e: _logger.error(f"Gagal unduh PDF Purchase Order: {str(e)}")
            elif status == 'rejected':
                purchase_order.write({'privy_status': 'rejected'})
            return {'status': 'success', 'message': 'Purchase Order webhook processed'}

        _logger.warning(f"Privy Webhook: Document token {doc_token} tidak ditemukan pada modul manapun di Odoo.")
        return {'status': 'error', 'message': 'Document token not found in Odoo'}
