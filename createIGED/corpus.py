import os
import pandas as pd
import pdfplumber
from pathlib import Path
import re
from collections import defaultdict


def clean_text(text):
    """
    Membersihkan teks dari karakter yang tidak valid
    """
    if not isinstance(text, str):
        return ""
    
    # Menghapus karakter surrogate
    text = text.encode('utf-8', 'ignore').decode('utf-8')
    
    # Menghapus karakter kontrol kecuali newline dan tab
    text = ''.join(char for char in text if char == '\n' or char == '\t' or char.isprintable())
    
    # Mengganti multiple spaces dan newlines dengan single
    text = re.sub(r'\s+', ' ', text)
    
    return text.strip()

def remove_table_text(text, tables):
    """
    Menghapus teks tabel dari teks halaman
    """
    for table in tables:
        # Gabungkan teks di tabel menjadi satu string
        table_text = " ".join([" ".join(str(cell) if cell is not None else "" for cell in row) for row in table])
        # Gantikan teks tabel di teks halaman
        text = text.replace(table_text, "")
    return text

def extract_text_from_pdf(pdf_path):
    """
    Mengekstrak teks dari file PDF dengan mengabaikan tabel
    """
    try:
        text = ""
        # Menggunakan pdfplumber untuk deteksi dan penghapusan tabel
        with pdfplumber.open(pdf_path) as pdf:
            for page in pdf.pages:
                try:
                    # Ekstrak teks dan tabel
                    page_text = page.extract_text()
                    page_tables = page.extract_tables()

                    # Jika ada tabel, hapus teks tabel
                    if page_tables:
                        page_text = remove_table_text(page_text, page_tables)

                    text += clean_text(page_text) + " "
                except Exception as e:
                    print(f"Error extracting text from page in {pdf_path}: {str(e)}")
                    continue
        return clean_text(text)
    except Exception as e:
        print(f"Error reading {pdf_path}: {str(e)}")
        return ""

def find_pdf_files(root_folder):
    """
    Mencari semua file PDF dalam folder dan subfolder
    """
    pdf_files = []
    for root, dirs, files in os.walk(root_folder):
        for file in files:
            if file.lower().endswith('.pdf'):
                full_path = os.path.join(root, file)
                pdf_files.append({
                    'filename': file,
                    'folder': os.path.relpath(root, root_folder),
                    'full_path': full_path
                })
    return pdf_files

def save_to_csv_chunks(df, output_csv, chunk_size=100):
    """
    Menyimpan DataFrame ke CSV dalam chunks dengan mode append
    """
    try:
        file_exists = os.path.isfile(output_csv)
        
        for i in range(0, len(df), chunk_size):
            chunk = df.iloc[i:i + chunk_size]
            
            if file_exists:
                chunk.to_csv(output_csv, mode='a', header=False, index=False, encoding='utf-8', errors='ignore')
            else:
                chunk.to_csv(output_csv, mode='w', header=True, index=False, encoding='utf-8', errors='ignore')
                file_exists = True
                
    except Exception as e:
        print(f"Error saving with UTF-8, trying with different encoding: {str(e)}")
        try:
            for i in range(0, len(df), chunk_size):
                chunk = df.iloc[i:i + chunk_size]
                if not file_exists:
                    chunk.to_csv(output_csv, mode='w', header=True, index=False, encoding='ascii', errors='ignore')
                    file_exists = True
                else:
                    chunk.to_csv(output_csv, mode='a', header=False, index=False, encoding='ascii', errors='ignore')
        except Exception as e:
            print(f"Failed to save CSV: {str(e)}")
            raise

def create_dataset(root_folder, output_csv):
    """
    Membuat atau menambahkan ke dataset dari file PDF
    """
    pdf_files = find_pdf_files(root_folder)
    dataset = []
    folder_counts = defaultdict(int) 
    
    total_files = len(pdf_files)
    for idx, pdf_file in enumerate(pdf_files, 1):
        print(f"Processing {idx}/{total_files}: {pdf_file['filename']}")
        
        # Ekstrak teks dari PDF dengan mengabaikan tabel
        text_content = extract_text_from_pdf(pdf_file['full_path'])
        
        dataset.append({
            'content': text_content
        })
        
        folder_counts[pdf_file['folder']] += 1

        # Menyimpan progress setiap 10 file
        if idx % 10 == 0:
            temp_df = pd.DataFrame(dataset)
            save_to_csv_chunks(temp_df, output_csv)
            dataset = []  # Clear memory
    
    # Menyimpan sisa file
    if dataset:
        temp_df = pd.DataFrame(dataset)
        save_to_csv_chunks(temp_df, output_csv)
    
    print(f"\nDataset berhasil ditambahkan ke {output_csv}")
    # Menampilkan jumlah dokumen per folder
    print("\nJumlah dokumen per folder:")
    for folder, count in sorted(folder_counts.items()):
        print(f"{folder}: {count} dokumen")
    
    print(f"\nTotal folder: {len(folder_counts)}")
    print(f"Total keseluruhan dokumen: {sum(folder_counts.values())}")
    return pd.read_csv(output_csv, encoding='utf-8')

# Contoh penggunaan
if __name__ == "__main__":
    root_folder = "/ssd-data1/sq2023/datasets/AcadUNUCorpus/THP"  # Sesuaikan dengan path folder Anda
    output_csv = "/ssd-data1/sq2023/datasets/AcadUNUCorpus/thp_corpus.csv"
    
    try:
        df = create_dataset(root_folder, output_csv)
    except Exception as e:
        print(f"Error dalam pemrosesan: {str(e)}")