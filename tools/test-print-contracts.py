"""Fault-injection checks for saved modifier placement and layer-band ownership."""
import copy
import importlib.util
from pathlib import Path
import tempfile
import unittest
import xml.etree.ElementTree as ET
import zipfile

spec = importlib.util.spec_from_file_location('verify_print', Path(__file__).with_name('verify-print.py'))
verify = importlib.util.module_from_spec(spec)
spec.loader.exec_module(verify)


class PrintContracts(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        with zipfile.ZipFile(verify.ROOT / 'print/assembly-petg.3mf') as archive:
            cls.payloads = {name:archive.read(name) for name in archive.namelist()}

    def setUp(self):
        self.model = ET.fromstring(self.payloads['3D/3dmodel.model'])
        self.cfg = ET.fromstring(self.payloads['Metadata/model_settings.config'])
        self.shell = self.cfg.findall('object')[0]
        self.parent = next(n for n in self.model.find(verify.NS + 'resources') if n.get('id') == self.shell.get('id'))

    def test_valid_modifiers(self):
        verify.audit_modifiers(self.model,self.shell,1)

    def test_displaced_volume_rejected(self):
        mesh = next(n for n in self.model.find(verify.NS + 'resources') if n.get('id') == '201')
        for vertex in mesh.iter(verify.NS + 'vertex'):
            vertex.set('x', str(float(vertex.get('x')) + 20))
        with self.assertRaisesRegex(ValueError,'bounds differ'):
            verify.audit_modifiers(self.model,self.shell,1)

    def test_detached_volume_rejected(self):
        components = self.parent.find(verify.NS + 'components')
        components.remove(next(n for n in components if n.get('objectid') == '201'))
        with self.assertRaisesRegex(ValueError,'attached exactly once'):
            verify.audit_modifiers(self.model,self.shell,1)

    def test_transformed_component_rejected(self):
        component = next(n for n in self.parent.find(verify.NS + 'components') if n.get('objectid') == '201')
        component.set('transform','1 0 0 0 1 0 0 0 1 20 0 0')
        with self.assertRaisesRegex(ValueError,'component is transformed'):
            verify.audit_modifiers(self.model,self.shell,1)

    def test_transformed_part_rejected(self):
        part = next(n for n in self.shell.findall('part') if n.get('id') == '201')
        next(n for n in part.findall('metadata') if n.get('key') == 'matrix').set('value','1 0 0 0 0 1 0 0 0 0 1 0 20 0 0 1')
        with self.assertRaisesRegex(ValueError,'part is transformed'):
            verify.audit_modifiers(self.model,self.shell,1)

    def test_duplicate_component_rejected(self):
        components = self.parent.find(verify.NS + 'components')
        components.append(copy.deepcopy(next(n for n in components if n.get('objectid') == '201')))
        with self.assertRaisesRegex(ValueError,'attached exactly once'):
            verify.audit_modifiers(self.model,self.shell,1)

    def test_duplicate_band_owner_rejected(self):
        bands = ET.fromstring(self.payloads['Metadata/layer_config_ranges.xml'])
        bands.findall('object')[1].set('id','1')
        payloads = dict(self.payloads, **{'Metadata/layer_config_ranges.xml':ET.tostring(bands)})
        original_root = verify.ROOT
        with tempfile.TemporaryDirectory(prefix='injs-contracts-') as folder:
            test_root = Path(folder).resolve()
            self.assertEqual(test_root.parent, Path(tempfile.gettempdir()).resolve())
            (test_root / 'print').mkdir()
            with zipfile.ZipFile(test_root / 'print/assembly-petg.3mf','w') as archive:
                for name,raw in payloads.items():
                    archive.writestr(name,raw)
            try:
                verify.ROOT = test_root
                with self.assertRaisesRegex(ValueError,'height-band object IDs'):
                    verify.audit_project('assembly-petg.3mf',5)
            finally:
                verify.ROOT = original_root


if __name__ == '__main__':
    unittest.main()
