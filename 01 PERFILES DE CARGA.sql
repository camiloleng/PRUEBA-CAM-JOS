-- ================================================================================
-- Author: 		Camilo Leng Olivares
-- Last update: 18-03-2019
-- Description: Seleccionar expediciones validas y calcular los perfiles promedio.
-- ================================================================================

-- (1) IDENTIFICAR EXPEDICIONES VALIDAS PARA EL CÁLCULO DE PERFILES DE CARGA.

-- alter table ago2019.perfiles drop column valido;
alter table ago2019.perfiles add column valido boolean;

-- subidas totales, bajadas totales, subidas expandidas totales, bajadas expandidas totales y mínimo de la carga por expedición.
with cte as(
	select 
		hini
		,idexpedicion
		,sum(subidastotal) as totalsubidas
		,sum(bajadastotal) as totalbajadas
		,sum(subidasexpandidas) as totalsubexpandidas
		,sum(bajadasexpandidas) as totalbajexpandidas
		,min(carga) as cargaminima
	from ago2019.perfiles
	group by hini, idexpedicion
)
-- definir expedición como válida cuando se cumplan las restricciones sobre las subidas, bajadas y carga. 
update ago2019.perfiles as p 
set valido=true 
from cte
where
	cte.totalsubidas>0					-- subidas totales > 0
	and cte.totalbajadas>0				-- bajadas totales > 0
	and cte.totalsubexpandidas>0		-- subidas expandidas totales > 0
	and cte.totalbajexpandidas>0		-- bajadas expandidas totales > 0
	and cte.cargaminima>-2				-- carga mínima > -2
	and p.hini = cte.hini
	and p.idexpedicion = cte.idexpedicion
	and p.expedicionconproblema=0
	and cumplimiento='C';

update ago2019.perfiles set valido=false where valido is null;


-- (2) EXTRAER SUBIDAS Y BAJADAS PROMEDIO POR TIPO DIA, PERIODO, SERVICIO, SENTIDO Y PARADA.

copy(
	select
		tipodia
		,periodotsexpedicion as periodo
		,serviciosentido
		,serviciousuariots
		,paradero
		,nombreparada
		,paraderousuario
		,correlativo
		,zp
		,case when nombreparada like '%(M)%' then 1 else 0 end as metro
		,avg(subidasexpandidas) as subidaspromedio
		,avg(bajadasexpandidas) as bajadaspromedio
		,avg(carga) as cargapromedio_adtp
		,avg(capacidad) as capacidad
		,count(distinct(hini, idexpedicion)) as nexpediciones
	from ago2019.perfiles
	where valido
	group by tipodia, periodotsexpedicion, serviciosentido, serviciousuariots, paradero, nombreparada, paraderousuario, correlativo, zp, metro
	order by tipodia, periodotsexpedicion, serviciosentido, correlativo
)
to 'C:\CLENG\PERFILES DE CARGA PROMEDIO_AGO2019.csv'
with(format csv, header true, delimiter ';');

-- GUARDAR EL ARCHIVO EN LA CARPETA "00 DATOS".