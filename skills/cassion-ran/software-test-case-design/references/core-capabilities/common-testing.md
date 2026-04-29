# General Testing Capabilities

This document integrates core methods for test case design, test type frameworks, linkage testing, routing testing, UI visual testing, API testing, and security testing, applicable to test case design across all platforms.

## Table of Contents

| Line | Chapter |
|------|------|
| 22 | Part 1: Test Case Design Methods |
| 87 | Part 2: Test Case Quality Standards |
| 116 | Part 3: Linkage Testing |
| 160 | Part 4: Routing Testing |
| 215 | Part 5: UI Visual Testing |
| 301 | Part 6: API Testing |
| 376 | Part 7: Security Testing |
| 444 | Part 8: Page Interaction Testing |
| 479 | Part 9: Component Interaction Testing |
| 512 | Part 10: Interaction Animation Testing |

---

## Part 1: Test Case Design Methods

### 1.1 Equivalence Partitioning

**Definition**: Divide all possible input data into several equivalence classes, selecting a few representative data points from each class as test cases.

**Steps**:
1. Analyze requirements specifications to determine the set of input conditions
2. Partition valid equivalence classes (reasonable, meaningful inputs)
3. Partition invalid equivalence classes (unreasonable, meaningless inputs)
4. Number each equivalence class
5. Design test cases covering valid equivalence classes
6. Design test cases covering invalid equivalence classes

**Example**: Username input field (6-18 alphanumeric characters)
- Valid equivalence class: 6-18 alphanumeric combinations
- Invalid equivalence class: Less than 6 characters, more than 18 characters, contains special characters, empty value

---

### 1.2 Boundary Value Analysis

**Definition**: Test boundary values of inputs and outputs, as errors often occur near boundaries.

**Boundary Types**: Upper bound, lower bound, minimum value, maximum value, empty value, first value, last value

**Example**: Password length 6-18 characters
- Boundary tests: 5 characters, 6 characters, 18 characters, 19 characters

---

### 1.3 Scenario-Based Method

**Definition**: Based on business process diagrams, design test cases by simulating user operation scenarios.

**Scenario Types**:
- Basic flow (normal process)
- Alternative flows (exception processes, branch processes)

---

### 1.4 Error Guessing Method

**Definition**: Based on tester's experience and intuition, guess potential errors in the system and design targeted test cases.

**Common Error Points**: Empty input, special character input, network exceptions, repeated operations, timeout handling

---

### 1.5 Cause-Effect Graphing

**Definition**: Analyze relationships between input conditions (causes) and output results (effects), represent with cause-effect graphs, then convert to decision tables.

**Applicable Scenarios**: Multiple input condition combinations with complex logical relationships

---

### 1.6 Orthogonal Experimental Method

**Definition**: Use orthogonal tables to select appropriate, representative test cases from comprehensive testing.

**Applicable Scenarios**: Multi-factor multi-level combination testing

---

## Part 2: Test Case Quality Standards

### 2.1 Completeness
- Cover all functional points
- Cover normal and exception scenarios
- Cover boundary conditions

### 2.2 Accuracy
- Step descriptions are clear and unambiguous
- Expected results are explicit and verifiable
- No redundant steps

### 2.3 Executability
- Preconditions are achievable
- Steps are operable
- Results are verifiable

### 2.4 Maintainability
- Clear structure
- Easy to understand and modify
- High reusability

### 2.5 Traceability
- Traceable to requirements
- Traceable to defects
- Clear version history

---

## Part 3: Linkage Testing

### 3.1 Form Linkage

| Test Scenario | Test Points |
|---------|---------|
| Province-City-District three-level linkage | Select province, city list updates; select city, district list updates; modify parent option, child automatically resets |
| Payment method linkage | Different payment methods display different form fields; switching payment methods clears entered data |
| Category selection linkage | Child category resets when parent category changes; options affect each other |

### 3.2 List Linkage

| Test Scenario | Test Points |
|---------|---------|
| Master-detail list linkage | Select master item, detail list filters display |
| Filter condition linkage | Multi-condition filters apply in real-time; clearing single condition doesn't affect others |
| Sort linkage | List reorders when sorting changes; sort state persists |

### 3.3 Search Linkage

| Test Scenario | Test Points |
|---------|---------|
| Keyword suggestion | Real-time display of suggestions during input; suggestions accurately match |
| Search history linkage | Display recent search terms; click history term to execute search |
| Popular search linkage | Display popular search terms; click to jump to search results |

### 3.4 State Linkage

| Test Scenario | Test Points |
|---------|---------|
| Button state linkage | Submit button only enabled when form is complete; disabled button is not clickable |
| Menu state linkage | Selected menu highlighted; insufficient permission menus hidden or disabled |
| Selection state linkage | List item selection state correct; batch operations enabled based on selection state |

### 3.5 Data Linkage

| Test Scenario | Test Points |
|---------|---------|
| Real-time data synchronization | Multi-page data updates in real-time; no manual refresh needed |
| Multi-device data synchronization | Mobile and PC data consistent; data persists when switching devices |
| Cache synchronization | Cache and database data consistent; cache expiration handled correctly |

---

## Part 4: Routing Testing

### 4.1 Direct Access

| Test Scenario | Test Points |
|---------|---------|
| Direct access to homepage | URL correct, page loads normally |
| Direct access to detail page | URL contains correct parameters, page displays correct content |
| Direct access to list page | URL parameters parsed correctly, list data correct |
| Direct access to personal center | Redirect to login if not logged in; display user info if logged in |

### 4.2 Navigation Jump

| Test Scenario | Test Points |
|---------|---------|
| Navigation bar click | Click to jump to correct page; navigation highlights current item |
| Breadcrumb navigation | Click breadcrumb to return to parent; breadcrumb path correct |
| Bottom/side navigation | Switch bottom tabs; side menu expand/collapse |
| Button click jump | Click button to jump to correct page; jump parameters correct |

### 4.3 Browser Navigation

| Test Scenario | Test Points |
|---------|---------|
| Browser back | Return to previous page; page state persists |
| Browser forward | Forward to next page; state persists |
| Browser refresh | Page data refreshes; current state not lost |
| History records | URL history correctly recorded; deep links accessible |

### 4.4 Deep Links

| Test Scenario | Test Points |
|---------|---------|
| External link open | Open specified page from WeChat/SMS; parameters passed correctly |
| Push notification open | Click push notification to open app specified page |
| Share link open | Share link correctly opens app or H5 page |

### 4.5 Error Pages

| Test Scenario | Test Points |
|---------|---------|
| 404 page | Display friendly 404 page; provide link to return to homepage |
| 403 page | Prompt no permission; provide entry to request permission |
| 500 page | Prompt server error; provide retry button |

### 4.6 Route Guards

| Test Scenario | Test Points |
|---------|---------|
| Login verification | Redirect to login page when accessing authenticated pages without login |
| Permission verification | Redirect to 403 page when accessing without permission |
| Post-login jump | Return to original page or jump to homepage after successful login |

---

## Part 5: UI Visual Testing

### 5.1 Layout Testing

| Check Item | Description |
|-------|------|
| Alignment | Element left/center/right alignment correct |
| Spacing consistency | Element spacing uniform; conforms to design specifications |
| Hierarchy structure | z-index level correct; overlay layer correctly covers |
| Responsive layout | Layout normal at different screen widths; no element overflow or overlap |
| Reasonable whitespace | Page margins, element spacing appropriate |
| Visual balance | Page visual center balanced or conforms to design intent |

### 5.2 Color Testing

| Check Item | Description |
|-------|------|
| Brand color | Primary color conforms to brand specifications |
| Auxiliary color | Secondary colors used correctly |
| State color | Success/failure/warning colors conform to specifications |
| Contrast | Text to background contrast ratio ≥4.5:1 |
| Theme adaptation | Light/dark theme colors correct |
| Color blind friendly | Important information not distinguished by color alone |

### 5.3 Font Testing

| Check Item | Description |
|-------|------|
| Font family | Correct font used; fallback fonts normal |
| Font size hierarchy | Title, body, auxiliary text sizes clearly distinguished |
| Line height | Line height appropriate; text not overlapping |
| Font weight | Title/body/auxiliary font weights correct |
| Text truncation | Long text correctly truncated with ellipsis |
| Multi-language adaptation | Chinese/English font switching normal; special characters display normal |

### 5.4 Icon Testing

| Check Item | Description |
|-------|------|
| Icon style | Icon style uniform (linear/filled) |
| Icon size | Icon size conforms to design specifications |
| Icon semantics | Icon meaning clear; no ambiguity |
| Icon state | Default/hover/click/disabled states correct |
| Icon clarity | Icons clear not blurry; not distorted |

### 5.5 Image Testing

| Check Item | Description |
|-------|------|
| Image quality | Images clear not distorted; compression ratio appropriate |
| Image ratio | Different ratio images display correctly; no stretching distortion |
| Loading state | Display placeholder/skeleton screen during loading |
| Error state | Display error placeholder when image fails to load |
| Lazy loading | First screen images load first; non-first screen delayed loading |

### 5.6 Animation Testing

| Check Item | Description |
|-------|------|
| Animation curve | Animation curve natural; conforms to intuition |
| Animation duration | Animation duration appropriate; not too fast or slow |
| Animation performance | Animation smooth ≥50fps; no lag |
| Animation interruptible | Rapid continuous operations can interrupt animation |
| No flickering | Animation has no visual flickering |

### 5.7 Interaction State Testing

| Check Item | Description |
|-------|------|
| Default state | Element default style correct |
| Hover state | Mouse hover style correct |
| Click state | Click feedback correct |
| Disabled state | Disabled element style clearly distinguished |
| Focus state | Keyboard focused element has clear indicator |

### 5.8 Multi-theme Testing

| Check Item | Description |
|-------|------|
| Light theme | Light theme displays correctly |
| Dark theme | Dark theme displays correctly; color contrast sufficient |
| Theme switching | Theme switching smooth; no flickering |
| Theme memory | Theme setting persists after refresh |

---

## Part 6: API Testing

### 6.1 Functional Testing

| Test Scenario | Test Points |
|---------|---------|
| GET request | Normal query single/list data; query with parameters; empty/type error parameter handling |
| POST request | Normal resource creation; required field validation; field format validation; duplicate creation handling |
| PUT/PATCH request | Full update/partial update; update non-existent resource; concurrent update handling |
| DELETE request | Normal deletion; delete non-existent resource; cascade deletion; soft deletion |
| Batch operations | Batch create/update/delete; partial success handling; transaction rollback |

### 6.2 Status Code Validation

| Status Code | Description |
|-------|------|
| 200 OK | Normal response |
| 201 Created | Creation successful |
| 204 No Content | Deletion successful |
| 400 Bad Request | Parameter error |
| 401 Unauthorized | Not authenticated |
| 403 Forbidden | No permission |
| 404 Not Found | Resource does not exist |
| 409 Conflict | Resource conflict |
| 422 Unprocessable | Validation failed |
| 500 Internal Error | Server error |

### 6.3 Data Validation

| Test Scenario | Test Points |
|---------|---------|
| Field validation | Required fields, type, length, format, range validation |
| Business rules | Uniqueness constraints, foreign key constraints, state transition rules |
| Data consistency | Database write validation, cache synchronization validation |

### 6.4 Authentication & Authorization

| Test Scenario | Test Points |
|---------|---------|
| Token authentication | Token generation, refresh, expiration, revocation |
| Permission control | Role permissions, resource permissions, data permissions validation |

### 6.5 Performance Testing

| Test Scenario | Test Points |
|---------|---------|
| Response time | Single API response time; P95/P99 latency |
| Concurrency testing | Concurrent users; throughput (QPS/TPS) |
| Stress testing | Peak stress; sustained stress; crash point |
| Stability | Long-time running; memory leak detection |

### 6.6 Error Handling

| Test Scenario | Test Points |
|---------|---------|
| Error response | Error code specifications; error message clarity |
| Exception handling | Database exceptions, third-party service exceptions, network exceptions, timeout handling |
| Retry mechanism | Automatic retry; retry count limit; idempotency guarantee |

### 6.7 Pagination & Sorting

| Test Scenario | Test Points |
|---------|---------|
| Pagination | Page number parameter, items per page, total count, out-of-bounds handling |
| Sorting | Single/multi-field sorting; sort direction; default sorting |

### 6.8 Search & Filtering

| Test Scenario | Test Points |
|---------|---------|
| Search | Exact search, fuzzy search, full-text search, multi-condition combination |
| Filtering | Time range, status, category, custom filtering |

---

## Part 7: Security Testing

### 7.1 Injection Attack Protection

| Test Scenario | Test Points |
|---------|---------|
| SQL injection | Classic injection, blind injection, time-based blind injection, union query, stacked injection |
| NoSQL injection | MongoDB injection, Redis injection |
| Command injection | OS command injection, path traversal, file inclusion |

### 7.2 XSS Protection

| Test Scenario | Test Points |
|---------|---------|
| Reflected XSS | URL parameter injection, form input injection |
| Stored XSS | Comment storage, profile storage, message storage |
| DOM-based XSS | document.write injection, innerHTML injection, eval injection |
| Protection measures | Input filtering, output encoding, CSP policy, HttpOnly flag |

### 7.3 Authentication Security

| Test Scenario | Test Points |
|---------|---------|
| Password security | Password strength validation, encrypted storage, transmission encryption |
| Multi-factor authentication | SMS verification code, email verification code, TOTP verification |
| Brute force protection | Login failure limit, account lockout, CAPTCHA mechanism |

### 7.4 Session Management

| Test Scenario | Test Points |
|---------|---------|
| Session security | Session ID secure generation, timeout setting, fixation attack protection |
| Cookie security | Secure, HttpOnly, SameSite flags |

### 7.5 Access Control

| Test Scenario | Test Points |
|---------|---------|
| Horizontal privilege escalation | User A accesses user B data; same-level resource access |
| Vertical privilege escalation | Regular user accesses admin functions; unauthorized backend access |
| Data permissions | Department data isolation, role data isolation, sensitive data masking |

### 7.6 CSRF Protection

| Test Scenario | Test Points |
|---------|---------|
| CSRF attacks | GET request CSRF, POST request CSRF, AJAX request CSRF |
| CSRF protection | Token validation, Referer validation, SameSite Cookie, secondary confirmation |

### 7.7 File Upload Security

| Test Scenario | Test Points |
|---------|---------|
| File type | Whitelist validation, MIME type validation, bypass detection |
| File size | Oversized file limit, compression bomb protection |
| File content | Content validation, virus scanning |
| Storage security | Upload directory permissions, access control, download validation |

### 7.8 Business Logic Security

| Test Scenario | Test Points |
|---------|---------|
| Payment security | Amount tampering, duplicate payment, payment status forgery, coupon abuse |
| Race conditions | Concurrent ordering, concurrent coupon claiming, inventory overselling |
| Business process | Step skipping, duplicate submission, state rollback |

---

## Part 8: Page Interaction Testing

### 8.1 Page Loading
- First load/refresh/weak network/offline loading
- Loading timeout handling
- Loading failure retry
- Skeleton screen display

### 8.2 Page Navigation
- Navigation bar displays correctly
- Back button, history records
- Deep link open page

### 8.3 Page Switching
- Tab switching/modal window/drawer/dialog
- Switching animation smooth
- State persistence, data refresh

### 8.4 Form Interaction
- Input field focus/blur
- Input validation, error prompts
- Auto-fill, input restrictions

### 8.5 List Interaction
- Pull-down refresh, pull-up load more
- List item operations (click, swipe, long press)
- List sorting, filtering

### 8.6 Dialog Interaction
- Overlay layer, close button
- ESC key close
- Multi-layer dialogs, dialog nesting

---

## Part 9: Component Interaction Testing

### 9.1 Button Component
- Normal/hover/click/disabled states
- Rapid continuous click handling
- Loading state, permission control

### 9.2 Input Component
- Special characters,超长文本
- Copy paste, clear input
- Input hints, error prompts

### 9.3 Dropdown Component
- Expand/collapse, option search
- Multi-select, cascade selection
- Keyboard operation

### 9.4 Table Component
- Column sorting, data filtering
- Pagination switching, row operations
- Batch operations, table export

### 9.5 Carousel Component
- Auto/manual switching
- Indicators, infinite loop
- Pause carousel

### 9.6 Tabs Component
- Click/slide switching
- Close tabs, drag sorting

---

## Part 10: Interaction Animation Testing

### 10.1 Transition Animation
- Page switching animation
- Component appear/disappear
- Animation interruptible

### 10.2 Feedback Animation
- Button click ripple
- Loading spinner, success/failure feedback
- Progress bar animation

### 10.3 Gesture Animation
- List slide inertia
- Image zoom, drag sorting
- Pull-down refresh bounce, side slide menu

### 10.4 Performance Optimization
- Animation frame rate ≥50fps
- No lag, reasonable memory usage
- GPU acceleration

---
