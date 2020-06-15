# ================================================================================
# Author: 	   Camilo Leng Olivares
# Last update: 28-05-2020
# Description: Generar archivo de reporte.
# ================================================================================

import pandas as pd
import numpy as np

pd.set_option('display.height', 1000)
pd.set_option('display.max_rows', 500)
pd.set_option('display.max_columns', 500)
pd.set_option('display.width', 150)

df = pd.read_csv('03 RESULTADOS/PERFILES DE CARGA (3).csv', sep=';')

# eliminar mediciones de tasa de ocupación por debajo de la carga promedio.
df.loc[df['toc']<df['cargapromedio'], 'toc'] = np.nan

# identificar mediciones donde el IC se cruza con la banda de error.
df.loc[df['toc'].notnull(), 'in_TOC'] = ~((df['toc']+df['IC']<df['cargamin']) | (df['toc']-df['IC']>df['cargamax']))

# ANALIZAR POR SERVICIO SENTIDO.
def my_agg(x):
	names = {
		'capacidad'				: x['capacidad'].mean(),
		'nexpediciones'			: x['nexpediciones'].mean(),
		'sum_zp' 				: x['zp'].sum(),
		'sum_metro' 			: x['metro'].sum(),
		'sum_subidaspromedio' 	: x['subidaspromedio'].sum(),
		'sum_subidasevasion' 	: x['subidasevasion'].sum(),
		'sum_subidascorregidas' : x['subidascorregidas'].sum(),
		'count_TOC'				: x['toc'].notnull().sum(),
		'in_TOC' 				: x['in_TOC'].sum(),
		'avg_IC'				: x['IC'].mean(),
		'any_P_OT03'			: x['P_OT03'].notnull().any(),
		'any_P_OT05'			: x['P_OT05'].notnull().any(),
		'any_P_OT07'			: x['P_OT07'].notnull().any(),
		'any_P_OT09'			: x['P_OT09'].notnull().any(),
		'any_dictuc2012'		: x['DICTUC2012'].notnull().any()
	}

	return pd.Series(names, index=list(names.keys()))

df = df.groupby(['serviciosentido','serviciousuariots','servicioPM','fmax','fmin']).apply(my_agg)

# calcular porcentaje de aforos validados.
df['porc_TOC'] = df['in_TOC'] / df['count_TOC']

# identificar si existe un perfil de OTs anteriores para comparar.
df['any_perfil'] = df[['any_P_OT03','any_P_OT05','any_P_OT07','any_P_OT09','any_dictuc2012']].any(axis=1)

# definir los estados de los perfiles.
df.loc[(df['count_TOC']==0) & (df['any_perfil']==False), 'estado'] = 'SIN INFO'
df.loc[(df['count_TOC']==0) & (df['any_perfil']==True) , 'estado'] = 'SOLO PERFIL'
df.loc[(df['count_TOC']>0)  & (df['porc_TOC']>=0.6), 'estado'] = 'VALIDO'
df.loc[(df['count_TOC']>0)  & (df['porc_TOC']<0.6),  'estado'] = 'NO VALIDO'

df.to_csv('03 RESULTADOS/PERFILES ANALISIS.csv', sep=';')