# pyodbc==4.0.32
* https://github.com/mkleehammer/pyodbc
* https://github.com/mkleehammer/pyodbc/wiki



## Getting started
* https://github.com/mkleehammer/pyodbc/wiki/Getting-started
```python
""" 
Connect to a Database 
Pass an ODBC connection string to the pyodbc connect() function which will return a Connection. Once you have a connection you can ask it for a Cursor. 
For example:
"""
import pyodbc

# Specifying the ODBC driver, server name, database, etc. directly
cnxn = pyodbc.connect('DRIVER={ODBC Driver 17 for SQL Server};SERVER=localhost;DATABASE=testdb;UID=me;PWD=pass')

# Using a DSN, but providing a password as well
cnxn = pyodbc.connect('DSN=test;PWD=password')

# Create a cursor from the connection
cursor = cnxn.cursor()


""" 
Select Basics
All SQL statements are executed using the Cursor execute() function. If the statement returns rows, such as a select statement, 
you can retrieve them using the Cursor fetch functions - fetchone(), fetchall(), fetchmany(). 
If there are no rows, fetchone() will return None, whereas fetchall() and fetchmany() will both return empty lists.
 """
cursor.execute("select user_id, user_name from users")
row = cursor.fetchone()
if row:
    print(row)

""" 
Row objects are similar to tuples, but they also allow access to columns by name:
"""
cursor.execute("select user_id, user_name from users")
row = cursor.fetchone()
print('name:', row[1])          # access by column index (zero-based)
print('name:', row.user_name)   # access by name

""" 
The fetchone() function returns None when all rows have been retrieved.
"""
while True:
    row = cursor.fetchone()
    if not row:
        break
    print('id:', row.user_id)

""" 
The fetchall() function returns all remaining rows in a list. Bear in mind those rows will all be stored in memory so if there a lot of rows, 
you may run out of memory. If there are no rows, an empty list is returned.
"""
cursor.execute("select user_id, user_name from users")
rows = cursor.fetchall()
for row in rows:
    print(row.user_id, row.user_name)

""" 
If you are going to process the rows one at a time, you can use the cursor itself as an iterator:
"""
cursor.execute("select user_id, user_name from users"):
for row in cursor:
    print(row.user_id, row.user_name)
# or just:
for row in cursor.execute("select user_id, user_name from users"):
    print(row.user_id, row.user_name)

""" 
Parameters
ODBC supports parameters using a question mark as a place holder in the SQL. You provide the values for the question marks by passing them after the SQL:
"""
cursor.execute("""
    select user_id, user_name
      from users
     where last_logon < ?
       and bill_overdue = ?
""", datetime.date(2001, 1, 1), 'y')

# The Python DB API specifies that parameters should be passed as a sequence, so this is also supported by pyodbc:
cursor.execute("""
    select user_id, user_name
      from users
     where last_logon < ?
       and bill_overdue = ?
""", [datetime.date(2001, 1, 1), 'y'])

""" 
Inserting Data
To insert data, pass the insert SQL to Cursor execute(), along with any parameters necessary:
"""
cursor.execute("insert into products(id, name) values ('pyodbc', 'awesome library')")
cnxn.commit()

# or, parameterized:
cursor.execute("insert into products(id, name) values (?, ?)", 'pyodbc', 'awesome library')
cnxn.commit()

""" 
Updating and Deleting
Updating and deleting work the same way, pass the SQL to execute. However, you often want to know how many records were affected when updating and deleting, 
in which case you can use the Cursor rowcount attribute:
"""
cursor.execute("delete from products where id <> ?", 'pyodbc')
print(cursor.rowcount, 'products deleted')
cnxn.commit()

# Since execute() always returns the cursor, you will sometimes see code like this (notice .rowcount on the end).
deleted = cursor.execute("delete from products where id <> 'pyodbc'").rowcount
cnxn.commit()

""" 
Tips and Tricks
Quotes
Since single quotes are valid in SQL, use double quotes to surround your SQL:
"""
deleted = cursor.execute("delete from products where id <> 'pyodbc'").rowcount

""" 
It's also worthwhile considering using 'raw' strings for your SQL to avoid any inadvertent escaping (unless you really do want to specify control characters):
"""
cursor.execute("delete from products where name like '%bad\name%'")   # Python will convert \n to 'new line'!
cursor.execute(r"delete from products where name like '%bad\name%'")  # no escaping

""" 
Naming Columns
Some databases (e.g. SQL Server) do not generate column names for calculated fields, e.g. COUNT(*). In that case you can either access the column by its index, 
or use an alias on the column (i.e. use the "as" keyword).
"""
row = cursor.execute("select count(*) as user_count from users").fetchone()
print('%s users' % row.user_count)

""" 
Formatting Long SQL Statements
Long SQL statements are best encapsulated using the triple-quote string format. Doing so does create a string with lots of blank space on the left, 
but whitespace should be ignored by database SQL engines. If you still want to remove the blank space on the left, you can use the dedent() function in the built-in textwrap module. 
For example:
"""
import textwrap
sql = textwrap.dedent("""
    select p.date_of_birth,
           p.email,
           a.city
    from person as p
    left outer join address as a on a.address_id = p.address_id
    where p.status = 'active'
      and p.name = ?
""")
rows = cursor.execute(sql, 'John Smith').fetchall()

""" 
fetchval
If you are selecting a single value you can use the fetchval convenience method. If the statement generates a row, it returns the value of the first column of the first row. 
If there are no rows, None is returned:
"""
maxid = cursor.execute("select max(id) from users").fetchval()

""" 
Most databases support COALESCE or ISNULL which can be used to convert NULL to a hardcoded value, but note that this will not cause a row to be returned if the SQL returns no rows. 
That is, COALESCE is great with aggregate functions like max or count, but fetchval is better when attempting to retrieve the value from a particular row:
"""
cursor.execute("select coalesce(max(id), 0) from users").fetchone()[0]
cursor.execute("select coalesce(count(*), 0) from users").fetchone()[0]

""" 
However, fetchval is a better choice if the statement can return an empty set:
"""
# Careful!
cursor.execute("""
    select create_timestamp
    from photos
    where user_id = 1
    order by create_timestamp desc
    limit 1
""").fetchone()[0]

# Preferred
cursor.execute("""
    select create_timestamp
    from photos
    where user = 1
    order by create_timestamp desc
    limit 1
""").fetchval()
""" 
The first example will raise an exception if there are no rows for user_id 1. The fetchone() call returns None. 
Python then attempts to apply [0] to the result (None[0]) which is not valid.

The fetchval method was created just for this situation - it will detect the fact that there are no rows and will return None.
"""
```

## Connection
* https://github.com/mkleehammer/pyodbc/wiki/Connection
```python
### Connection Attributes
""" 
autocommit
Setting autocommit True will cause the database to issue a commit after each SQL statement, otherwise database transactions will have to be explicity committed. 
As per the Python DB API, the default value is False (even though the ODBC default value is True). 
Typically, you will probably want to set autocommit True when creating a connection.
This value can be changed on a connection dynamically (e.g. cnxn.autocommit = True), and all subsequent SQL statements will be executed using the new setting.
Auto-commit typically needs to be True for DDL operations that cannot be rolled-back, e.g. dropping a database.
""" 

""" 
timeout
The timeout value, in seconds, for SQL queries (note, not database connections). Use zero, the default, to disable.
The timeout is applied to all cursors created by the connection, so it cannot be changed for a specific cursor or SQL statement. 
If a query timeout occurs, the database should raise an OperationalError exception with SQLSTATE HYT00 or HYT01.
Note, this attribute affects only SQL queries. To set the timeout when making a database connection, 
use the timeout parameter with the pyodbc connect() function[https://github.com/mkleehammer/pyodbc/wiki/The-pyodbc-Module#connect]
""" 

### Connection Functions
""" 
cursor()
Returns a new Cursor object using the connection.
mycursor = cnxn.cursor()
pyodbc supports multiple cursors per connection but your database may not.

commit()
Commits all SQL statements executed on the connection since the last commit/rollback.
cnxn.commit()
Note, this will commit the SQL statements from ALL the cursors created from this connection.

rollback()
Rolls back all SQL statements executed on the connection since the last commit.
cnxn.rollback()
You can call this even if no SQL statements have been executed on the connection, allowing it to be used in finally statements, etc.

close()
Closes the connection. Note, any uncommitted effects of SQL statements on the database from this connection will be rolled back and lost forever!
cnxn.close()
Connections are automatically closed when they are deleted (typically when they go out of scope) so you should not normally need to call this, 
but you can explicitly close the connection if you wish.
Trying to use a connection after it has been closed will result in a ProgrammingError exception.

getinfo()
This function is not part of the Python DB API.
Returns general information about the driver and data source associated with a connection by calling SQLGetInfo, e.g.:
data_source_name = cnxn.getinfo(pyodbc.SQL_DATA_SOURCE_NAME)
See Microsoft's SQLGetInfo documentation for the types of information available.

execute()
This function is not part of the Python DB API.
Creates a new Cursor object, calls its execute method, and returns the new cursor.
num_products = cnxn.execute("SELECT COUNT(*) FROM product")
See Cursor.execute() for more details. This is a convenience method that is not part of the DB API. 
Since a new Cursor is allocated by each call, this should not be used if more than one SQL statement needs to be executed on the connection.
""" 

### Context Manager
""" 
Connection objects do support the Python context manager syntax (the with statement), but it's important to understand the "context" in this scenario. 
For example, the following code:
""" 
with pyodbc.connect('mydsn') as cnxn:
    do_stuff

# is essentially equivalent to:
cnxn = pyodbc.connect('mydsn')
do_stuff
if not cnxn.autocommit:
    cnxn.commit()

""" 
As you can see, commit() is called when the context is exited, even if autocommit is False. 
Hence, the "context" here is not so much the connection itself. 
Rather, it's better to think of it as a database transaction that will be committed without explicitly calling commit().
Note, the connection object is not closed when the context is exited.
""" 
```


## Cursor
* https://github.com/mkleehammer/pyodbc/wiki/Cursor
```python
### Cursor Attributes
""" 
description
This read-only attribute is a list of 7-item tuples, one tuple for each column returned by the last SQL select statement. Each tuple contains:
1. column name (or alias, if specified in the SQL)
2. type code
3. display size (pyodbc does not set this value)
4. internal size (in bytes)
5. precision
6. scale
7. nullable (True/False)
This attribute will be None for operations that do not return rows or if one of the execute methods has not been called. 
The 'type code' value is the class type used to create the Python objects when reading rows. For example, a varchar column's type will be str.
"""

""" 
messages
Any descriptive messages generated by the query as part of the processing, as described in PEP-0249. Typically, these messages include PRINT statements and logs. 
The messages attribute is returned as a list of tuples. The first element in the tuple is the type of the message (similar to pyodbc error messages). 
The second element contains the text of the message. For example (on SQL Server):
"""
cnxn = pyodbc.connect(cnxn_str, autocommit=True)
crsr = cnxn.cursor()
crsr.execute("PRINT 'Hello world!'")
print(crsr.messages)
""" 
Results in:
[('[01000] (0)', '[Microsoft][ODBC Driver 17 for SQL Server][SQL Server]Hello world!')]
"""

""" 
rowcount
The number of rows modified by the last SQL statement.
This is -1 if no SQL has been executed or if the number of rows is unknown. 
Note that it is not uncommon for databases to report -1 immediately after a SQL select statement for performance reasons. 
(The exact number may not be known before the first records are returned to the application.)
"""

### Cursor Functions
""" 
execute(sql, *parameters)
Prepares and executes a SQL statement, returning the Cursor object itself. The optional parameters may be passed as a sequence, as specified by the DB API, or as individual values.
"""
# standard
cursor.execute("select a from tbl where b=? and c=?", (x, y))

# pyodbc extension
cursor.execute("select a from tbl where b=? and c=?", x, y)

# The return value is always the cursor itself:
for row in cursor.execute("select user_id, user_name from users"):
    print(row.user_id, row.user_name)

row  = cursor.execute("select * from tmp").fetchone()
rows = cursor.execute("select * from tmp").fetchall()

count = cursor.execute("update users set last_logon=? where user_id=?", now, user_id).rowcount
count = cursor.execute("delete from users where user_id=1").rowcount

""" 
executemany(sql, *params), with fast_executemany=False (the default)
Executes the same SQL statement for each set of parameters, returning None. The single params parameter must be a sequence of sequences, or a generator of sequences.
"""
params = [ ('A', 1), ('B', 2) ]
cursor.executemany("insert into t(name, id) values (?, ?)", params)

# This will execute the SQL statement twice, once with ('A', 1) and once with ('B', 2). That is, the above code is essentially equivalent to:
params = [ ('A', 1), ('B', 2) ]
for p in params:
    cursor.execute("insert into t(name, id) values (?, ?)", p)
""" 
Hence, running executemany() with fast_executemany=False is generally not going to be much faster than running multiple execute() commands directly.
Note, after running executemany(), the number of affected rows is NOT available in the rowcount attribute.

Also, be careful if autocommit is True. In this scenario, the provided SQL statement will be committed for each and every record in the parameter sequence. 
So if an error occurs part-way through processing, you will end up with some of the records committed in the database and the rest not, 
and it may be not be easy to tell which records have been committed. 
Hence, you may want to consider setting autocommit to False (and explicitly commit() / rollback()) to make sure either all the records are committed to the database or none are, 
e.g.:
"""
try:
    cnxn.autocommit = False
    params = [ ('A', 1), ('B', 2) ]
    cursor.executemany("insert into t(name, id) values (?, ?)", params)
except pyodbc.DatabaseError as err:
    cnxn.rollback()
else:
    cnxn.commit()
finally:
    cnxn.autocommit = True

""" 
executemany(sql, *params), with fast_executemany=True
Executes the SQL statement for the entire set of parameters, returning None. The single params parameter must be a sequence of sequences, or a generator of sequences.
"""
params = [ ('A', 1), ('B', 2) ]
cursor.fast_executemany = True
cursor.executemany("insert into t(name, id) values (?, ?)", params)
""" 
Here, all the parameters are sent to the database server in one bundle (along with the SQL statement), 
and the database executes the SQL against all the parameters as one database transaction. Hence, this form of executemany() should be much faster than the default executemany(). 
However, there are limitations to it, 
see fast_executemany[https://github.com/mkleehammer/pyodbc/wiki/Features-beyond-the-DB-API#fast_executemany] for more details.

Note, after running executemany(), the number of affected rows is NOT available in the rowcount attribute.

Under the hood, there is one important difference when fast_executemany=True. In that case, on the client side, 
pyodbc converts the Python parameter values to their ODBC "C" equivalents, based on the target column types in the database. 
E.g., a string-based date parameter value of "2018-07-04" is converted to a C date type binary value by pyodbc before sending it to the database. 
When fast_executemany=False, that date string is sent as-is to the database and the database does the conversion. 
This can lead to some subtle differences in behavior depending on whether fast_executemany is True or False.
"""

""" 
fetchone()
Returns the next row in the query, or None when no more data is available.
A ProgrammingError exception is raised if no SQL has been executed or if it did not return a result set (e.g. was not a SELECT statement).
"""
cursor.execute("select user_name from users where user_id=?", userid)
row = cursor.fetchone()
if row:
    print(row.user_name)

""" 
fetchval()
Returns the first column of the first row if there are results. 
For more info see Features beyond the DB API [https://github.com/mkleehammer/pyodbc/wiki/Features-beyond-the-DB-API#fetchval]
"""

""" 
fetchall()
Returns a list of all the remaining rows in the query.
Since this reads all rows into memory, it should not be used if there are a lot of rows. Consider iterating over the rows instead. 
However, it is useful for freeing up a Cursor so you can perform a second query before processing the resulting rows.
A ProgrammingError exception is raised if no SQL has been executed or if it did not return a result set (e.g. was not a SELECT statement).
"""
cursor.execute("select user_id, user_name from users where user_id < 100")
rows = cursor.fetchall()
for row in rows:
    print(row.user_id, row.user_name)

""" 
fetchmany(size=cursor.arraysize)
Returns a list of remaining rows, containing no more than size rows, used to process results in chunks. The list will be empty when there are no more rows.
The default for cursor.arraysize is 1 which is no different than calling fetchone().
Do not include the size= keyword when calling this method with an ad-hoc array size. Simply use
"""
rows = crsr.fetchmany(3)
# or
rows = crsr.fetchmany(size=3)

""" 
commit()
Commits all SQL statements executed on the connection that created this cursor, since the last commit/rollback.
This affects all cursors created by the same connection!
This is no different than calling commit on the connection. The benefit is that many uses can now just use the cursor and not have to track the connection.
"""

""" 
rollback()
Rolls back all SQL statements executed on the connection that created this cursor, since the last commit/rollback.
This affects all cursors created by the same connection!
"""

""" 
skip(count)
Skips the next count records in the query by calling SQLFetchScroll[https://msdn.microsoft.com/en-us/library/ms714682%28v=vs.85%29.aspx] with SQL_FETCH_NEXT.
For convenience, skip(0) is accepted and will do nothing.
"""

""" 
nextset()
This method will make the cursor skip to the next available result set, discarding any remaining rows from the current result set. 
If there are no more result sets, the method returns False. Otherwise, it returns a True and subsequent calls to the fetch methods will return rows from the next result set.
This method is primarily used if you have stored procedures that return multiple results.
"""

""" 
close()
Closes the cursor. A ProgrammingError exception will be raised if any operation is attempted with the cursor.
Cursors are closed automatically when they are deleted (typically when they go out of scope), so calling this is not usually necessary.
"""

""" 
setinputsizes(list_of_value_tuples)
This optional method can be used to explicitly declare the types and sizes of query parameters. For example:
"""
sql = "INSERT INTO product (item, price) VALUES (?, ?)"
params = [('bicycle', 499.99), ('ham', 17.95)]
# specify that parameters are for NVARCHAR(50) and DECIMAL(18,4) columns
crsr.setinputsizes([(pyodbc.SQL_WVARCHAR, 50, 0), (pyodbc.SQL_DECIMAL, 18, 4)])
#
crsr.executemany(sql, params)

""" 
tables(table=None, catalog=None, schema=None, tableType=None)
Returns an iterator for generating information about the tables in the database that match the given criteria.
The table, catalog, and schema interpret the '_' and '%' characters as wildcards. The escape character is driver specific, so use Connection.searchescape.
Each row has the following columns. See the SQLTables[https://msdn.microsoft.com/en-us/library/ms711831.aspx] documentation for more information.
1. table_cat: The catalog name.
2. table_schem: The schema name.
3. table_name: The table name.
4. table_type: One of the string values 'TABLE', 'VIEW', 'SYSTEM TABLE', 'GLOBAL TEMPORARY', 'LOCAL TEMPORARY', 'ALIAS', 'SYNONYM', or a datasource specific type name.
5. remarks: A description of the table.
"""
for row in cursor.tables():
    print(row.table_name)

# Does table 'x' exist?
if cursor.tables(table='x').fetchone():
   print('yes it does')

""" 
columns(table=None, catalog=None, schema=None, column=None)
Creates a result set of column information in the specified tables using the SQLColumns[https://msdn.microsoft.com/en-us/library/ms711683(VS.85).aspx] function.
Each row has the following columns:
1. table_cat
2. table_schem
3. table_name
4. column_name
5. data_type
6. type_name
7. column_size
8. buffer_length
9. decimal_digits
10. num_prec_radix
11. nullable
12. remarks
13. column_def
14. sql_data_type
15. sql_datetime_sub
16. char_octet_length
17. ordinal_position
18. is_nullable: One of SQL_NULLABLE, SQL_NO_NULLS, SQL_NULLS_UNKNOWN.
"""
# columns in table x
for row in cursor.columns(table='x'):
    print(row.column_name)

""" 
procedures(procedure=None, catalog=None, schema=None)
Executes SQLProcedures[http://msdn.microsoft.com/en-us/library/ms715368%28VS.85%29.aspx] and creates a result set of information about the procedures in the data source. 
Each row has the following columns:
1. procedure_cat
2. procedure_schem
3. procedure_name
4. num_input_params
5. num_output_params
6. num_result_sets
7. remarks
8. procedure_type
"""

### Context manager
""" 
Cursor objects do support the Python context manager syntax (the with statement), but it's important to understand the "context" in this scenario. The following code:
"""
with cnxn.cursor() as crsr:
    do_stuff

# is essentially equivalent to:
crsr = cnxn.cursor()
do_stuff
if not cnxn.autocommit:
    cnxn.commit()  
""" 
As you can see, commit() is called on the cursor's connection even if autocommit is False. Hence, the "context" is not so much the cursor itself. 
Rather, it's better to think of it as a database transaction that will be committed without explicitly calling commit().
Note, the cursor object is not explicitly closed when the context is exited.
"""
```


## Row
* https://github.com/mkleehammer/pyodbc/wiki/Row
```python
""" 
Row objects are returned from Cursor fetch functions. As specified in the DB API, they are tuple-like.
"""
row = cursor.fetchone()
print(row[0])

""" 
However, there are some pyodbc additions that make them very convenient:
- Values can be accessed by column name.
- The Cursor.description values can be accessed even after the cursor is closed.
- Values can be replaced.
- Rows from the same select statement share memory.
Accessing rows by column name is very convenient, readable, and Pythonish:
"""
cursor.execute("select album_id, photo_id from photos where user_id=1")
row = cursor.fetchone()
print(row.album_id, row.photo_id)
print(row[0], row[1])  # same as above, but less readable

""" 
This will not work if the column name is an invalid Python label (e.g. contains a space or is a Python reserved word), 
but you can still accessed by name using row.__getattribute__('My Value').
Having access to the cursor's description even after the cursor is closed makes Rows very convenient data structures - you can pass them around and they are self describing:
"""
def getuser(userid):
    cnxn = pyodbc.connect(...)
    cursor = cnxn.cursor()
    return cursor.execute("""
                          select album_id, photo_id 
                            from photos
                           where user_id = ?
                          """, userid).fetchall()

row = getuser(7)
# At this point the cursor has been closed and deleted
# But the columns and datatypes can still be access:
print('columns:', ', '.join(t[0] for t in row.cursor_description))

""" 
Unlike normal tuples, values in Row objects can be replaced. (This means you shouldn't use rows as dictionary keys!)
The intention is to make Rows convenient data structures to replace small or short-lived classes. While SQL is powerful, 
there are sometimes slight changes that need to be made after reading values:
"""
# Replace the 'start_date' datetime in each row with one that has a time zone.
rows = cursor.fetchall()
for row in rows:
    row.start_date = row.start_date.astimezone(tz)
# Note that slicing rows returns tuples, not Row objects!

"""
Attributes
cursor_description
A copy of the Cursor.description object from the Cursor that created this row. This contains the column names and data types of the columns. 
See Cursor.description[https://github.com/mkleehammer/pyodbc/wiki/Cursor#description]
"""
```

## Exceptions
* https://github.com/mkleehammer/pyodbc/wiki/Exceptions
```python
"""
Python exceptions are raised by pyodbc when ODBC errors are detected. The exception classes specified in the Python DB API specification are used:

Error
    DatabaseError
        DataError
        OperationalError
        IntegrityError
        InternalError
        ProgrammingError
        NotSupportedError

When an error occurs, the type of exception raised is based on the SQLSTATE value, typically provided by the database.

SQLSTATE  Exception
0A000     pyodbc.NotSupportedError
40002     pyodbc.IntegrityError
22***     pyodbc.DataError
23***     pyodbc.IntegrityError
24***     pyodbc.ProgrammingError
25***     pyodbc.ProgrammingError
42***     pyodbc.ProgrammingError
HYT00     pyodbc.OperationalError
HYT01     pyodbc.OperationalError

For example, a primary key error (attempting to insert a value when the key already exists) will raise an IntegrityError.
"""
```

## Data Types
* https://github.com/mkleehammer/pyodbc/wiki/Data-Types
```python
### Python 3
"""
Python parameters sent to the database
The following table describes how Python objects passed to Cursor.execute() as parameters are formatted and passed to the driver/database.

Python              Datatype        Description ODBC Datatype
None                null            varies (1)
bool                boolean         BIT
int                 integer         SQL_BIGINT
float               floating point  SQL_DOUBLE
decimal.Decimal     decimal         SQL_NUMERIC
str                 UTF-16LE (2)    SQL_VARCHAR or SQL_LONGVARCHAR (2)(3)
bytes,bytearray     binary          SQL_VARBINARY or SQL_LONGVARBINARY (3)
datetime.date       date            SQL_TYPE_DATE
datetime.time       time            SQL_TYPE_TIME
datetime.datetime   timestamp       SQL_TYPE_TIMESTAMP
uuid.UUID           UUID / GUID     SQL_GUID

1. If the driver supports it, SQLDescribeParam is used to determine the appropriate type. If it is not supported, SQL_VARCHAR is used.
2. The encoding and ODBC data type can be changed using Connection.setencoding(). See the Unicode page for more information.
3. SQLGetTypeInfo is used to determine when the LONG types are used. If it is not supported, 1MB is used.



SQL values received from the database
The following table describes how database results are converted to Python objects.

Description     ODBC Datatype                                       Python Datatype
NULL            any                                                 None
bit             SQL_BIT                                             bool
integers        SQL_TINYINT, SQL_SMALLINT, SQL_INTEGER, SQL_BIGINT  int
floating point  SQL_REAL, SQL_FLOAT, SQL_DOUBLE                     float
decimal,numeric SQL_DECIMAL, SQL_NUMERIC                            decimal.Decimal
1-byte text     SQL_CHAR                                            str via UTF-8 (1)
2-byte text     SQL_WCHAR                                           str via UTF-16LE (1)
binary          SQL_BINARY, SQL_VARBINARY                           bytes
date            SQL_TYPE_DATE                                       datetime.date
time            SQL_TYPE_TIME                                       datetime.time
SQL Server time SQL_SS_TIME2                                        datetime.time
timestamp       SQL_TIMESTAMP                                       datetime.datetime
UUID / GUID     SQL_GUID                                            str or uuid.UUID (2)
XML             SQL_XML                                             str via UTF-16LE (1)

1. The encoding can be changed using Connection.setdecoding(). See the Unicode page for more information.
2. The default is str. Setting pyodbc.native_uuid to True will cause them to be returned as uuid.UUID objects.

"""
```

## Database Transaction Management
* https://github.com/mkleehammer/pyodbc/wiki/Database-Transaction-Management
```python
"""
Those of you who come from a database background will be familiar with the idea of database transactions, 
i.e. where a series of SQL statements are committed together (or rolled-back) in one operation. 
Transactions are crucial if you need to make multiple updates to a database where each update in isolation would leave the database in an invalid or inconsistent state, 
albeit temporarily. The classic example of this is processing a check, where money is transferred from one bank account to another, 
i.e. a debit from one account and a credit to another account. 
It is important that both the debit and credit are committed together otherwise it will appear as if money has been (temporarily) created or destroyed.

Note, this whole article is relevant only when autocommit is set to False on the pyodbc connection (False is the default). Additionally, 
details may differ across database systems and ODBC drivers so check the relevant documentation where applicable. 
When autocommit is set to True, the database executes a commit automatically after every SQL statement, so transaction management by the client is not possible. 
Note, those automatic commits are executed by the database itself, not pyodbc. In this scenario, the database essentially runs every SQL statement within its own transaction.

When using pyodbc with autocommit=False, it is important to understand that you never explicitly open a database transaction in your Python code. 
Instead, a database transaction is implicitly opened when a Connection object is created with pyodbc.connect(). 
That database transaction is then either committed or rolled-back by explicitly calling commit() or rollback(), at which point a new database transaction is implicitly opened. 
SQL statements are executed using the Cursor execute() function, hence the equivalent of the following SQL:
---------------------------------------------------------------------------------SQL
BEGIN TRANSACTION
  UPDATE T1 SET ...
  DELETE FROM T1 WHERE ...
  INSERT INTO T1 VALUES ...
COMMIT TRANSACTION
BEGIN TRANSACTION
  INSERT INTO T2 VALUES ...
  INSERT INTO T3 VALUES ...
COMMIT TRANSACTION
---------------------------------------------------------------------------------SQL
in Python would be:
"""
cnxn = pyodbc.connect('mydsn', autocommit=False)
crsr = cnxn.cursor()
crsr.execute("UPDATE T1 SET ...")
crsr.execute("DELETE FROM T1 WHERE ...")
crsr.execute("INSERT INTO T1 VALUES ...")
cnxn.commit()
crsr.execute("INSERT INTO T2 VALUES ...")
crsr.execute("INSERT INTO T3 VALUES ...")
cnxn.commit()
cnxn.close()

"""
As you can see, no database transaction is ever explicitly opened using pyodbc but they are explicitly committed.

To be clear, database transactions are managed through connections, not cursors. 
Cursors are merely vehicles to execute SQL statements and manage their results, nothing more. 
Yes, there is a convenience function commit() on the Cursor object but that simply calls commit() on the cursor's parent Connection object. 
Bear in mind too that when commit() is called on a connection, ALL the updates from ALL the cursors on that connection are committed together (ditto for rollback()). 
If you want to have separate concurrent transactions, you will probably need to create a separate connection object for each transaction.

When autocommit is False, you must positively commit a transaction otherwise the transaction will almost certainly get rolled back eventually. 
For example, when a connection is closed with the close() function, a rollback is always issued on the connection. 
When a Connection object goes out of scope before it's closed (e.g. because an exception occurs), 
the Connection object is automatically deleted by Python, and a rollback is issued as part of the deletion process. 
The default database behavior is to rollback transactions so always remember to commit your transactions.
"""

### Specifying a Transaction Isolation level
"""
Database management systems that support transactions often support several levels of transaction isolation to control the effects of multiple processes 
performing simultaneous operations within their own transactions. ODBC supports four (4) levels of transaction isolation:
- SQL_TXN_READ_UNCOMMITTED
- SQL_TXN_READ_COMMITTED
- SQL_TXN_REPEATABLE_READ
- SQL_TXN_SERIALIZABLE
You can specify one of these in your Python code using the Connection set_attr() method on SQL_ATTR_TXN_ISOLATION, e.g.,
"""
cnxn = pyodbc.connect(conn_str, autocommit=True)
cnxn.set_attr(pyodbc.SQL_ATTR_TXN_ISOLATION, pyodbc.SQL_TXN_SERIALIZABLE)
cnxn.autocommit = False  # enable transactions
"""
Note that a particular database engine may not support all four isolation levels. For example, Microsoft Access only supports SQL_TXN_READ_COMMITTED.
"""
```


## Calling Stored Procedures
* https://github.com/mkleehammer/pyodbc/wiki/Calling-Stored-Procedures
```python
""" 
pyodbc does not currently implement the optional .callproc method. (It has been investigated[https://github.com/mkleehammer/pyodbc/issues/184].)
However, ODBC defines a {CALL ...} escape sequence[https://msdn.microsoft.com/en-us/library/ms403294.aspx] that should be supported by well-behaved ODBC drivers.
For example, to call a stored procedure named "usp_NoParameters" that takes no parameters, we can do
"""
crsr.execute("{CALL usp_NoParameters}")

# To call a stored procedure that takes only input parameters, we can do
params = (14, "Dinsdale")
crsr.execute("{CALL usp_UpdateFirstName (?,?)}", params)

""" 
Output Parameters and Return Values
Because pyodbc does not have .callproc we need to use a workaround for retrieving the values of output parameters and return values. 
The specific method will depend on what your particular ODBC driver supports, 
but for Microsoft's ODBC drivers for SQL Server we can use an "anonymous code block" to EXEC the stored procedure and then SELECT the output parameters and/or return values. 
For example, for the SQL Server stored procedure
---------------------------------------------------------------------------------SQL
CREATE PROCEDURE [dbo].[test_for_pyodbc] 
    @param_in nvarchar(max) = N'', 
    @param_out nvarchar(max) OUTPUT
AS
BEGIN
    SET NOCOUNT ON;

    -- set output parameter
    SELECT @param_out = N'Output parameter value: You said "' + @param_in + N'".';
    
    -- also return a couple of result sets
    SELECT N'SP result set 1, row 1' AS foo
    UNION ALL
    SELECT N'SP result set 1, row 2' AS foo;
    
    SELECT N'SP result set 2, row 1' AS bar
    UNION ALL
    SELECT N'SP result set 2, row 2' AS bar;
END
---------------------------------------------------------------------------------SQL
our Python code can do this
"""
sql = """\
DECLARE @out nvarchar(max);
EXEC [dbo].[test_for_pyodbc] @param_in = ?, @param_out = @out OUTPUT;
SELECT @out AS the_output;
"""
params = ("Burma!", )
crsr.execute(sql, params)
rows = crsr.fetchall()
while rows:
    print(rows)
    if crsr.nextset():
        rows = crsr.fetchall()
    else:
        rows = None
# to produce this:
""" 
[('SP result set 1, row 1', ), ('SP result set 1, row 2', )]
[('SP result set 2, row 1', ), ('SP result set 2, row 2', )]
[('Output parameter value: You said "Burma!".', )]
"""

""" 
Notice that the result set(s) created by the stored procedure are returned first, 
followed by the result set with the output parameter(s) as returned by the SELECT statement in the anonymous code block passed to the pyodbc .execute method.
Similarly, for a SQL Server stored procedure with a RETURN value we can use something like this:
"""
sql = """\
DECLARE @rv int;
EXEC @rv = [dbo].[another_test_sp];
SELECT @rv AS return_value;
"""
crsr.execute(sql)
return_value = crsr.fetchval()
```


## Features beyond the DB API
* https://github.com/mkleehammer/pyodbc/wiki/Features-beyond-the-DB-API
* https://www.python.org/dev/peps/pep-0249/
```python
""" 
fetchval
The fetchval() convenience method returns the first column of the first row if there are results, otherwise it returns None.
"""
count = cursor.execute('select count(*) from users').fetchval()

""" 
fast_executemany
(New in version 4.0.19.) Simply adding
"""
# crsr is a pyodbc.Cursor object
crsr.fast_executemany = True
""" 
can boost the performance of executemany operations by greatly reducing the number of round-trips to the server.
Notes:
- This feature is "off" by default, and is currently only recommended for applications that use Microsoft's ODBC Driver for SQL Server.
- The parameter values are held in memory, so very large numbers of records (tens of millions or more) may cause memory issues.
- Writing fractional seconds of datetime.time values is supported, 
  unlike normal pyodbc behavior[https://github.com/mkleehammer/pyodbc/wiki/Tips-and-Tricks-by-Database-Platform#time-columns]
- See this tip[https://github.com/mkleehammer/pyodbc/wiki/Tips-and-Tricks-by-Database-Platform#using-fast_executemany-with-a-temporary-table] 
  regarding fast_executemany and temporary tables.
- For information on using fast_executemany with SQLAlchemy (and pandas) see the Stack Overflow question here[https://stackoverflow.com/q/48006551/2144390].
"""

""" 
Access Values By Name
The DB API specifies that results must be tuple-like, so columns are normally accessed by indexing into the sequence (e.g. row[0]) and pyodbc supports this. 
However, columns can also be accessed by name:
"""
cursor.execute("select album_id, photo_id from photos where user_id=1")
row = cursor.fetchone()
print(row.album_id, row.photo_id)
print(row[0], row[1])  # same as above, but less readable
""" 
This makes the code easier to maintain when modifying SQL, more readable, and allows rows to be used where a custom class might otherwise be used. 
All rows from a single execute share the same dictionary of column names, so using Row objects to hold a large result set may also use less memory 
than creating a object for each row.
"""

""" 
The SQL "as" keyword allows the name of a column in the result set to be specified. This is useful if a column name has spaces or if there is no name:
"""
cursor.execute("select count(*) as photo_count from photos where user_id < 100")
row = cursor.fetchone()
print(row.photo_count)

""" 
Rows Values Can Be Replaced
Though SQL is very powerful, values sometimes need to be modified before they can be used. 
Rows allow their values to be replaced, which makes them even more convenient ad-hoc data structures.
"""
# Replace the 'start_date' datetime in each row with one that has a time zone.
rows = cursor.fetchall()
for row in rows:
    row.start_date = row.start_date.astimezone(tz)
# Note that columns cannot be added to rows; only values for existing columns can be modified.

""" 
Cursors are Iterable
The DB API makes this an optional feature. Each iteration returns a row object.
"""
cursor.execute("select album_id, photo_id from photos where user_id=1")
for row in cursor:
    print(row.album_id, row.photo_id)

""" 
Cursor.execute() Returns the Cursor
The DB API specification does not specify the return value of Cursor.execute(). 
Previous versions of pyodbc (2.0.x) returned different values, but the 2.1+ versions always return the Cursor itself.
This allows for compact code such as:
"""
for row in cursor.execute("select album_id, photo_id from photos where user_id=1"):
    print(row.album_id, row.photo_id)

row  = cursor.execute("select * from tmp").fetchone()
rows = cursor.execute("select * from tmp").fetchall()

count = cursor.execute("update photos set processed=1 where user_id=1").rowcount
count = cursor.execute("delete from photos where user_id=1").rowcount

""" 
Passing Parameters
As specified in the DB API, Cursor.execute() accepts an optional sequence of parameters:
"""
cursor.execute("select a from tbl where b=? and c=?", (x, y))

""" 
However, this seems complicated for something as simple as passing parameters, so pyodbc also accepts the parameters directly. 
Note in this example that x & y are not in a tuple:
"""
cursor.execute("select a from tbl where b=? and c=?", x, y)

""" 
Autocommit Mode
The DB API specifies that connections require a manual commit and pyodbc complies with this. 
However, connections also support autocommit, using the autocommit keyword of the connection function or the autocommit attribute of the Connection object:
"""
cnxn = pyodbc.connect(cstring, autocommit=True)

# or
cnxn.autocommit = True
cnxn.autocommit = False

""" 
Lowercase
Setting pyodbc.lowercase=True will cause all column names in rows to be lowercased. 
Some people find this easier to work with, particularly if a database has a mix of naming conventions. 
If your database is case-sensitive, however, it can cause some confusion.
"""

""" 
Connection Pooling
ODBC connection pooling is turned on by default. It can be turned off by setting pyodbc.pooling=False before any connections are made.
"""

""" 
Query Timeouts
The Connection.timeout attribute can be set to a number of seconds after which a query should raise an error. 
The value is in seconds and will cause an OperationalError to be raised with SQLSTATE HYT00 or HYT01. 
By default the timeout value is 0 which disables the timeout.
"""

""" 
Miscellaneous ODBC Functions
Most of the ODBC catalog functions are available as methods on Cursor objects. 
The results are presented as SELECT results in rows that are fetched normally. 
The Cursor page documents these, but it may be helpful to refer to Microsoft's ODBC documentation for more details.
For example:
"""
cnxn   = pyodbc.connect(...)
cursor = cnxn.cursor()
for row in cursor.tables():
    print(row.table_name)
"""
"ODBC Function"   "Method"  "Description"
"SQLTables"   "Cursor.tables"   Returns a list of table, catalog, or schema names, and table types.
"SQLColumns"  "Cursor.columns"  Returns a list of column names in specified tables.
"SQLStatistics"   "Cursor.statistics"   Returns a list of statistics about a single table and the indexes associated with the table.
"SQLSpecialColumns"   "Cursor.rowIdColumns" Returns a list of columns that uniquely identify a row.
"SQLSpecialColumns"   "Cursor.rowVerColumns"    Returns a list of columns that are automatically updated when any value in the row is updated.
"SQLPrimaryKeys"  "Cursor.primaryKeys"  Returns a list of column names that make up the primary key for a table.
"SQLForeignKeys"  "Cursor.foreignKeys"  Returns a list of column names that are foreign keys in the specified table (columns in the specified table that refer to primary 
                                        keys in other tables) or foreign keys in other tables that refer to the primary key in the specified table.
"SQLProcedures"   "Cursor.procedures"   Returns information about the procedures in the data source.
"SQLProcedures"   "Cursor.getTypeInfo"  Returns a information about the specified data type or all data types supported by the driver. 
"""
```


## Driver support for fast_executemany
* https://github.com/mkleehammer/pyodbc/wiki/Driver-support-for-fast_executemany
```python
""" 
Not all ODBC drivers support parameter arrays, the internal ODBC mechanism that fast_executemany uses to do its magic. 
If you have additional or updated information on a particular driver please feel free to update this list.
"Database"             "Driver Name"                   "Driver Version"  "OS"            "Result"  "Notes"
"Microsoft SQL Server" "ODBC Driver 17 for SQL Server" "17.x"            "Linux/Windows" "works"   "local temporary tables, TVPs"

local temporary tables
https://github.com/mkleehammer/pyodbc/wiki/Tips-and-Tricks-by-Database-Platform#using-fast_executemany-with-a-temporary-table

TVPs
https://github.com/mkleehammer/pyodbc/issues/601
"""

""" 
"No effect" means that enabling fast_executemany does not seem to cause problems, 
but it also doesn't make any significant difference to the amount of network traffic generated by an executemany call.
"""
```


## Using fast_executemany with a #temporary table
* https://github.com/mkleehammer/pyodbc/wiki/Tips-and-Tricks-by-Database-Platform
```python
""" 
Connecting to a named instance of SQL Server from a Linux client
Microsoft's SQL Server ODBC Driver for Linux is unable to resolve SQL Server instance names. 
However, if the SQL Browser service is running on the target machine we can use the (free) third-party 
sqlserverport[https://github.com/gordthompson/sqlserverport] module to look up the TCP port based on the instance name.
"""

""" 
DATETIMEOFFSET columns (e.g., "ODBC SQL type -155 is not yet supported")
Use an Output Converter function to retrieve such values. 
See the examples on the Using an Output Converter function[https://github.com/mkleehammer/pyodbc/wiki/Using-an-Output-Converter-function] wiki page.
Query parameters for DATETIMEOFFSET columns currently must be sent as strings. 
Note that SQL Server is rather fussy about the format of the string:
"""
# sample data
dto = datetime(2018, 8, 2, 0, 28, 12, 123456, tzinfo=timezone(timedelta(hours=-6)))

dto_string = dto.strftime("%Y-%m-%d %H:%M:%S.%f %z")  # 2018-08-02 00:28:12.123456 -0600
# Trying to use the above will fail with
#   "Conversion failed when converting date and/or time from character string."
# We need to add the colon for SQL Server to accept it
dto_string = dto_string[:30] + ":" + dto_string[30:]  # 2018-08-02 00:28:12.123456 -06:00

""" 
TIME columns
Due to legacy considerations, pyodbc uses the ODBC TIME_STRUCT structure for datetime.time query parameters. 
TIME_STRUCT does not understand fractional seconds, so datetime.time values have their fractional seconds truncated when passed to SQL Server.
"""
crsr.execute("CREATE TABLE #tmp (id INT, t TIME)")
t = datetime.time(hour=12, minute=23, second=34, microsecond=567890)
crsr.execute("INSERT INTO #tmp (id, t) VALUES (1, ?)", t)
rtn = crsr.execute("SELECT CAST(t AS VARCHAR) FROM #tmp WHERE id=1").fetchval()
print(rtn)  # 12:23:34.0000000

# The workaround is to pass the query parameter as a string
crsr.execute("INSERT INTO #tmp (id, t) VALUES (1, ?)", str(t))
rtn = crsr.execute("SELECT CAST(t AS VARCHAR) FROM #tmp WHERE id=1").fetchval()
print(rtn)  # 12:23:34.5678900

# Note that TIME columns retrieved by pyodbc have their microseconds intact
rtn = crsr.execute("SELECT t FROM #tmp WHERE id=1").fetchval()
print(repr(rtn))  # datetime.time(12, 23, 34, 567890)

""" 
SQL Server Numeric Precision vs. Python Decimal Precision
Python's decimal.Decimal type can represent floating point numbers with greater than 35 digits of precision, which is the maximum supported by SQL server. 
Binding parameters that exceed this precision will result in an invalid precision error from the driver ("HY104 [Microsoft][...]Invalid precision value").
"""

""" 
Using fast_executemany with a #temporary table
fast_executemany can have difficulty identifying the column types of a local #temporary table under some circumstances (#295[https://github.com/mkleehammer/pyodbc/issues/295]).

-- Workaround 1: ODBC Driver 17 for SQL Server and UseFMTONLY=Yes or ColumnEncryption=Enabled
Use "ODBC Driver 17 for SQL Server" (or newer) and include UseFMTONLY=Yes or ColumnEncryption=Enabled in the connection string, e.g.,
"""
cnxn_str = (
    "Driver=ODBC Driver 17 for SQL Server;"
    "Server=192.168.1.144,49242;"
    "UID=sa;PWD=_whatever_;"
    "Database=myDb;"
    "UseFMTONLY=Yes;"
)

# or
cnxn_str = (
    "Driver=ODBC Driver 17 for SQL Server;"
    "Server=192.168.1.144,49242;"
    "UID=sa;PWD=_whatever_;"
    "Database=myDb;"
    "ColumnEncryption=Enabled;"
)

""" 
-- Workaround 2: pyodbc 4.0.24 and Cursor.setinputsizes
Upgrade to pyodbc 4.0.24 (or newer) and use setinputsizes to specify the parameter type, etc..
"""
crsr.execute("""\
CREATE TABLE #issue295 (
    id INT IDENTITY PRIMARY KEY, 
    txt NVARCHAR(50), 
    dec DECIMAL(18,4)
    )""")
sql = "INSERT INTO #issue295 (txt, dec) VALUES (?, ?)"
params = [('Ώπα', 3.141)]
# explicitly set parameter type/size/precision
crsr.setinputsizes([(pyodbc.SQL_WVARCHAR, 50, 0), (pyodbc.SQL_DECIMAL, 18, 4)])
crsr.fast_executemany = True
crsr.executemany(sql, params)

""" 
-- Workaround 3: Use a global ##temporary table
If neither of the previous workarounds is feasible, simply use a global ##temporary table instead of a local #temporary table.
"""
```
