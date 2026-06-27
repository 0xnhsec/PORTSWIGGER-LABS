# SQL Injection (SQLi) Fundamentals

SQL injection (SQLi) is a critical web security vulnerability that allows an attacker to interfere with the queries that an application makes to its database. This can allow an attacker to view data that they are not normally able to retrieve. This might include data that belongs to other users, or any other data that the application can access. 

In many cases, an attacker can modify or delete this database data, causing persistent changes to the application'content or behavior. In some situations, an attacker can escalate a SQL injection attack to compromise the underlying server or other back-end infrastructure, or perform denial-of-service attacks.

---

## Root Cause — WHY it exists

SQL injection vulnerabilities arise when user-supplied input is directly concatenated into a dynamic SQL query string instead of using parameterized queries (or prepared statements). The database interpreter is unable to distinguish between the intended code structure and the malicious data payload injected by the user.

```
[User Input: ' OR 1=1--] ──→ [Dynamic SQL Concatenation] ──→ [Database Interpreter Executes Input as Code]
```

---

## Detection Methodology

You can detect SQL injection manually using a systematic set of tests against every entry point in the application:

1. **Submit single quote character `'` (or `"`):** Analyze responses for database errors, 500 Internal Server Errors, or visual anomalies.
2. **Boolean Condition Verification:** Submit `OR 1=1` and `OR 1=2`, and look for differences in the application's responses.
3. **Database-Specific Syntax Testing:** Try using query concatenation operators or built-in functions.
4. **Time Delay Payloads:** Inject payloads designed to trigger time delays (e.g. `pg_sleep(10)` or `dbms_pipe.receive_message`) and observe response latency.

---

## Impact of Successful SQLi

A successful SQL injection attack can result in:
- Unauthorized access to sensitive data (passwords, credit cards, user information).
- Bypassing authentication screens.
- Modifying or destroying database records (Data Manipulation/Integrity Loss).
- Executing administrative operations (shutting down database, clearing logs).
- Reading/writing local files on the database server.
- Command execution on the operating system of the hosting server.
