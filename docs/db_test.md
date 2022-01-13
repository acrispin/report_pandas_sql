# module db from repo
* https://github.com/acrispin/job_analytics.git

```python
from src import db
from src.constants import *

_uni = Marca(1)
_cmx = Marca(2)

db.test_connection_all()

db.__get_conn_str_default()
db.__get_conn_str_general('VMX')
db.__get_conn_str_sdc(_uni)
db.__get_conn_str_sdc(_cmx)
db.__get_conn_str_cmd(_uni)
db.__get_conn_str_cmd(_cmx)

db.test_connection_default()
db.test_connection_general('VMX')
db.test_connection_sdc(_uni)
db.test_connection_sdc(_cmx)
db.test_connection_cmd(_uni)
db.test_connection_cmd(_cmx)

db.check_conection_default()
db.check_conection_general('VMX')
db.check_conection_sdc(_uni)
db.check_conection_sdc(_cmx)
db.check_conection_cmd(_uni)
db.check_conection_cmd(_cmx)

db.get_connection_default()
db.get_connection_general('VMX')
db.get_connection_sdc(_uni)
db.get_connection_sdc(_cmx)
db.get_connection_cmd(_uni)
db.get_connection_cmd(_cmx)

c = db.get_connection_default()
db.query_val(c, "select * from toat.mrc;")
db.query_val(c, "select * from toat.mrc;", _params=None)
db.query_val(c, "select * from toat.mrc;", _params=[])
db.query_val(c, "select * from toat.mrc;", _params=())
db.query_val(c, "select * from toat.mrc where id_mrc = ?;", 2)
db.query_val(c, "select * from toat.mrc where id_mrc = ?;", (2,))
db.query_val(c, "select * from toat.mrc where id_mrc = ?;", [2])
db.query_val(c, "select * from toat.mrc where id_mrc = ?;", [2,])
db.query_val(c, "select ? as 'input', * from toat.mrc where id_mrc = ?;", ["Test", 3,])
db.query_val(c, "select ? as 'input', * from toat.mrc where id_mrc = ?;", _params=["Test", 3,])

db.query_one(c, "select * from toat.mrc;")
db.query_one(c, "select * from toat.mrc;", _params=None)
db.query_one(c, "select * from toat.mrc;", _params=[])
db.query_one(c, "select * from toat.mrc;", _params=())
db.query_one(c, "select * from toat.mrc where id_mrc = ?;", 2)
db.query_one(c, "select * from toat.mrc where id_mrc = ?;", (2,))
db.query_one(c, "select * from toat.mrc where id_mrc = ?;", [2])
db.query_one(c, "select * from toat.mrc where id_mrc = ?;", [2,])
db.query_one(c, "select ? as 'input', * from toat.mrc where id_mrc = ?;", ["Test", 3,])
db.query_one(c, "select ? as 'input', * from toat.mrc where id_mrc = ?;", _params=["Test", 3,])

db.query(c, "select * from toat.mrc;")
db.query(c, "select * from toat.mrc;", _params=None)
db.query(c, "select * from toat.mrc;", _params=[])
db.query(c, "select * from toat.mrc;", _params=())
db.query(c, "select * from toat.mrc where id_mrc = ?;", 2)
db.query(c, "select * from toat.mrc where id_mrc = ?;", (2,))
db.query(c, "select * from toat.mrc where id_mrc = ?;", [2])
db.query(c, "select * from toat.mrc where id_mrc = ?;", [2,])
db.query(c, "select ? as 'input', * from toat.mrc where id_mrc = ?;", ["Test", 3,])
db.query(c, "select ? as 'input', * from toat.mrc where id_mrc = ?;", _params=["Test", 3,])
db.query(c, "select * from toat.mrc where cod_pais = ?;", ["PER",])
db.query(c, "select * from toat.mrc where cod_pais = ?;", _params=["PER",])
db.query(c, "select * from toat.mrc;", None, 2)
db.query(c, "select * from toat.mrc;", _size=2)
db.query(c, "select * from toat.mrc where cod_pais = ?;", ["PER",], 3)

c = db.get_connection_sdc(_uni)
db.query(c, "select top 100 * from dbo.rcl with(nolock) order by fe_ing_rcl desc;")

db.query(c, "select top 10 co_art, de_art, es_art from dbo.art with(nolock) order by fe_ing_art desc;")
db.dml(c, "update dbo.art set es_art = 'ALT' where co_art=?", ["084433",])


# WITH CURSOR
from src import db
from src.constants import Marca

_uni = Marca(1)
_cmx = Marca(2)
_cnxn = db.get_connection_sdc(_uni)
with _cnxn.cursor() as _cur:
    res = db.query_val_tran(_cur, "select * from toat.mrc;")
    print(res)
    res = db.query_one_tran(_cur, "select * from toat.mrc where id_mrc = ?;", [2,])
    print(res)
    res = db.query_tran(_cur, "select id_mrc, de_mrc, dom, cod_pais from toat.mrc where cod_pais = ?;", _params=["PER",])
    print(res)
    res = db.query_tran(_cur, "select top 10 co_art, de_art, es_art from dbo.art with(nolock) order by fe_ing_art desc;")
    print(res)
    res = db.dml_tran(_cur, "update dbo.art set es_art = 'ALT' where co_art=?", ["084433",])
    print(res)
    res = db.dml_tran(_cur, "update dbo.art set es_art = 'ALT' where co_art=?", ["084434",])
    print(res)

```


## Is it possible to pass values to a table type parameter from PYODBC to SQL Server?
* https://stackoverflow.com/questions/61148084/is-it-possible-to-pass-values-to-a-table-type-parameter-from-pyodbc-to-sql-serve
* https://github.com/mkleehammer/pyodbc/issues/595
### Creacion de tipo u procedimiento en base de datos
```sql
USE TEST_DB
GO

-- Create schema
CREATE SCHEMA [rep_analytics]
GO

-- Create type
CREATE TYPE [rep_analytics].[TestType] AS TABLE
(
    [TestField] [varchar](10) NULL,
    [TestField2] [int] NULL
)
GO
GRANT EXEC ON TYPE::[rep_analytics].[TestType] TO [Public]
GO

-- Create procedure
CREATE PROCEDURE rep_analytics.TestTypeProcedure (@tt rep_analytics.TestType READONLY)
AS
/* 
USE TEST_DB
GO

DECLARE @v_tt rep_analytics.TestType;

INSERT INTO  @v_tt 
    (TestField, TestField2)
VALUES 
    ('102149', 100),
    ('102521', 101),
    ('103269', 102),
    ('104923', 103);
    
EXEC rep_analytics.TestTypeProcedure @tt=@v_tt;
GO
*/
BEGIN
    SELECT *
    FROM @tt;
END
GO
GRANT EXECUTE ON [rep_analytics].[TestTypeProcedure] TO PUBLIC
GO

```

### Invocacion en python
```py
### 1
from src import db
# db.test_connection_default()
c = db.get_connection_default()
my_tvp = [('Hello!', 1), ('Goodbye!', 2), ('Otro!', 3), ]
my_tvp = ["TestType", "rep_analytics", ] + my_tvp # Solo si se usa un schema diferente a 'dbo', se esta usando 'rep_analytics' como esquema
# res = db.query(c, "EXEC rep_analytics.TestTypeProcedure ?", _params=(my_tvp, ))
res = db.query(c, "EXEC rep_analytics.TestTypeProcedure @tt=?", _params=(my_tvp, ))
print(res)
print(res[0].TestField, res[0].TestField2)



### 2
from src import db
# db.test_connection_default()
c = db.get_connection_default()
my_tvp = [('Hello!', 1), ('Goodbye!', 2), ('Otro!', 3), ]
my_tvp = ["TestType", "rep_analytics", ] + my_tvp # Solo si se usa un schema diferente a 'dbo', se esta usando 'rep_analytics' como esquema
# sql = "EXEC rep_analytics.TestTypeProcedure ?"
sql = "EXEC rep_analytics.TestTypeProcedure @tt=?"
params = (my_tvp, )
res = db.query(c, sql, _params=params)
print(res)
print(res[0].TestField, res[0].TestField2)



### 3
from src import db
# db.test_connection_default()
c = db.get_connection_default()
my_tvp = [('Hello!', 1), ('Goodbye!', 2), ('Otro!', 3), ]
my_tvp = ["TestType", "rep_analytics", ] + my_tvp # Solo si se usa un schema diferente a 'dbo', se esta usando 'rep_analytics' como esquema
# sql = "{ CALL rep_analytics.TestTypeProcedure (?) }"
sql = "{ CALL rep_analytics.TestTypeProcedure (@tt=?) }"
params = (my_tvp, )
res = db.query(c, sql, _params=params)
print(res)
print(res[0].TestField, res[0].TestField2)



### 4
import textwrap
from src import db
# db.test_connection_default()
c = db.get_connection_default()
my_tvp = [('Hello!', 1), ('Goodbye!', 2), ('Otro!', 3), ]
my_tvp = ["TestType", "rep_analytics", ] + my_tvp  # Solo si se usa un schema diferente a 'dbo', se esta usando 'rep_analytics' como esquema
sql = textwrap.dedent("""
SET NOCOUNT ON

DECLARE @v_tt rep_analytics.TestType;
INSERT INTO  @v_tt 
    (TestField, TestField2)
VALUES 
    ('102149', 100),
    ('102521', 101),
    ('103269', 102),
    ('104923', 103);
    
-- EXEC rep_analytics.TestTypeProcedure ?;
EXEC rep_analytics.TestTypeProcedure @tt=?;
""")
params = (my_tvp,)
res = db.query(c, sql, _params=params)
print(res)



### 5
import textwrap
from src import db
# db.test_connection_default()
c = db.get_connection_default()
my_tvp = [('Hello!', 1), ('Goodbye!', 2), ('Otro!', 3), ]
my_tvp = ["TestType", "rep_analytics", ] + my_tvp  # Si es necesario asi sea esquema 'dbo', se esta usando 'rep_analytics' como esquema
sql = textwrap.dedent("""
SET NOCOUNT ON

SELECT * FROM ?;
""")
params = (my_tvp,)
res = db.query(c, sql, _params=params)
print(res)



### 6
import textwrap
from src import db
# db.test_connection_default()
c = db.get_connection_default()
my_tvp = [('Hello!', 1), ('Goodbye!', 2), ('Otro!', 3), ]
my_tvp = ["TestType", "rep_analytics", ] + my_tvp  # Si es necesario asi sea esquema 'dbo', se esta usando 'rep_analytics' como esquema
sql = textwrap.dedent("""
SELECT * FROM ?;
""")
params = (my_tvp,)
res = db.query(c, sql, _params=params)
print(res)



### 7
from src import db
# db.test_connection_default()
c = db.get_connection_default()
my_tvp = [('Hello!', 1), ('Goodbye!', 2), ('Otro!', 3), ]
my_tvp = ["TestType", "rep_analytics", ] + my_tvp  # Si es necesario asi sea esquema 'dbo', se esta usando 'rep_analytics' como esquema
sql = "SELECT * FROM ?;"
params = (my_tvp,)
res = db.query(c, sql, _params=params)
print(res)



### 8
import textwrap
from src import db
# db.test_connection_default()
c = db.get_connection_default()
my_tvp = [('Hello!', 1), ('Goodbye!', 2), ('Otro!', 3), ]
my_tvp = ["TestType", "rep_analytics", ] + my_tvp  # Solo si se usa un schema diferente a 'dbo', se esta usando 'rep_analytics' como esquema
sql = textwrap.dedent("""
SET NOCOUNT ON

DECLARE @v_tt rep_analytics.TestType;
INSERT INTO  @v_tt 
(TestField, TestField2)
-- SELECT * FROM ?;
SELECT TestField, TestField2 FROM ?;
    
-- EXEC rep_analytics.TestTypeProcedure @v_tt;
EXEC rep_analytics.TestTypeProcedure @tt=@v_tt;
""")
params = (my_tvp,)
res = db.query(c, sql, _params=params)
print(res)
```
