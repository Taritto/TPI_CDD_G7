"""Pruebas del código real del notebook, sin reimplementar su evaluación."""
import ast
import json
from pathlib import Path
import tempfile
import unittest
import sys
from unittest.mock import patch
import matplotlib
matplotlib.use('Agg')

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'output/modelado-deps'))
NOTEBOOK = json.loads((ROOT / 'temporal_version_tp_entrega03.ipynb').read_text(encoding='utf-8'))
TEMP_ROOT = ROOT / 'output' / 'verificacion'
TEMP_ROOT.mkdir(parents=True, exist_ok=True)


def fuente(prefijo):
    coincidencias = [''.join(c['source']) for c in NOTEBOOK['cells']
                     if c['cell_type'] == 'code' and ''.join(c['source']).startswith(prefijo)]
    if len(coincidencias) != 1:
        raise AssertionError(f'Celda no identificada de forma única: {prefijo}')
    return coincidencias[0]


class ModeladoTest(unittest.TestCase):
    def entorno(self, carpeta):
        # Importar y definir funciones reales sin ejecutar carga de archivos ni entrenamientos.
        espacio = {'__name__': 'verificacion_notebook'}
        arbol = ast.parse(fuente('from pathlib import Path'))
        permitidos = [n for n in arbol.body if isinstance(n, (ast.Import, ast.ImportFrom, ast.FunctionDef))]
        exec(compile(ast.Module(body=permitidos, type_ignores=[]), '<imports>', 'exec'), espacio)
        exec("SEMILLA=42\nN_SPLITS=5\nETAPAS=['W','N1','N2','N3','R']\nCLAVES=['patient_id','epoch']", espacio)
        espacio['SALIDA'] = Path(carpeta)
        pd, np = espacio['pd'], espacio['np']
        rng = np.random.default_rng(42)
        dev = pd.DataFrame({'patient_id': np.repeat(np.arange(20), 10),
                            'epoch': np.tile(np.arange(10), 20),
                            'tiempo_relativo_segundos': np.tile(np.arange(10) * 30, 20),
                            'Sleep_Stage': np.tile(espacio['ETAPAS'], 40)})
        y = dev.Sleep_Stage.map({e:i for i,e in enumerate(espacio['ETAPAS'])}).to_numpy()
        X = pd.DataFrame({'senal': y + rng.normal(0, .3, len(y)), 'ruido': rng.normal(size=len(y))})
        espacio.update(dev=dev, y=y, X=X, folds={
            'pacientes': list(espacio['StratifiedGroupKFold'](5, shuffle=True, random_state=42).split(X,y,dev.patient_id)),
            'epochs': list(espacio['StratifiedKFold'](5, shuffle=True, random_state=42).split(X,y))})
        exec(fuente('def crear_pipeline('), espacio)
        espacio.update(ajustes={}, opciones_experimento={})
        return espacio

    def test_sintaxis_y_test_desactivado(self):
        for i, celda in enumerate(NOTEBOOK['cells']):
            if celda['cell_type'] == 'code':
                compile(''.join(celda['source']), f'celda_{i}', 'exec')
        self.assertIn('AUTORIZAR_APERTURA_TEST_FINAL = False', fuente('# 4.8'))

    def test_evaluacion_oof_pesos_y_probabilidades(self):
        with tempfile.TemporaryDirectory(dir=TEMP_ROOT) as carpeta:
            e = self.entorno(carpeta)
            for protocolo in e['folds']:
                r = e['evaluar'](e['RandomForestClassifier'](n_estimators=5, max_depth=3, random_state=42),
                                 e['X'], protocolo, protocolo, pesos=True, importancia=True)
                self.assertEqual(len(r['oof']), len(e['dev']))
                self.assertFalse(r['oof'].duplicated(e['CLAVES']).any())
                self.assertEqual(len(r['metricas']), 10)
                self.assertEqual(len(r['etapas']), 50)
                self.assertEqual(len(r['importancia']), 5 * 5 * 2)
                self.assertTrue(e['np'].allclose(r['oof'].filter(like='prob_').sum(axis=1), 1))
                self.assertEqual(set(r['metricas'].conjunto), {'entrenamiento', 'validacion'})
                if protocolo == 'pacientes':
                    for tr, va in e['folds'][protocolo]:
                        self.assertFalse(set(e['dev'].iloc[tr].patient_id) & set(e['dev'].iloc[va].patient_id))

    def test_rechaza_fuga_y_no_finitos(self):
        with tempfile.TemporaryDirectory(dir=TEMP_ROOT) as carpeta:
            e = self.entorno(carpeta)
            modelo = e['DummyClassifier']()
            with self.assertRaisesRegex(ValueError, 'Identificador'):
                e['evaluar'](modelo, e['X'].assign(patient_id=1), 'fuga', 'pacientes')
            invalido = e['X'].copy()
            invalido.iloc[0,0] = float('nan')
            with self.assertRaisesRegex(ValueError, 'no finitas'):
                e['evaluar'](modelo, invalido, 'nulos', 'pacientes')

    def test_cohortes_incompatibles_se_detienen_antes_de_dividir(self):
        with tempfile.TemporaryDirectory(dir=TEMP_ROOT) as carpeta:
            e = self.entorno(carpeta)
            e['base'] = e['dev'].copy()
            e['candidato'] = e['dev'].iloc[:-1].copy()
            with self.assertRaisesRegex(ValueError, 'misma cohorte'):
                exec(fuente('columnas_principal ='), e)
            self.assertFalse((Path(carpeta) / 'asignacion_pacientes.json').exists())

    def test_particion_sintetica_y_reutilizacion(self):
        with tempfile.TemporaryDirectory(dir=TEMP_ROOT) as carpeta:
            e = self.entorno(carpeta)
            base = e['dev'].copy()
            # Columnas completas necesarias para ejecutar la celda real de controles.
            arbol = ast.parse(fuente('columnas_principal ='))
            columnas = ast.literal_eval(arbol.body[0].value)
            for c in columnas:
                base[c] = 1.0
            e.update(base=base.copy(), candidato=base.copy(), ruta_base=Path(carpeta)/'base.csv',
                     ruta_candidato=Path(carpeta)/'candidato.csv')
            base.to_csv(e['ruta_base'], index=False)
            base.to_csv(e['ruta_candidato'], index=False)
            exec(fuente('columnas_principal ='), e)
            self.assertFalse(set(e['dev'].patient_id) & set(e['test'].patient_id))
            original = (Path(carpeta)/'asignacion_pacientes.json').read_text()
            exec(fuente('columnas_principal ='), e)
            self.assertEqual(original, (Path(carpeta)/'asignacion_pacientes.json').read_text())

    def test_tablas_html_no_heredan_truncamiento_de_pandas(self):
        with tempfile.TemporaryDirectory(dir=TEMP_ROOT) as carpeta:
            e = self.entorno(carpeta)
            mostrados = []
            e['display'] = mostrados.append
            tabla = e['pd'].DataFrame(e['np'].arange(2000).reshape(100,20) / 10)
            with e['pd'].option_context('display.max_rows', 1, 'display.max_columns', 1):
                e['mostrar_tabla'](tabla, 'Tabla completa')
            html = [x.data for x in mostrados if isinstance(x, e['HTML'])][0]
            self.assertEqual(html.count('<tr>'), 100)
            self.assertEqual(html.count('<td>'), 2000)
            self.assertIn('199.9000', html)
            self.assertNotIn('...', html)

    def test_presentacion_modelo_y_comparacion_controlada(self):
        with tempfile.TemporaryDirectory(dir=TEMP_ROOT) as carpeta:
            e = self.entorno(carpeta)
            modelo = e['DummyClassifier'](strategy='most_frequent')
            r = e['evaluar'](modelo, e['X'], 'pacientes_Baseline_pesos0', 'pacientes')
            mostrados = []
            e['display'] = mostrados.append
            e['mostrar_resultados_modelo'](r)
            tablas = [x.data for x in mostrados if isinstance(x, e['HTML'])]
            self.assertEqual(len(tablas), 4)
            self.assertIn('F1 macro', tablas[0])
            self.assertIn('Desviación estándar', tablas[1])
            self.assertIn('Brecha', tablas[2])
            self.assertIn('REM', tablas[3])
            control = e['comparar_prueba']('pacientes_Baseline_pesos0',r,'referencia',r,'Control','Repetición')
            self.assertEqual(control['delta_f1'], 0)
            self.assertEqual(control['delta_brecha'], 0)
            self.assertEqual(control['delta_segundos'], 0)
            protocolo = e['comparar_prueba']('epochs_Baseline_pesos0',r,'referencia',r,'Protocolo','División')
            self.assertIsNone(protocolo['folds_mejora'])

    def test_historia_respeta_paciente_huecos_y_causalidad(self):
        with tempfile.TemporaryDirectory(dir=TEMP_ROOT) as carpeta:
            e = self.entorno(carpeta)
            tabla = e['pd'].DataFrame({'patient_id':[1]*6+[2]*4,
                'tiempo_relativo_segundos':[0,30,60,200,230,260,0,30,60,90]})
            entradas = e['pd'].DataFrame({'senal':range(10)})
            enriquecida,cobertura = e['agregar_historia'](entradas,tabla,[1])
            self.assertTrue(e['np'].isnan(enriquecida.loc[0,'senal__lag1m']))
            self.assertEqual(enriquecida.loc[2,'senal__lag1m'],0)
            self.assertTrue(e['np'].isnan(enriquecida.loc[3,'senal__lag1m']))
            self.assertTrue(e['np'].isnan(enriquecida.loc[6,'senal__lag1m']))
            self.assertEqual(enriquecida.loc[5,'senal__lag1m'],3)
            modificada = entradas.copy()
            modificada.loc[5:,'senal'] = 9999
            otra,_ = e['agregar_historia'](modificada,tabla,[1])
            e['pd'].testing.assert_series_equal(enriquecida.loc[:4,'senal__lag1m'],otra.loc[:4,'senal__lag1m'])
            self.assertEqual(cobertura.disponibles.iloc[0],4)

    def test_cronologia_gap_y_oof_solo_elegibles(self):
        with tempfile.TemporaryDirectory(dir=TEMP_ROOT) as carpeta:
            e = self.entorno(carpeta)
            np,pd = e['np'],e['pd']
            tabla = pd.DataFrame({'patient_id':np.repeat([1,2],360),
                'epoch':np.tile(np.arange(360),2),
                'tiempo_relativo_segundos':np.tile(np.arange(360)*30,2)})
            rondas,bloques = e['particiones_cronologicas'](tabla)
            visitas = np.zeros(len(tabla),dtype=int)
            for tr,va in rondas:
                visitas[va]+=1
                for paciente in [1,2]:
                    a=tabla.iloc[tr].query('patient_id == @paciente').tiempo_relativo_segundos
                    b=tabla.iloc[va].query('patient_id == @paciente').tiempo_relativo_segundos
                    self.assertLess(a.max(),b.min()-900)
            self.assertTrue(np.array_equal(visitas,(bloques>0).astype(int)))
            e.update(dev=tabla,y=np.tile(np.arange(5),144),
                folds={'temporal':rondas})
            entradas=pd.DataFrame({'senal':np.arange(len(tabla))%5})
            r=e['evaluar'](e['DummyClassifier'](strategy='most_frequent'),entradas,
                'cronologia','temporal',mostrar_progreso=False)
            self.assertEqual(len(r['oof']),600)
            self.assertTrue(np.array_equal(r['oof'].index,np.flatnonzero(bloques>0)))

    def test_smote_solo_entrenamiento_y_metricas_sobre_reales(self):
        from imblearn.over_sampling import SMOTE
        with tempfile.TemporaryDirectory(dir=TEMP_ROOT) as carpeta:
            e = self.entorno(carpeta)
            e['y'][:20] = 2
            e['folds']={'epochs':list(e['StratifiedKFold'](5,shuffle=True,random_state=42).split(e['X'],e['y']))}
            llamadas=[]
            original=SMOTE.fit_resample
            def observar(instancia,X,y,**kwargs):
                llamadas.append((len(X),e['np'].bincount(y,minlength=5)))
                return original(instancia,X,y,**kwargs)
            with patch.object(SMOTE,'fit_resample',new=observar):
                r=e['evaluar'](e['RandomForestClassifier'](n_estimators=5,random_state=42),
                    e['X'],'smote_RF_prueba','epochs',smote={'ratio':1.,'k':3},mostrar_progreso=False)
            self.assertEqual(len(llamadas),5)
            self.assertTrue(all(cantidad==160 for cantidad,_ in llamadas))
            self.assertEqual(len(r['oof']),200)
            self.assertGreater(r['muestreo'].sinteticos.sum(),0)
            for fold,datos in r['etapas'].groupby('fold'):
                self.assertEqual(datos.query("conjunto == 'entrenamiento'").soporte.sum(),160)
                self.assertEqual(datos.query("conjunto == 'validacion'").soporte.sum(),40)
            with self.assertRaisesRegex(ValueError,'SMOTE y pesos'):
                e['evaluar'](e['DummyClassifier'](),e['X'],'doble','epochs',pesos=True,smote={'ratio':1.,'k':3})

    def test_imputacion_aprende_solo_entrenamiento_y_conserva_columnas_vacias(self):
        with tempfile.TemporaryDirectory(dir=TEMP_ROOT) as carpeta:
            e=self.entorno(carpeta)
            pd,np=e['pd'],e['np']
            tr=pd.DataFrame({'actual':[1.,2.,3.,4.,5.], 'pasado':[np.nan,2.,4.,np.nan,6.],
                             'sin_historia':[np.nan]*5})
            va=pd.DataFrame({'actual':[1000.], 'pasado':[np.nan], 'sin_historia':[np.nan]})
            pipe=e['crear_pipeline'](e['DummyClassifier'](strategy='most_frequent'),imputar=True)
            pipe.fit(tr,np.arange(5))
            imputer=pipe.named_steps['imputacion']
            self.assertEqual(imputer.statistics_[1],4.)
            self.assertEqual(imputer.transform(va).shape,(1,3))
            self.assertTrue(np.isfinite(imputer.transform(va)).all())
            self.assertEqual(imputer.transform(va)[0,1],4.)

    def test_smote_y_xgboost_comparten_pipeline_de_inferencia(self):
        from xgboost import XGBClassifier
        with tempfile.TemporaryDirectory(dir=TEMP_ROOT) as carpeta:
            e=self.entorno(carpeta)
            modelo=XGBClassifier(n_estimators=3,max_depth=2,n_jobs=1,
                objective='multi:softprob',num_class=5,random_state=42,tree_method='hist')
            pipe=e['crear_pipeline'](modelo,smote={'k':3,'cantidades':{c:60 for c in range(5)}})
            pipe.fit(e['X'],e['y'])
            prob=pipe.predict_proba(e['X'])
            self.assertEqual(prob.shape,(200,5))
            self.assertTrue(e['np'].allclose(prob.sum(axis=1),1))
            self.assertEqual(len(pipe.predict(e['X'])),200)


if __name__ == '__main__':
    unittest.main()
