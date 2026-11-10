import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

SCRIPTS = Path(__file__).resolve().parents[1] / 'scripts'
sys.path.insert(0, str(SCRIPTS))
from common import canonical, decode, diagnostic_metrics, new_output, parse_gen
from audit_server import scan_split
from audit_draft_table import spearman
from eval_gen_v2 import validate_streams


class Tests(unittest.TestCase):
    def test_word_set_inflation_order(self):
        r = diagnostic_metrics(['saya buku membaca'], ['saya membaca buku'], ['buku saya membaca'])
        self.assertEqual(r['legacy_word_set_f1_pct'], 100)
        self.assertEqual(r['exact_match_pct'], 0)

    def test_word_set_inflation_repetition(self):
        r = diagnostic_metrics(['saya saya makan'], ['saya makan'], ['saya saya makan'])
        self.assertEqual(r['legacy_word_set_f1_pct'], 100)
        self.assertEqual(r['erroneous_exact_correction_pct'], 0)

    def test_copy_and_oracle(self):
        s, t = ['saya makan', 'dia buku'], ['saya makan', 'dia membaca buku']
        copy = diagnostic_metrics(s, t, s)
        gold = diagnostic_metrics(s, t, t)
        self.assertEqual(copy['changed_sentence_pct'], 0)
        self.assertEqual(copy['exact_match_pct'], 50)
        self.assertEqual(copy['clean_overcorrection_pct'], 0)
        self.assertEqual(gold['exact_match_pct'], 100)

    def test_decoders(self):
        self.assertEqual(decode('mem@@ beri@@ kan buku', 'bpe'), 'memberikan buku')
        self.assertEqual(decode('mem ##beri ##kan buku', 'wordpiece'), 'memberikan buku')
        self.assertEqual(decode('▁mem beri kan ▁buku', 'sentencepiece'), 'memberikan buku')
        self.assertEqual(decode('memberikan buku', 'text'), 'memberikan buku')

    def test_canonical_does_not_hide_detached_affix(self):
        self.assertNotEqual(canonical('kadın a'), canonical('kadına'))
        self.assertEqual(canonical("Ankara ' da ."), canonical("Ankara'da."))
        self.assertNotEqual(canonical('Buku'), canonical('buku'))
        self.assertEqual(canonical('Buku', 'lower'), canonical('buku', 'lower'))

    def test_alignment_blocks_wrong_reference(self):
        d = validate_streams({'S': {0: 'saya makan'}, 'T': {0: 'saya minum'}},
                             ['saya makan'], ['saya makan'], 'text', 'preserve')
        self.assertEqual(d['T']['mismatches'], 1)

    def test_parser_sort_and_reject_missing_duplicate(self):
        with tempfile.TemporaryDirectory() as d:
            p = Path(d) / 'gen.out'
            content = 'S-1\tb\nT-1\tb\nH-1\t-1\tb\nS-0\ta\nT-0\ta\nH-0\t-1\ta\n'
            p.write_text(content)
            self.assertEqual(parse_gen(p, 2)['H'][0], 'a')
            with self.assertRaises(ValueError):
                parse_gen(p, 3)
            p.write_text(content + 'H-0\t-2\tb\n')
            with self.assertRaises(ValueError):
                parse_gen(p, 2)

    def test_parser_rejects_extra_and_malformed(self):
        with tempfile.TemporaryDirectory() as d:
            p = Path(d) / 'gen.out'
            p.write_text('S-5\ta\nT-5\ta\nH-5\t-1\ta\n')
            with self.assertRaises(ValueError):
                parse_gen(p, 1)
            p.write_text('S-0\ta\nT-0\ta\nH-0\tbroken\n')
            with self.assertRaises(ValueError):
                parse_gen(p, 1)

    def test_scan_duplicates_and_length_failure(self):
        with tempfile.TemporaryDirectory() as d:
            raw = Path(d)
            (raw / 'train.source').write_text('a\na\nb\n')
            (raw / 'train.target').write_text('x\nx\ny\n')
            (raw / 'train.group_id').write_text('doc1\ndoc1\ndoc2\n')
            r, hashes = scan_split(raw, 'train', 'source', 'target')
            self.assertEqual(r['duplicate_pair_rows'], 1)
            self.assertEqual(len(hashes['group_id']), 2)
            (raw / 'train.target').write_text('x\n')
            r, _ = scan_split(raw, 'train', 'source', 'target')
            self.assertTrue(r['errors'])

    def test_spearman_with_ties_and_wp(self):
        self.assertEqual(spearman([1, 1, 2], [3, 3, 4]), 1)
        self.assertAlmostEqual(spearman([.407, .423, .408, .392],
                                       [97.09, 96.51, 96.57, 96.21]), .2)

    def test_existing_output_rejected(self):
        with tempfile.TemporaryDirectory() as d:
            with self.assertRaises(FileExistsError):
                new_output(d)

    def test_cli_end_to_end_and_fail_closed(self):
        with tempfile.TemporaryDirectory() as d:
            p = Path(d)
            (p / 'src').write_text('saya baca buku\nsaya makan\n')
            (p / 'tgt').write_text('saya membaca buku\nsaya makan\n')
            good = ('S-1\tsaya makan\nT-1\tsaya makan\nH-1\t-1\tsaya makan\n'
                    'S-0\tsaya baca buku\nT-0\tsaya membaca buku\nH-0\t-1\tsaya membaca buku\n')
            (p / 'good.out').write_text(good)
            cfg = {'source': 'src', 'target': 'tgt', 'case': 'preserve',
                   'runs': [{'id': 'model_seed42', 'generation': 'good.out', 'decoder': 'text'}]}
            (p / 'manifest.json').write_text(json.dumps(cfg))
            cmd = [sys.executable, str(SCRIPTS / 'eval_gen_v2.py'), '--manifest', str(p / 'manifest.json'), '--out']
            proc = subprocess.run(cmd + [str(p / 'ok')], capture_output=True, text=True)
            self.assertEqual(proc.returncode, 0, proc.stderr)
            status = json.loads((p / 'ok/run_status.json').read_text())
            self.assertEqual(status[0]['status'], 'DIAGNOSTIC_ONLY')
            (p / 'good.out').write_text(good.replace('T-0\tsaya membaca buku', 'T-0\twrong reference'))
            proc = subprocess.run(cmd + [str(p / 'bad')], capture_output=True, text=True)
            self.assertEqual(proc.returncode, 2, proc.stderr)
            self.assertNotIn('model_seed42', (p / 'bad/diagnostics.csv').read_text())

    def test_audit_cli_overlap_and_artifacts(self):
        with tempfile.TemporaryDirectory() as d:
            p = Path(d); raw = p / 'raw'; project = p / 'Paper6'
            raw.mkdir(); project.mkdir()
            for split in ('train', 'valid', 'test'):
                (raw / f'{split}.source').write_text('saya baca\n')
                (raw / f'{split}.target').write_text('saya membaca\n')
                (raw / f'{split}.category').write_text('afiksasi\n')
            (p / 'evaluate_model_new.py').write_text('# fixture\n')
            cmd = [sys.executable, str(SCRIPTS / 'audit_server.py'), '--project', str(project),
                   '--raw', str(raw), '--out', str(p / 'audit')]
            proc = subprocess.run(cmd, capture_output=True, text=True)
            self.assertEqual(proc.returncode, 0, proc.stderr)
            report = json.loads((p / 'audit/audit.json').read_text())
            self.assertEqual(report['overlap']['train__test']['target'], 1)
            self.assertTrue((p / 'audit/REPORT.md').exists())
            self.assertTrue((p / 'audit/legacy_evidence/evaluate_model_new.py').exists())
            proc = subprocess.run([sys.executable, str(SCRIPTS / 'overlap_details.py'),
                '--audit', str(p / 'audit/audit.json'), '--out', str(p / 'details')],
                capture_output=True, text=True)
            self.assertEqual(proc.returncode, 0, proc.stderr)
            detail = json.loads((p / 'details/overlap_details.json').read_text())
            self.assertEqual(detail['splits']['test']['affected_rows']['target_in_train'], 1)
            self.assertEqual(detail['splits']['test']['affected_rows']['any_flag'], 1)
            (raw / 'test.target').write_text('changed\n')
            proc = subprocess.run([sys.executable, str(SCRIPTS / 'overlap_details.py'),
                '--audit', str(p / 'audit/audit.json'), '--out', str(p / 'details_changed')],
                capture_output=True, text=True)
            self.assertNotEqual(proc.returncode, 0)
            self.assertIn('Data changed since Step 1', proc.stderr)


if __name__ == '__main__':
    unittest.main()
