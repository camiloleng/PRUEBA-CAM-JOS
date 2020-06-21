import pandas as pd
import numpy as np

pd.set_option('display.max_rows', 500)
pd.set_option('display.max_columns', 500)
pd.set_option('display.width', 150)
'''
Debido a que solo estoy trabajando con la OT25 por ahora tuve que crear el archivo .csv que indico en el PATH1, 
por lo que debes hacer el copy paste y guardarlo como csv para poder leerlo. Además ya no leí con encoding 'latin' debido a que se guarta don utf-8
'''
PATH1 = '01 ORIGINALES/BBDD_OT25_v02.csv'
PATH2 = 'VARIANZA POR TIPO DE BUS.csv'

COLS1 = ['Hora', 'Fecha', 'COD TSTGO', 'Pasajeros_Después', 'POE', 'Servicio', 'Sentido_Servicio', 'Punto', 'OT', 'Tipo_Bus', 'Plazas', 'TOC_Después']
COLS2 = ['tipo_bus', 'plazas', 'toc_categoria', 'Var']

# leer datos de TOCs consolidados.
df = pd.read_csv(PATH1, sep=';', dtype=str, na_values='-', usecols=COLS1, encoding='latin-1')
va = pd.read_csv(PATH2, sep=';', usecols=COLS2)


df.rename({'Pasajeros_Después':'toc', 'COD TSTGO':'paradero', 'OT':'ot', 'Punto':'punto', 'TOC_Después':'toc_categoria', 'Tipo_Bus':'tipo_bus', 'Plazas':'plazas','Fecha':'fecha', 'Hora':'hora'}, axis=1, inplace=True)

# corregir formato de columna paradero.
def CorrCodTSGO(df, column='paradero'):
	x = df[column].str.split('-', expand=True)
	df.loc[df[column].str[-2:].isin(['NS', 'SN', 'PO', 'OP']), column] = x[0]+'-'+x[1]+'-'+x[2]+'-'+x[4]+'-'+x[3]
	return df

df = CorrCodTSGO(df, 'paradero')

# eliminar observación sin información suficiente:
df = df[df['toc'].notnull()]							# sin tasa de ocupación
df = df[df['POE'].isnull()]								# mediciones durante eventos
df = df[~df['Servicio'].isin(['EN TRANSITO', 'SS'])]	# en tránsito
df = df[df['Servicio'].notnull()]						# sin servicio
df = df[df['plazas'].notnull()]							# sin plazas del bus
df = df[df['tipo_bus'].notnull()]						# sin tipo de bus
df = df[df['toc_categoria'].notnull()]					# sin categoría de tasa de ocupación

# cambiar tipo de datos.
'''
-Jose
Revisar que el formato fecha este en español
'''
df['fecha'] = pd.to_datetime(df['fecha']).dt.strftime('%d/%m/%Y')
df['hora']  	= pd.to_timedelta(df['hora'])
df['dow'] 		= pd.to_datetime(df['fecha']).dt.dayofweek
df['plazas'] 	= df['plazas'].astype(int)
df['toc'] 		= df['toc'].astype(float)

'''
Verificar formatos fecha
print(df['fecha'].unique())
print(df['dow'].unique())
print(df[['dow', 'fecha']])
'''



# asignar periodo.
df.loc[(df['dow']< 5) & (df['hora']< '01:00:00'), 'periodo'] = 1
df.loc[(df['dow']< 5) & (df['hora']>='01:00:00') & (df['hora']<'05:30:00'), 'periodo'] = 2
df.loc[(df['dow']< 5) & (df['hora']>='05:30:00') & (df['hora']<'06:30:00'), 'periodo'] = 3
df.loc[(df['dow']< 5) & (df['hora']>='06:30:00') & (df['hora']<'08:30:00'), 'periodo'] = 4
df.loc[(df['dow']< 5) & (df['hora']>='08:30:00') & (df['hora']<'09:30:00'), 'periodo'] = 5
df.loc[(df['dow']< 5) & (df['hora']>='09:30:00') & (df['hora']<'12:30:00'), 'periodo'] = 6
df.loc[(df['dow']< 5) & (df['hora']>='12:30:00') & (df['hora']<'14:00:00'), 'periodo'] = 7
df.loc[(df['dow']< 5) & (df['hora']>='14:00:00') & (df['hora']<'17:30:00'), 'periodo'] = 8
df.loc[(df['dow']< 5) & (df['hora']>='17:30:00') & (df['hora']<'20:30:00'), 'periodo'] = 9
df.loc[(df['dow']< 5) & (df['hora']>='20:30:00') & (df['hora']<'21:30:00'), 'periodo'] = 10
df.loc[(df['dow']< 5) & (df['hora']>='21:30:00') & (df['hora']<'23:00:00'), 'periodo'] = 11
df.loc[(df['dow']< 5) & (df['hora']>='23:00:00'), 'periodo'] = 12
df.loc[(df['dow']==5) & (df['hora']< '01:00:00'), 'periodo'] = 13
df.loc[(df['dow']==5) & (df['hora']>='01:00:00') & (df['hora']<'05:30:00'), 'periodo'] = 14
df.loc[(df['dow']==5) & (df['hora']>='05:30:00') & (df['hora']<'06:30:00'), 'periodo'] = 15
df.loc[(df['dow']==5) & (df['hora']>='06:30:00') & (df['hora']<'11:00:00'), 'periodo'] = 16
df.loc[(df['dow']==5) & (df['hora']>='11:00:00') & (df['hora']<'13:30:00'), 'periodo'] = 17
df.loc[(df['dow']==5) & (df['hora']>='13:30:00') & (df['hora']<'17:30:00'), 'periodo'] = 18
df.loc[(df['dow']==5) & (df['hora']>='17:30:00') & (df['hora']<'20:30:00'), 'periodo'] = 19
df.loc[(df['dow']==5) & (df['hora']>='20:30:00') & (df['hora']<'23:00:00'), 'periodo'] = 20
df.loc[(df['dow']==5) & (df['hora']>='23:00:00'), 'periodo'] = 21
df.loc[(df['dow']==6) & (df['hora']< '01:00:00'), 'periodo'] = 22
df.loc[(df['dow']==6) & (df['hora']>='01:00:00') & (df['hora']<'05:30:00'), 'periodo'] = 23
df.loc[(df['dow']==6) & (df['hora']>='05:30:00') & (df['hora']<'09:30:00'), 'periodo'] = 24
df.loc[(df['dow']==6) & (df['hora']>='09:30:00') & (df['hora']<'13:30:00'), 'periodo'] = 25
df.loc[(df['dow']==6) & (df['hora']>='13:30:00') & (df['hora']<'17:30:00'), 'periodo'] = 26
df.loc[(df['dow']==6) & (df['hora']>='17:30:00') & (df['hora']<'21:00:00'), 'periodo'] = 27
df.loc[(df['dow']==6) & (df['hora']>='21:00:00') & (df['hora']<'23:00:00'), 'periodo'] = 28
df.loc[(df['dow']==6) & (df['hora']>='23:00:00'), 'periodo'] = 29




#Filtrar solo Periodos a utilizar
print(df['periodo'].unique())



df=df[df['periodo'].isin([4,6,9])]
# print(df['periodo'].unique())


print(df[df['Servicio'].notnull()]['Servicio'])
print(df[df['Sentido_Servicio'].notnull()]['Sentido_Servicio'])


# construir identificador de servicio-sentido.
df['Servicio'] = df['Servicio'].str.upper()


'''
Linea 121 se modificó debido a que no agarraba el valor de la columna 'Sentido_Servicio' 
y quedaba un Dataframe con un solo dato.
Verificar con lineas 117 y 118-

# print(df['Sentido_Servicio'].values)
# print(df['Sentido_Servicio'][:1])
'''

df['serviciousuariots'] = df['Servicio'] + df['Sentido_Servicio'].values
df = df[df['serviciousuariots'].notnull()]
df = df[['ot', 'serviciousuariots', 'paradero', 'punto', 'fecha', 'periodo', 'tipo_bus', 'plazas', 'toc_categoria', 'toc']]
# df.to_csv('MEDICIONES TOC_FORMATO.csv', sep=';', index=False)
#reemplazar nulls por caracter para no eliminarlos al agrupar.
df['paradero'].fillna('-', inplace=True)
df['punto'].fillna('-', inplace=True)

# agregar varianza de la medición.
df['toc_categoria'].replace({'1A':'1', '1B':'1', '4A':'4', '4B':'4', '4C':'4'}, inplace=True)
print(df[['tipo_bus', 'plazas', 'toc_categoria']])
df = df.merge(va, on=['tipo_bus', 'plazas', 'toc_categoria'], how='left', indicator=True)

def my_agg(x):
	names = {
		'toc'		: x['toc'].mean(),
		'varianza' 	: x['Var'].sum(),
		'n'			: x['Var'].count(),
		'fecha'		: x['fecha'].max()
	}
	return pd.Series(names, index=list(names.keys()))

# agrupar.
df = df.groupby(['ot', 'periodo', 'serviciousuariots', 'paradero', 'punto'], as_index=False).apply(my_agg).reset_index()

# calcular intervalo de confianza.
df['IC'] = 1.96 * df['varianza'].apply(np.sqrt) / df['n'].apply(np.sqrt)


# IDENTIFICAR TOCS QUE TIENEN MAL ASOCIADO EL PARADERO. ===========================================

# leer perfiles de carga.
PATH3 = '../00 DATOS/PERFILES DE CARGA PROMEDIO_AGO19.csv'
COLS3 = ['serviciousuariots','paradero']

dd = pd.read_csv(PATH3, sep=';', usecols=COLS3)
dd.drop_duplicates(inplace=True)
dd = CorrCodTSGO(dd, 'paradero')

# modificar formato de serviciousuariots para cruzar servicios PM con BBDD TOCs.
dd['servicioPM'] = (dd['serviciousuariots'].str[-2:]=='PM')


dd.loc[dd['servicioPM'], 'serviciousuariots'] = dd['serviciousuariots'].str[:-2]


# cruzar perfiles de carga con TOCs por servicio-sentido-paradero.
df = df.merge(dd, on=['serviciousuariots', 'paradero'], how='left', indicator=True)
df['servicioPM'].fillna(False, inplace=True)
'''
Total df: 103
Total df['both']= 25
print(len(df[df['_merge']=='both']))
print(len(df[df['_merge']=='left_only']))
'''

df=df[df['_merge']=='both']

# restaurar formato original de serviciousuatiots.
df.loc[df['servicioPM'], 'serviciousuariots'] = df['serviciousuariots'] + 'PM'

# crear variable boolean del cruce.
df['match'] = (df['_merge']=='both')
df.drop(['_merge', 'servicioPM'], axis=1, inplace=True)

df.to_csv('OT25.csv', sep=';', index=False)
