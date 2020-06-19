-- ================================================================================
-- Author: 		Camilo Leng Olivares
-- Last update: 18-03-2019
-- Description: Extraer MOD de etapas.
-- ================================================================================

-- EXTRAER MATRIZ OD DE ETAPAS POR PERIODO, SERVICIO, SENTIDO, PARADA DE SUBIDA Y PARADA DE BAJADA.

-- << IMPORTANTE >>

-- Todas las etapas deben ser llevadas a la hora de inicio de sus respectivas expediciones para ser asignadas 
-- a la matriz del periodo correspondiente. De otra forma, se definen las probabilidades de bajada con demandas distintas
-- a las utilizadas por los perfiles de carga.

-- Para llevar a cabo esto es necesario poder identificar a que expedición se asigna cada etapa. Sin embargo esta 
-- información no se encuentra disponible. Por lo tanto, se extraerá la información relajando este problema. 

copy(
	select
		periodo_subida as periodo,
		servicio_subida as serviciosentido,
		par_subida,
		par_bajada,
		sum(fexpansionzonaperiodots) as netapas
	from ago2019.etapas
	where
		servicio_subida is not null
		and par_subida is not null
		and par_bajada is not null
		and tipo_transporte in ('BUS', 'ZP')
		and tipo_dia = 'LABORAL'
	group by periodo_subida, servicio_subida, par_subida, par_bajada
	order by periodo_subida, servicio_subida, par_subida, par_bajada
)
to 'C:\CLENG\MOD_PERIODO-SERVICIO-PARADA_AGO19.csv'
with(format csv, header true, delimiter ';');
