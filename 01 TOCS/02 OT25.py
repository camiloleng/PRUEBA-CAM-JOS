import pandas as pd
import numpy as np

pd.set_option('display.max_rows', 500)
pd.set_option('display.max_columns', 500)
pd.set_option('display.width', 150)

PATH1 = 'BBDD_TOC.csv'						# Mediciones TOCs
PATH2 = 'VARIANZA POR TIPO DE BUS.csv'		# Varianza de mediciones

COLS1 = ['Hora', 'Periodo', 'Fecha', 'COD TSTGO', 'Pasajeros_Después', 'POE', 'Servicio', 'Sentido', 'Punto', 'OT', 'Tipo_Bus', 'Plazas', 'TOC_Después']
COLS2 = ['tipo_bus', 'plazas', 'toc_categoria', 'var']

# FUNCION: Corregir formato de columna paradero.
def CorrCodTSGO(df, column='paradero'):
	x = df[column].str.split('-', expand=True)
	df.loc[df[column].str[-2:].isin(['NS', 'SN', 'PO', 'OP']), column] = x[0]+'-'+x[1]+'-'+x[2]+'-'+x[4]+'-'+x[3]
	return df

# Leer datos.
df = pd.read_csv(PATH1, sep=';', dtype=str, na_values='-', usecols=COLS1, encoding='latin-1')
va = pd.read_csv(PATH2, sep=';', usecols=COLS2)

# Log file.
f = open('log_OT25.txt', 'w')

# Seleccionar Orden de Trabajo: 25
df = df[df['OT']=='OT25']

NEWNAMES = {
	'Pasajeros_Después'	: 'toc',
	'COD TSTGO'			: 'paradero',
	'OT'				: 'ot',
	'Punto'				: 'punto',
	'TOC_Después'		: 'toc_categoria',
	'Tipo_Bus'			: 'tipo_bus',
	'Plazas'			: 'plazas',
	'Fecha'				: 'fecha',
	'Hora'				: 'hora',
	'Periodo'			: 'periodo'
}

# Cambiar nombre de atributos.
df.rename(NEWNAMES, axis=1, inplace=True)

f.write('Cantidad de mediciones por periodo realizadas:\n'+ df.groupby('periodo').size().to_string() + '\n\n')

# Corregir formato de paraderos.
df = CorrCodTSGO(df, 'paradero')

# Eliminar observación sin información suficiente:
df = df[df['toc'].notnull()]							# sin tasa de ocupación
df = df[df['POE'].isnull()]								# mediciones durante eventos
df = df[df['periodo'].notnull()]						# periodo asignado
df = df[~df['Servicio'].isin(['EN TRANSITO', 'SS'])]	# en tránsito
df = df[df['Servicio'].notnull()]						# sin servicio
df = df[df['Sentido'].notnull()]						# sin sentido
df = df[df['plazas'].notnull()]							# sin plazas del bus
df = df[df['tipo_bus'].notnull()]						# sin tipo de bus
df = df[df['toc_categoria'].notnull()]					# sin categoría de tasa de ocupación

# Cambiar tipo de datos.
# ========================================================
#  OJO: Revisar que la fecha venga en formato: dd/mm/aaaa
# ========================================================
df['fecha'] 	= pd.to_datetime(df['fecha'], format='%d/%m/%Y')
#df['hora']  	= pd.to_timedelta(df['hora'])
#df['dow'] 		= pd.to_datetime(df['fecha']).dt.dayofweek
df['plazas'] 	= df['plazas'].astype(int)
df['toc'] 		= df['toc'].astype(float)
df['periodo']	= df['periodo'].astype(int)

f.write('Cantidad de mediciones con información suficiente:\n'+ df.groupby('periodo').size().to_string() + '\n\n')

# Construir identificador de servicio-sentido.
df['serviciousuariots'] = (df['Servicio'] + df['Sentido']).str.upper()

# Agrupar y calcular varianza de mediciones.
df['toc_categoria'].replace({'1A':'1', '1B':'1', '4A':'4', '4B':'4', '4C':'4'}, inplace=True)
df = df.merge(va, on=['tipo_bus', 'plazas', 'toc_categoria'], how='left') # both: all

def my_agg(x):
	names = {
		'toc'		: x['toc'].mean(),
		'varianza' 	: x['var'].sum(),
		'n'			: x['var'].count(),
		'fecha'		: x['fecha'].max()
	}
	return pd.Series(names, index=list(names.keys()))

df = df.groupby(['ot', 'periodo', 'serviciousuariots', 'paradero', 'punto'], as_index=False).apply(my_agg).reset_index()

# Calcular intervalo de confianza.
df['IC'] = 1.96 * df['varianza'].apply(np.sqrt) / df['n'].apply(np.sqrt)

# Guardar resultados.
df.to_csv('02 RESULTADOS/OT25.csv', sep=';', index=False)

f.write('Cantidad tasas de ocupación promedio calculadas:\n'+ df.groupby('periodo').size().to_string())
