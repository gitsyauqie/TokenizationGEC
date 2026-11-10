import csv,json,sys,tempfile,unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'scripts'))
from build_and_smoke import preflight,architecture,TAGS
from common import sha256

class BuildGates(unittest.TestCase):
    def test_policy_and_input_gates(self):
        with tempfile.TemporaryDirectory() as td:
            p=Path(td);f=p/'fixture';f.write_text('immutable')
            tm={tag:{'files':{'fixture':sha256(f)}} for tag in TAGS}
            (p/'tokenizer_manifest.json').write_text(json.dumps(tm))
            (p/'data_manifest.json').write_text(json.dumps({'splits':{'train':{'retained_n':1},'valid':{'retained_n':1}},'surface_files':{'fixture':sha256(f)}}))
            (p/'status.json').write_text(json.dumps([{'tag':t,'status':'PREPARED_PENDING_LENGTH_AND_UNK_REVIEW'} for t in TAGS]))
            rows=[dict(tag=t,split=split,side=side,n=1,max_tokens_with_eos=3139,roundtrip_mismatch_without_unknown=0,unknown_rows=int(split=='valid')) for t in TAGS for split in ('train','valid') for side in ('source','target')]
            def save():
                with (p/'lengths_and_roundtrip.csv').open('w',newline='') as handle:
                    w=csv.DictWriter(handle,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)
            save();self.assertEqual(len(preflight(p)[2]),24)
            rows[0]['max_tokens_with_eos']=4097;save()
            with self.assertRaises(ValueError):preflight(p)
            rows[0]['max_tokens_with_eos']=3139;rows[0]['unknown_rows']=1;save()
            with self.assertRaises(ValueError):preflight(p)
            rows[0]['unknown_rows']=0;save();f.write_text('changed')
            with self.assertRaises(ValueError):preflight(p)
        args=architecture('/tmp/fixture')
        self.assertNotIn('--skip-invalid-size-inputs-valid-test',args)
        self.assertNotIn('--truncate-source',args)
        self.assertIn('--share-decoder-input-output-embed',args)
        self.assertEqual(args[args.index('--max-source-positions')+1],'4096')

if __name__=='__main__':unittest.main()
