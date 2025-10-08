# Bug: Disable Input During Query Execution and Add Request Debouncing

## Bug Description
The application currently allows users to submit multiple queries simultaneously by clicking the query button multiple times or pressing Cmd+Enter/Ctrl+Enter repeatedly before a query completes. This can result in:
- Multiple concurrent API requests
- Race conditions in displaying results
- Confusing user experience with overlapping query results
- Potential server overload from rapid-fire requests

The query input textarea remains enabled during query execution, allowing users to modify or submit new queries before the current one completes.

## Problem Statement
Users can spam the query button or keyboard shortcut (Cmd+Enter/Ctrl+Enter) while a query is processing, creating multiple concurrent requests. The input area should be disabled during query execution to prevent this behavior, and requests should be debounced to prevent accidental rapid submissions.

## Solution Statement
Implement input disabling and request debouncing by:
1. Disabling the query textarea when a query starts processing
2. Re-enabling the textarea when the query completes (success or error)
3. Adding visual feedback (cursor, opacity) to indicate the disabled state
4. Implementing debounce on the query button click handler to prevent rapid-fire submissions
5. Ensuring keyboard shortcuts respect the disabled state

## Steps to Reproduce
1. Start the application (server + client)
2. Upload sample data (e.g., users.json)
3. Enter a query in the textarea
4. Rapidly click the Query button multiple times before the first query completes
5. OR: Rapidly press Cmd+Enter (Mac) or Ctrl+Enter (Windows/Linux) multiple times
6. Observe multiple concurrent requests being sent to the backend

## Root Cause Analysis
In `app/client/src/main.ts`, the `initializeQueryInput()` function:
- Only disables the query button during execution (line 24)
- Does not disable the textarea input field
- Does not implement debouncing on the button click handler
- Keyboard shortcut handler (lines 46-50) triggers `queryButton.click()` which can fire multiple times if the user holds down the keys

The current implementation:
```typescript
queryButton.addEventListener('click', async () => {
  const query = queryInput.value.trim();
  if (!query) return;

  queryButton.disabled = true;  // Only button is disabled
  queryButton.innerHTML = '<span class="loading"></span>';

  try {
    const response = await api.processQuery({...});
    displayResults(response, query);
    queryInput.value = '';
  } catch (error) {
    displayError(error instanceof Error ? error.message : 'Query failed');
  } finally {
    queryButton.disabled = false;
    queryButton.textContent = 'Query';
  }
});
```

The textarea (`queryInput`) is never disabled, allowing users to continue interacting with it and triggering multiple queries.

## Relevant Files
Use these files to fix the bug:

- **`app/client/src/main.ts`** (lines 16-51) - Contains the `initializeQueryInput()` function that handles query submission. This is where we need to:
  - Disable the textarea during query execution
  - Add debouncing to the query button click handler
  - Update the keyboard shortcut handler to respect disabled state
  - Add visual feedback for disabled state

- **`app/client/src/style.css`** - Contains the styling for the application. We need to add CSS rules for:
  - Disabled textarea appearance (cursor, opacity, pointer-events)
  - Visual indication that input is processing

### New Files

- **`.claude/commands/e2e/test_query_debounce.md`** - E2E test to validate that:
  - Query input is disabled during execution
  - Multiple rapid clicks don't create concurrent requests
  - Visual feedback is shown when disabled
  - Keyboard shortcuts respect disabled state

## Step by Step Tasks
IMPORTANT: Execute every step in order, top to bottom.

### 1. Add Debounce Utility Function
- Add a generic debounce utility function at the top of `app/client/src/main.ts` (after imports, before global state)
- Use a simple debounce implementation that delays function execution until after a specified wait time has elapsed since the last invocation
- Set debounce delay to 300ms to prevent accidental double-clicks

### 2. Update Query Input Handler to Disable Textarea
- Modify `initializeQueryInput()` in `app/client/src/main.ts`
- Add `queryInput.disabled = true` when query execution starts (alongside existing `queryButton.disabled = true`)
- Add `queryInput.disabled = false` in the finally block when query execution completes
- Wrap the query button click handler with the debounce utility function

### 3. Update Keyboard Shortcut to Respect Disabled State
- Modify the keyboard event listener in `initializeQueryInput()` (lines 46-50)
- Check if `queryButton.disabled` is true before calling `queryButton.click()`
- This prevents keyboard shortcuts from triggering when a query is already running

### 4. Add CSS for Disabled Textarea Visual Feedback
- Add CSS rules in `app/client/src/style.css` for `textarea:disabled` state
- Set `cursor: not-allowed` to indicate the field is disabled
- Set `opacity: 0.6` to visually dim the textarea
- Set `pointer-events: none` to prevent any mouse interactions
- Ensure the styling is consistent with the existing design

### 5. Create E2E Test for Query Debouncing
- Read `.claude/commands/e2e/test_basic_query.md` and `.claude/commands/e2e/test_complex_query.md` to understand the E2E test format
- Create a new E2E test file `.claude/commands/e2e/test_query_debounce.md` that:
  - Validates the textarea is disabled when a query is running
  - Attempts to click the query button multiple times rapidly (within 300ms)
  - Verifies only one request is sent to the backend
  - Takes screenshots showing the disabled state (dimmed textarea, not-allowed cursor)
  - Validates that the textarea is re-enabled after query completion
  - Tests keyboard shortcut (Cmd+Enter) doesn't fire when disabled

### 6. Run Validation Commands
- Execute all validation commands listed below to ensure the bug is fixed with zero regressions

## Validation Commands
Execute every command to validate the bug is fixed with zero regressions.

- Read `.claude/commands/test_e2e.md`, then read and execute the new E2E test file `.claude/commands/e2e/test_query_debounce.md` to validate the debouncing and input disabling functionality works
- `cd app/server && uv run pytest` - Run server tests to validate the bug is fixed with zero regressions
- `cd app/client && bun run build` - Run frontend build to validate the bug is fixed with zero regressions

## Notes
- The debounce delay of 300ms strikes a balance between preventing accidental double-clicks and maintaining responsive UX
- Disabling the textarea prevents users from modifying the query mid-execution, which could cause confusion
- The visual feedback (opacity + cursor) clearly communicates to users that the input is temporarily unavailable
- The keyboard shortcut respecting the disabled state ensures consistent behavior across input methods
- No new libraries are required - we implement a simple debounce function directly in the codebase
