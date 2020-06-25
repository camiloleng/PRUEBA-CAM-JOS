
import pandas as pd
import numpy as np

# pd.set_option('display.height', 1000)
pd.set_option('display.max_rows', 500)
pd.set_option('display.max_columns', 500)
pd.set_option('display.width', 150)

PATH1 = '03 RESULTADOS/PERFILES DE CARGA (1).csv'
PATH2 = '01 TOCS/02 RESULTADOS/TOC_A&M-OT05.csv'
PATH3 = '02 PERFILES OTS/PERFILES DE CARGA (3).csv'

col3= ['ot','periodotsexpedicion', 'serviciousuariots', 'paradero', 'cargacorregida']

# leer datos
df = pd.read_csv(PATH1, sep=';')		# PERFILES CORREGIDOS.
af = pd.read_csv(PATH2, sep=';')		# TASAS DE OCUPACIÓN MEDIDAS.
pc = pd.read_csv(PATH3, sep=';', usecols=col3)		# PERFILES DE CARGA OT14.
pc.rename(columns={'periodotsexpedicion':'periodo', 'cargacorregida':'cargacorregida_OT14'}, inplace=True)

PERIODOS=[4,6,9]

df_FINAL= pd.DataFrame([])
for j in PERIODOS:

	# seleccionar periodo (4:PUNTA MAÑANA, 6:FUERA PUNTA, 9:PUNTA TARDE).
	af2 = af[af['periodo']==j].copy()
	pc2 = pc[pc['periodo']==j].copy()
	df2 = df[df['periodo']==j].copy()
	af3 = af[af['periodo']==j].copy()
	
	# mantener la última medición de tasa de ocupación por servicio, sentido, parada.
	af2.sort_values('fecha', inplace=True)
	af2.drop_duplicates(['serviciousuariots', 'paradero'], keep='last', inplace=True)

	# cruzar información de tasas de ocupación de perfiles corregidos.
	af2 = af2[['serviciousuariots', 'paradero', 'ot', 'toc', 'IC']]
	df2 = pd.merge(df2, af2, on=['serviciousuariots', 'paradero'], how='left')

	
	# cruzar perfil de carga ADATRAP con perfiles de carga OT 14.
	df2 = df2.merge(pc2, on=['ot','periodo','serviciousuariots', 'paradero'], how='left')
	

	# pivotear perfiles de carga de OTs.
	af3['key'] = af3['serviciousuariots'] + '~' + af3['paradero']
	af3.drop_duplicates(['ot','serviciousuariots', 'paradero'], keep='last', inplace=True)
	af3 = af3.pivot('key', 'ot', 'periodo').reset_index()
	
	# recuperar formato.
	af3['serviciousuariots'] = af3['key'].str.split('~', expand=True)[0]
	af3['paradero']   = af3['key'].str.split('~', expand=True)[1]
	af3.drop('key', axis=1, inplace=True)
	df2 = df2.merge(af3, on=['serviciousuariots', 'paradero'], how='left')

	# guardar resultados.
	if j==4:
		df2.to_csv('03 RESULTADOS/PM/PERFILES DE CARGA (2) P-{}.csv'.format(j), sep=';', index=False)
	elif j==6:
		df2.to_csv('03 RESULTADOS/FP/PERFILES DE CARGA (2) P-{}.csv'.format(j), sep=';', index=False)
	elif j==9:
		df2.to_csv('03 RESULTADOS/PT/PERFILES DE CARGA (2) P-{}.csv'.format(j), sep=';', index=False)

	columnas= df2.columns
	df_FINAL = df_FINAL.append(df2, ignore_index=True, sort=True)


df_FINAL=df_FINAL[columnas]
df_FINAL.to_csv('03 RESULTADOS/PERFILES DE CARGA (2).csv', sep=';', index=False)



