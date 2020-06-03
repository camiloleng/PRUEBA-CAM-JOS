# ================================================================================
# Author: 	   Camilo Leng Olivares
# Last update: 28-05-2020
# Description: Construir perfiles de carga corregidos.
# ================================================================================

import pandas as pd
import numpy as np

pd.set_option('display.max_rows', 500)
pd.set_option('display.max_columns', 500)
pd.set_option('display.width', 150)

PATH1 = '00 DATOS/PERFILES DE CARGA PROMEDIO_AGO19.csv'
PATH2 = '00 DATOS/ESTIMACION EVASION EMME AGO19.csv'
PATH3 = '03 RESULTADOS/MATRIZ PROBABILIDADES.csv'
PATH4 = '03 RESULTADOS/FACTOR DE EXPANSION Y REDUCCION.csv'

EV_COL = ['periodo','paradero','factor_ev_parada']
MP_COL = ['periodo','serviciosentido','par_subida','par_bajada','correlativo_sub','correlativo_baj','probabilidad']
FF_COL = ['periodo','serviciosentido', 'fmax', 'fmin']

# leer datos
df = pd.read_csv(PATH1, sep=';')					# PERFILES MODELADOS (ADATRAP).
ev = pd.read_csv(PATH2, sep=';', usecols=EV_COL)	# EVASIÓN (EMME).
mp = pd.read_csv(PATH3, sep=';', usecols=MP_COL)	# MATRIZ DE PROBABILIDADES (ADATRAP).
ff = pd.read_csv(PATH4, sep=';', usecols=FF_COL)	# FACTORES DE EXPANSION Y REDUCCIÓN (ADATRAP).


# seleccionar solo servicios normales y de punta mañana (00: Normal, 01: PM, 02: PT).
df = df[df['serviciosentido'].str[-3:-1].isin(['00','01','02'])]

# mantener servicio-sentidos con al menos 5 expediciones por periodo.
df = df[df['nexpediciones']>4]

# corregir formato de columna "paradero": L-4-13-2-OP >> L-4-13-OP-2
def CorrCodTSGO(df, column='paradero'):
	x = df[column].str.split('-', expand=True)
	df.loc[df[column].str[-2:].isin(['NS', 'SN', 'PO', 'OP']), column] = x[0]+'-'+x[1]+'-'+x[2]+'-'+x[4]+'-'+x[3]
	return df

df = CorrCodTSGO(df, 'paradero')
ev = CorrCodTSGO(ev, 'paradero')


# CALCULAR PERFIL PROMEDIO. =======================================================================

# corregir inicio de subidas y bajadas promedio según carga promedio de adatrap.
df.loc[
	(df['correlativo']==1) &
	(df['subidaspromedio']-df['bajadaspromedio']!=df['cargapromedio_adtp']) & 
	(df['subidaspromedio']<df['cargapromedio_adtp']), 
	'subidaspromedio'] = df['cargapromedio_adtp'] + df['bajadaspromedio']

df.loc[
	(df['correlativo']==1) &
	(df['subidaspromedio']-df['bajadaspromedio']!=df['cargapromedio_adtp']) & 
	(df['subidaspromedio']>=df['cargapromedio_adtp']), 
	'bajadaspromedio'] = df['subidaspromedio'] - df['cargapromedio_adtp']

# calcular carga promedio sin corrección por evasión.
df['cargapromedio'] = df.groupby(['periodo','serviciosentido'])['subidaspromedio'].cumsum() - df.groupby(['periodo','serviciosentido'])['bajadaspromedio'].cumsum()


# ESTIMAR EVASIÓN POR SS-PARADA Y DISTRIBUIR EN PARADAS POSTERIORES. ==============================

# cruzar subidas y bajadas promedio con evasión por paradero.
df = pd.merge(df, ev, on=['periodo','paradero'], indicator=True) # both: all

# calcular cantidad de evasores por servicio, sentido y parada.
df['subidasevasion'] = df['subidaspromedio'] * df['factor_ev_parada']

# cruzar subidas de evasores con matriz de probabilidad de bajada.
aux = df.loc[df['subidasevasion']>0,['periodo','serviciosentido','paradero','correlativo','subidasevasion']]
aux.rename({'paradero':'par_subida', 'correlativo':'correlativo_sub'}, axis=1, inplace=True)
mp = pd.merge(mp, aux, on=['periodo','serviciosentido','par_subida','correlativo_sub'], how='right', indicator=True)
del aux

# en caso de no existir la distribución de bajada de una parada, asignar la de la parada siguiente.
mp = mp.sort_values(['periodo','serviciosentido','correlativo_sub','correlativo_baj']).reset_index(drop=True)
mp['correlativo_sig'] = mp.groupby(['periodo','serviciosentido'])['correlativo_sub'].shift(-1)

# extraer servicios-paradas que no encontraron distribución de bajada.
aux1 = mp.loc[mp['_merge']=='right_only', ['periodo','serviciosentido','correlativo_sub','correlativo_sig']]
aux1. rename({'correlativo_sub':'correlativo_sininfo', 'correlativo_sig':'correlativo_sub'}, axis=1, inplace=True)

aux2 = mp[['periodo','serviciosentido','correlativo_sub','par_bajada','probabilidad']]

# extraer la distribución de bajada de las paradas siguientes.
aux3 = pd.merge(aux1, aux2, on=['periodo','serviciosentido','correlativo_sub'])
aux3 = aux3.drop('correlativo_sub', axis=1).rename({'correlativo_sininfo':'correlativo_sub'}, axis=1)

# cruzar la distribución de la parada siguiente con la parada que no encontró distribución.
mp = mp.merge(aux3, on=['periodo','serviciosentido','correlativo_sub'], how='outer')

# reconstruir variables.
mp['probabilidad'] = mp['probabilidad_x']
mp['par_bajada'] = mp['par_bajada_x']
mp.loc[mp['probabilidad'].isnull(), 'probabilidad'] = mp['probabilidad_y']
mp.loc[mp['par_bajada'].isnull(), 'par_bajada'] = mp['par_bajada_y']

# calcular bajadas de evasores según servicio, sentido y parada de subida.
mp['bajadasevasion'] = mp['subidasevasion'] * mp['probabilidad']
mp = mp.groupby(['periodo','serviciosentido','par_bajada'], as_index=False)['bajadasevasion'].sum()

# cruzar bajadas de evasores con perfiles de carga.
mp.rename({'par_bajada':'paradero'}, axis=1, inplace=True)
df = pd.merge(df, mp, how='left', on=['periodo','serviciosentido', 'paradero'])
df['bajadasevasion'].fillna(0, inplace=True)


# CALCULAR CARGA PROMEDIO CORREGIDA CON SU RESPECTIVA BANDA DE ERROR. =============================

# calcular carga promedio con corrección por evasión.
df['subidascorregidas'] = df['subidaspromedio'] + df['subidasevasion']
df['bajadascorregidas'] = df['bajadaspromedio'] + df['bajadasevasion']

df.sort_values(['periodo','serviciosentido', 'correlativo'], inplace=True)
df['cargacorregida'] = df.groupby(['periodo','serviciosentido'])['subidascorregidas'].cumsum() - df.groupby(['periodo','serviciosentido'])['bajadascorregidas'].cumsum()

# cruzar con ponderadores y calcular los perfiles de carga máximos y mínimos.
df = pd.merge(df, ff, on=['periodo','serviciosentido'])
df['cargamax'] = df['cargacorregida'] * df['fmax']
df['cargamin'] = df['cargacorregida'] * df['fmin']

# ordenar y guardar resultados.
df.sort_values(['periodo','serviciosentido', 'correlativo'], inplace=True)
df.to_csv('03 RESULTADOS/PERFILES DE CARGA (1).csv', sep=';', index=False)
