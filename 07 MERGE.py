# ================================================================================
# Author: 	   Camilo Leng Olivares
# Last update: 28-05-2020
# Description: Cruzar información de perfiles con mediciones.
# ================================================================================

import pandas as pd
import numpy as np

pd.set_option('display.height', 1000)
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

# seleccionar periodo (4:PUNTA MAÑANA).
af = af[af['periodo']==4]
pc = pc[pc['periodo']==4]

# cambiar nombre de servicios en PM.
df['servicioPM'] = (df['serviciousuariots'].str[-2:]=='PM')
df.loc[df['servicioPM'], 'serviciousuariots'] = df['serviciousuariots'].str[:-2]

# mantener la última medición de tasa de ocupación por servicio, sentido, parada.
af.sort_values('fecha', inplace=True)
af.drop_duplicates(['serviciousuariots', 'paradero'], keep='last', inplace=True)

# cruzar información de tasas de ocupación de perfiles corregidos.
af = af[['serviciousuariots', 'paradero', 'ot', 'toc', 'IC']]
df = pd.merge(df, af, on=['serviciousuariots', 'paradero'], how='left')

# cruzar con mediciones de perfiles de carga en OTs anteriores.
di.rename({'carga':'DICTUC2012'}, axis=1, inplace=True)
di = di[['serviciousuariots', 'paradero', 'DICTUC2012']]
df = df.merge(di, on=['serviciousuariots', 'paradero'], how='left')

# pivotear perfiles de carga de OTs.
pc['key'] = pc['serviciousuariots'] + '~' + pc['paraderousuario']
pc = pc.pivot('key', 'ot', 'carga').reset_index()

# recuperar formato.
pc['serviciousuariots'] = pc['key'].str.split('~', expand=True)[0]
pc['paraderousuario']   = pc['key'].str.split('~', expand=True)[1]
pc.drop('key', axis=1, inplace=True)

# cruzar perfil de carga ADATRAP con perfiles de carga OTs.
df = df.merge(pc, on=['serviciousuariots', 'paraderousuario'], how='left')

# guardar resultados.
df.to_csv('03 RESULTADOS/PERFILES DE CARGA (2).csv', sep=';', index=False)
