# Audit kode Paper 6

Tanggal: 7 Oktober 2026. Sumber lokal: `/Users/syauqiemuhammad/Documents/Claude/Projects/Paper 6/scripts`.

**Batas bukti:** kode yang tersedia diperiksa secara statis dan skrip audit baru diuji dengan fixture kecil. Dataset, checkpoint, log eksekusi lengkap, dan prediksi asli ada di server dan belum diperiksa. Kode menunjukkan risiko/konfigurasi yang direncanakan; log server diperlukan untuk memastikan yang benar-benar dijalankan.

## Temuan yang memengaruhi hasil utama

| ID | Bukti dalam skrip lama | Dampak | Tindakan |
|---|---|---|---|
| A01 | `eval_gen.py:word_f1` dan `bootstrap_ci.py` memakai irisan `set(h.split())`/`set(r.split())` | Urutan dan multiplicity kata hilang; ini bukan edit-based GEC F1 | Labeli hasil lama **word-set overlap F1**, jangan gunakan sebagai metrik utama koreksi |
| A02 | `eval_gen.py:parse_gen` memakai intersection ID T/H; duplikat H menimpa hipotesis sebelumnya | Sampel hilang/duplikat tidak menghentikan scoring | Parser v2 mewajibkan semua S/T/H tepat 0..n-1, satu H per ID |
| A03 | Reference diambil dari T setiap output; BERT WP dilatih lowercase dalam `paper6_sweep_server.sh` | Reference bisa berbeda casing/normalisasi antarsistem | Gunakan raw reference bersama; common lowercase hanya untuk audit legacy dengan label eksplisit |
| A04 | Detokenisasi Unigram lama mengganti `▁` dengan spasi tanpa menghapus spasi antarpiece | Output SentencePiece mentah bisa terpecah salah; output yang sudah decoded bisa baik | Decoder eksplisit per run: `sentencepiece` hanya untuk raw pieces; `text` untuk yang sudah decoded |
| A05 | `m2scorer_simple.py` menggunakan `SequenceMatcher`; annotator alternatives digabung; panjang mismatch hanya warning dan loop `zip` | Tidak ekuivalen algoritma MaxMatch resmi; dapat menghilangkan sampel | Jangan labeli hasilnya M2Scorer. Verifikasi scorer/log Turki lalu hitung ulang dengan scorer resmi/port tervalidasi |
| A06 | Sweep WP menggunakan lowercase; BPE/Unigram tidak; source+target dipakai training tokenizer | Faktor selain algoritma berubah; tidak cocok appendix source-only | Tetapkan normalisasi bersama dan provenance train corpus pada pipeline baru |
| A07 | Sweep memakai `--best-checkpoint-metric bleu`, Moses dan remove-BPE yang berbeda | Tidak cocok klaim checkpoint validation loss; decoding validasi berpotensi memengaruhi checkpoint terpilih | Audit namespace/log, tetapkan protokol seleksi checkpoint baru |
| A08 | Semua sweep memakai `--skip-invalid-size-inputs-valid-test` | Ukuran/easy subset evaluasi bisa berbeda antartokenizer | Generate v2 tidak skip; semua ID wajib ada. Jika gagal panjang, audit batas bersama |
| A09 | `fairseq-preprocess` server tidak memakai `--joined-dictionary`, tidak memakai batas vocab appendix | Ukuran dictionary/model tidak dapat disimpulkan dari nama 5K/10K | Laporkan vocabulary tokenizer, source/target dictionary dan parameter model aktual |
| A10 | 10K berasal dari pipeline lama; kondisi baru dari skrip berbeda | Bukan otomatis sweep terkontrol | Tetapkan status legacy sampai dataset/config cocok; sweep baru mencakup 10K juga |
| A11 | Multi-seed menulis CSV berulang ke folder yang sama; seed tidak disimpan sebagai kolom hasil | File terakhir dapat menimpa run sebelumnya; korelasi bisa memilih run keliru | Manifest memiliki run ID unik termasuk seed; folder run terpisah |
| A12 | `compute_table1.py --word-level` menggabungkan token menjadi string lalu menghitung character edit distance | Opsi bernama word-level tetap character-level | Jangan pakai angka itu sebagai word edit distance; implementasi token edit distance diperlukan saat tabel dibangun ulang |
| A13 | Alignment melewatkan kata jika rekonstruksi tokenizer gagal | Jumlah/identitas kata dapat berbeda per tokenizer | Simpan daftar kata tetap, alasan eksklusi, common support dan coverage per tokenizer |
| A14 | Cabang nasal `_analyze_single` tidak mewajibkan suffix remainder tertutup inventory; `_cluster_bounds` bisa mengembalikan kosong saat invalid | Kandidat boundary dapat diterima tanpa seluruh bentuk terverifikasi | Validasi boundary manual, bukan hanya akurasi stem; revisi algoritma sesudah referensi disepakati |
| A15 | Turkish alignment tetap memakai boundaries saat gabungan surface morpheme tidak sama dengan kata (komentar dan kode) | Offset karakter bisa salah | Tolak/labeli analisis tidak rekonstruabel dan audit sampel |
| A16 | Alignment menggunakan corrected test words | Sah untuk analisis post-hoc, tidak sah sebagai bukti seleksi independen jika dipakai memilih konfigurasi | Seleksi pada dev/reference terpisah; test untuk evaluasi final |
| A17 | IndoBERT encoder tokenizer tetap; decoder berubah; fungsi bernama konversi BPE sebenarnya melatih ulang HF BPE | Menguji decoder tokenization, bukan replikasi identik tokenizer lama; BPE bukan codes lama | Pisahkan sebagai eksperimen tambahan; jangan prioritaskan sebelum benchmark utama sahih |

## Contoh masalah metrik lama

Gold `saya membaca buku` dan prediksi `buku saya membaca` mendapat word-set F1 100%. Gold `saya makan` dan prediksi `saya saya makan` juga mendapat 100%. Exact sentence match keduanya 0%. Ini diuji oleh unit test baru, bukan hanya dugaan.

Exact match pun bukan pengganti tunggal edit-based GEC: koreksi alternatif yang sah dapat tidak sama dengan single reference. Karena itu laporan v2 diberi label **diagnostik**, bukan hasil final publikasi.

## Audit angka tabel naskah

Input di `draft_table_snapshot.csv` ditranskripsi dari naskah yang dikirim pengguna. Hasil dihitung ulang di `results_local/draft_table_audit/`.

| Kelompok | n konfigurasi | Spearman rho dari tabel |
|---|---:|---:|
| BPE | 4 | 1,000000 |
| WP | 4 | 0,200000 |
| Unigram | 4 | 0,800000 |
| BPE + WP gabungan | 8 | 0,714286 |
| Semua | 12 | 0,111888 |

Best–worst semua kondisi: 97,09 − 94,52 = **2,57 pp**, bukan 2,39 pp. Unigram tidak mengungguli BPE pada semua ukuran di Indonesia. WP-5K mengungguli BPE-5K **1,38 pp**, bukan 0,14 pp. Ranking BLEU 10K berbeda dari ranking word-set F1.

Kesimpulan dari angka tabel saja: klaim reliabilitas seleksi F_b dan monotonisitas WP belum didukung. Jangan mengubah angka hasil agar cocok dengan klaim; ubah klaim setelah verifikasi output asli.

## Hal yang belum diketahui

- Ukuran/split asli: appendix 134.025 training vs test bootstrap dengan n sama.
- Apakah split dibuat sebelum atau sesudah synthetic corruption; apakah dokumen/kalimat induk muncul lintas split.
- Apakah semua output lengkap; apakah raw-basic sesuai dengan bin/checkpoint lama.
- Apakah hasil Turki dalam naskah benar memakai `m2scorer_simple.py` atau scorer resmi lain.
- Environment dan namespace sebenarnya untuk kondisi legacy 10K.
- Besar bias angka lama setelah raw reference dan casing disamakan.

## Rujukan teknis yang diperiksa

- [NUS M2Scorer](https://github.com/nusnlp/m2scorer): MaxMatch, alternative annotation sets, input dengan token offsets; repository menyebut rilis resmi 3.2 dan runtime Python 2. Jangan menganggap perintah `pip install m2scorer` menghasilkan implementasi yang identik.
- [Fairseq data utilities](https://github.com/facebookresearch/fairseq/blob/main/fairseq/data/data_utils.py): referensi upstream; versi server tetap harus diperiksa lewat environment/log.

Catatan konteks lama yang perlu diganti: pernyataan dalam `konteks-penelitian.md` bahwa bootstrap cukup menggantikan multi-seed tidak dipakai dalam protokol revisi. Bootstrap sampling test dan variasi training adalah dua sumber ketidakpastian berbeda.
