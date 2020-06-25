
import pandas as pd
import numpy as np

pd.set_option('display.max_rows', 500)
pd.set_option('display.max_columns', 500)
pd.set_option('display.width', 150)

PATH1 = '03 RESULTADOS/PERFILES DE CARGA (1).csv'	# PERFILES DE CARGA CORREGIDOS (Ago2019).
PATH2 = '01 TOCS/02 RESULTADOS/TOC_A&M-OT05.csv'	# MEDICIONES DE TASA DE OCUPACIÓN.
PATH3 = '02 PERFILES OTS/PERFILES DE CARGA (3).csv'	# PERFILES DE CARGA CORREGIDOS (Oct2018).

COL3 = ['periodotsexpedicion', 'serviciosentido', 'paradero', 'cargacorregida']

# Leer datos
df = pd.read_csv(PATH1, sep=';')
af = pd.read_csv(PATH2, sep=';')
pc = pd.read_csv(PATH3, sep=';', usecols=COL3)
pc.rename(columns={'periodotsexpedicion':'periodo', 'cargacorregida':'cargacorregida_OT14'}, inplace=True)


# Mantener la última medición de tasa de ocupación por periodo, servicio, sentido, parada.
af = af.sort_values(['fecha','periodo']).copy()
af.drop_duplicates(['periodo','serviciousuariots', 'paradero'], keep='last', inplace=True)

# Cruzar información de tasas de ocupación con perfiles corregidos.
COLS = ['periodo','serviciousuariots','paradero','ot','toc','IC']
df = pd.merge(df, af[COLS], on=['periodo', 'serviciousuariots', 'paradero'], how='left')

# Cruzar resultados de perfiles corregidos de Oct 2018 con Ago 2019.
df = df.merge(pc, on=['periodo','serviciosentido','paradero'], how='left')

# Guardar resultados.
df.to_csv('03 RESULTADOS/PERFILES DE CARGA (2).csv', sep=';', index=False)
