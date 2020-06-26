# ================================================================================
# Author: 	   Camilo Leng Olivares
# Description: Generar archivo de reporte.
# ================================================================================

import pandas as pd
import numpy as np

pd.set_option('display.max_rows', 500)
pd.set_option('display.max_columns', 500)
pd.set_option('display.width', 150)

df = pd.read_csv('03 RESULTADOS/PERFILES DE CARGA (3).csv', sep=';')

# Eliminar mediciones de tasa de ocupación por debajo de la carga promedio.
#df.loc[df['toc']<df['cargapromedio'], 'toc'] = np.nan

# Identificar mediciones donde el IC se cruza con la banda de error.
df.loc[df['toc'].notnull(), 'in_TOC'] = ~((df['toc']+df['IC']<df['cargamin']) | (df['toc']-df['IC']>df['cargamax']))

# Calcular diferencia 
df['difcarga_O18_A19'] = (df['cargacorregida'] - df['cargacorregida_OT14']).abs()
df['difsubidas_O18_A19'] = (df['subidascorregidas'] - df['subidascorregidas_OT14']).abs()

# Función de agrupación.
def my_agg(x):
	names = {
		'capacidad'					: x['capacidad'].mean(),
		'nexpediciones'				: x['nexpediciones'].mean(),
		'sum_zp' 					: x['zp'].sum(),
		'sum_metro' 				: x['metro'].sum(),
		'sum_subidaspromedio' 		: x['subidaspromedio'].sum(),
		'sum_subidasevasion' 		: x['subidasevasion'].sum(),
		'sum_subidascorregidas' 	: x['subidascorregidas'].sum(),
		'sum_subidascorregidas_OT14': x['subidascorregidas_OT14'].sum(),
		'count_TOC'					: x['toc'].notnull().sum(),
		'in_TOC' 					: x['in_TOC'].sum(),
		'avg_IC'					: x['IC'].mean(),
		'sum_cargacorregida'		: x['cargacorregida'].sum(),
		'sum_cargacorregida_OT14'	: x['cargacorregida_OT14'].sum(),
		'sum_difcarga_O18_A19'		: x['difcarga_O18_A19'].sum(),
		'max_difcarga_O18_A19'		: x['difcarga_O18_A19'].max(),
		'sum_difsubidas_O18_A19'	: x['difsubidas_O18_A19'].sum(),
		'max_difsubidas_O18_A19'	: x['difsubidas_O18_A19'].max()
	}

	return pd.Series(names, index=list(names.keys()))

df = df.groupby(['periodo','serviciosentido','serviciousuariots','fmax','fmin']).apply(my_agg)

# Calcular porcentaje de aforos validados.
df['porc_TOC'] = df['in_TOC'] / df['count_TOC']

# Identificar perfiles que cruzaron con resultados de Oct 2018.
df['conperfil_O18'] = 1 * (df['sum_subidascorregidas_OT14']>0)

# Asignar NULL a columnas asociadas al perfil de 2018 cuando no este presente.
df.loc[df['conperfil_O18']==0, ['sum_subidascorregidas_OT14','sum_cargacorregida_OT14','sum_difcarga_O18_A19','max_difcarga_O18_A19','sum_difsubidas_O18_A19','max_difsubidas_O18_A19']] = np.nan

# Variación porcentual entre carga y subidas totales de perfiles de Oct 2018 y Ago 2019.
df.loc[df['conperfil_O18']==1,'varporc_cargatotal'] = (df['sum_cargacorregida'] / df['sum_cargacorregida_OT14']) - 1
df.loc[df['conperfil_O18']==1,'varporc_subidastotal'] = (df['sum_subidascorregidas'] / df['sum_subidascorregidas_OT14']) - 1

# Guardar resultados.
df.to_csv('03 RESULTADOS/ANALISIS PERFILES.csv', sep=';')