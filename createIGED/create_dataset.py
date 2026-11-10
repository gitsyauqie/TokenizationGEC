import pandas as pd
import re
import nltk
from nltk.tokenize import sent_tokenize

def simple_sentence_tokenize(text):
    """
    Tokenisasi kalimat sederhana berdasarkan kriteria:
    1. Diakhiri dengan titik (.) dan diawali dengan huruf besar.
    2. Diakhiri dengan titik (.) dan diawali dengan angka.
    3. Diakhiri dengan titik dua (:) dan diawali dengan angka.
    """
    # Pola regex untuk mencocokkan akhir kalimat dan awal kalimat baru
    pattern = r'(?<=[.:])\s+(?=(?!Rp\.)\d|[A-Z])'
    
    # Split teks berdasarkan pola
    sentences = re.split(pattern, text)
    
    # Membersihkan hasil split
    sentences = [s.strip() for s in sentences if s.strip()]
    
    return sentences

def clean_sentence(sentence):
    """
    Membersihkan kalimat dari karakter yang tidak diinginkan, dengan mempertahankan elemen penting.
    """
    # Daftar pola untuk dihapus jika ada di awal kalimat
    patterns = [
        r'^BAB V KESIMPULAN DAN SARAN',
        r'^BAB II KAJIAN PUSTAKA LANDASAN TEORI',
        r'^BAB II LANDASAN TEORI DAN TINJAUAN PUSTAKA'
        r'^BAB IV HASIL DAN PEMBAHASAN',
        r'^BAB III METODOLOGI PENELITIAN',
        r'^BAB III METODE PENELITIAN',
        r'^BAB I PENDAHULUAN',
        r'^BAB II TINJAUAN PUSTAKA'
    ]
    combined_pattern = r'|'.join(patterns)
    
    # Hapus pola subheading seperti "17 2.3 Definisi Point" atau "1.4 Tujuan Penelitian"
    sentence = re.sub(r'^\d+\s+\d+\.\d+\s+[^\d]', '', sentence)
    sentence = re.sub(r'^\d+\.\d+\s+[^\d]', '', sentence)
    sentence = re.sub(r'^\d+(\.\d+)*\s+', '', sentence)
    
    # Hapus pola "BAB" tertentu di awal kalimat
    sentence = re.sub(rf'^{combined_pattern}', '', sentence)
    
    # Menghapus tanda baca di awal kalimat, kecuali tanda kutip
    # sentence = re.sub(r'^[^\w"\']+', '', sentence)
    
    # Menghapus tanda petik di awal dan akhir kalimat
    sentence = re.sub(r'^["\']|["\']$', '', sentence)
    
    # Menghapus spasi berlebih
    sentence = re.sub(r'\s+', ' ', sentence).strip()
    
    # Menghapus rangkaian titik yang lebih dari satu, tetapi mempertahankan '...'
    sentence = re.sub(r'(?<!\.)\.{2,}(?!\.)', '.', sentence).strip()
    
    # Memastikan kalimat diakhiri dengan titik, kecuali jika sudah berakhir dengan simbol tertentu
    if sentence and not sentence.endswith(('.', '!', '?')):
        sentence += '.'
    
    return sentence




def is_valid_sentence(sentence):
    """
    Mengecek apakah kalimat valid berdasarkan kriteria tertentu
    """
    # Minimal panjang kalimat (karakter)
    MIN_LENGTH = 20
    
    # Maksimal panjang kalimat (karakter)
    MAX_LENGTH = 1000
    
    # Minimal kata dalam kalimat
    MIN_WORDS = 6
    
    # Hitung jumlah kata
    word_count = len(sentence.split())
    
    # Kriteria validasi
    if len(sentence) < MIN_LENGTH or len(sentence) > MAX_LENGTH:
        return False
    
    if word_count < MIN_WORDS:
        return False
    
    # Pastikan kalimat mengandung huruf
    if not any(c.isalpha() for c in sentence):
        return False
    
    return True

def tokenize_text(text):
    """
    Tokenisasi teks dengan fallback ke metode sederhana
    """
    try:
        # Coba gunakan NLTK
        return sent_tokenize(text)
    except:
        # Jika gagal, gunakan metode sederhana
        return simple_sentence_tokenize(text)

def create_sentence_dataset(input_csv, output_csv):
    """
    Membuat dataset kalimat dari dataset file
    """
    # print("Mendownload resource NLTK yang diperlukan...")
    # download_nltk_resources()
    
    print("Membaca dataset file...")
    df = pd.read_csv(input_csv)
    
    sentences = []
    total_files = len(df)
    
    print("Memproses dan membersihkan kalimat...")
    for idx, row in df.iterrows():
        if idx % 10 == 0:
            print(f"Memproses file {idx+1}/{total_files}")
        
        content = str(row['content'])
        
        # Tokenisasi kalimat dengan fallback
        raw_sentences = tokenize_text(content)
        
        # Proses setiap kalimat
        for sentence in raw_sentences:
            # Bersihkan kalimat
            clean_sent = clean_sentence(sentence)
            
            # Validasi kalimat
            if is_valid_sentence(clean_sent):
                sentences.append({
                    'sentence': clean_sent
                })
    
    print("Membuat DataFrame baru...")
    sentences_df = pd.DataFrame(sentences)
    
    # Menghapus duplikat
    sentences_df.drop_duplicates(subset=['sentence'], inplace=True)
    sentences_df.to_csv(output_csv, index=False, encoding='utf-8')
    
    # Menghitung statistik teks
    total_sentences, total_tokens = analyze_sentence_dataset(sentences_df['sentence'])
    print(f"\nJumlah total kalimat: {total_sentences}")
    print(f"Jumlah total token: {total_tokens}")
    
    return sentences_df

def analyze_sentence_dataset(df):
    """
    Menganalisis dataset kalimat
    """
    # Menghitung statistik panjang kalimat
    df['sentence_length'] = df['sentence'].str.len()
    df['word_count'] = df['sentence'].str.split().str.len()
    
    print("\nAnalisis Dataset:")
    print(f"Rata-rata panjang kalimat (karakter): {df['sentence_length'].mean():.2f}")
    print(f"Rata-rata jumlah kata per kalimat: {df['word_count'].mean():.2f}")
    print(f"Kalimat terpendek: {df['sentence_length'].min()} karakter")
    print(f"Kalimat terpanjang: {df['sentence_length'].max()} karakter")
    
    # Menampilkan beberapa contoh kalimat
    print("\nContoh 5 kalimat dari dataset:")
    for idx, row in df.sample(n=5).iterrows():
        print(f"- {row['sentence']}")

# Contoh penggunaan
if __name__ == "__main__":
    input_csv = "datasets/AcadUNUCorpus/elektro_corpus.csv"  # Dataset file
    output_csv = "datasets/AcadUNUCorpus/elektro_dataset.csv"  # Dataset kalimat
    
    try:
        # Membuat dataset kalimat
        sentences_df = create_sentence_dataset(input_csv, output_csv)
        
        # Menganalisis dataset
        analyze_sentence_dataset(sentences_df)
        
    except Exception as e:
        print(f"Error dalam pemrosesan: {str(e)}")