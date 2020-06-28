# ================================================================================
# Author: 	   Camilo Leng Olivares
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

# COLORES Y DICCIONARIOS.
ColorP = ['tab:green', 'tab:grey', 'tab:blue', 'tab:purple', 'tab:orange', '#B4D584']
TOC_CP = {'OT01':'#AC3B61', 'OT03':'#116466', 'OT09':'#99C5B5', 'OT12':'#ff3737'}

# Orden para recorrer perfiles en busca de información complementaria.
PERFILES_OTS = ['P_OT09','P_OT07','P_OT05','P_OT03']
POT_LB = {'P_OT03':'OT03', 'P_OT05':'OT05', 'P_OT07':'OT07', 'P_OT09':'OT09'}

PATH1 = '03 RESULTADOS/PERFILES DE CARGA (3).csv'
PATH2 = '03 RESULTADOS/ANALISIS PERFILES.csv'

COLUMNS2 = ['periodo','serviciosentido','estado60']

# Leer datos.
df1 = pd.read_csv(PATH1, sep=';')
df2 = pd.read_csv(PATH2, sep=';', usecols=COLUMNS2)

# Juntar información de perfiles.
df = pd.merge(df1, df2, on=['periodo','serviciosentido'])

# Generar plots para cada servicio sentido.
for p in sorted(df['periodo'].unique()):
	for x in sorted(df.loc[df['periodo']==p,'serviciosentido'].unique()):

		print(p,x)
		dd = df[(df['periodo']==p)&(df['serviciosentido']==x)].reset_index(drop=True).sort_values('correlativo')

		# Identificar nombre del servicio y si posee información para su validación.
		SERVICIO = dd['serviciousuariots'].unique()[0]
		ESTADO 	 = dd['estado60'].unique()[0]

		# Crear figura.
		fig, ax = plt.subplots(figsize=(10,6))
		plt.axhline(color='k', lw=.8, zorder=0)

		# Identificar paradas con zonas pagas.
		for y in dd.loc[dd['zp']==1, 'correlativo']:
			plt.axvline(x=y-1, color='moccasin', lw=6, ls='-', zorder=0)

		# Identificar paradas asociadas a metro. 
		for j in dd.loc[dd['metro']==1, 'correlativo']:
			plt.axvline(x=j-1, color='tab:grey', lw=1.5, ls=':', zorder=1)

		# Plotear carga promedio y corregida por evasión.
		plt.plot(dd['cargapromedio'],  marker='o', markersize=3, color=ColorP[1], ls='--', lw=.8, label='Carga Promedio', zorder=7)
		plt.plot(dd['cargacorregida'], marker='o', markersize=4, color=ColorP[0], ls='-',  lw=1.2, label='Carga Corregida', zorder=10)

		# Plotear banda de error.
		plt.fill_between(dd.index, dd['cargamin'], dd['cargamax'], color=ColorP[0], label='Banda de Error', alpha=.2, zorder=5)
	
		# Plotear carga corregida de octubre 2018.
		PERFIL_OT14 = False
		if dd['cargacorregida_OT14'].sum()>0:
			plt.plot(dd['cargacorregida_OT14'], marker='o', markersize=3, color=ColorP[2], ls=':',  lw=.8, label='Carga Corregida Oct 2018', zorder=9)
			PERFIL_OT14 = True
	
		# Plotear carga corregida por TOCs.
		if dd['cargaTOCcorregida'].sum()>0:
			plt.plot(dd['cargaTOCcorregida'], marker='o', markersize=3, color=ColorP[4], ls=':',  lw=.8, alpha=.7, label='Carga TOC Corregida', zorder=9)
	
		# Plotear perfil de carga obtenidos de OTs (Ind3) anteriores.
		if PERFIL_OT14 == False:
			for pot in PERFILES_OTS:
				if dd[pot].sum()>0:
					plt.plot(dd[pot], marker='o', markersize=3, color=ColorP[3], ls=':',  lw=.8, alpha=.7, label='Carga {} (Ind 3)'.format(POT_LB[pot]), zorder=9)
					break

		# Plotear mediciones de tasas de ocupación.
		mrkr = ['_','x','.','d','*','v','X']
		m = 0
		for ot in dd['ot'].unique():
			dd_toc = dd[dd['ot']==ot]
			if dd_toc['toc'].sum()>0:
				plt.errorbar(dd_toc.index, dd_toc['toc'], yerr=dd_toc['IC'], fmt=mrkr[m], color='k', ecolor='k', elinewidth=.8, capsize=1.2, label='IC TOC {} (Ind 3)'.format(ot), zorder=11)
				m += 1

		# Agregar título y información de ejes.
		plt.title('PERFIL DE CARGA\nServicio: {} ({})   Periodo: {}   Agosto 2019'.format(x,SERVICIO,p), fontsize='x-large')
		plt.ylabel('Carga [pax/veh]')
		plt.xticks(range(len(dd)), dd['nombreparada'].str[:25] + ' - ' +  dd['paradero'], rotation=90, fontsize='x-small')

		plt.xlim(-1, len(dd))

		# Fijar eje Y en 90 o 160.
		if ax.get_ylim()[1]>90:
			plt.ylim(0,160)
		else:
			plt.ylim(0,90)

		# Agregar leyenda.
		plt.axvline(x=-10, color='tab:grey', lw=1.5, ls=':', label='Metro')
		plt.axvline(x=-10, color='moccasin', lw=6,   ls='-', label='Zona Paga')

		plt.legend(fontsize='small')

		plt.tight_layout()

		# Guardar figura.
		PERIODO_FOLDER = {4: '01 PUNTA MAÑANA', 6:'02 FUERA DE PUNTA', 9:'03 PUNTA TARDE'}
		ESTADO_FOLDER = {'VALIDO':'01 VALIDOS', 'NO VALIDO':'02 NO VALIDOS', 'SIN INFO':'03 SIN INFORMACION'}

		SAVEPATH = '04 FIGURAS/{}/{}/{}.png'.format(PERIODO_FOLDER[p],ESTADO_FOLDER[ESTADO],x)
		plt.savefig(SAVEPATH)
		plt.close()
		
		