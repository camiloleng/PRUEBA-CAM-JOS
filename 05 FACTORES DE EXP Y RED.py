# ================================================================================
# Author: 	   Camilo Leng Olivares
# Last update: 28-05-2020
# Description: Calcular factores de expansión y reducción.
# ================================================================================

import pandas as pd

pd.set_option('display.max_rows', 500)
pd.set_option('display.max_columns', 500)
pd.set_option('display.width', 150)

df1 = pd.read_csv('00 DATOS/SUBIDAS PROMEDIO_AGO19.csv', sep=';')
df2 = pd.read_csv('00 DATOS/SUBIDAS MAX Y MIN_AGO19.csv', sep=';')

df = pd.merge(df1, df2, on=['tipodia', 'periodotsexpedicion', 'serviciosentido'])

df.rename({'periodotsexpedicion':'periodo'}, axis=1, inplace=True)

df['fmax'] = df['subidasmax']**2 / df['subidasprom']
df['fmin'] = df['subidasmin'] / df['subidasprom']

# mantener periodos PM, FP y PT de días laborales.
df = df[(df['tipodia']==0) & (df['periodo'].isin([4,6,9]))]

df.to_csv('03 RESULTADOS/FACTOR DE EXPANSION Y REDUCCION.csv', sep=';', index=False)