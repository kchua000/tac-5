#!/usr/bin/env python3
"""E2E test for SQL injection protection - API-based approach"""

import json
import sys
import requests
import time

def run_test():
    base_path = "/home/kchua000/Python Repositories/Training/tactical-agentic-coding/tac-5"

    test_result = {
        "test_name": "SQL Injection Protection",
        "status": "passed",
        "screenshots": [],
        "error": None
    }

    try:
        base_url = "http://localhost:8000"

        # Step 1: Check health
        print("Step 1: Checking API health")
        response = requests.get(f"{base_url}/api/health")
        if response.status_code != 200:
            test_result["status"] = "failed"
            test_result["error"] = f"(Step 1 ❌) API health check failed with status {response.status_code}"
            return test_result

        health_data = response.json()
        print(f"API Health: {health_data}")

        # Step 2: Get schema to verify tables exist
        print("\nStep 2: Getting database schema")
        response = requests.get(f"{base_url}/api/schema")
        if response.status_code != 200:
            test_result["status"] = "failed"
            test_result["error"] = f"(Step 2 ❌) Schema retrieval failed with status {response.status_code}"
            return test_result

        schema_before = response.json()
        tables_before = [table["name"] for table in schema_before.get("tables", [])]
        print(f"Tables before attack: {tables_before}")

        # Step 3: Attempt SQL injection with DROP TABLE
        print("\nStep 3: Attempting SQL injection: DROP TABLE users;")
        malicious_query = "DROP TABLE users;"

        response = requests.post(
            f"{base_url}/api/query",
            json={"query": malicious_query}
        )

        print(f"Response status: {response.status_code}")
        response_data = response.json()
        print(f"Response data: {json.dumps(response_data, indent=2)}")

        # Step 4: Verify error response
        print("\nStep 4: Verifying security error response")

        # Check if error field is present in response
        error_detail = response_data.get("error", "")
        if not error_detail:
            error_detail = response_data.get("detail", "")

        print(f"Error detail: {error_detail}")

        # Verify there's an error message
        if not error_detail:
            test_result["status"] = "failed"
            test_result["error"] = f"(Step 4 ❌) No error message returned for malicious query"
            print(f"FAILED: {test_result['error']}")
            return test_result

        # Check if error message contains security-related text
        if "security" not in error_detail.lower() and "dangerous" not in error_detail.lower() and "not allowed" not in error_detail.lower():
            test_result["status"] = "failed"
            test_result["error"] = f"(Step 4 ❌) Error message does not indicate security protection. Got: {error_detail}"
            print(f"FAILED: {test_result['error']}")
            return test_result

        print("SUCCESS: Security error received as expected")

        # Step 5: Verify database tables are intact
        print("\nStep 5: Verifying database integrity")
        response = requests.get(f"{base_url}/api/schema")
        if response.status_code != 200:
            test_result["status"] = "failed"
            test_result["error"] = f"(Step 5 ❌) Schema retrieval failed after attack with status {response.status_code}"
            return test_result

        schema_after = response.json()
        tables_after = [table["name"] for table in schema_after.get("tables", [])]
        print(f"Tables after attack: {tables_after}")

        # Verify all original tables still exist
        if set(tables_before) != set(tables_after):
            test_result["status"] = "failed"
            test_result["error"] = f"(Step 5 ❌) Database structure changed! Before: {tables_before}, After: {tables_after}"
            print(f"FAILED: {test_result['error']}")
            return test_result

        print("SUCCESS: All tables remain intact")

        # Additional test: Try another malicious query
        print("\nStep 6: Testing additional SQL injection vector")
        malicious_queries = [
            "'; DROP TABLE users; --",
            "1' OR '1'='1",
            "SELECT * FROM users; DELETE FROM users;"
        ]

        for idx, query in enumerate(malicious_queries):
            print(f"\n  Testing query {idx+1}: {query}")
            response = requests.post(
                f"{base_url}/api/query",
                json={"query": query}
            )

            if response.status_code == 200:
                # This shouldn't succeed for direct SQL
                response_data = response.json()
                # If it's a natural language response, that's okay
                if "sql" in response_data and response_data.get("sql", "").startswith(("DROP", "DELETE", "UPDATE", "INSERT")):
                    test_result["status"] = "failed"
                    test_result["error"] = f"(Step 6.{idx+1} ❌) Dangerous SQL was generated: {response_data.get('sql')}"
                    print(f"FAILED: {test_result['error']}")
                    return test_result

            print(f"  Query {idx+1} properly handled")

        print("\nALL TESTS PASSED!")

    except Exception as e:
        test_result["status"] = "failed"
        test_result["error"] = f"Unexpected error: {str(e)}"
        print(f"FAILED: {test_result['error']}")
        import traceback
        traceback.print_exc()

    # Output JSON result
    print("\n" + "="*80)
    print(json.dumps(test_result, indent=2))
    print("="*80)

    return test_result

if __name__ == "__main__":
    result = run_test()
    sys.exit(0 if result["status"] == "passed" else 1)
