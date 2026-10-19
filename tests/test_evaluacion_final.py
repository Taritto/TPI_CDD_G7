"""Flujo real de 4.8 con archivos sintéticos; nunca evalúa el test del proyecto."""
import json
import hashlib
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch
import numpy as np
import pandas as pd
from test_modelado_notebook import fuente, TEMP_ROOT
import test_modelado_notebook as anteriores


def entorno_final():
    e={'__name__':'prueba_final'}
    exec(compile(fuente('# 4.8'),'<4.8 independiente>','exec'),e)
    return e


def fixture_final(carpeta,e):
    raiz=Path(carpeta); (raiz/'etl_v1').mkdir()
    n=240; etiquetas=e['PLANTILLA_FINAL']['etapas']; rng=np.random.default_rng(42)
    tabla=pd.DataFrame({'patient_id':np.repeat(np.arange(8),30),'epoch':np.tile(np.arange(30),8),
        'tiempo_relativo_segundos':np.tile(np.arange(30)*30,8),
        'Sleep_Stage':np.tile(etiquetas,48)})
    tabla.loc[(tabla.patient_id==0)&(tabla.epoch>=8),'tiempo_relativo_segundos']+=90
    columnas=e['PLANTILLA_FINAL']['columnas_actuales']
    for c in columnas:
        tabla[c]=np.tile(np.arange(5),48)+rng.uniform(.01,.1,n)
        tabla.loc[tabla.patient_id>=6,c]+=10000  # Detectar imputación contaminada por test.
    cfg=json.loads(json.dumps(e['PLANTILLA_FINAL']))
    cfg['configuracion']='prueba_sintetica'
    cfg['pacientes_test']=[6,7]
    cfg['cantidades']={'desarrollo':{'epochs':180,'pacientes':6},'test':{'epochs':60,'pacientes':2}}
    cfg['parametros'].update(n_estimators=5,max_depth=2,n_jobs=1)
    cfg['huella']={}
    for nombre in ['dataset_epochs_v1.csv','dataset_modelado_candidato.csv']:
        ruta=raiz/'etl_v1'/nombre; tabla.to_csv(ruta,index=False)
        cfg['huella'][nombre]=e['hash_archivo_final'](ruta)
    return raiz,raiz/'salida',cfg


class EvaluacionFinalTest(unittest.TestCase):
    def test_requiere_autorizacion_sin_escribir(self):
        e=entorno_final()
        with tempfile.TemporaryDirectory(dir=TEMP_ROOT) as c:
            raiz,salida,cfg=fixture_final(c,e)
            with self.assertRaisesRegex(RuntimeError,'autorización'):
                e['ejecutar_final'](raiz,salida,cfg)
            self.assertFalse(salida.exists())

    def test_inferencia_unica_y_relectura_sin_entrenamiento(self):
        e=entorno_final()
        with tempfile.TemporaryDirectory(dir=TEMP_ROOT) as c:
            raiz,salida,cfg=fixture_final(c,e)
            llamadas=[]; original=e['XGBClassifier'].predict_proba
            def observar(modelo,X,**kwargs):
                estado=json.loads((salida/'test_abierto.json').read_text())
                self.assertTrue((salida/'configuracion_congelada.json').exists())
                llamadas.append((len(X),estado['estado']))
                return original(modelo,X,**kwargs)
            with patch.object(e['XGBClassifier'],'predict_proba',new=observar):
                r=e['ejecutar_final'](raiz,salida,cfg,autorizar=True)
            self.assertEqual(sum(estado=='abierto' for _,estado in llamadas),1)
            self.assertIn((60,'abierto'),llamadas)
            self.assertEqual(len(r['datos']),60)
            self.assertEqual(json.loads((salida/'test_abierto.json').read_text())['estado'],'evaluado')
            archivos={p:(p.stat().st_mtime_ns,hashlib.sha256(p.read_bytes()).hexdigest()) for p in salida.rglob('*') if p.is_file()}
            with patch.object(e['Pipeline'],'fit',side_effect=AssertionError('No volver a entrenar')),patch.object(e['XGBClassifier'],'predict_proba',side_effect=AssertionError('No repetir inferencia')):
                leido=e['ejecutar_final'](raiz,salida,cfg,autorizar=False)
            self.assertTrue(leido['reutilizado'])
            pd.testing.assert_frame_equal(r['datos'],leido['datos'])
            self.assertEqual(archivos,{p:(p.stat().st_mtime_ns,hashlib.sha256(p.read_bytes()).hexdigest()) for p in archivos})

    def test_imputacion_solo_desarrollo_y_modelo_guardado(self):
        e=entorno_final()
        with tempfile.TemporaryDirectory(dir=TEMP_ROOT) as c:
            raiz,salida,cfg=fixture_final(c,e)
            r=e['ejecutar_final'](raiz,salida,cfg,autorizar=True)
            _,_,Xdes,Xtest=e['leer_datos_final'](raiz,cfg)
            cargado=e['joblib'].load(salida/'test_final/pipeline.joblib')
            np.testing.assert_allclose(cargado.named_steps['imputacion'].statistics_,np.nanmedian(Xdes,axis=0))
            self.assertLess(cargado.named_steps['imputacion'].statistics_[0],10)
            self.assertGreater(np.nanmedian(Xtest.iloc[:,0]),1000)
            self.assertTrue(json.loads((salida/'test_final/verificacion_serializacion.json').read_text())['iguales'])
            pesos=pd.read_csv(salida/'test_final/pesos_desarrollo.csv')
            self.assertEqual(pesos.epochs.sum(),180)
            self.assertEqual(r['metricas']['epochs'],60)

    def test_falla_tras_apertura_no_se_reintenta(self):
        e=entorno_final()
        with tempfile.TemporaryDirectory(dir=TEMP_ROOT) as c:
            raiz,salida,cfg=fixture_final(c,e)
            original=e['XGBClassifier'].predict_proba
            def fallar(modelo,X,**kwargs):
                if len(X)==60: raise RuntimeError('falla simulada')
                return original(modelo,X,**kwargs)
            with patch.object(e['XGBClassifier'],'predict_proba',new=fallar):
                with self.assertRaisesRegex(RuntimeError,'falla simulada'):
                    e['ejecutar_final'](raiz,salida,cfg,autorizar=True)
            self.assertEqual(json.loads((salida/'test_abierto.json').read_text())['estado'],'abierto')
            self.assertFalse((salida/'predicciones_test.csv').exists())
            with patch.object(e['Pipeline'],'fit',side_effect=AssertionError('No reintentar')):
                with self.assertRaisesRegex(RuntimeError,'incompleta'):
                    e['ejecutar_final'](raiz,salida,cfg,autorizar=True)

    def test_detecta_resultados_alterados_y_configuracion_diferente(self):
        e=entorno_final()
        with tempfile.TemporaryDirectory(dir=TEMP_ROOT) as c:
            raiz,salida,cfg=fixture_final(c,e)
            e['ejecutar_final'](raiz,salida,cfg,autorizar=True)
            otra=json.loads(json.dumps(cfg)); otra['parametros']['max_depth']=3
            with self.assertRaisesRegex(ValueError,'configuración'):
                e['ejecutar_final'](raiz,salida,otra)
            with (salida/'predicciones_test.csv').open('ab') as archivo: archivo.write(b'\n')
            with self.assertRaisesRegex(ValueError,'protegido'):
                e['ejecutar_final'](raiz,salida,cfg)

    def test_historia_coincide_con_experimentos_previos(self):
        e=entorno_final()
        with tempfile.TemporaryDirectory(dir=TEMP_ROOT) as c:
            raiz,_,cfg=fixture_final(c,e)
            antiguo=anteriores.ModeladoTest().entorno(raiz)
            t=pd.read_csv(raiz/'etl_v1/dataset_modelado_candidato.csv')
            X=t[cfg['columnas_actuales']]
            esperado,_=antiguo['agregar_historia'](X,t,[1,2])
            obtenido=e['historia_final'](X,t,[1,2])
            pd.testing.assert_frame_equal(esperado,obtenido)
            self.assertTrue(obtenido.iloc[8].filter(like='__lag').isna().any())
            cambiado=X.copy(); cambiado.iloc[20:]=99999
            otra=e['historia_final'](cambiado,t,[1,2])
            pd.testing.assert_frame_equal(obtenido.iloc[:20],otra.iloc[:20])

    def test_datos_con_fuente_o_columnas_diferentes_se_rechazan(self):
        e=entorno_final()
        with tempfile.TemporaryDirectory(dir=TEMP_ROOT) as c:
            raiz,_,cfg=fixture_final(c,e)
            otra=json.loads(json.dumps(cfg)); otra['columnas']=list(reversed(otra['columnas']))
            with self.assertRaisesRegex(ValueError,'Orden de columnas'):
                e['leer_datos_final'](raiz,otra)
            ruta=raiz/'etl_v1/dataset_modelado_candidato.csv'
            with ruta.open('ab') as archivo: archivo.write(b'\n')
            with self.assertRaisesRegex(ValueError,'fuente'):
                e['leer_datos_final'](raiz,cfg)


if __name__=='__main__': unittest.main()
