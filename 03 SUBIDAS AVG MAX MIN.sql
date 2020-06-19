-- ================================================================================
-- Author: 		Camilo Leng Olivares
-- Last update: 18-03-2019
-- Description: Calcular subidas totales, máximas y mínimas.
-- ================================================================================

-- CALCULAR SUBIDAS TOTALES PROMEDIO POR PERIODO, SERVICIO, SENTIDO.
copy(
	
	-- subidas totales por periodo, servicio, sentido y expedición
	with cte as(
		select
			tipodia
			,periodotsexpedicion
			,serviciosentido
			,hini
			,idexpedicion
			,sum(subidasexpandidas) as sumsubidas
		from ago2019.perfiles
		where valido
		group by tipodia, periodotsexpedicion, serviciosentido, hini, idexpedicion
		order by tipodia, periodotsexpedicion, serviciosentido, hini, idexpedicion
	)
	
	-- promedio de subidas totales por periodo, servicio y sentido.
	select
		tipodia
		,periodotsexpedicion
		,serviciosentido
		,avg(sumsubidas) as subidasprom
	from cte
	group by tipodia, periodotsexpedicion, serviciosentido
	order by tipodia, periodotsexpedicion, serviciosentido
)
to 'C:\CLENG\SUBIDAS PROMEDIO_AGO19.csv'
with(format csv, header true, delimiter ';');


-- CALCULAR SUBIDAS TOTALES MÁXIMAS Y MÍNIMAS POR SERVICIO, SENTIDO Y MEDIA HORA.
copy(
	with recursive
	
	-- subidas totales por periodo, media hora, servicio, sentido y expedición.
	cte1 as(
		select
			tipodia
			,periodotsexpedicion
			,mhsalida
			,serviciosentido
			,hini
			,idexpedicion
			,sum(subidasexpandidas) as sumsubidas
		from ago2019.perfiles
		where valido 
		group by tipodia, periodotsexpedicion, mhsalida, serviciosentido, hini, idexpedicion
		order by tipodia, periodotsexpedicion, mhsalida, serviciosentido, hini, idexpedicion
	)
	
	-- promedio de subidas totales por periodo, media hora, servicio y sentido.
	,cte2 as(
		select
			tipodia
			,periodotsexpedicion
			,mhsalida
			,serviciosentido
			,avg(sumsubidas) as avg_sumsubidas
		from cte1
		group by tipodia, periodotsexpedicion, mhsalida, serviciosentido
		order by tipodia, periodotsexpedicion, mhsalida, serviciosentido
	)
	
	-- máximo y mínimo de los promedios de subidas totales por periodo, servicio y sentido.
	select
		tipodia
		,periodotsexpedicion
		,serviciosentido
		,max(avg_sumsubidas) as subidasmax
		,min(avg_sumsubidas) as subidasmin
	from cte2
	group by tipodia, periodotsexpedicion, serviciosentido
	order by tipodia, periodotsexpedicion, serviciosentido
)
to 'C:\CLENG\SUBIDAS MAX Y MIN_AGO19.csv'
with(format csv, header true, delimiter ';');
