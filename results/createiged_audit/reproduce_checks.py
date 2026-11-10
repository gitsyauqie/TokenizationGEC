import ast,json,hashlib,re,random,logging
from collections import namedtuple
from typing import List,Dict,Tuple,Optional
from pathlib import Path
p=Path('/Users/syauqiemuhammad/Documents/Claude/Projects/Paper 6/paper6_revision_20261007/createIGED')
ns=dict(re=re,random=random,logging=logging,namedtuple=namedtuple,List=List,Dict=Dict,Tuple=Tuple,Optional=Optional)
for name in ['corpus.py','create_dataset.py','SynGECIndo.py']:
 tree=ast.parse((p/name).read_text());tree.body=[x for x in tree.body if isinstance(x,(ast.FunctionDef,ast.ClassDef))];exec(compile(tree,str(p/name),'exec'),ns)
results={
 'fallback_currency':ns['simple_sentence_tokenize']('Harga barang itu Rp. 100.000 untuk satu paket.'),
 'fallback_abbreviation':ns['simple_sentence_tokenize']('Dr. Budi datang ke rumah pagi ini.'),
 'heading_cleanup':ns['clean_sentence']('BAB IV HASIL DAN PEMBAHASAN Penelitian ini dilakukan pada sekolah.'),
 'subheading_cleanup':ns['clean_sentence']('1.4 Tujuan Penelitian'),
 'ellipsis_cleanup':ns['clean_sentence']('Ia berkata... lalu berhenti.'),
 'table_removal_layout':ns['remove_table_text']('Nama Nilai\nAndi 90',[[['Nama','Nilai'],['Andi','90']]]),
 'short_target_passes_filter':ns['is_valid_sentence']('Munir Mulkhan (90) 35.'),
 'affix_nonmorphological':ns['IndonesianDataAugmentation']([], '').remove_affixes('sekolah berita sebagai')
}
assert results['fallback_currency']==['Harga barang itu Rp.','100.000 untuk satu paket.']
assert results['fallback_abbreviation']==['Dr.','Budi datang ke rumah pagi ini.']
assert results['table_removal_layout']=='Nama Nilai\nAndi 90'
assert results['short_target_passes_filter'] is False
assert results['heading_cleanup'].startswith('BAB IV')
assert results['subheading_cleanup']=='ujuan Penelitian.'
assert results['ellipsis_cleanup']=='Ia berkata. lalu berhenti.'
assert results['affix_nonmorphological']=='kolah ita baga'
o=Path('paper6_revision_20261007/results_local/createiged_audit');o.mkdir(parents=True,exist_ok=True)
(o/'checks.json').write_text(json.dumps({'method':'AST extracts function/class definitions only; original entrypoints, PDF reads, NLTK path and dataset generation not executed','source_sha256':{x.name:hashlib.sha256(x.read_bytes()).hexdigest() for x in p.glob('*.py')},'checks':results},indent=2,ensure_ascii=False)+'\n')
print(json.dumps(results,ensure_ascii=False,indent=2))
