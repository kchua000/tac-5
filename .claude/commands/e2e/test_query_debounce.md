# E2E Test: Query Debouncing and Input Disabling

Test that the query input is properly disabled during query execution and that rapid clicking is debounced.

## User Story

As a user
I want the query input to be disabled while a query is processing
So that I cannot accidentally submit multiple queries simultaneously

## Test Steps

1. Navigate to the `Application URL`
2. Take a screenshot of the initial state
3. **Verify** the page title is "Natural Language SQL Interface"
4. **Verify** query input textarea is enabled (not disabled)

5. Enter the query: "Show me all users from the users table"
6. Take a screenshot of the query input before submission

7. Click the Query button
8. **Immediately verify** (within 100ms) that:
   - Query input textarea is disabled
   - Query button is disabled
   - Query button shows loading spinner
9. Take a screenshot showing the disabled state (should show dimmed textarea)

10. **Attempt to click** the Query button 3 more times rapidly (within 300ms)
11. **Verify** that only 1 query request was sent to the backend (check network logs or response count)

12. Wait for query to complete
13. **Verify** that:
    - Query input textarea is re-enabled
    - Query button is re-enabled
    - Query button text is "Query" (not loading spinner)
14. Take a screenshot showing the re-enabled state

15. Enter another query: "Show me users from San Francisco"
16. Press Cmd+Enter (Mac) or Ctrl+Enter (Windows/Linux) to submit
17. **Immediately verify** that query input is disabled
18. **Attempt to press** Cmd+Enter / Ctrl+Enter 3 more times rapidly
19. **Verify** that only 1 query request was sent (keyboard shortcut respects disabled state)

20. Wait for query to complete
21. **Verify** query input is re-enabled
22. Take a screenshot of the final state

## Success Criteria
- Query input is disabled when query starts
- Query input is re-enabled when query completes
- Visual feedback is shown (opacity: 0.6, cursor: not-allowed)
- Rapid clicking is debounced (only 1 request sent for multiple clicks within 300ms)
- Keyboard shortcut (Cmd+Enter/Ctrl+Enter) respects disabled state
- No concurrent requests are sent
- 5 screenshots are taken
