# Feature: Random Natural Language Query Button

## Feature Description
A new button that automatically generates interesting natural language queries based on the existing database schema and table structures. When clicked, it uses the LLM processor to create contextually relevant queries (limited to two sentences maximum) based on the available tables and their columns. The generated query immediately overwrites the existing content in the query input field, allowing users to manually execute it. The button is styled like the "Upload Data" button and positioned with space-between justification from the existing primary buttons.

## User Story
As a user
I want to generate random natural language queries based on my data
So that I can discover interesting insights and learn what types of questions I can ask without having to think of queries myself

## Problem Statement
Users often don't know what questions to ask or how to phrase natural language queries when they first upload data. There's no quick way to explore the capabilities of the natural language interface or get inspiration for meaningful queries. New users especially struggle with understanding what types of questions work well with their specific dataset.

## Solution Statement
Add a "Generate Query" button that leverages the existing `llm_processor.py` module to automatically create interesting, contextually relevant natural language queries based on the current database schema. The button will analyze available tables, their columns, data types, and row counts to generate queries that make sense for the user's data. Each generated query will be concise (max two sentences) and immediately populate the input field, ready for the user to execute or modify as needed.

## Relevant Files
Use these files to implement the feature:

**Server-side files:**
- `app/server/server.py` - Add new endpoint `/api/generate-query` for generating random queries
- `app/server/core/llm_processor.py` - Add function to generate interesting queries based on schema
- `app/server/core/data_models.py` - Add Pydantic models for generate query request/response
- `app/server/core/sql_processor.py` - Use existing `get_database_schema()` to provide context to LLM

**Client-side files:**
- `app/client/src/main.ts` - Add button event handler and query generation logic
- `app/client/src/api/client.ts` - Add API method for generating queries
- `app/client/src/types.d.ts` - Add TypeScript interfaces for generate query request/response
- `app/client/index.html` - Add "Generate Query" button to the query controls section
- `app/client/src/style.css` - Add styles for the new button (matching Upload Data style)

**Testing files:**
- `app/server/tests/core/test_llm_processor.py` - Add tests for query generation function
- `.claude/commands/test_e2e.md` - Read to understand E2E test execution
- `.claude/commands/e2e/test_basic_query.md` - Reference example for creating E2E tests

### New Files
- `.claude/commands/e2e/test_generate_query.md` - E2E test to validate query generation feature

## Implementation Plan
### Phase 1: Foundation
Create the backend infrastructure for query generation. This includes adding a new function to the LLM processor that analyzes the database schema and generates contextually relevant natural language queries. Set up the necessary data models and API endpoint to support the feature.

### Phase 2: Core Implementation
Implement the server-side query generation logic with proper prompt engineering to create interesting, diverse queries. Build the client-side button UI component and wire it to the backend API. Ensure the generated queries properly overwrite the input field content.

### Phase 3: Integration
Connect all components, add proper error handling, loading states, and ensure the feature integrates seamlessly with existing functionality. Create comprehensive tests including E2E validation to ensure the feature works as expected.

## Step by Step Tasks
IMPORTANT: Execute every step in order, top to bottom.

### Add Data Models
- Add `GenerateQueryRequest` model to `app/server/core/data_models.py` with optional fields for customization (e.g., complexity level, specific tables)
- Add `GenerateQueryResponse` model with fields: `query` (str), `context` (str explaining what the query does), `error` (Optional[str])
- Add TypeScript interfaces in `app/client/src/types.d.ts` matching the Pydantic models

### Implement Query Generation Function
- Add `generate_natural_language_query()` function to `app/server/core/llm_processor.py`
- Function should accept schema_info dict and return a natural language query string
- Create a prompt that instructs the LLM to:
  - Analyze available tables, columns, and their data types
  - Generate an interesting, actionable query (max 2 sentences)
  - Create diverse query types (filtering, aggregation, joins, date ranges, etc.)
  - Ensure queries are meaningful given the actual data structure
- Support both OpenAI and Anthropic providers using existing routing logic
- Add proper error handling with fallback generic queries if LLM fails
- Include temperature setting (0.7-0.9) to ensure variety in generated queries

### Add API Endpoint
- Create `POST /api/generate-query` endpoint in `app/server/server.py`
- Endpoint should call `get_database_schema()` to get current schema
- Call `generate_natural_language_query()` with schema info
- Return `GenerateQueryResponse` with the generated query
- Add proper error handling and logging
- Validate that tables exist before generating queries (return helpful error if no tables)

### Add API Client Method
- Add `generateQuery()` method to `app/client/src/api/client.ts`
- Method should call the `/api/generate-query` endpoint
- Return properly typed `GenerateQueryResponse`
- Handle errors gracefully with user-friendly messages

### Add Generate Query Button to UI
- Add a new button in `app/client/index.html` in the `.query-controls` div
- Button ID: `generate-query-button`
- Button text: "Generate Query" (or "✨ Generate Query" with emoji)
- Button class: `secondary-button` (matching Upload Data button style)
- Position button using CSS flexbox with `justify-content: space-between` so primary button (Query) is on left, secondary buttons (Generate Query, Upload Data) are on right

### Style the Generate Query Button
- Update `app/client/src/style.css` to ensure the new button matches the Upload Data button style
- Add hover effects and loading states
- Ensure button is disabled when no tables are loaded
- Update `.query-controls` layout to use `justify-content: space-between`
- Group secondary buttons together with appropriate spacing

### Implement Button Click Handler
- Add event listener in `app/client/src/main.ts` for the Generate Query button
- On click, show loading state (spinner/disabled button)
- Call `api.generateQuery()`
- On success: overwrite the query input field value with the generated query (using `queryInput.value = response.query`)
- On error: display user-friendly error message
- Re-enable button after completion
- Add visual feedback when query is populated (e.g., brief highlight animation)

### Add Loading and Error States
- Implement loading spinner for the Generate Query button (matching Query button pattern)
- Show disabled state when no tables are loaded in the database
- Display helpful tooltip when hovering over disabled button: "Upload data first to generate queries"
- Add error toast/notification for generation failures
- Ensure button is keyboard accessible (Tab navigation, Enter to activate)

### Write Unit Tests
- Add tests to `app/server/tests/core/test_llm_processor.py` for the query generation function
- Test cases:
  - Single table with various column types
  - Multiple tables (should generate join queries sometimes)
  - Empty database (should return appropriate error)
  - LLM API failure scenarios (should use fallback)
  - Query length validation (max 2 sentences)
- Mock LLM API calls for consistent testing

### Create E2E Test
- Create `.claude/commands/e2e/test_generate_query.md` based on the format in `test_basic_query.md`
- Test steps should include:
  - Navigate to application
  - Upload sample data (users table)
  - Click "Generate Query" button
  - Verify query input field is populated
  - Verify query text is not empty and under 2 sentences
  - Take screenshot of generated query
  - Click "Query" button to execute the generated query
  - Verify results are displayed
  - Take screenshot of results
  - Click "Generate Query" again to verify different query is generated
- Success criteria: Button works, queries are generated, queries are different each time, generated queries execute successfully

### Integration Testing
- Manually test the full flow:
  - Start with empty database, verify button is disabled
  - Upload sample data (users.json)
  - Click Generate Query multiple times, verify different queries are generated
  - Execute generated queries and verify they return valid results
  - Test with multiple tables loaded
  - Test with both OpenAI and Anthropic API keys
  - Test error scenarios (network failures, API key issues)

### Run Validation Commands
- Execute all validation commands to ensure zero regressions
- Run E2E test to validate the feature works end-to-end
- Verify existing features still work (file upload, query execution, table management)

## Testing Strategy
### Unit Tests
- Test query generation function with various schema configurations
- Test API endpoint with valid and invalid requests
- Test LLM fallback logic when API fails
- Test query length validation and truncation
- Mock LLM responses for deterministic testing

### Integration Tests
- Test full flow from button click to query population
- Test with empty database (button disabled)
- Test with single table vs multiple tables
- Test query variety (ensure different queries on repeated clicks)
- Test that generated queries actually execute successfully

### Edge Cases
- No tables in database (button disabled state)
- Single table with one column
- Tables with special characters in names
- Very large schemas (many tables/columns)
- LLM API rate limiting or failures
- Network timeouts during generation
- Query generation taking longer than expected (loading states)
- Concurrent query generation requests
- Generated queries with ambiguous natural language

## Acceptance Criteria
- "Generate Query" button is visible and styled consistently with "Upload Data" button
- Button is positioned separately from primary "Query" button using space-between layout
- Button is disabled when no tables are loaded in the database
- Clicking button generates a unique natural language query based on current schema
- Generated query is limited to two sentences maximum
- Generated query completely overwrites existing content in input field
- Button shows loading state while query is being generated
- Generated queries are contextually relevant to the available tables and columns
- Queries vary on repeated clicks (not always the same query)
- Generated queries successfully execute when user clicks "Query" button
- Proper error messages displayed if query generation fails
- All existing functionality continues to work without regression
- E2E test validates the feature works as expected with screenshots

## Validation Commands
Execute every command to validate the feature works correctly with zero regressions.

Read `.claude/commands/test_e2e.md`, then read and execute the new E2E test file `.claude/commands/e2e/test_generate_query.md` to validate this functionality works.

- `cd app/server && uv run pytest` - Run server tests to validate the feature works with zero regressions
- `cd app/server && uv run pytest tests/core/test_llm_processor.py -v` - Run specific LLM processor tests including new query generation tests
- `cd app/client && bun tsc --noEmit` - Run frontend type checking to validate the feature works with zero regressions
- `cd app/client && bun run build` - Run frontend build to validate the feature works with zero regressions
- Manual validation:
  - Start the application with `./scripts/start.sh`
  - Upload sample data (users.json, products.csv)
  - Click "Generate Query" button 5 times and verify unique queries
  - Execute each generated query and verify results are correct
  - Test with empty database (verify button is disabled)
  - Test with single vs multiple tables
  - Take screenshots to document the feature

## Notes
- The query generation uses the existing LLM routing logic (OpenAI priority, then Anthropic fallback)
- Temperature should be set higher (0.7-0.9) than SQL generation (0.1) to ensure query variety
- Consider adding a "complexity" parameter in future iterations (simple vs complex queries)
- Future enhancement: Allow users to specify which tables to focus on for query generation
- Future enhancement: Add a "favorites" feature to save interesting generated queries
- The two-sentence limit is enforced in the LLM prompt; add validation in the backend to truncate if needed
- Generated queries should avoid dangerous operations (DELETE, DROP, etc.) - same validation as user queries
- Consider adding query templates/categories (aggregation, filtering, joins, time-based) for more diverse generation
- The button could be enhanced with a dropdown for different query styles (simple, complex, analytical)
- Accessibility: Ensure button has proper ARIA labels and keyboard navigation
