# ================================================================================
# Author: 	   Camilo Leng Olivares
# Last update: 28-05-2020
# Description: Corregir perfiles en Zonas Pagas.
# ================================================================================

import pandas as pd
import numpy as np

pd.set_option('display.height', 1000)
pd.set_option('display.max_rows', 500)
pd.set_option('display.max_columns', 500)
pd.set_option('display.width', 150)

PATH1 = '03 RESULTADOS/PERFILES DE CARGA (2).csv'
PATH2 = '03 RESULTADOS/MATRIZ PROBABILIDADES.csv'

COLUMNS1 = ['serviciosentido','paradero','correlativo','zp','metro','subidascorregidas','bajadascorregidas','cargacorregida','toc']

# leer datos.
df = pd.read_csv(PATH1, sep=';', usecols=COLUMNS1)
mp = pd.read_csv(PATH2, sep=';')

# identificar primera parada por servicio donde exista una medición TOC y sea ZP.
df.loc[df[(df['zp']==1)&(df['toc'].notnull())].groupby(['serviciosentido'])['correlativo'].idxmin(), 'edit'] = True
df.loc[df['edit'].isnull(), 'edit'] = False

# calcular diferencia de pasajeros.
df.loc[(df['edit']) & (df['toc']>df['cargacorregida']), 'subidasTOC'] = df['toc'] - df['cargacorregida']
df['subidasTOC'].fillna(0, inplace=True)

# cruzar subidas de TOC con matriz de probabilidad de bajada.
aux = df[['serviciosentido', 'paradero', 'subidasTOC']].rename({'paradero':'par_subida'}, axis=1)
mp = pd.merge(mp, aux, how='left', on=['serviciosentido', 'par_subida'])

# calculadr bajAdas de TOC según periodo - servicio - sentido - parada de subida.
mp['bajadasTOC'] = mp['subidasTOC'] * mp['probabilidad']

mp = mp[['serviciosentido', 'par_bajada', 'bajadasTOC']].rename({'par_bajada':'paradero'}, axis=1)
mp = mp.groupby(['serviciosentido', 'paradero'], as_index=False).sum()

# cruzar bajadas de TOC con perfiles de carga.
df = pd.merge(df, mp, how='left', on=['serviciosentido', 'paradero'])
df['bajadasTOC'].fillna(0, inplace=True)

# calcular carga promedio con corrección por TOC.
df['subidasTOCcorregidas'] = df['subidascorregidas'] + df['subidasTOC']
df['bajadasTOCcorregidas'] = df['bajadascorregidas'] + df['bajadasTOC']

df['cargaTOCcorregida'] = df.groupby('serviciosentido')['subidasTOCcorregidas'].cumsum() - df.groupby('serviciosentido')['bajadasTOCcorregidas'].cumsum()

# seleccionar perfiles modificados.
keep = df.loc[(df['edit']) & (df['toc']>df['cargacorregida']), 'serviciosentido'].drop_duplicates().values
df = df[df['serviciosentido'].isin(keep)]

# guardar resultados.
df.to_csv('03 RESULTADOS/PERFILES DE CARGA TOC CORREGIDOS.csv', sep=';', index=False)

# merge con base de datos original.
df = df[['serviciosentido', 'paradero', 'subidasTOCcorregidas', 'bajadasTOCcorregidas', 'cargaTOCcorregida']]
data = pd.read_csv(PATH1, sep=';')

data = data.merge(df, on=['serviciosentido', 'paradero'], how='left')
data.to_csv('03 RESULTADOS/PERFILES DE CARGA (3).csv', sep=';', index=False)
