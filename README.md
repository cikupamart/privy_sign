Ringkasan Eksekutif Fitur Modul (odoo_privy_cost_control)
Pengendalian Biaya Kuota (Cost Control & Threshold):

Dilengkapi parameter konfigurasi di menu Settings (res.config_settings) untuk menentukan batas minimum nilai transaksi (privy.min_amount).

Validasi otomatis (@api.constrains) pada dokumen komersial untuk menolak penggunaan TTE jika nilainya di bawah ambang batas, mencegah pemborosan kuota berbayar pada dokumen kecil.

Dukungan Multi-Modul Komprehensif:

Customer Invoices (account.move): Penandatanganan sah untuk dokumen penagihan dan pengembalian dana.

Sales Orders (sale.order): Pengamanan surat pesanan/kontrak penjualan sebelum diproses lanjut.

Purchase Orders (purchase.order): Verifikasi perjanjian pembelian barang/jasa dengan vendor.

Manajemen Rantai Penandatangan (Multi-Signer Routing):

Model relasi kustom (privy.document.signer) yang memungkinkan pengaturan urutan (sequence) pihak internal perusahaan dan pihak eksternal (klien/vendor) secara fleksibel langsung dari tab khusus pada form dokumen.

Komunikasi REST API & Webhook Cerdas:

Pengiriman file QWeb PDF secara biner (multipart/form-data) ke endpoint Privy (Sandbox/Production).

Webhook Controller publik (/privy/webhook/callback) yang mendeteksi token dokumen secara global di semua model, otomatis memperbarui status menjadi Signed atau Rejected, serta mengunduh dokumen bertanda tangan resmi ke menu Attachments Odoo secara real-time.

Pelaporan & Analisis Rekapitulasi (Pivot Report):

Database SQL View (privy.usage.report) yang menggabungkan rekapitulasi penggunaan dari seluruh modul ke dalam tampilan Pivot dan Graph interaktif untuk kebutuhan audit manajemen.

Langkah Final Implementasi:
Unggah folder modul ke direktori custom addons server Anda.

Jalankan pembaruan daftar aplikasi (Update Apps List) di Odoo dengan Developer Mode aktif.

Lakukan instalasi modul, masukkan API Key Privy Anda, tetapkan batas minimum threshold, dan modul siap digunakan untuk mengamankan serta menghemat kuota operasional perusahaan!
