# Rencana eksperimen Paper 6 — langkah demi langkah

Versi dasar: 2026-10-07 / putaran audit 1.

**Update setelah hasil server diterima:** Tahap 1 selesai dan ditinjau. Gunakan `STEP01_REVIEW_AND_NEXT.md` untuk perintah aktif Tahap 1b dan 2; instruksi di bawah dipertahankan sebagai rencana dasar/historis.

**Jalankan Tahap 1 dahulu, kemudian kirim hasilnya.** Tahap 2 sudah memiliki kode, tetapi manifest perlu disesuaikan berdasarkan inventaris Tahap 1. Tahap 3–8 adalah rencana bersyarat; kode training/scorer final akan disiapkan pada putaran berikutnya setelah data dan environment jelas. Tidak ada eksperimen server baru yang sudah selesai pada dokumen ini.

## Prinsip keputusan

- Tidak menggunakan test untuk memilih tokenizer, seed, checkpoint, atau mengubah hipotesis demi meningkatkan hasil.
- Karena test lama sudah diperiksa berkali-kali, klaim konfirmatori baru idealnya memerlukan external/natural holdout yang belum dipakai. Analisis test lama diberi label retrospektif.
- Simpan semua seed yang dijadwalkan, termasuk yang rendah; run gagal dicatat dan hanya diulang dengan alasan teknis yang tercatat.
- Perubahan protokol menghasilkan versi eksperimen baru. Jangan mencampur angka legacy dan rerun sebagai satu sweep terkontrol.
- Kriteria sukses adalah evaluasi yang benar, stabilitas yang diketahui, dan kesimpulan sesuai data; tidak ada target F1 atau p-value wajib.

## Tahap 0 — salin paket ke server dan uji singkat

Environment dan path dikonfirmasi pengguna:

```text
environment: fairseq
host yang digunakan pengguna: amax
base: /ssd-data1/sq2023/DidugaCASTLE_asli_n_paper6
project: /ssd-data1/sq2023/DidugaCASTLE_asli_n_paper6/Paper6
raw: /ssd-data1/sq2023/DidugaCASTLE_asli_n_paper6/raw-basic
```

Salin **seluruh folder `paper6_revision_20261007`** ke dalam folder `Paper6` di server memakai metode transfer yang biasa Anda gunakan. Tidak perlu menimpa folder `scripts` lama. Hasil akhirnya harus:

```text
Paper6/paper6_revision_20261007/scripts/audit_server.py
Paper6/paper6_revision_20261007/EXPERIMENT_PLAN.md
```

Di server:

```bash
conda activate fairseq
cd /ssd-data1/sq2023/DidugaCASTLE_asli_n_paper6/Paper6
python --version
python -m unittest discover -s paper6_revision_20261007/tests -v
```

Lulus jika seluruh test sukses. Python minimal 3.8. Tidak perlu `pip install` untuk audit. Jika gagal, kirim output lengkap, jangan ubah paket environment dulu.

## Tahap 1 — audit data, environment, dan artefak (CPU)

Perintah pertama yang perlu Anda jalankan:

```bash
cd /ssd-data1/sq2023/DidugaCASTLE_asli_n_paper6/Paper6
python paper6_revision_20261007/scripts/audit_server.py \
  --project /ssd-data1/sq2023/DidugaCASTLE_asli_n_paper6/Paper6 \
  --raw /ssd-data1/sq2023/DidugaCASTLE_asli_n_paper6/raw-basic \
  --src-ext source --tgt-ext target --valid-name valid \
  --out paper6_revision_20261007/server_results/step01_run01
```

Skrip membaca dataset dan log; tidak memuat checkpoint ke GPU. Untuk korpus jutaan baris, hash sets dapat memakai ratusan MB sampai beberapa GB RAM dan pemindaian log bisa memerlukan beberapa menit. Penanda `Auditing split ...` menunjukkan kemajuan. Tidak ada estimasi waktu training yang diasumsikan.

Jika file bernama `dev.*` dan bukan `valid.*`, gunakan `--valid-name dev`. Jika ekstensi berbeda, sesuaikan dua argumen ekstensi. Jangan menyalin sembarang target dari pipeline lain hanya agar file tersedia; pasangan sumber/target harus dibuktikan cocok seluruhnya.

Output utama:

```text
server_results/step01_run01/
  REPORT.md
  audit.json
  environment.json
  inventory.json
  legacy_evidence.json
  legacy_evidence/
```

**Kirim kembali:** lima file `.md/.json` di atas dan, jika tersedia, `legacy_evidence/evaluate_model_new.py` serta `legacy_evidence/combine_dataset_for_fairseq.py`. Tidak perlu mengirim checkpoint atau seluruh dataset. Audit tidak mengekspor kalimat mentah, tetapi memuat path dan cuplikan konfigurasi log.

Yang akan kita putuskan dari hasil ini:

1. Ukuran train/valid/test aktual dan data yang benar-benar digunakan.
2. Adakah source, target bersih, atau pair yang sama lintas split.
3. Apakah semua output punya jumlah S/T/H konsisten; parser Tahap 2 memeriksa ID secara lebih ketat.
4. Format output per run: BPE mentah, WP mentah, SentencePiece mentah, atau sudah decoded.
5. Legacy 10K/checkpoint masih ada atau perlu digenerate ulang.
6. Normalisasi dan pemilihan checkpoint lama yang benar-benar tampak dalam log.

**Gate:** baris tidak selaras/blank adalah blocker. Overlap target/group harus ditinjau sebelum rerun. Nol exact overlap tidak membuktikan nol near-duplicate/document leakage. Jika tersedia, tambahkan `train.group_id`, `valid.group_id`, `test.group_id` yang masing-masing berisi ID dokumen/kalimat induk per baris; jangan membuat ID asal palsu dari nomor baris. Tanpa provenance, klaim independensi split tetap belum terverifikasi.

Status `REVIEW REQUIRED` berarti audit selesai, bukan izin otomatis untuk training. Exit code 2 tetap menghasilkan laporan apabila ditemukan kesalahan data; kirim laporan itu apa adanya.

## Tahap 2 — evaluasi ulang prediksi lama (CPU; setelah manifest ditetapkan)

Tujuan: menilai seberapa besar metrik lama terdorong copy behavior dan apakah raw reference sama untuk setiap kondisi. Tidak perlu training ulang untuk mengetahui ini.

Salin `manifest.example.json` menjadi `manifest_legacy_run01.json` di folder paket, lalu isi semua run yang benar-benar ada. Path relatif dihitung dari folder manifest, bukan current working directory. Setiap run wajib memiliki ID berbeda, termasuk seed.

Decoder harus ditetapkan dari bukti output/generation flags:

| `decoder` | Bentuk input yang diharapkan | Catatan |
|---|---|---|
| `bpe` | `mem@@ beri@@ kan` | Hapus separator subword-nmt |
| `wordpiece` | `mem ##beri ##kan` | Gabungkan continuation; punctuation dinilai dengan aturan bersama |
| `sentencepiece` | `▁mem beri kan ▁buku` | Gabungkan pieces dahulu, lalu ubah `▁` menjadi spasi |
| `text` | `memberikan buku` | Hanya untuk output yang sudah decoded |

**Jangan memakai `sentencepiece` pada teks yang sudah decoded:** seluruh spasi akan hilang. Jika marker WordPiece sudah dibuang sehingga menjadi `kadın a`, batas kata asli tidak bisa dipulihkan dengan aman; regenerasi dari checkpoint.

Manifest contoh memakai `case: lower` untuk diagnosis legacy karena WP lama lowercases. Kebijakan itu berlaku pada **semua** source, reference, hypothesis dan baseline, dan akan dicatat. Hasil ini bukan replikasi identik angka lama serta bukan evaluasi case-sensitive final. Rerun utama nanti memakai common normalization yang diputuskan di Tahap 4.

```bash
python paper6_revision_20261007/scripts/eval_gen_v2.py \
  --manifest paper6_revision_20261007/manifest_legacy_run01.json \
  --out paper6_revision_20261007/server_results/step02_run01
```

Parser baru menolak ID hilang/ekstra/duplikat. Semua S/T setelah decoding dan canonical tokenization harus sama dengan raw source/target pada ID yang sama. Canonical tokenization memisahkan word/punctuation secara Unicode dan konsisten untuk semua kondisi; ini khusus diagnostik, **bukan** tokenisasi resmi M2/GECTurk. Mismatch menghasilkan `BLOCKED`, bukan mengurangi sampel diam-diam. Unknown token pada S/T juga dapat memblokir; itu bukti yang perlu diperiksa, bukan alasan mengganti raw gold dengan T yang rusak.

Output:

- `REPORT.md`, `diagnostics.csv`, `subcategory_diagnostics.csv`.
- `run_status.json`, `provenance.json`, `manifest_used.json`.
- Per run yang lolos: `hyp.decoded.txt` dan `hyp.canonical.txt` untuk pemrosesan berikutnya.
- Dua baseline otomatis: `COPY_INPUT` dan `REFERENCE_ORACLE_SANITY`. Oracle hanya tes jalur evaluasi, bukan model pembanding.

Metrik diagnostik: legacy word-set F1, exact sentence match, persentase kalimat diubah, overcorrection pada kalimat bersih, exact correction pada kalimat bermasalah. Jika denominator kategori bersih kosong, nilainya kosong/null, bukan 0% palsu.

**Kirim kembali:** REPORT, kedua CSV, run_status, provenance, dan manifest. Jangan membuat kesimpulan paper dari ranking ini sebelum scorer utama divalidasi.

### Tahap 2b — hanya jika perlu: regenerate dari checkpoint (GPU inference)

Contoh untuk WP-5K Indonesia, setelah memastikan path checkpoint ada:

```bash
GPU=0 bash paper6_revision_20261007/scripts/regenerate_raw.sh \
  tokensweep/bin_wp_5k \
  tokensweep/ckpt_wp_5k/checkpoint_best.pt \
  test \
  paper6_revision_20261007/server_results/regenerated/wp_5k_seed42.raw.out
```

Pilih GPU yang tersedia sesuai aturan sekolah. Ini inference, bukan training. Tidak menggunakan `--remove-bpe`, tidak melewatkan contoh panjang, dan meminta satu hypothesis per ID. Jika ukuran kalimat tidak didukung, proses harus gagal dan kita meninjau batas input bersama. Jangan mengaktifkan skip untuk membuat proses terlihat sukses.

Output parsial jika gagal harus dicatat sebagai FAILED dan tidak diskor; gunakan nama output baru untuk retry. Inferensi lama dengan checkpoint yang dipilih menggunakan validasi keliru tidak memperbaiki pemilihan checkpoint tersebut; statusnya tetap legacy.

Untuk Turki, gunakan path bin/checkpoint hasil inventaris, bukan menebak. Pertahankan tokenisasi source M2 asli ketika scorer resmi akhirnya dijalankan; `hyp.canonical.txt` audit tidak otomatis cocok dengan offset gold M2.

## Tahap 3 — tetapkan scorer utama dan anotasi edit

**Belum dijalankan; perlu hasil Tahap 1–2.**

Indonesia:

1. Cari metadata edit dari synthetic generator (span source, replacement, category, parent ID). Ini lebih kuat daripada menebak gold edits dari pasangan akhir.
2. Jika gold edit tidak tersedia, buat alignment source–target deterministik dan dokumentasikan sebagai silver edits. Jangan menyebutnya gold manusia. Anotasi/validasi manual sampel dan cek pemulihan target dari edits.
3. Gunakan scorer edit berbasis MaxMatch yang versi/commit-nya dipin, dengan tokenisasi kata bersama yang kompatibel dengan offset. Jangan menerapkan ERRANT Inggris tanpa adaptasi/validasi Indonesia.
4. Tes: source-copy, target oracle, insertion, deletion, substitution, repeated words, noop, alternative annotators, panjang mismatch. Verifikasi terhadap contoh resmi scorer; port Python 3 harus lolos parity fixtures sebelum dipakai.
5. Laporan utama: edit P/R/F0.5; tambahkan F1 edit bila relevan, exact match dan metrik overlap sekunder dengan definisi jelas. Jangan membandingkan F1 set lama langsung dengan F0.5 baru.

Turki: gunakan M2 yang disediakan dataset dan scorer resmi/port tervalidasi. Semua model termasuk WP harus punya surface output yang dapat dievaluasi pada tokenisasi yang sama. Jika hanya formatting pipeline yang gagal, perbaiki pipeline; jangan mengecualikan keluarga tokenizer berdasarkan ranking.

Kode yang akan disiapkan sesudah hasil server: exporter/validator edit, wrapper scorer dengan provenance, evaluasi semua run dan kategori. Tidak ada dependensi baru yang diinstal sebelum runtime server diketahui.

**Gate:** scorer valid pada fixtures dan sampel nyata; tidak ada silent dropping; raw gold tetap sama; copy dan oracle berperilaku sesuai definisi. Baru kemudian putuskan kebutuhan retraining.

## Tahap 4 — bekukan protokol rerun terkontrol

Rancangan awal (akan difinalkan dari audit):

- Bahasa utama Indonesia; BPE, WP, Unigram × 5K/10K/20K/30K. Semua kondisi termasuk 10K dibuat dengan protokol baru yang sama.
- Tokenizer dilatih hanya dari train split; boleh source+target asalkan **sama untuk semua** dan dinyatakan di paper. Dev/test tidak masuk pelatihan tokenizer.
- Normalisasi bersama: preserve case/diacritics untuk semua sebagai pilihan awal. Semua perubahan Unicode/whitespace harus eksplisit. Jika lowercase dipakai, terapkan identik dan jelaskan ruang lingkup.
- Ukuran BPE merge bukan vocabulary aktual. Catat merge budget dan vocabulary aktual, dictionary source/target, OOV, panjang sequence, truncation, parameter embedding/backbone/total.
- Backbone sama; parameter total berubah bersama vocabulary dan dilaporkan. Jangan mengklaim parameter total identik bila tidak demikian. Jika klaim kausal murni diperlukan, tambah kontrol kapasitas yang dirancang terpisah.
- Data/group split sudah diaudit. Jika harus membuat split baru, simpan versi lama dan mapping/provenance baru; jangan mencampur hasil dua split.
- Pilihan checkpoint awal: minimum validation loss **di dalam run yang sama**; loss antar-tokenizer tidak dipakai untuk memilih tokenizer. Hindari jalur BLEU detokenization lama. Jika memilih edit F0.5 pada dev, semua kondisi harus menggunakan scorer yang sudah lolos Tahap 3.
- Tetapkan budget optimizer updates atau sentence exposure dengan alasan eksplisit. Max-tokens sama tidak menjamin jumlah kalimat/update sama; log keduanya. Tentukan gradient accumulation/OOM policy sebelum full sweep.
- Pilih seed **13, 42, 87** sebagai set awal tetap. Jangan memilih best seed. Seed tokenizer dipisahkan dari seed model; tokenizer disimpan dan digunakan ulang untuk ketiga seed model.
- Simpan manifest, hash data/tokenizer, command/namespace, versi environment, jumlah update, waktu training, memory, dan konfigurasi decoding setiap run.
- Checkpoint/output ke folder versi baru, bukan `tokensweep/ckpt_*` lama. Tidak menghapus optimizer state jika resume diperlukan.

Pilot: BPE-5K, WP-5K, Unigram-5K seed 42, hanya pada data development/smoke subset yang ditetapkan. Pilot untuk memverifikasi alur dan biaya; jangan masuk tabel final jika budget berbeda. Setelah pilot teknis lulus, full sweep **36 run** (12 kondisi × 3 seed). Jika compute terbatas, tetapkan ruang lingkup lebih kecil di muka; jangan mengklaim robustness seluruh sweep dari dua ekstrem saja.

Kode training v2 akan disiapkan setelah scorer dan environment jelas. Tidak menjalankan skrip multiseed lama sekarang.

## Tahap 5 — validasi F_b, seleksi, dan input rusak

1. Buat reference boundary dari dev atau resource terpisah. Tetapkan konvensi surface boundaries untuk nasal assimilation/reduplication/circumfix dan posisi karakter Unicode.
2. Buat sampel validasi manual **boundary**, bukan hanya stem, dengan cakupan kasus mudah/sulit dan exclusion reason. Idealnya dua anotator; catat kesepakatan sebelum adjudication.
3. Bekukan word list, token/type weighting, P/R/F macro vs micro, aturan zero boundaries dan reconstruction failures.
4. Semua tokenizer dinilai pada common support yang sama. Laporkan coverage tiap tokenizer dan sensitivity terhadap excluded words; jangan hanya membandingkan mean dari himpunan berbeda.
5. Laporkan korelasi per keluarga dan pooled secara terpisah. Dengan empat ukuran per keluarga, hasil tetap eksploratif. Periksa pengaruh vocabulary size/sequence length; jangan menganggap pooled correlation sebagai sebab morfologis.
6. Uji seleksi F_b terhadap baseline `always 5K`, `always 10K`, serta fitur murah seperti fertility/compression/OOV. Definisikan tie-breaking dan regret terlebih dahulu.
7. Pilih kandidat menggunakan dev/reference terpisah, evaluasi pilihan di held-out data. Analisis oracle seluruh sweep test hanya diagnostik retrospektif, bukan aturan pemilihan deploy.
8. Jika mempertahankan hipotesis robust pada corrupt input, ukur segmentation changes pada pasangan bersih–rusak, unknown rate, fragmentasi dan contoh koreksi aktual. Jangan menjadikan contoh token saja sebagai bukti kausal.

Kode tahap ini: frozen boundary exporter, annotation sheet, strict reconstruction checker, common-support evaluation, correlation dan selection-regret analysis. Ditulis setelah referensi/protokol disepakati dari hasil awal.

## Tahap 6 — multi-seed dan ketidakpastian

- Laporkan mean ± sample SD atas seed model untuk setiap kondisi; tetap simpan hasil individual.
- Gunakan paired bootstrap dengan unit yang sama antar-model untuk beda skor, menghitung ulang agregat TP/FP/FN tiap resample.
- Jika banyak varian synthetic berasal dari parent yang sama, gunakan cluster bootstrap berdasarkan parent/document bila provenance tersedia.
- Bootstrap test tidak menggantikan variasi training. Tiga seed bukan 36 titik independen untuk korelasi F_b dari 12 tokenizer.
- Tentukan perbandingan utama di awal, laporkan efek dan interval; jika banyak uji, jelaskan koreksi multiplicity. Jangan mengambil CI paling menguntungkan.

## Tahap 7 — generalisasi dan analisis error

- Perbaiki pipeline Turki dan masukkan WP. Skor ulang legacy dulu, baru rerun yang diperlukan.
- Prioritaskan external/natural learner holdout yang tidak pernah dipakai memilih tokenizer. Audit domain, overlap dan kualitas anotasi.
- Bandingkan perubahan per kategori, tetapi hindari menyebut 11,41 pp sebagai fakta baru sebelum scorer edit dan seluruh sweep dihitung ulang.
- IndoBERT/ByT5 opsional sesudah inti valid. IndoBERT lama hanya mengubah decoder tokenization; perlu ditulis demikian dan BPE-nya tidak boleh diklaim sama jika dilatih ulang dengan library lain.
- Dua bahasa memberi bukti terbatas pada dua setting; tidak membuktikan semua bahasa aglutinatif.

## Tahap 8 — penulisan dan kesiapan submit

- Semua tabel/figure/angka abstrak berasal dari satu hasil machine-readable final, bukan copy-paste manual.
- Metode menyatakan scorer, tokenization, normalization, split, seed, checkpoint rule, parameter dan compute yang benar-benar digunakan.
- Posisi ilmiah mengikuti hasil. Jika F_b gagal memilih tokenizer terbaik, laporkan batasnya sebagai temuan.
- Pisahkan kontribusi paper ini dari CASTLE: reuse dataset/model dijelaskan; tidak membuat klaim lima kali architectural gain dari dua protokol berbeda.
- Reproducibility package, availability/license data, anotasi dan keterbatasan sudah jelas.
- Tidak ada mismatch data/prediksi, tidak ada hasil legacy yang diam-diam masuk mean rerun, dan semua error audit ditutup dengan bukti.
- Pilihan jurnal final dilakukan setelah kontribusi stabil. Catatan lama menyebut kebutuhan Q1/non-APC; status kebutuhan itu dan kebijakan jurnal perlu dikonfirmasi kembali saat pemilihan, bukan diasumsikan dari rekomendasi sebelumnya.

## Format setiap hasil yang dikirim kembali

Kirim folder laporan kecil atau file yang disebut pada tiap tahap, disertai:

```text
Tahap/run:
Perintah yang dijalankan:
Environment:
Status selesai/gagal:
Perubahan path/argumen dari panduan:
Nama file hasil:
Jika gagal: traceback lengkap / bagian akhir log:
```

Saya akan mencatat temuan pada `EXPERIMENT_LOG.md`, memperbarui keputusan, dan menyiapkan kode tahap berikutnya. Setiap angka ditandai apakah hasil lokal sintetis, hasil server asli, atau hanya angka dari naskah lama.
