import textwrap

SELECT_ANALYTICS_COMP_FINANCIERO = textwrap.dedent("""
EXEC TOAT.[rep_analytics].[usp_task_analytics_comp_financiero] 
""")

SELECT_ANALYTICS_PRECIO_UNACEM = textwrap.dedent("""
EXEC TOAT.[rep_analytics].[usp_task_analytics_precio_unacem] 
""")

SELECT_ANALYTICS_COSTO = textwrap.dedent("""
EXEC TOAT.[rep_analytics].[usp_task_analytics_costo] 
""")

SELECT_ANALYTICS_PROYECCION = textwrap.dedent("""
EXEC TOAT.[rep_analytics].[usp_task_analytics_proyeccion] 
""")

SELECT_MARCAS_POR_PAIS = textwrap.dedent("""
SELECT 
   [id_mrc]
  ,[de_mrc]
  ,[es_mrc]
  ,[url]
  ,[dom]
  ,[no_server_sdc]
  ,[no_server_cmd]
  ,[no_server_sdc_siunicon]
  ,[cod_pais]
FROM TOAT.[toat].[mrc] WITH(NOLOCK)
WHERE mrc.cod_pais = ?
""")

INSERT_PROCESS = textwrap.dedent("""
SET NOCOUNT ON;
DECLARE @v_id TABLE(id INT);

INSERT INTO TOAT.rep_analytics.process (es_pro, id_task, tipo)
OUTPUT inserted.id_process INTO @v_id(id)
VALUES (?, ?, ?);

SELECT id FROM @v_id
""")

UPDATE_PROCESS = textwrap.dedent("""
UPDATE TOAT.rep_analytics.process
SET es_pro = ?,
    idDataset = ?,
    resultado = ?,
    mensaje = ?,
    fe_mod = GETDATE(),
    usu_mod = SUSER_SNAME()
WHERE id_process = ?;
""")

REGISTER_COMP_FINANCIERO = "{ CALL TOAT.rep_analytics.usp_registro_resultados_comp_financiero (@resultados=?) }"

REGISTER_PRECIO_UNACEM = "{ CALL TOAT.rep_analytics.usp_registro_resultados_precio_unacem (@resultados=?) }"

REGISTER_COSTO = "{ CALL TOAT.rep_analytics.usp_registro_resultados_costo (@resultados=?) }"

REGISTER_PROYECCION = "{ CALL TOAT.rep_analytics.usp_registro_resultados_proyeccion (@resultados=?) }"
