"""Run with the same sacrebleu==1.5.1 dependency as the server."""
import csv
import importlib.util
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

SCRIPTS=Path(__file__).resolve().parents[1]/'scripts'
sys.path.insert(0,str(SCRIPTS))
from common import sha256
import eval_reconstruction as evaluation
import sacrebleu

class ReconstructionTests(unittest.TestCase):
    def test_metric_sanity(self):
        evaluation.self_check(sacrebleu)
        self.assertEqual(evaluation.surface('A_b, C','lower'),'a _ b , c')
        with self.assertRaises(ValueError):evaluation.metric_scores(['a'],[],sacrebleu)

    def test_full_cli_and_changed_generation(self):
        with tempfile.TemporaryDirectory() as td:
            p=Path(td);verified=p/'verified';verified.mkdir()
            raw=['saya membaca buku baru di rumah hari ini .','dia membeli dua buku baru untuk adiknya .']
            cfg={'case':'lower','expected_sha256':{},'runs':[]}
            for k,rows in [('source',raw),('target',raw),('category',['cat_a','cat_b'])]:
                f=p/k;f.write_text('\n'.join(rows)+'\n');cfg[k]=str(f);cfg['expected_sha256'][k]=sha256(f)
            gen=p/'gen.out';gen.write_text(''.join('S-%d\t%s\nT-%d\t%s\nH-%d\t-1\t%s\n'%(i,t,i,t,i,t) for i,t in enumerate(raw)))
            cfg['runs']=[{'id':'toy','generation':str(gen),'decoder':'text','expected_n':2},
                         {'id':'prior_blocked','generation':str(p/'absent'),'decoder':'text','expected_n':2}]
            manifest=p/'manifest.json';manifest.write_text(json.dumps(cfg))
            previous=[{'run_id':'toy','status':'VERIFIED_FOR_RETROSPECTIVE_DIAGNOSTICS','generation_sha256':sha256(gen),
                       'artifact_sha256':{},'verification':{'S':{'failures':0},'T':{'failures':0}}},
                      {'run_id':'prior_blocked','status':'BLOCKED','error':'fixture missing coverage'}]
            (verified/'verification.json').write_text(json.dumps(previous))
            provenance={'manifest_sha256':sha256(manifest),'common_sha256':sha256(SCRIPTS/'common.py'),
                        'case':'lower','surface_rule':r'[^\W_]+|[^\w\s]|_','raw_sha256':cfg['expected_sha256']}
            (verified/'provenance.json').write_text(json.dumps(provenance))
            def run(out):
                return subprocess.run([sys.executable,str(SCRIPTS/'eval_reconstruction.py'),'--manifest',str(manifest),
                                       '--verified',str(verified),'--out',str(out)],capture_output=True,text=True,env=os.environ.copy())
            result=run(p/'out');self.assertEqual(result.returncode,0,result.stderr)
            scores=list(csv.DictReader((p/'out/scores.csv').read_text().splitlines()))
            self.assertEqual(len(scores),3)
            for row in scores:
                self.assertAlmostEqual(float(row['chrf2_pct']),100)
                self.assertAlmostEqual(float(row['bleu']),100)
                self.assertAlmostEqual(float(row['exact_match_pct']),100)
            self.assertEqual(len(list(csv.DictReader((p/'out/category_scores.csv').read_text().splitlines()))),6)
            self.assertNotEqual(run(p/'out').returncode,0)
            gen.write_text(gen.read_text()+'changed\n')
            self.assertEqual(run(p/'changed').returncode,0)
            status=json.loads((p/'changed/run_status.json').read_text())
            self.assertEqual(status[0]['status'],'BLOCKED')
            self.assertEqual(len(list(csv.DictReader((p/'changed/scores.csv').read_text().splitlines()))),2)
            (p/'target').write_text('changed\n')
            self.assertNotEqual(run(p/'bad_raw').returncode,0)
            self.assertFalse((p/'bad_raw').exists())

if __name__=='__main__':unittest.main()
