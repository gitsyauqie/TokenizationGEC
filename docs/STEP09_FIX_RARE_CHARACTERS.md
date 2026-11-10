# Perbaikan Step09 — karakter training sangat jarang pada SentencePiece

## Diagnosis dari artefak server

Keempat model SentencePiece memiliki pola yang sama: unknown pada 4 baris train.source dan 6 baris train.target. WordPiece memiliki nol unknown training. Mismatch tanpa unknown bernilai nol pada seluruh enam kondisi. Maka ini bukan bukti pergeseran urutan dataset atau kesalahan decoding umum.

Pemeriksaan corpus training gabungan dan model unduhan menemukan 410 karakter berbeda termasuk spasi. Delapan karakter training tidak memiliki piece karakter dasar pada model SentencePiece yang diperiksa:

| Karakter | Codepoint | Frekuensi dalam gabungan train source+target |
|---|---|---:|
| 𝜺 | U+1D73A | 2 |
| 𝜶 | U+1D736 | 2 |
| 會 | U+6703 | 1 |
| 空 | U+7A7A | 1 |
| ⅳ | U+2173 | 1 |
| ٗ | U+0657 | 1 |
| ₇ | U+2087 | 1 |
| ֩ | U+05A9 | 1 |

Angka 4+6 adalah jumlah baris pada dua stream; jangan dianggap 10 pasangan unik karena ID dapat tumpang tindih.

Konfigurasi tersimpan memang menggunakan character_coverage=1.0 dan identity normalization. Pada kode SentencePiece0.2.0, coverage kumulatif dikonversi ke float sebelum dibandingkan dengan character_coverage. Rasio yang sangat dekat dengan satu dapat membulat menjadi satu sebelum karakter paling jarang dimasukkan. Ini menjelaskan mengapa fitting corpus besar tidak terwakili sepenuhnya walaupun parameter coverage bernilai1.0.

Mekanisme berhasil direproduksi dengan library versi0.2.0 yang sama dan corpus TSV berbobot: karakter langka berubah menjadi unknown pada BPE dan Unigram; menambahkan required_chars mengembalikan karakter dan roundtrip yang tepat. Fixture memakai frekuensi tinggi sebagai reproduksi numerik kecil, bukan training ulang corpus pengguna.

Rujukan: [SentencePiece0.2.0 trainer_interface.cc](https://github.com/google/sentencepiece/blob/v0.2.0/src/trainer_interface.cc#L498-L515). Skrip awal saya terlalu bergantung pada coverage1.0 tanpa memastikan seluruh alfabet training diwajibkan; hal itu sudah diperbaiki.

## Perbaikan kode dan batasnya

prepare_controlled.py kini:

1. Mengambil alfabet secara eksplisit hanya dari retained train.source+target, tanpa karakter valid/test.
2. Menambahkan alfabet tersebut ke required_chars pada trainer SentencePiece dan menyimpan inventory karakter/frekuensinya.
3. Memeriksa setiap karakter wajib memiliki piece setelah fitting; vocabulary tetap tepat5K/20K dan special ID tidak berubah.
4. Tetap menjalankan roundtrip penuh dan menolak unknown training. Tidak mengubah threshold agar status sekadar terlihat lolos.
5. Mendukung --reuse-from untuk memverifikasi hash, menyalin common surface dan menggunakan kembali dua WordPiece yang sudah berhasil. Empat SentencePiece dilatih/di-encode ulang karena memasukkan karakter wajib dapat mengubah vocabulary dan segmentasinya.

Tidak memperbaiki model dengan menambahkan piece setelah training, tidak NFKC atau menghapus karakter, tidak menyalin gold ke input, dan tidak mengubah batas vocabulary. Unknown validasi yang berasal dari karakter di luar training tetap dicatat; tidak harus menjadi nol.

## Satu file diperbarui, satu perintah

Ganti hanya scripts/prepare_controlled.py di server dengan versi lokal terbaru. Folder controlled_pilot_v1 tetap dipertahankan. Jalankan:

```bash
python paper6_revision_20261007/scripts/prepare_controlled.py \
  --audit paper6_revision_20261007/server_results/step01_run01/audit.json \
  --reuse-from paper6_revision_20261007/controlled_pilot_v1 \
  --out paper6_revision_20261007/controlled_pilot_v2
```

Ini CPU saja. WordPiece tidak dilatih ulang. Surface dan artefak WP disalin ke folder hasil baru agar dataset lama tidak ditimpa; karena corpus encoded ikut disalin, perlu ruang disk tambahan. Hash isi WP harus tetap identik. Jangan menghapus v1 sebelum v2 selesai diverifikasi. Bila folder v2 sudah ada, simpan kegagalannya dan pilih nama baru saat menjalankan perbaikan selanjutnya.

Download ringkasan v2 ke server_results/step09_prepare_run02 lokal:

- REPORT.md
- status.json
- data_manifest.json
- tokenizer_manifest.json
- lengths_and_roundtrip.csv
- excluded_ids.csv
- provenance.json

Jika masih BLOCKED, tambahkan roundtrip_examples.json terkait. required_character_inventory.json per SentencePiece tersedia bila perlu diperiksa. Tidak perlu mengunduh ulang seluruh corpus.

Target verifikasi: keenam kondisi mencapai PREPARED_PENDING_LENGTH_AND_UNK_REVIEW, semua unknown training dan mismatch tanpa unknown bernilai nol, data train=1.072.191 dan valid=134.023, dan tidak ada perubahan isi artefak WordPiece.

## Panjang input dan langkah GPU berikutnya

Hasil v1 menunjukkan maksimum3139 token termasuk EOS pada train dan2344 pada valid. Jadi default max-positions1024/2048 tidak cukup untuk mempertahankan semua contoh. Ini menjelaskan mengapa flag skip-invalid sebelumnya tidak boleh dipakai. Setelah v2, hitung ulang maksimum karena tokenizer berubah; shared max-positions4096 merupakan kandidat jika seluruh maksimum tetap di bawahnya, bukan keputusan final sebelum hasil v2.

Setelah pemeriksaan ini lulus, lanjut binarisasi Fairseq dan smoke training pendek pada satu GPU, dengan dictionary bersama dan pengecekan jumlah parameter. Belum menjalankan training model pada putaran perbaikan tokenizer ini.

## Uji yang sudah dilakukan

- Regression berbobot pada SentencePiece asli: bug tereproduksi pada BPE dan Unigram, required_chars memperbaikinya.
- Fixture ketiga tokenizer tetap lulus vocabulary/special IDs/roundtrip karakter yang dikenal dan deteksi Unicode yang tidak dikenal.
- Fixture jalur reuse (trainer berat dimock): hanya empat trainer SP dipanggil, dua artefak WP identik,24 baris ringkasan tersusun, dan perubahan surface menolak reuse sebelum membuat output.

Perbaikan belum dinyatakan berhasil pada corpus server penuh sebelum hasil v2 tersedia.


Hasil v2 sudah diterima dan lolos gate training unknown/roundtrip. Langkah aktif sekarang STEP10_BINARIZE_AND_SMOKE.md; tidak perlu melatih ulang tokenizer lagi.
