# ================================================================================
# Author: 	   Camilo Leng Olivares
# Description: Corregir perfiles en Zonas Pagas.
# ================================================================================

import pandas as pd
import numpy as np

pd.set_option('display.max_rows', 500)
pd.set_option('display.max_columns', 500)
pd.set_option('display.width', 150)

PATH1 = '03 RESULTADOS/PERFILES DE CARGA (2).csv'
PATH2 = '03 RESULTADOS/MATRIZ PROBABILIDADES.csv'

COLUMNS1 = ['periodo','serviciosentido','paradero','correlativo','zp','metro','subidascorregidas','bajadascorregidas','cargacorregida','toc']


# Leer datos.
data = pd.read_csv(PATH1, sep=';')
mp 	 = pd.read_csv(PATH2, sep=';')

df = data[COLUMNS1].copy()

# Identificar primera parada por servicio donde exista una medición TOC y sea ZP.
df.loc[df[(df['zp']==1)&(df['toc'].notnull())].groupby(['serviciosentido'])['correlativo'].idxmin(), 'edit'] = True
df.loc[df['edit'].isnull(), 'edit'] = False

# Calcular diferencia de pasajeros.
df.loc[(df['edit']) & (df['toc']>df['cargacorregida']), 'subidasTOC'] = df['toc'] - df['cargacorregida']
df['subidasTOC'].fillna(0, inplace=True)

# Cruzar subidas de TOC con matriz de probabilidad de bajada.
aux = df[['periodo','serviciosentido', 'paradero', 'subidasTOC']].rename({'paradero':'par_subida'}, axis=1)
mp = pd.merge(mp, aux, how='left', on=['periodo','serviciosentido', 'par_subida'])

# Calculadr bajadas de TOC según periodo - servicio - sentido - parada de subida.
mp['bajadasTOC'] = mp['subidasTOC'] * mp['probabilidad']

mp = mp[['periodo','serviciosentido', 'par_bajada', 'bajadasTOC']].rename({'par_bajada':'paradero'}, axis=1)
mp = mp.groupby(['periodo','serviciosentido', 'paradero'], as_index=False).sum()

# Cruzar bajadas de TOC con perfiles de carga.
df = pd.merge(df, mp, how='left', on=['periodo','serviciosentido', 'paradero'])
df['bajadasTOC'].fillna(0, inplace=True)

# Calcular carga promedio con corrección por TOC.
df['subidasTOCcorregidas'] = df['subidascorregidas'] + df['subidasTOC']
df['bajadasTOCcorregidas'] = df['bajadascorregidas'] + df['bajadasTOC']

df.sort_values(['periodo','serviciosentido','correlativo'], inplace=True)
df['cargaTOCcorregida'] = df.groupby(['periodo','serviciosentido'])['subidasTOCcorregidas'].cumsum() - df.groupby(['periodo','serviciosentido'])['bajadasTOCcorregidas'].cumsum()

# Seleccionar perfiles modificados.
keep = df.loc[(df['edit']) & (df['toc']>df['cargacorregida']), ['periodo','serviciosentido']].drop_duplicates()
df = df.merge(keep, on=['periodo','serviciosentido'])

# Guardar resultados.
df.to_csv('03 RESULTADOS/PERFILES DE CARGA TOC CORREGIDOS.csv', sep=';', index=False)

# Merge con base de datos original.
df = df[['periodo','serviciosentido','paradero','subidasTOCcorregidas','bajadasTOCcorregidas','cargaTOCcorregida']]
data = data.merge(df, on=['periodo','serviciosentido','paradero'], how='left')

# Guardar base de datos actualizada.
data.to_csv('03 RESULTADOS/PERFILES DE CARGA (3).csv', sep=';', index=False)
