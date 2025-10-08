# E2E Test: Generate Query Button

Test the query generation functionality in the Natural Language SQL Interface application.

## User Story

As a user
I want to generate random natural language queries based on my data
So that I can discover interesting insights without having to think of queries myself

## Test Steps

1. Navigate to the `Application URL`
2. Take a screenshot of the initial state
3. **Verify** the page title is "Natural Language SQL Interface"
4. **Verify** core UI elements are present:
   - Query input textbox
   - Query button
   - Generate Query button
   - Upload Data button
   - Available Tables section

5. **Verify** the Generate Query button is disabled (no tables loaded yet)
6. Take a screenshot showing disabled state

7. Click the "Upload Data" button
8. Click on "Users Data" sample data button
9. **Verify** the users table appears in Available Tables section
10. Take a screenshot of the loaded table

11. **Verify** the Generate Query button is now enabled
12. Click the "Generate Query" button
13. **Verify** loading state appears on button
14. **Verify** a query is populated in the query input field
15. **Verify** the query is not empty
16. Take a screenshot of the generated query

17. **Verify** the query input field has the highlight animation
18. **Verify** the generated query text makes sense for the users table

19. Click the "Query" button to execute the generated query
20. **Verify** query results are displayed
21. **Verify** results contain data from the users table
22. Take a screenshot of the query results

23. Click the "Generate Query" button again
24. **Verify** a different query is generated (ensure variety)
25. Take a screenshot of the second generated query

26. Click the "Generate Query" button a third time
27. **Verify** another different query is generated
28. Take a screenshot of the third generated query

29. **Verify** all three generated queries are unique

## Success Criteria
- Generate Query button is disabled when no tables are loaded
- Generate Query button becomes enabled after uploading data
- Button shows loading state while generating
- Generated queries populate the input field
- Generated queries are contextually relevant to the available tables
- Generated queries vary on repeated clicks (not always the same)
- Generated queries successfully execute when user clicks Query button
- Visual feedback (animation) when query is populated
- At least 6 screenshots are taken documenting the feature

## Edge Cases to Verify
- Button disabled state with empty database
- Button enabled state after data upload
- Loading state during query generation
- Query variety (different queries on repeated clicks)
- Generated queries are executable and return valid results
