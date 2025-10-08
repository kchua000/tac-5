# Bug: SQLite Tests Running Against Live Database

## Bug Description
One of our SQLite tests is running against the 'live' database (`db/database.db`) and saving a `data___DROP_TABLE_users____` table. The test should be using an in-memory SQLite database instead to ensure proper test isolation and prevent pollution of the production database.

The bug manifests as:
- Tests in `tests/core/test_sql_processor.py` create test data in the live `db/database.db` file
- Tests in `tests/core/test_file_processor.py` create test tables in the live database
- A malicious test table `data___DROP_TABLE_users____` exists in the live database from `test_integration_upload_malicious_filename` test
- Expected behavior: All tests should use isolated in-memory databases (`:memory:`) or temporary database files

## Problem Statement
The test fixtures in `test_sql_processor.py` and `test_file_processor.py` attempt to patch `sqlite3.connect` to use an in-memory database, but the patch context manager exits before the fixture yields to the test. This means when the actual test runs and calls functions in `sql_processor.py` or `file_processor.py`, the patch is no longer active, and the code connects to the live database at `db/database.db`.

Additionally, `test_integration_upload_malicious_filename` in `test_sql_injection.py` calls `convert_csv_to_sqlite()` which creates a real table in the live database because it doesn't properly use a patched database connection.

## Solution Statement
Fix the test fixtures to maintain the database connection patch throughout the test execution by restructuring the patch context manager. The patch should remain active when the fixture yields, ensuring all database operations during tests use the in-memory or temporary database instead of the live database.

We'll use pytest's `@patch` decorator at the fixture level to ensure the patch persists for the entire test duration, and pass the mocked connection explicitly to ensure proper test isolation.

## Steps to Reproduce
1. Navigate to `app/server` directory
2. Check the live database for test tables:
   ```bash
   python3 -c "import sqlite3; conn = sqlite3.connect('db/database.db'); cursor = conn.cursor(); cursor.execute('SELECT name FROM sqlite_master WHERE type=\"table\"'); print([row[0] for row in cursor.fetchall()]); conn.close()"
   ```
3. Observe the `data___DROP_TABLE_users____` table exists
4. Run the tests:
   ```bash
   cd app/server && uv run pytest tests/core/test_sql_processor.py -v
   ```
5. Check the database again and observe test data persists in the live database

## Root Cause Analysis
In `tests/core/test_sql_processor.py` lines 43-46 and `tests/core/test_file_processor.py` lines 14-17:

```python
# Patch the database connection to use our in-memory database
with patch('core.sql_processor.sqlite3.connect') as mock_connect:
    mock_connect.return_value = conn
    yield conn
```

The `with` block creates a context manager for the patch, but it exits immediately after the `yield` statement. The test execution happens *after* the fixture yields, at which point the `with` block has already exited and the patch is no longer active. When the test calls functions in `sql_processor.py` or `file_processor.py`, those functions call `sqlite3.connect("db/database.db")` without any patch in effect, connecting to the live database.

The correct approach is to use the `@patch` decorator or restructure the fixture so the patch context manager remains active throughout the test execution.

## Relevant Files
Use these files to fix the bug:

- `app/server/tests/core/test_sql_processor.py` - Test file with broken fixture that needs fixing. Lines 7-48 contain the `test_db` fixture with the improperly scoped patch.
- `app/server/tests/core/test_file_processor.py` - Test file with the same broken fixture pattern. Lines 8-19 contain the `test_db` fixture with the improperly scoped patch.
- `app/server/tests/test_sql_injection.py` - Contains `test_integration_upload_malicious_filename` (line 328) that creates tables in the live database. This test uses a `test_db` fixture (lines 25-66) that creates a temporary file but the test doesn't properly isolate the `convert_csv_to_sqlite` call.
- `app/server/core/sql_processor.py` - Contains hardcoded database path `"db/database.db"` on line 18 and line 66.
- `app/server/core/file_processor.py` - Contains hardcoded database path `"db/database.db"` on line 58 and other locations.

## Step by Step Tasks
IMPORTANT: Execute every step in order, top to bottom.

### 1. Fix test_sql_processor.py fixture to properly patch database connection
- Restructure the `test_db` fixture in `tests/core/test_sql_processor.py` to use pytest's `@patch` decorator or ensure the patch context manager remains active during test execution
- The patch should be active from before the fixture yields until after the test completes
- Verify the in-memory database connection is used throughout the test lifecycle

### 2. Fix test_file_processor.py fixture to properly patch database connection
- Apply the same fix pattern to the `test_db` fixture in `tests/core/test_file_processor.py`
- Ensure the patch remains active during test execution
- Verify file processor tests use the in-memory database

### 3. Fix test_sql_injection.py integration test to use test database
- Update `test_integration_upload_malicious_filename` in `tests/test_sql_injection.py` to properly patch the database connection before calling `convert_csv_to_sqlite()`
- Ensure this test uses the temporary `test_db` fixture database instead of the live database
- Add proper mocking/patching to intercept the database connection in `file_processor.py`

### 4. Clean up polluted live database
- Remove the `data___DROP_TABLE_users____` table from the live database
- Verify no other test tables exist in `db/database.db`
- Document this cleanup step for future reference

### 5. Run Validation Commands to verify bug is fixed
- Execute all validation commands listed in the "Validation Commands" section below
- Verify no test tables are created in the live database after running tests
- Confirm all tests pass with proper isolation

## Validation Commands
Execute every command to validate the bug is fixed with zero regressions.

- Check live database before tests:
  ```bash
  cd app/server && python3 -c "import sqlite3; conn = sqlite3.connect('db/database.db'); cursor = conn.cursor(); cursor.execute('SELECT name FROM sqlite_master WHERE type=\"table\" ORDER BY name'); tables_before = [row[0] for row in cursor.fetchall()]; print('Tables before tests:', tables_before); conn.close()"
  ```
- `cd app/server && uv run pytest tests/core/test_sql_processor.py -v` - Run sql_processor tests to validate they use in-memory database
- `cd app/server && uv run pytest tests/core/test_file_processor.py -v` - Run file_processor tests to validate they use in-memory database
- `cd app/server && uv run pytest tests/test_sql_injection.py::test_integration_upload_malicious_filename -v` - Run the specific integration test that was creating tables in live database
- Check live database after tests to ensure no new tables were created:
  ```bash
  cd app/server && python3 -c "import sqlite3; conn = sqlite3.connect('db/database.db'); cursor = conn.cursor(); cursor.execute('SELECT name FROM sqlite_master WHERE type=\"table\" ORDER BY name'); tables_after = [row[0] for row in cursor.fetchall()]; print('Tables after tests:', tables_after); conn.close()"
  ```
- `cd app/server && uv run pytest` - Run all server tests to validate the bug is fixed with zero regressions
- `cd app/client && bun tsc --noEmit` - Run frontend type checking to validate no regressions
- `cd app/client && bun run build` - Run frontend build to validate no regressions

## Notes
- The root cause is a common pytest fixture pitfall: context managers exiting before the test runs
- The fix requires ensuring the mock/patch remains active throughout the entire test execution, not just during fixture setup
- This is a critical bug because tests should never modify production data or databases
- After fixing, consider adding a test that verifies test isolation by checking that the live database remains unchanged after test runs
- The `test_sql_injection.py` file already uses the correct pattern with temporary database files - we should consider this approach for consistency
- Consider documenting this pattern in the project's testing guidelines to prevent similar issues in the future
