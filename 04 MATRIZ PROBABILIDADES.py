# ================================================================================
# Author: 	   Camilo Leng Olivares
# Last update: 28-05-2020
# Description: Construir matriz de probabilidades de bajada.
# ================================================================================

import pandas as pd

pd.set_option('display.max_rows', 500)
pd.set_option('display.max_columns', 500)
pd.set_option('display.width', 150)

# CORREGIR FORMATO DE COLUMNA PARADERO: L-4-13-2-OP >> L-4-13-OP-2
def CorrCodTSGO(df, column='paradero'):
	x = df[column].str.split('-', expand=True)
	df.loc[df[column].str[-2:].isin(['NS', 'SN', 'PO', 'OP']), column] = x[0]+'-'+x[1]+'-'+x[2]+'-'+x[4]+'-'+x[3]
	return df

PATH1 = '00 DATOS/MOD_PERIODO-SERVICIO-PARADA_AGO19.csv'
PATH2 = '00 DATOS/PERFILES DE CARGA PROMEDIO_AGO19.csv'

COLS2 = ['periodo','serviciosentido', 'paradero', 'correlativo']

df = pd.read_csv(PATH1, sep=';')
op = pd.read_csv(PATH2, sep=';', usecols=COLS2)		# Orden Paradas

# corregir formato de periodos
df['periodo'] = df['periodo'].str[:2].astype(int)

# seleccionar periodos de interes (PM: 4, FP: 6, PT: 9)
df = df[df['periodo'].isin([4,6,9])]
op = op[op['periodo'].isin([4,6,9])]

# corregir formato de paraderos.
df = CorrCodTSGO(df, 'par_subida')
df = CorrCodTSGO(df, 'par_bajada')
op = CorrCodTSGO(op, 'paradero')

# eliminar secuencia de paradas duplicadas por periodos.
op.drop_duplicates(inplace=True)

# eliminar pares origen-destino que no estén en el orden de avance del servicio.
df = df.merge(op, left_on=['periodo','serviciosentido', 'par_subida'], right_on=['periodo','serviciosentido', 'paradero'], how='left')
df = df.merge(op, left_on=['periodo','serviciosentido', 'par_bajada'], right_on=['periodo','serviciosentido', 'paradero'], how='left', suffixes=['_sub', '_baj'])

df = df[df['correlativo_sub']<df['correlativo_baj']]
df.drop(['paradero_sub', 'paradero_baj'], axis=1, inplace=True)

# calcular probabilidad de bajada utilizando la demanda potencial por parada de subida y bajada.
df['dda_OD'] = df.groupby(['periodo','par_subida', 'par_bajada'])['netapas'].transform(sum)
df['total_sub'] = df.groupby(['periodo','serviciosentido', 'par_subida'])['dda_OD'].transform(sum)

df['probabilidad'] = df['dda_OD'] / df['total_sub']

# ordenar y guardar matriz de probabilidades de bajadas.
df.sort_values(['periodo','serviciosentido', 'correlativo_sub', 'correlativo_baj'], inplace=True)
df.to_csv('03 RESULTADOS/MATRIZ PROBABILIDADES.csv', sep=';', index=False)
