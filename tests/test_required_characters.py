"""Regression for SentencePiece 0.2.0 float coverage rounding on rare characters."""
import sys,tempfile,unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'scripts'))
import sentencepiece as sp
from prepare_controlled import training_alphabet

class RequiredCharacters(unittest.TestCase):
    def test_training_alphabet_only(self):
        with tempfile.TemporaryDirectory() as td:
            p=Path(td)/'train';p.write_text('a 𝜺\na\n')
            chars,counts=training_alphabet(p)
            self.assertEqual(set(chars),{'a','𝜺'})
            self.assertEqual(counts['a'],2)
            self.assertNotIn('🦉',chars)

    def test_rare_character_rounding_and_fix(self):
        with tempfile.TemporaryDirectory() as td:
            p=Path(td);text='kalimat umum untuk penelitian bahasa indonesia .'
            weighted=p/'weighted.tsv';weighted.write_text(text+'\t100000000\n𝜺\t1\n')
            required=''.join(sorted(set(text+'𝜺')-{' '}))
            for family in ('bpe','unigram'):
                for fixed in (False,True):
                    prefix=str(p/(family+str(fixed)))
                    sp.SentencePieceTrainer.train(input=str(weighted),input_format='tsv',model_prefix=prefix,
                        model_type=family,vocab_size=40,hard_vocab_limit=False,character_coverage=1.0,
                        normalization_rule_name='identity',num_threads=1,required_chars=required if fixed else '')
                    model=sp.SentencePieceProcessor(model_file=prefix+'.model')
                    if fixed:
                        self.assertNotIn(model.unk_id(),model.encode('𝜺'))
                        self.assertEqual(model.decode(model.encode('𝜺')),'𝜺')
                    else:self.assertIn(model.unk_id(),model.encode('𝜺'))

if __name__=='__main__':unittest.main()
