import pandas as pd
import random
import re
from collections import namedtuple
from typing import List, Dict, Tuple, Optional
import logging

class IndonesianDataAugmentation:
    def __init__(self, input_files: List[str], output_file: str):
        """
        Inisialisasi class dengan file input dan output.
        
        Args:
            input_files: List path file input CSV
            output_file: Path file output CSV
        """
        self.input_files = input_files
        self.output_file = output_file
        self.data_augmented = []
        self.AugmentPair = namedtuple('AugmentPair', 'src trg')
        
        # Setup logging
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s'
        )
        self.logger = logging.getLogger(__name__)
        
        # Load data dictionaries
        self._load_dictionaries()

    def _load_dictionaries(self):
        """Load semua dictionary yang diperlukan untuk augmentasi."""
        self.common_misspellings = {
            'yang': 'yg',
            'dengan': 'dgn',
            'tidak': 'tdk',
            'untuk': 'utk',
            'bagaimana': 'gmn',
            'sangat': 'sgt',
            'saya': 'sy',
            'bisa': 'bs',
            'juga': 'jg',
            'sudah': 'sdh',
            'akan': 'akn',
            'dari': 'dr',
            'mereka': 'mrk',
            'tentang': 'ttg',
            'kalau': 'klo',
            'sampai': 'smp',
            'karena': 'krn',
            'banyak': 'bnyk',
            'hanya': 'hny',
            'masih': 'msh'
        }
        
        self.keyboard_layout = {
            'q': ['w', 'a'],
            'w': ['q', 'e', 's', 'a'],
            'e': ['w', 'r', 'd', 's'],
            'r': ['e', 't', 'f', 'd'],
            't': ['r', 'y', 'g', 'f'],
            'y': ['t', 'u', 'h', 'g'],
            'u': ['y', 'i', 'j', 'h'],
            'i': ['u', 'o', 'k', 'j'],
            'o': ['i', 'p', 'l', 'k'],
            'p': ['o', 'l'],
            'a': ['q', 'w', 's', 'z'],
            's': ['w', 'e', 'd', 'x', 'z', 'a'],
            'd': ['e', 'r', 'f', 'c', 'x', 's'],
            'f': ['r', 't', 'g', 'v', 'c', 'd'],
            'g': ['t', 'y', 'h', 'b', 'v', 'f'],
            'h': ['y', 'u', 'j', 'n', 'b', 'g'],
            'j': ['u', 'i', 'k', 'm', 'n', 'h'],
            'k': ['i', 'o', 'l', 'm', 'j'],
            'l': ['o', 'p', 'k'],
            'z': ['a', 's', 'x'],
            'x': ['s', 'd', 'c', 'z'],
            'c': ['d', 'f', 'v', 'x'],
            'v': ['f', 'g', 'b', 'c'],
            'b': ['g', 'h', 'n', 'v'],
            'n': ['h', 'j', 'm', 'b'],
            'm': ['j', 'k', 'n']
        }
        
        self.affixes = {
            'prefixes': ['me', 'ber', 'di', 'ter', 'ke', 'pe', 'se'],
            'suffixes': ['kan', 'an', 'i', 'nya']
        }

    def generate_typo(self, word: str, typo_probability: float = 0.3) -> str:
        """
        Menghasilkan typo berdasarkan kedekatan huruf pada keyboard.
        
        Args:
            word: Kata yang akan diberi typo
            typo_probability: Probabilitas terjadinya typo per huruf
            
        Returns:
            Kata dengan kemungkinan typo
        """
        if not word or len(word) < 2:
            return word
            
        result = list(word.lower())
        
        for i in range(len(result)):
            if random.random() < typo_probability and result[i] in self.keyboard_layout:
                typo_type = random.choice(['replace', 'insert', 'delete'])
                
                try:
                    if typo_type == 'replace':
                        nearby_keys = self.keyboard_layout[result[i]]
                        result[i] = random.choice(nearby_keys)
                        
                    elif typo_type == 'insert':
                        nearby_keys = self.keyboard_layout[result[i]]
                        result.insert(i, random.choice(nearby_keys))
                        
                    elif typo_type == 'delete' and len(result) > 1:
                        result.pop(i)
                        break
                except (KeyError, IndexError) as e:
                    self.logger.warning(f"Error generating typo for word '{word}': {str(e)}")
                    continue
        
        # Preserve original capitalization
        if word[0].isupper():
            result[0] = result[0].upper()
            
        return ''.join(result)

    def generate_sentence_typos(self, sentence: str, word_typo_probability: float = 0.4) -> str:
        """
        Menghasilkan typo pada level kalimat.
        
        Args:
            sentence: Kalimat yang akan diberi typo
            word_typo_probability: Probabilitas typo per kata
            
        Returns:
            Kalimat dengan kemungkinan typo
        """
        if not sentence:
            return sentence
            
        words = sentence.split()
        result = []
        
        for word in words:
            if random.random() < word_typo_probability:
                result.append(self.generate_typo(word))
            else:
                result.append(word)
                
        return ' '.join(result)
    
    def misspelling_indonesian(self, sentence: str, prob: float = 0.5) -> str:
        """
        Membuat kesalahan ejaan umum dalam Bahasa Indonesia.
        
        Args:
            sentence: Kalimat input
            prob: Probabilitas modifikasi per kata
            
        Returns:
            Kalimat dengan kesalahan ejaan
        """
        if not sentence:
            return sentence
            
        words = sentence.split()
        modified_words = []
        
        for word in words:
            if random.random() < prob:
                lower_word = word.lower()
                if lower_word in self.common_misspellings:
                    modified_words.append(self.common_misspellings[lower_word])
                elif len(word) > 3:
                    # Remove one vowel randomly
                    modified = re.sub(r'[aiueo]', '', word, count=1)
                    modified_words.append(modified)
                else:
                    modified_words.append(word)
            else:
                modified_words.append(word)
                
        return ' '.join(modified_words)

    def swap_words(self, sentence: str, swap_probability: float = 0.3) -> str:
        """
        Menukar posisi kata yang berdekatan.
        
        Args:
            sentence: Kalimat input
            swap_probability: Probabilitas penukaran
            
        Returns:
            Kalimat dengan kata-kata yang ditukar
        """
        words = sentence.split()
        if len(words) < 2:
            return sentence
            
        for i in range(0, len(words)-1, 2):
            if random.random() < swap_probability:
                words[i], words[i+1] = words[i+1], words[i]
                
        return ' '.join(words)

    def remove_affixes(self, sentence: str) -> str:
        """
        Menghapus imbuhan dari kata-kata.
        
        Args:
            sentence: Kalimat input
            
        Returns:
            Kalimat tanpa imbuhan
        """
        if not sentence:
            return sentence
            
        words = sentence.split()
        modified_words = []
        
        for word in words:
            if len(word) > 4:
                # Remove prefix
                for prefix in self.affixes['prefixes']:
                    if word.startswith(prefix) and len(word) > len(prefix) + 2:
                        word = word[len(prefix):]
                        break
                
                # Remove suffix
                for suffix in self.affixes['suffixes']:
                    if word.endswith(suffix) and len(word) > len(suffix) + 2:
                        word = word[:-len(suffix)]
                        break
                        
            modified_words.append(word)
            
        return ' '.join(modified_words)

    def add_reduplication(self, sentence: str, prob: float = 0.2) -> str:
        """
        Menambahkan reduplikasi pada kata-kata tertentu.
        
        Args:
            sentence: Kalimat input
            prob: Probabilitas reduplikasi per kata
            
        Returns:
            Kalimat dengan reduplikasi
        """
        if not sentence:
            return sentence
            
        words = sentence.split()
        modified_words = []
        
        for word in words:
            if random.random() < prob and len(word) > 3:
                modified_words.append(f"{word}-{word}")
            else:
                modified_words.append(word)
                
        return ' '.join(modified_words)

    def augment_data(self):
        """Melakukan augmentasi data dari file input."""
        try:
            # Read and concatenate all input files
            dfs = []
            for file in self.input_files:
                try:
                    df = pd.read_csv(file)
                    dfs.append(df)
                except Exception as e:
                    self.logger.error(f"Error reading file {file}: {str(e)}")
                    continue
            
            if not dfs:
                raise Exception("No valid input files found")
                
            df = pd.concat(dfs, ignore_index=True)
            
            if 'sentence' not in df.columns:
                raise Exception("Column 'sentence' not found in dataset")

            self.logger.info(f"Processing {len(df)} sentences...")
            
            for sentence in df['sentence']:
                if not isinstance(sentence, str):
                    continue
                    
                # Apply various augmentations
                augmentations = [
                    self.misspelling_indonesian(sentence),
                    self.generate_sentence_typos(sentence),
                    self.swap_words(sentence),
                    self.remove_affixes(sentence),
                    self.add_reduplication(sentence)
                ]
                
                # Add all valid augmentations
                for aug in augmentations:
                    if aug and aug != sentence:
                        self.data_augmented.append(self.AugmentPair(src=aug, trg=sentence))
            
            self.logger.info(f"Generated {len(self.data_augmented)} augmented sentences")
            
        except Exception as e:
            self.logger.error(f"Error in data augmentation: {str(e)}")
            raise

    def save_augmented_data(self):
        """Menyimpan hasil augmentasi ke file output."""
        if not self.data_augmented:
            self.logger.warning("No augmented data to save")
            return
            
        try:
            data_dict = {
                'src': [pair.src for pair in self.data_augmented],
                'trg': [pair.trg for pair in self.data_augmented]
            }
            
            augmented_df = pd.DataFrame(data_dict)
            
            # Remove duplicates
            augmented_df.drop_duplicates(inplace=True)
            
            # Save to CSV
            augmented_df.to_csv(self.output_file, index=False, encoding='utf-8')
            
            self.logger.info(f"Successfully saved {len(augmented_df)} augmented samples to {self.output_file}")
            
        except Exception as e:
            self.logger.error(f"Error saving augmented data: {str(e)}")
            raise

def main():
    INPUT_FILES = [
        "datasets/AcadUNUCorpus/agribisnis_dataset.csv", 
        "datasets/AcadUNUCorpus/akuntansi_dataset.csv", 
        "datasets/AcadUNUCorpus/informatika_dataset.csv",
        "datasets/AcadUNUCorpus/manajemen_dataset.csv",
        "datasets/AcadUNUCorpus/elektro_dataset.csv",
        "datasets/AcadUNUCorpus/komputer_dataset.csv",
        "datasets/AcadUNUCorpus/thp_dataset.csv",
        "datasets/AcadUNUCorpus/farmasi_dataset.csv"
    ]
    OUTPUT_FILE = "/ssd-data1/sq2023/data/acadUNU_augmented8Prodi.csv"

    try:
        augmenter = IndonesianDataAugmentation(INPUT_FILES, OUTPUT_FILE)
        augmenter.augment_data()
        augmenter.save_augmented_data()
    except Exception as e:
        logging.error(f"Program failed: {str(e)}")

if __name__ == "__main__":
    main()