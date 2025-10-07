#!/usr/bin/env python3
"""E2E test for SQL injection protection"""

import json
import sys
import os
import subprocess
from playwright.sync_api import sync_playwright, expect

def check_playwright_dependencies():
    """Check if Playwright system dependencies are installed"""
    try:
        # Try to check for key dependencies
        result = subprocess.run(
            ["dpkg", "-l", "libnspr4", "libnss3"],
            capture_output=True,
            text=True
        )
        return result.returncode == 0
    except Exception:
        return False

def run_test():
    base_path = "/home/kchua000/Python Repositories/Training/tactical-agentic-coding/tac-5"
    screenshot_dir = f"{base_path}/agents/a7dd3c03/e2e_test_runner_0_0/img/sql_injection"

    test_result = {
        "test_name": "SQL Injection Protection",
        "status": "passed",
        "screenshots": [],
        "error": None
    }

    # Check for Playwright dependencies
    if not check_playwright_dependencies():
        test_result["status"] = "failed"
        test_result["error"] = (
            "Playwright system dependencies not installed. "
            "Run './scripts/setup_playwright.sh' to install required packages "
            "(libnspr4, libnss3, libasound2t64, etc.). "
            "Note: This requires sudo access."
        )
        print(f"SKIPPED: {test_result['error']}")
        print("\n" + "="*80)
        print(json.dumps(test_result, indent=2))
        print("="*80)
        return test_result

    try:
        with sync_playwright() as p:
            # Launch browser in headed mode
            browser = p.chromium.launch(headless=False)
            page = browser.new_page()

            try:
                # Step 1: Navigate to application
                print("Step 1: Navigating to http://localhost:5173")
                page.goto("http://localhost:5173", wait_until="networkidle", timeout=10000)

                # Step 2: Take screenshot of initial state
                print("Step 2: Taking screenshot of initial state")
                screenshot_path = f"{screenshot_dir}/01_initial_state.png"
                page.screenshot(path=screenshot_path)
                test_result["screenshots"].append(screenshot_path)

                # Step 3: Clear the query input
                print("Step 3: Clearing query input")
                query_input = page.locator('[data-testid="query-input"]')
                query_input.click()
                query_input.fill("")

                # Step 4: Enter malicious SQL
                print("Step 4: Entering malicious SQL: DROP TABLE users;")
                query_input.fill("DROP TABLE users;")

                # Step 5: Take screenshot of malicious query input
                print("Step 5: Taking screenshot of malicious query input")
                screenshot_path = f"{screenshot_dir}/02_malicious_query.png"
                page.screenshot(path=screenshot_path)
                test_result["screenshots"].append(screenshot_path)

                # Step 6: Click Query button
                print("Step 6: Clicking Query button")
                query_button = page.locator('[data-testid="query-button"]')
                query_button.click()

                # Wait for response
                page.wait_for_timeout(2000)

                # Step 7: Verify error message appears
                print("Step 7: Verifying security error message")
                error_message = page.locator('[data-testid="error-message"]')

                # Check if error message is visible
                if not error_message.is_visible():
                    test_result["status"] = "failed"
                    test_result["error"] = "(Step 7 ❌) Failed to find visible error message with selector 'error-message'"
                    print(f"FAILED: {test_result['error']}")
                else:
                    error_text = error_message.text_content()
                    print(f"Found error message: {error_text}")

                    # Verify it contains "Security error" or similar
                    if "security" not in error_text.lower() and "error" not in error_text.lower():
                        test_result["status"] = "failed"
                        test_result["error"] = f"(Step 7 ❌) Error message does not contain security-related text. Found: {error_text}"
                        print(f"FAILED: {test_result['error']}")

                # Step 8: Take screenshot of security error
                print("Step 8: Taking screenshot of security error")
                screenshot_path = f"{screenshot_dir}/03_security_error.png"
                page.screenshot(path=screenshot_path)
                test_result["screenshots"].append(screenshot_path)

                # Step 9: Verify users table still exists
                print("Step 9: Verifying users table still exists in Available Tables")
                tables_section = page.locator('[data-testid="available-tables"]')

                if not tables_section.is_visible():
                    # Try alternate selector
                    tables_section = page.locator('text=Available Tables')
                    if tables_section.count() == 0:
                        test_result["status"] = "failed"
                        test_result["error"] = "(Step 9 ❌) Failed to find Available Tables section"
                        print(f"FAILED: {test_result['error']}")
                else:
                    # Check if users table is listed
                    page_content = page.content()
                    if "users" not in page_content.lower():
                        test_result["status"] = "failed"
                        test_result["error"] = "(Step 9 ❌) Users table not found in Available Tables section"
                        print(f"FAILED: {test_result['error']}")
                    else:
                        print("SUCCESS: Users table still exists")

                # Step 10: Take screenshot showing tables are intact
                print("Step 10: Taking screenshot of intact tables")
                screenshot_path = f"{screenshot_dir}/04_tables_intact.png"
                page.screenshot(path=screenshot_path)
                test_result["screenshots"].append(screenshot_path)

                # Keep browser open for a moment
                page.wait_for_timeout(2000)

            finally:
                browser.close()

    except Exception as e:
        test_result["status"] = "failed"
        test_result["error"] = f"Unexpected error: {str(e)}"
        print(f"FAILED: {test_result['error']}")

    # Output JSON result
    print("\n" + "="*80)
    print(json.dumps(test_result, indent=2))
    print("="*80)

    return test_result

if __name__ == "__main__":
    result = run_test()
    sys.exit(0 if result["status"] == "passed" else 1)
