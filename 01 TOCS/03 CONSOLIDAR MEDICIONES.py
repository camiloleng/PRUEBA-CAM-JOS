import pandas as pd

PATH1 = '02 RESULTADOS/TOC_OCT18_IND3-OT14.csv'
PATH2 = '02 RESULTADOS/OT23.csv'
PATH3 = '02 RESULTADOS/OT25.csv'

df 		= pd.read_csv(PATH1, sep=';')
ot23 	= pd.read_csv(PATH2, sep=';')
ot25 	= pd.read_csv(PATH3, sep=';')

# Concatenar mediciones TOC de las ordenes de trabajo 23 y 25 con mediciones anteriores (Ind3-OT14)
df = pd.concat([df, ot23, ot25], ignore_index=True, sort=True)

# Ordenar columnas.
df = df[['ot','fecha','periodo','serviciousuariots','paradero','toc','varianza','n','IC']]

# Guardar resultados.
df.to_csv('02 RESULTADOS/TOC_A&M-OT05.csv', sep=';', index=False)