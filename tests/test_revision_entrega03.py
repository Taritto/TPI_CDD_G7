"""Verifica la copia de revisión con datos sintéticos, sin abrir el test real."""
import ast
import hashlib
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch
import test_modelado_notebook as base_tests

ROOT=Path(__file__).resolve().parents[1]
ORIGINAL=json.loads((ROOT/'temporal_version_tp_entrega03.ipynb').read_text())
REVISION=json.loads((ROOT/'temporal_version_tp_entrega03_revision.ipynb').read_text())


def cell_functions(prefix, espacio):
    codigo=base_tests.fuente(prefix)
    nodes=[n for n in ast.parse(codigo).body if isinstance(n,(ast.FunctionDef,ast.Import,ast.ImportFrom))]
    exec(compile(ast.Module(body=nodes,type_ignores=[]),'<funciones revisión>','exec'),espacio)


class RevisionTest(base_tests.ModeladoTest):
    def setUp(self):
        self._notebook_patch=patch.object(base_tests,"NOTEBOOK",REVISION)
        self._notebook_patch.start()
        self.addCleanup(self._notebook_patch.stop)

    # La cronología fue retirada de esta copia; el test histórico sigue en el módulo original.
    test_cronologia_gap_y_oof_solo_elegibles=None

    def entorno(self,carpeta):
        e=super().entorno(carpeta)
        cell_functions('columnas_principal =',e)
        np=e['np']
        e.update(huella={},versiones={},especificaciones={},huellas_folds={p:hashlib.sha256(
            b''.join(np.asarray(i,dtype='<i8').tobytes() for tr,va in rondas for i in (tr,va))).hexdigest()
            for p,rondas in e['folds'].items()})
        return e

    def test_original_y_bloque_historico_preservados(self):
        evidencia=REVISION['metadata']['revision']
        self.assertEqual(hashlib.sha256((ROOT/'temporal_version_tp_entrega03.ipynb').read_bytes()).hexdigest(),evidencia['sha256_origen'])
        celdas={''.join(c['source']):c for c in REVISION['cells'] if c['cell_type']=='code'}
        for c in ORIGINAL['cells'][35:49]:
            if c['cell_type']!='code':continue
            nueva=celdas[''.join(c['source'])]
            self.assertEqual(''.join(c['source']),''.join(nueva['source']))
            for campo in ['outputs','execution_count']:
                self.assertEqual(c[campo],nueva[campo])
            self.assertIn('skip-execution',nueva['metadata']['tags'])

    def test_protocolos_y_retiros_solo_en_bloques_activos(self):
        activos='\n'.join(''.join(c['source']) for c in REVISION['cells']
            if c['cell_type']=='code' and 'skip-execution' not in c.get('metadata',{}).get('tags',[]))
        for prohibido in ["folds['temporal']",'particiones_cronologicas','precision_recall_curve','average_precision_score']:
            self.assertNotIn(prohibido,activos)
        self.assertIn("ESCENARIOS = ['pacientes', 'epochs']",activos)
        self.assertIn('RUTA_BASE_ADICIONAL = None',activos)
        self.assertIn("'desviacion','segundos_entrenamiento','desempate_nombre'",activos)

    def test_cache_evitar_reentrenar_y_rechazar_manipulaciones(self):
        with tempfile.TemporaryDirectory(dir=base_tests.TEMP_ROOT) as carpeta:
            e=self.entorno(carpeta)
            modelo=e['RandomForestClassifier'](n_estimators=3,random_state=42,n_jobs=1)
            r=e['evaluar'](modelo,e['X'],'primera','epochs',mostrar_progreso=False)
            with patch.object(e['RandomForestClassifier'],'fit',side_effect=AssertionError('No repetir')):
                copia=e['evaluar'](modelo,e['X'],'segunda','epochs',mostrar_progreso=False)
            e['pd'].testing.assert_frame_equal(r['oof'],copia['oof'],check_dtype=False)
            ruta=Path(carpeta)/'segunda'/'oof.csv'
            ruta.write_text(ruta.read_text()+'\n')
            with self.assertRaisesRegex(ValueError,'huellas'):
                e['evaluar'](modelo,e['X'],'tercera','epochs',mostrar_progreso=False)

    def adicional_fixture(self,carpeta):
        e=self.entorno(carpeta);pd,np=e['pd'],e['np']
        columnas=ast.literal_eval(ast.parse(base_tests.fuente('columnas_principal =')).body[0].value)
        e['columnas_principal']=columnas
        necesarias=set(columnas+['BVP_std','EDA_median','ACC_X_std','ACC_Y_std','ACC_Z_std','E1_std','E2_std','LAT_std','RAT_std'])
        dev=e['dev'].copy()
        for c in necesarias:dev[c]=np.arange(len(dev))%5+1.
        e['base']=dev.copy();e['dev']=dev
        e['X']=dev[columnas]
        cell_functions('def construir_representaciones(',e)
        cell_functions('# Configurar únicamente',e)
        e['planes_candidatos']={};e['candidatos_escenario']={}
        for p in ['pacientes','epochs']:
            nombre=f'{p}_RF_pesos0'
            e['candidatos_escenario'][p]=nombre
            e['planes_candidatos'][p]=dict(columnas=columnas,retardos=[],representacion='candidata',imputar=False,smote=None)
            e['especificaciones'][nombre]=(e['RandomForestClassifier'](n_estimators=3,max_depth=2,random_state=42,n_jobs=1),False,False,e['X'])
            e['planes_candidatos'][p].update(parametros=e['especificaciones'][nombre][0].get_params(),pesos=False,escalar=False,huella_entradas=hashlib.sha256(pd.util.hash_pandas_object(e['X'],index=True).values.tobytes()).hexdigest())
        nuevos=dev.iloc[:20].copy();nuevos['patient_id']=100+np.repeat([0,1],10)
        b=Path(carpeta)/'base_extra.csv';c=Path(carpeta)/'candidato_extra.csv'
        nuevos.to_csv(b,index=False);nuevos.to_csv(c,index=False)
        return e,b,c

    def test_comparacion_adicional_mismos_pacientes_y_relectura(self):
        with tempfile.TemporaryDirectory(dir=base_tests.TEMP_ROOT) as carpeta:
            e,b,c=self.adicional_fixture(carpeta)
            resultados=e['comparar_adicionales'](b,c)
            e['pd'].testing.assert_frame_equal(resultados['pacientes']['datos'][e['CLAVES']],resultados['epochs']['datos'][e['CLAVES']])
            with patch.object(e['RandomForestClassifier'],'fit',side_effect=AssertionError('No entrenar')),patch.object(e['RandomForestClassifier'],'predict_proba',side_effect=AssertionError('No inferir')):
                e['comparar_adicionales'](b,c)
            e['planes_candidatos']['epochs']['retardos']=[1]
            with self.assertRaisesRegex(ValueError,'Cambió'):
                e['comparar_adicionales'](b,c)

    def test_adicional_rechaza_pacientes_ya_utilizados(self):
        with tempfile.TemporaryDirectory(dir=base_tests.TEMP_ROOT) as carpeta:
            e,b,c=self.adicional_fixture(carpeta)
            tabla=e['pd'].read_csv(b);tabla['patient_id']-=100
            tabla.to_csv(b,index=False);tabla.to_csv(c,index=False)
            with self.assertRaisesRegex(ValueError,'cohorte histórica'):
                e['preparar_adicionales'](b,c)

    def test_candidato_no_cambia_antes_de_comparar_adicionales(self):
        with tempfile.TemporaryDirectory(dir=base_tests.TEMP_ROOT) as carpeta:
            e,b,c=self.adicional_fixture(carpeta)
            nombre=e['candidatos_escenario']['pacientes']
            e['especificaciones'][nombre][0].set_params(max_depth=3)
            with self.assertRaisesRegex(ValueError,'candidato cambió'):
                e['comparar_adicionales'](b,c)

    def test_adicional_rechaza_identidades_con_otro_formato(self):
        with tempfile.TemporaryDirectory(dir=base_tests.TEMP_ROOT) as carpeta:
            e,b,c=self.adicional_fixture(carpeta)
            tabla=e['pd'].read_csv(b);tabla['patient_id']='S'+tabla.patient_id.astype(str)
            tabla.to_csv(b,index=False);tabla.to_csv(c,index=False)
            with self.assertRaisesRegex(ValueError,'Formato de patient_id'):
                e['preparar_adicionales'](b,c)

    def test_comparacion_incompleta_no_se_repite(self):
        with tempfile.TemporaryDirectory(dir=base_tests.TEMP_ROOT) as carpeta:
            e,b,c=self.adicional_fixture(carpeta)
            with patch.object(e['RandomForestClassifier'],'predict_proba',side_effect=RuntimeError('fallo simulado')):
                with self.assertRaisesRegex(RuntimeError,'fallo simulado'):
                    e['comparar_adicionales'](b,c)
            with self.assertRaisesRegex(RuntimeError,'incompleta'):
                e['comparar_adicionales'](b,c)


if __name__=='__main__':unittest.main()
