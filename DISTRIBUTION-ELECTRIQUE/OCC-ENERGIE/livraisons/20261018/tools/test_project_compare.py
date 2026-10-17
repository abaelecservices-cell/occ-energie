"""Contrôles des décisions de comparaison et d’application de l’import."""
import copy
import json
import tempfile
import unittest
from pathlib import Path
from project_compare import compare, board_ids, normalize
from apply_project_import import apply

class ProjectComparison(unittest.TestCase):
    def test_cells_and_conflicts(self):
        excel = dict(sheets=[dict(sheet='TR 1A & 1B', cells={'A1':'Éclairage'},
            halves={'A':dict(cell='A2',board='TGBT1A',items=[dict(cell='A3',label='Pompe')])},
            blocks=[dict(cell='B1',header='TS1',items=[dict(cell='B2',label='Labo')])])])
        cells = [('A1','E\u0301clairage'),('A2','TGBT1A'),('A3','Pompe'),('B1','TS1'),('B2','Différent'),('Z1','Nouveau')]
        incoming = dict(distribution=[dict(sheet='TR 1A & 1B',cell=c,text=t) for c,t in cells])
        result = compare(incoming,excel)
        self.assertEqual([x['status'] for x in result],['identique']*4+['ecart','nouveau'])
        self.assertTrue(all(x['board']=='TGBT1' for x in result))
        self.assertEqual(normalize('  A  B '),'a b')
    def test_board_mapping(self):
        boards={'TS17','PL20','TGBT3','VARIVOLT','PEG'}
        for name,expected in [('TS17A',['TS17']),('HTA20',['PL20']),('TGBT3-SUP',['TGBT3']),('VARIVOLT-PLAQUE',['VARIVOLT']),('POMPES',['PEG']),('UPS',[])]:
            self.assertEqual(board_ids(name,boards),expected)
        self.assertEqual(board_ids('GRADATHYR',boards),['TGBT8','GRADATHYR'])
    def test_apply_missing_and_idempotent(self):
        original=dict(boards=[dict(id='TS8',photos=['old'])],edges=[['a','b']])
        with tempfile.TemporaryDirectory() as folder:
            self.assertEqual(apply(copy.deepcopy(original),folder),original)
            path=Path(folder)/'build';path.mkdir()
            patch=dict(summary={'photos':1},boards={'TS8':dict(photos=['new'],documentPages=1)})
            (path/'project-import.json').write_text(json.dumps(patch),encoding='utf-8')
            changed=apply(copy.deepcopy(original),folder)
            self.assertEqual(changed['edges'],original['edges'])
            self.assertEqual(apply(copy.deepcopy(changed),folder),changed)
            self.assertEqual(changed['boards'][0]['photos'],['old'])
            self.assertEqual(changed['boards'][0]['projectImport']['sourceCount'],1)

if __name__=='__main__':
    unittest.main()
