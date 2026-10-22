"""Interpretación del candidato congelado, con funciones reales y datos sintéticos."""
import ast
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch
import sys

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'output/modelado-deps'))
import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.pipeline import Pipeline


def entorno():
    nb=json.loads((ROOT/'temporal_version_tp_entrega03_revision.ipynb').read_text(encoding='utf-8'))
    fuente=next(''.join(c['source']) for c in nb['cells'] if c['cell_type']=='code'
                and ''.join(c['source']).startswith('# 4.6.1 · Interpretación'))
    tree=ast.parse(fuente)
    nodes=[x for x in tree.body if isinstance(x,(ast.FunctionDef,ast.Import,ast.ImportFrom))]
    e={}
    exec(compile(ast.Module(body=nodes,type_ignores=[]),'<importancia real>','exec'),e)
    return e


def fixture():
    tabla=pd.DataFrame({'patient_id':np.repeat(np.arange(10),15)})
    y=np.tile(np.arange(5),30)
    rng=np.random.default_rng(42)
    x=pd.DataFrame({'senal':y+rng.normal(0,.2,len(y)),
        'senal__lag1m':y+rng.normal(0,.3,len(y)),
        'senal__lag2m':np.full(len(y),np.nan),
        'historia_disponible__lag1m':np.tile([0,0,1,1,1],30),
        'historia_disponible__lag2m':np.zeros(len(y),dtype=int)})
    rondas=[(np.flatnonzero(tabla.patient_id.to_numpy()%5!=k),
             np.flatnonzero(tabla.patient_id.to_numpy()%5==k)) for k in range(5)]
    modelo=RandomForestClassifier(n_estimators=4,max_depth=3,random_state=42,n_jobs=1)
    return x,y,tabla,rondas,modelo


class InterpretacionHistoriaTest(unittest.TestCase):
    def test_permutacion_conjunta_preserva_relacion_y_otras_columnas(self):
        e=entorno()
        x=pd.DataFrame({'a':[10,20,30],'b':[11,21,31],'resto':[7,8,9]},index=[4,5,6])
        p=e['permutar_bloque'](x,['a','b'],[2,0,1])
        np.testing.assert_array_equal(p.a,[30,10,20])
        np.testing.assert_array_equal(p.b-p.a,[1,1,1])
        pd.testing.assert_series_equal(p.resto,x.resto)
        self.assertTrue(p.index.equals(x.index))
        self.assertEqual(x.a.tolist(),[10,20,30])
        with self.assertRaisesRegex(ValueError,'inválidos'):
            e['permutar_bloque'](x,['a'],[0,0,1])

    def test_grupos_completos_sin_superposicion(self):
        e=entorno();x,*_=fixture();g=e['grupos_historia'](list(x))
        self.assertEqual([len(v) for v in g.values()],[1,1,1,2])
        self.assertEqual(sorted(c for cols in g.values() for c in cols),sorted(x.columns))
        with self.assertRaisesRegex(ValueError,'Retardo'):
            e['grupos_historia'](['senal__lag5m'])

    def test_cinco_folds_medias_imputacion_y_pesos_solo_entrenamiento(self):
        e=entorno();x,y,tabla,rondas,modelo=fixture()
        with tempfile.TemporaryDirectory(dir=ROOT/'output/verificacion') as tmp:
            out=Path(tmp)/'nuevo'
            r=e['calcular_importancia_historia'](x,y,tabla,rondas,modelo,out,{'fuente':'sintetica'},repeticiones=2)
            self.assertEqual(len(r['individual']),5)
            self.assertEqual(len(r['grupos']),4)
            raw=pd.read_csv(out/'permutaciones_individuales.csv')
            self.assertEqual(len(raw),5*5*2)
            joint=pd.read_csv(out/'permutaciones_grupos.csv')
            self.assertEqual(len(joint),4*5*2)
            byfold=raw.groupby(['variable','fold']).caida_f1_macro.mean()
            esperado=byfold.groupby('variable').agg(['mean','std'])
            observado=r['individual'].set_index('variable')
            np.testing.assert_allclose(observado.loc[esperado.index,'media'],esperado['mean'])
            np.testing.assert_allclose(observado.loc[esperado.index,'desviacion'],esperado['std'])
            medianas=pd.read_csv(out/'medianas_entrenamiento.csv')
            pesos=pd.read_csv(out/'pesos_entrenamiento.csv')
            for k,(tr,va) in enumerate(rondas,1):
                self.assertTrue(set(tabla.iloc[tr].patient_id).isdisjoint(tabla.iloc[va].patient_id))
                obs=medianas.query('fold == @k').set_index('variable').mediana
                np.testing.assert_allclose(obs.loc[x.columns],x.iloc[tr].median().fillna(0))
                w=pesos.query('fold == @k').set_index('clase')
                counts=np.bincount(y[tr],minlength=5)
                np.testing.assert_allclose(w.peso,len(tr)/(5*counts))
            self.assertEqual(r['metricas_folds'].epochs_validacion.sum(),len(x))

    def test_relectura_sin_entrenar_y_rechazo_de_alteraciones(self):
        e=entorno();args=fixture()
        with tempfile.TemporaryDirectory(dir=ROOT/'output/verificacion') as tmp:
            out=Path(tmp)/'nuevo'
            e['calcular_importancia_historia'](*args,out,{},repeticiones=1)
            before={p:p.read_bytes() for p in out.iterdir()}
            with patch.object(Pipeline,'fit',side_effect=AssertionError('No entrenar')):
                e['calcular_importancia_historia'](*args,out,{},repeticiones=1)
            self.assertEqual(before,{p:p.read_bytes() for p in out.iterdir()})
            path=out/'individual.csv';path.write_bytes(path.read_bytes()+b'\n')
            with self.assertRaisesRegex(ValueError,'modificadas'):
                e['calcular_importancia_historia'](*args,out,{},repeticiones=1)

    def test_fallo_deja_evidencia_y_no_reintenta(self):
        e=entorno();args=fixture()
        with tempfile.TemporaryDirectory(dir=ROOT/'output/verificacion') as tmp:
            out=Path(tmp)/'nuevo'
            with patch.object(Pipeline,'fit',side_effect=RuntimeError('fallo simulado')):
                with self.assertRaisesRegex(RuntimeError,'simulado'):
                    e['calcular_importancia_historia'](*args,out,{},repeticiones=1)
            with self.assertRaisesRegex(RuntimeError,'incompleta'):
                e['calcular_importancia_historia'](*args,out,{},repeticiones=1)

    def test_rechaza_fuga_identificadores_y_folds_invalidos(self):
        e=entorno();x,y,t,r,m=fixture()
        with tempfile.TemporaryDirectory(dir=ROOT/'output/verificacion') as tmp:
            with self.assertRaisesRegex(ValueError,'identificadores'):
                e['calcular_importancia_historia'](x.assign(patient_id=1),y,t,r,m,Path(tmp)/'a',{})
            mezclados=[(np.arange(1,len(x)),np.array([0]))]
            with self.assertRaisesRegex(ValueError,'Pacientes compartidos'):
                e['calcular_importancia_historia'](x,y,t,mezclados,m,Path(tmp)/'b',{})
            with self.assertRaisesRegex(ValueError,'única validación'):
                e['calcular_importancia_historia'](x,y,t,r+r,m,Path(tmp)/'c',{})

    def test_recuperacion_historica_trazable(self):
        registros=json.loads((ROOT/'output/verificacion/hiperparametros_recuperados.json').read_text(encoding='utf-8'))
        self.assertEqual(len(registros),6)
        for r in registros:
            self.assertEqual(r['protocolo'],'pacientes')
            self.assertTrue(r['pesos'])
            m=pd.read_csv(ROOT/r['archivo_metricas']).query("conjunto == 'validacion'")
            self.assertAlmostEqual(m.f1_macro.mean(),r['f1_validacion'])


if __name__=='__main__':unittest.main()
