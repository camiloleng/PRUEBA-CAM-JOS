# ================================================================================
# Author: 	   Camilo Leng Olivares
# Last update: 28-05-2020
# Description: Cruzar información de perfiles con mediciones.
# ================================================================================

import pandas as pd
import numpy as np

# pd.set_option('display.height', 1000)
pd.set_option('display.max_rows', 500)
pd.set_option('display.max_columns', 500)
pd.set_option('display.width', 150)

PATH1 = '03 RESULTADOS/PERFILES DE CARGA (1).csv'
PATH2 = '01 TOCS/02 RESULTADOS/TOC (HPASADA).csv'
PATH3 = '02 PERFILES OTS/PERFILES DE CARGA OT.csv'
PATH4 = '02 PERFILES OTS/PERFILES DE CARGA DICTUC 2012.csv'

# leer datos
df = pd.read_csv(PATH1, sep=';')		# PERFILES CORREGIDOS.
af = pd.read_csv(PATH2, sep=';')		# TASAS DE OCUPACIÓN MEDIDAS.
pc = pd.read_csv(PATH3, sep=';')		# PERFILES DE CARGA MEDIDOS.
di = pd.read_csv(PATH4, sep=';')		# PERFILES DE CARGA ESTUDIO DICTUC 2012.


PERIODOS=[4,6,9]

df_FINAL= pd.DataFrame([])
for j in PERIODOS:

	# seleccionar periodo (4:PUNTA MAÑANA, 6:FUERA PUNTA, 9:PUNTA TARDE).
	af2 = af[af['periodo']==j].copy()
	pc2 = pc[pc['periodo']==j].copy()
	df2 = df[df['periodo']==j].copy()

	''' NO SE REALIZA ESTE PASO DEBIDO A QUE NO ES NECESARIO SEGUN LA DATA QUE SE UTILIZA

	# cambiar nombre de servicios en PM.
	'''
	df['servicioPM'] = (df['serviciousuariots'].str[-2:]=='PM')
	df.loc[df['servicioPM'], 'serviciousuariots'] = df['serviciousuariots'].str[:-2]
	# mantener la última medición de tasa de ocupación por servicio, sentido, parada.
	af2.sort_values('fecha', inplace=True)
	af2.drop_duplicates(['serviciousuariots', 'paradero'], keep='last', inplace=True)

	# cruzar información de tasas de ocupación de perfiles corregidos.
	af2 = af2[['serviciousuariots', 'paradero', 'ot', 'toc', 'IC']]
	df2 = pd.merge(df2, af2, on=['serviciousuariots', 'paradero'], how='left')

	# cruzar con mediciones de perfiles de carga en OTs anteriores.
	di.rename({'carga':'DICTUC2012'}, axis=1, inplace=True)
	di = di[['serviciousuariots', 'paradero', 'DICTUC2012']]
	df2 = df2.merge(di, on=['serviciousuariots', 'paradero'], how='left')

	# pivotear perfiles de carga de OTs.
	pc2['key'] = pc2['serviciousuariots'] + '~' + pc2['paraderousuario']
	pc2 = pc2.pivot('key', 'ot', 'carga').reset_index()

	# recuperar formato.
	pc2['serviciousuariots'] = pc2['key'].str.split('~', expand=True)[0]
	pc2['paraderousuario']   = pc2['key'].str.split('~', expand=True)[1]
	pc2.drop('key', axis=1, inplace=True)

	# cruzar perfil de carga ADATRAP con perfiles de carga OTs.
	df2 = df2.merge(pc2, on=['serviciousuariots', 'paraderousuario'], how='left')
	# guardar resultados.
	df2.to_csv('03 RESULTADOS/PERFILES DE CARGA (2) P-{}.csv'.format(j), sep=';', index=False)
	columnas= df2.columns
	df_FINAL = df_FINAL.append(df2, ignore_index=True, sort=True)


df_FINAL=df_FINAL[columnas]
df_FINAL.to_csv('03 RESULTADOS/PERFILES DE CARGA (2).csv', sep=';', index=False)



