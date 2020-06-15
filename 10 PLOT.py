# ================================================================================
# Author: 	   Camilo Leng Olivares
# Last update: 28-05-2020
# Description: Generar figuras con perfiles corregidos y mediciones.
# ================================================================================

import pandas as pd
import numpy as np
import matplotlib
import matplotlib.pyplot as plt

pd.set_option('display.max_rows', 500)
pd.set_option('display.max_columns', 500)
pd.set_option('display.width', 150)

matplotlib.rcParams['font.sans-serif'] = 'Century Gothic'

# COLORES Y DICCIONARIOS DE LABELS.
ColorP = ['#82AF00', '#635B4F', '#bbbbbb', '#835E3A', '#E18D1D', '#B4D584']
POT_CP = {'POT03':'#116466', 'POT05':'#BCAB79', 'POT07':'#D79922', 'POT09':'#99C5B5', 'DICTUC2012':'#39b03b'}
POT_LB = {'P_OT03':'OT03', 'P_OT05':'OT05', 'P_OT07':'OT07', 'P_OT09':'OT09', 'DICTUC2012':'DICTUC 2012'}
TOC_CP = {'OT01':'#AC3B61', 'OT03':'#116466', 'OT09':'#99C5B5', 'OT12':'#ff3737'}

PATH1 = '03 RESULTADOS/PERFILES DE CARGA (3).csv'
PATH2 = '03 RESULTADOS/PERFILES ANALISIS.csv'

#COLUMNS1 = ['serviciosentido','serviciousuariots','servicioPM','paradero','paraderousuario','correlativo','nombreparada','zp','metro','cargapromedio_adtp','cargapromedio','cargacorregida','cargamax','cargamin','TOC','IC','OT','POT03','POT05','POT07','POT09','DICTUC2012','cargaTOCcorregida']
COLUMNS2 = ['serviciosentido','estado']

# leer datos.
df1 = pd.read_csv(PATH1, sep=';')
df2 = pd.read_csv(PATH2, sep=';', usecols=COLUMNS2)

# juntar información de perfiles.
df = pd.merge(df1, df2, on='serviciosentido')

# eliminar mediciones de tasa de ocupación por debajo de la carga promedio.
df.loc[df['toc']<df['cargapromedio'], 'toc'] = np.nan

# corregir nombre de serviciousuariots.
df.loc[df['servicioPM'], 'serviciousuariots'] = df['serviciousuariots'] + 'PM'

# identificar perfiles de carga OTs a graficar.
PERFILES_OTS = df.columns[31:-4]

# generar plots para cada servicio sentido.
for x in df['serviciosentido'].unique():

	print(x)
	dd = df[df['serviciosentido']==x].reset_index(drop=True).sort_values('correlativo')

	# identificar nombre del servicio y si posee información para su validación.
	SERVICIO = dd.loc[0,'serviciousuariots']
	ESTADO 	 = df2.loc[df2['serviciosentido']==x, 'estado'].values

	# crear figura.
	fig, ax = plt.subplots(figsize=(10,6))
	plt.axhline(color='k', lw=.8, zorder=0)

	# identificar paradas con zonas pagas.
	for y in dd.loc[dd['zp']==1, 'correlativo']:
		plt.axvline(x=y-1, color='#ecfd63', lw=6, ls='-', zorder=0)

	# identificar paradas asociadas a metro. 
	for j in dd.loc[dd['metro']==1, 'correlativo']:
		plt.axvline(x=j-1, color='dimgray', lw=1.5, ls=':', zorder=1)

	# plotear carga promedio y corregida por evasión.
	plt.plot(dd['cargapromedio'],  marker='o', markersize=3, color=ColorP[1], ls='-.', lw=.8, label='Carga Promedio', zorder=7)
	plt.plot(dd['cargacorregida'], marker='o', markersize=4, color=ColorP[0], ls='-',  lw=1, label='Carga Corregida', zorder=10)

	# plotear banda de error.
	plt.fill_between(dd.index, dd['cargamin'], dd['cargamax'], color=ColorP[2], label='Banda de Error', alpha=.7, zorder=5)
	
	# plotear carga corregida por TOCs.
	TOC_CORREGIDO = False
	if dd['cargaTOCcorregida'].sum()>0:
		TOC_CORREGIDO = True
		plt.plot(dd['cargaTOCcorregida'], marker='o', markersize=4, color=ColorP[4], ls='-',  lw=1, label='Carga TOC Corregida', zorder=9)

	# plotear perfiles de carga obtenidos de OTs anteriores.
	m=0
	PLOT_DICTUC = True
	mrkr=['o', '^', '+', '2', '*']
	for pot in PERFILES_OTS:
		if dd[pot].sum()>0:
			plt.plot(dd[pot], marker=mrkr[m], markersize=3, color='#1b83a3', ls=':', lw=.8, label='Carga {}'.format(POT_LB[pot]), zorder=6)
			PLOT_DICTUC = False
			m+=1

	# plotear perfil de carga de DICTUC 2012, solo si no se ha ploteado otro perfil.
	if PLOT_DICTUC and dd['DICTUC2012'].sum()>0:
		plt.plot(dd['DICTUC2012'], marker='o', markersize=3, color='#1b83a3', ls=':', lw=.8, label='Carga DICTUC 2012', zorder=6)

	# plotear mediciones en terreno (aforos) de OTs anteriores.
	n=0
	mrkr=['_','x','.','d', '*']
	for ot in dd['ot'].unique():
		dd_toc = dd[dd['ot']==ot]
		if dd_toc['toc'].sum()>0:
			plt.errorbar(dd_toc.index, dd_toc['toc'], yerr=dd_toc['IC'], fmt=mrkr[n], color='#040404', ecolor='#040404', elinewidth=1, capsize=2, label='IC TOC {}'.format(ot), zorder=11)
			n+=1

	# agregar título y información de ejes.
	plt.title('PERFIL DE CARGA\nSERVICIO: {} ({})'.format(x,SERVICIO), fontsize='x-large')
	plt.ylabel('Carga [pax/veh]')
	plt.xticks(range(len(dd)), dd['nombreparada'].str[:25] + ' - ' +  dd['paradero'], rotation=90, fontsize='x-small')

	plt.xlim(-1, len(dd))

	# fijar eje Y en 90 o 160.
	if ax.get_ylim()[1]>90:
		plt.ylim(0,160)
	else:
		plt.ylim(0,90)

	# agregar leyenda.
	plt.axvline(x=-10, color='dimgray', lw=1.5, ls=':', label='Metro')
	plt.axvline(x=-10, color='#ecfd63', lw=6,   ls='--', label='Zona Paga')

	plt.legend(fontsize='small')

	plt.tight_layout()

	# guardar perfil en distinta carpeta dependiendo de clasificación.
	if ESTADO=='SIN INFO':
		SAVEPATH = '04 FIGURAS/01 PERFILES/01 SIN INFORMACION/{}.png'.format(x)
	elif ESTADO=='SOLO PERFIL':
		SAVEPATH = '04 FIGURAS/01 PERFILES/02 SOLO PERFIL/{}.png'.format(x)
	elif ESTADO=='VALIDO':
		SAVEPATH = '04 FIGURAS/01 PERFILES/03 VALIDO/{}.png'.format(x)
	elif ESTADO=='NO VALIDO':
		SAVEPATH = '04 FIGURAS/01 PERFILES/04 NO VALIDO/{}.png'.format(x)
	else:
		print('>>PERFIL NO CLASIFICADO<<')
	
	plt.savefig(SAVEPATH)
	plt.close()