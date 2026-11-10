import sys,tempfile,random,json,csv
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'scripts'))
import prepare_controlled as p
from common import sha256
assert p.surface('Áda_A.  B')=='áda _ a . b'
assert p.failure_marker(' "Error in API call" ')
assert not p.failure_marker('Error in API call: timeout')
with tempfile.TemporaryDirectory() as td:
 root=Path(td);out=root/'out';out.mkdir();audit={'splits':{}}
 for split in ['train','valid']:
  info={'files':{},'n_pairs':3,'categories':{'a':3},'errors':[]}
  for k,vals in {'source':['Kalimat ini.','Error in API call','Áda rumah baru.'],'target':['Kalimat ini.','Target benar.','Áda rumah baru.'],'category':['a']*3}.items():
   f=root/(split+'.'+k);f.write_text('\n'.join(vals)+'\n');info['files'][k]={'path':str(f),'sha256':sha256(f)}
  audit['splits'][split]=info
 stats,inputs,corpus,mb,mw=p.prepare_text(audit,out)
 assert stats['train']['retained_n']==2 and stats['valid']['excluded_n']==1
 assert len(corpus.read_text().splitlines())==4
 with (out/'surface/train.ids.csv').open() as f: assert [x['original_id_zero_based'] for x in csv.DictReader(f)]==['0','2']
 rng=random.Random(42);words=[''.join(rng.choice('abcdefghijklmn') for _ in range(8)) for _ in range(400)]
 strings=[' '.join(words[i:i+10])+' .' for i in range(0,400,10)]*3
 large=root/'corpus.txt';large.write_text('\n'.join(strings)+'\n')
 for family in ['spbpe','wp','spuni']:
  folder=root/family;folder.mkdir()
  encode,pieces,artifact=p.train_tokenizer(family,64,large,folder,100,8)
  assert len(pieces)==64 and pieces[:4]==p.SPECIALS
  for text in strings:
   tokens,decoded,unk=encode(text);assert decoded==text,(family,text,decoded);assert not unk
  tokens,decoded,unk=encode('🦉');assert unk
 print('PASS: marker policy, surface, exclusion ID mapping, train-only corpus; all 3 real tokenizer libraries achieve vocabulary 64 and exact known-text roundtrip; unseen Unicode detected.')
