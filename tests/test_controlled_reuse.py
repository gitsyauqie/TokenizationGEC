"""Reuse orchestration fixture; heavy trainer mocked, libraries covered separately."""
import csv,json,sys,tempfile,unittest
from pathlib import Path
from unittest.mock import patch
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'scripts'))
import prepare_controlled as prep
from common import sha256

class ReuseTest(unittest.TestCase):
    def test_reuse_preserves_wp_and_rejects_changed_surface(self):
        with tempfile.TemporaryDirectory() as td:
            p=Path(td);old=p/'old';old.mkdir();audit={'splits':{}}
            for split in ('train','valid'):
                info={'errors':[],'n_pairs':2,'categories':{'cat':2},'files':{}}
                for key,vals in {'source':['teks awal .','Error in API call'],'target':['teks awal .','referensi .'],'category':['cat','cat']}.items():
                    f=p/(split+'.'+key);f.write_text('\n'.join(vals)+'\n');info['files'][key]={'path':str(f),'sha256':sha256(f)}
                audit['splits'][split]=info
            ap=p/'audit.json';ap.write_text(json.dumps(audit))
            stats,inputs,corpus,mb,mw=prep.prepare_text(audit,old)
            dm={'splits':stats,'raw_inputs':inputs,'case':'lower','surface_rule':r'[^\W_]+|[^\w\s]|_',
                'corpus_sha256':sha256(corpus),'surface_files':{str(f.relative_to(old)):sha256(f) for f in (old/'surface').iterdir()}}
            (old/'data_manifest.json').write_text(json.dumps(dm))
            (old/'provenance.json').write_text(json.dumps({'audit_sha256':sha256(ap),'common_sha256':sha256(Path(prep.__file__).with_name('common.py')),
                'versions':{'sentencepiece':'0.2.0','tokenizers':'0.20.3'}}))
            models={};statuses=[];lengths=[]
            for tag in ('wp_5k','wp_20k'):
                folder=old/tag;folder.mkdir();(folder/'tokenizer.json').write_text('fixture immutable')
                models[tag]={'files':{str((folder/'tokenizer.json').relative_to(old)):sha256(folder/'tokenizer.json')}}
                statuses.append({'tag':tag,'status':'PREPARED_PENDING_LENGTH_AND_UNK_REVIEW'})
                for split in ('train','valid'):
                    for side in ('source','target'):
                        lengths.append(dict(tag=tag,split=split,side=side,n=1,tokens=3,max_tokens_with_eos=4,over_1024_with_eos=0,over_2048_with_eos=0,unknown_rows=0,roundtrip_mismatch_with_unknown=0,roundtrip_mismatch_without_unknown=0))
            (old/'tokenizer_manifest.json').write_text(json.dumps(models));(old/'status.json').write_text(json.dumps(statuses))
            with (old/'lengths_and_roundtrip.csv').open('w',newline='') as f:
                w=csv.DictWriter(f,fieldnames=list(lengths[0]));w.writeheader();w.writerows(lengths)
            calls=[]
            def trainer(family,size,corpus,folder,*args):
                self.assertNotEqual(family,'wp');calls.append((family,size));artifact=folder/'fixture.model';artifact.write_text('fixture')
                return (lambda t:(t.split(),t,False)),list(range(size)),artifact
            args=['prepare_controlled','--audit',str(ap),'--reuse-from',str(old),'--out',str(p/'new')]
            with patch.object(sys,'argv',args),patch.object(prep,'train_tokenizer',trainer):prep.main()
            self.assertEqual(len(calls),4)
            for tag in ('wp_5k','wp_20k'):
                self.assertEqual((old/tag/'tokenizer.json').read_bytes(),(p/'new'/tag/'tokenizer.json').read_bytes())
            with (p/'new/lengths_and_roundtrip.csv').open() as f:self.assertEqual(len(list(csv.DictReader(f))),24)
            (old/'surface/train.source').write_text('changed\n');args[-1]=str(p/'bad')
            with patch.object(sys,'argv',args),self.assertRaises(ValueError):prep.main()
            self.assertFalse((p/'bad').exists())

if __name__=='__main__':unittest.main()
