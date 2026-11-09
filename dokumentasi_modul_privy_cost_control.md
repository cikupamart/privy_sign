# Panduan Fitur & Penggunaan: Privy Digital Signature & Cost Control (Odoo 18)

Modul **`odoo_privy_cost_control`** dirancang khusus untuk mengintegrasikan layanan Tanda Tangan Elektronik (TTE) PrivyID ke dalam ekosistem Odoo 18. Modul ini dilengkapi dengan mekanisme **Pengendalian Biaya (*Cost Control*)** berbasis batasan minimum nilai transaksi (*Threshold*) untuk mencegah pemborosan kuota berbayar pada dokumen bernilai kecil.

---

## 1. Ikhtisar Fitur Utama

1. **Pengendalian Biaya Kuota (*Cost Control Threshold*):**
   * Mencegah staf menggunakan kuota Privy untuk dokumen bernilai kecil di bawah batas minimum yang telah ditentukan oleh perusahaan.
   * Dikonfigurasi secara terpusat melalui menu *Settings*.

2. **Dukungan Multi-Modul Komprehensif:**
   * Terintegrasi penuh pada tiga modul utama Odoo:
     * **Customer Invoices** (`account.move`)
     * **Sales Orders** (`sale.order`)
     * **Purchase Orders** (`purchase.order`)

3. **Manajemen Rantai Penandatangan (*Multi-Signer Routing*):**
   * Memungkinkan penambahan lebih dari satu penandatangan pada dokumen (pihak internal perusahaan dan pihak eksternal/klien/vendor) lengkap dengan pengaturan urutan (`sequence`) dan peran penandatangan.

4. **Otomatisasi Webhook & Sinkronisasi PDF *Real-Time*:**
   * Mendengarkan *callback* dari server Privy secara otomatis.
   * Mengubah status dokumen menjadi *Signed* (Selesai) atau *Rejected* (Ditolak) secara instan tanpa intervensi manual.
   * Mengunduh dan melampirkan file PDF resmi bertanda tangan ke bagian *Attachments* dokumen di Odoo.

5. **Laporan Rekapitulasi & Analisis Pivot (*Privy Usage Report*):**
   * Menyediakan laporan analitik interaktif berbasis SQL View untuk memantau volume penggunaan kuota dan total nilai nominal dokumen yang ditandatangani.

---

## 2. Panduan Konfigurasi Awal (Administrator)

Sebelum modul dapat digunakan oleh tim operasional, administrator harus memasukkan kredensial API dan menetapkan batas minimum nilai transaksi:

1. Masuk ke halaman utama Odoo dengan akun **Administrator**.
2. Buka menu **Invoicing / Accounting > Configuration > Settings**.
3. Gulir ke bagian **Privy Digital Signature & Cost Control**, lalu isi kolom berikut:
   * **Privy API Key:** Masukkan token API resmi yang Anda dapatkan dari portal pengembang Privy.
   * **Privy Environment:** Pilih mode lingkungan, yaitu `Sandbox` (untuk uji coba/pengembangan) atau `Production` (untuk operasional nyata).
   * **Minimum Amount Threshold (Rp):** Masukkan angka batas minimum (contoh: `5000000` untuk Rp 5 Juta). Dokumen dengan total tagihan/pesanan di bawah angka ini akan ditolak sistem jika dicoba untuk ditandatangani menggunakan Privy guna menghemat kuota.
4. Klik tombol **Save** di pojok kiri atas.

---

## 3. Panduan Penggunaan Harian (Operational Usage)

### A. Mengaktifkan & Mengirim Dokumen ke Privy
Langkah-langkah ini berlaku sama untuk modul **Invoice**, **Sales Order**, maupun **Purchase Order**:
1. Buat dokumen baru (*Invoice*, *Sales Order*, atau *Purchase Order*).
2. Isi data produk, kuantitas, harga, dan pilih mitra (*Partner/Customer/Vendor*). Pastikan email dan nomor telepon mitra sudah terisi dengan benar.
3. Pada form dokumen, temukan dan centang opsi **"Gunakan TTE Privy"** (*use_privy_signature*).
   * *Catatan:* Jika total nilai dokumen berada di bawah batas minimum *threshold* yang diatur di *Settings*, Odoo akan memunculkan peringatan (*ValidationError*) dan membatalkan centang tersebut demi efisiensi kuota.
4. Jika diperlukan penandatangan tambahan, buka tab **"Penandatangan Privy"** di bagian bawah form, lalu atur daftar penandatangan internal maupun eksternal beserta urutannya (`sequence`).
5. Simpan dokumen, lalu klik tombol **"Kirim ke Privy"** (*action_send_to_privy* / *action_send_so_to_privy* / *action_send_po_to_privy*) yang berada di bilah aksi atas.
6. Status dokumen akan berubah menjadi **Menunggu Tanda Tangan** (*sent*), dan token dokumen unik dari Privy akan terisi otomatis.

### B. Pembaruan Status Otomatis via Webhook
* Anda tidak perlu mengecek status dokumen secara manual terus-menerus.
* Ketika semua pihak telah menandatangani dokumen melalui aplikasi/portal Privy, server Privy akan mengirimkan sinyal (*callback*) ke URL webhook Odoo Anda (`https://domain-anda.com/privy/webhook/callback`).
* Odoo akan otomatis memperbarui status dokumen menjadi **Selesai (Signed)** dan mengunduh file PDF bertanda tangan resmi ke menu lampiran (*Attachments*) di dokumen tersebut.

### C. Mengakses Laporan & Rekapitulasi Kuota
Untuk memantau penggunaan kuota dan audit transaksi:
1. Pastikan modul laporan telah terpasang.
2. Buka menu **Accounting/Invoicing > Reporting > Laporan Privy** (*Privy Usage Report*).
3. Anda dapat melihat data dalam bentuk **Pivot View** atau **Graph View**, mengelompokkannya berdasarkan tipe dokumen (Invoice, Sales, Purchase), status tanda tangan, atau melihat jumlah total nilai transaksi (*Amount Total*) yang diproses.

---

## 4. Panduan Pemecahan Masalah (*Troubleshooting*)

* **Error: "API Key Privy belum dikonfigurasi"**
  * *Solusi:* Masuk ke menu *Settings*, pastikan Anda sudah mengisi kolom API Key dan menekan tombol *Save*.
* **Error: "Penggunaan TTE Privy pada... ditolak di bawah batas minimum"**
  * *Solusi:* Ini adalah fitur pengaman biaya (*cost control*). Jika dokumen tersebut memang wajib ditandatangani secara elektronik, turunkan nilai *Minimum Amount Threshold* di *Settings* atau tingkatkan nilai transaksi dokumen.
* **Webhook tidak merespons / status tidak berubah otomatis**
  * *Solusi:* Pastikan URL webhook server Odoo Anda dapat diakses secara publik dari internet (memiliki SSL/HTTPS yang valid) dan tidak terhalang oleh *firewall* atau *NAT server local*.