# Next Steps - Streaming Workflow Testbed

## Recent Developments

**Live Workflow Monitoring Operational**: Monitor now records and displays real testbed activity - STF files, runs, and agent activity are being tracked end-to-end from DAQ simulator through agents to web interface.

## IMMEDIATE PRIORITY: DataTables Server-Side Pattern

### Goal
Create consistent, performant list views across all monitor pages using DataTables server-side processing with AJAX.

### Phase 1: Establish Pattern (Logs as Exemplar)

1. **Base Template Creation**
   - Create `_datatable_base.html` template with standard DataTables server-side setup
   - Include standard AJAX configuration, pagination, search, sorting
   - URL parameter handling for bookmarkable states

2. **AJAX Endpoint Pattern**
   - Create `logs_datatable_ajax()` view as reference implementation
   - Standard parameter handling: draw, start, length, search, ordering
   - Consistent response format for all DataTables endpoints

3. **JavaScript Reusables**
   - Common DataTables configuration object
   - Standard column formatters (timestamps, status badges, actions)
   - URL state management utilities

4. **Logs Implementation**
   - Convert existing logs page to use new pattern
   - Maintain all current filtering (app_name, instance_name, time range)
   - Ensure proper URL parameter integration

### Phase 2: Pattern Documentation
- Document the server-side DataTables pattern
- Create implementation guide for other list views
- Code examples and best practices

### Phase 3: Gradual Migration
- Apply pattern to STF Files list
- Apply pattern to Runs list
- Apply pattern to Subscribers list
- Apply pattern to other list views

### Benefits
- **Consistent UX** across all monitor pages
- **Performance**: Only load data actually being viewed
- **URL Addressability**: All table states in URL for bookmarking/sharing
- **Maintainability**: Shared templates and JavaScript
- **Scalability**: Handles large datasets efficiently

## Success Metrics
- All list views use same DataTables pattern
- Sub-second response times for paginated data
- Bookmarkable URLs, fast navigation
- Shared code reduces duplication by 80%