# General Test Examples

This file shows standard formats for various general test cases, including functional testing, linkage testing, routing testing, UI visual testing, API testing, and security testing.

> **File Path**: `references/examples/common.md`

## Table of Contents

| Line | Chapter |
|------|------|
| 20 | Part 1: Functional Testing |
| 295 | Part 3: Linkage Testing |
| 354 | Part 4: Routing Testing |
| 418 | Part 5: UI Visual Testing |
| 472 | Part 6: API Testing |
| 543 | Part 7: Security Testing |

---

## Part 1: Functional Testing

### TC_FUNC_CRUD_001 Verify Create Data Function

**Test Type**: Functional Testing - CRUD  
**Function Module**: Data Management  
**Test Case Level**: P0

**Preconditions**: 
1. User logged in
2. Has create data permission

**Test Steps**:
1. Click "Create" button
2. Fill form required fields
3. Fill form optional fields
4. Click "Save" button
5. Check create success prompt
6. Find newly created record in list

**Expected Results**:
1. Create page opens normally
2. Required fields have indicators
3. Data saved successfully
4. Display create success prompt
5. List displays new record
6. Data consistent with input

---

### TC_FUNC_CRUD_002 Verify Edit Data Function

**Test Type**: Functional Testing - CRUD  
**Function Module**: Data Management  
**Test Case Level**: P0

**Preconditions**: 
1. System has editable data records

**Test Steps**:
1. Find target record in list
2. Click "Edit" button
3. Modify some fields
4. Click "Save" button
5. Check update success prompt
6. Check list data updated

**Expected Results**:
1. Edit page opens normally
2. Original data correctly backfilled
3. Data update successful
4. Display update success prompt
5. List displays latest data
6. Data persists on re-edit

---

### TC_FUNC_CRUD_003 Verify Delete Data Function

**Test Type**: Functional Testing - CRUD  
**Function Module**: Data Management  
**Test Case Level**: P1

**Preconditions**: 
1. System has deletable data records

**Test Steps**:
1. Find target record in list
2. Click "Delete" button
3. Check confirmation dialog
4. Click "Confirm" delete
5. Check delete success prompt
6. Confirm record deleted in list

**Expected Results**:
1. Delete button available
2. Popup confirmation prompt
3. Secondary confirmation before delete
4. Display delete success prompt
5. Record removed from list
6. Data deleted in database

---

### TC_FUNC_CRUD_004 Verify Data Query Function

**Test Type**: Functional Testing - CRUD  
**Function Module**: Data Query  
**Test Case Level**: P1

**Preconditions**: 
1. System has multiple data records
2. Query function normally configured

**Test Steps**:
1. Enter keyword in search box
2. Click search button
3. Check search results
4. Enter exact condition query
5. Use filter condition query
6. Clear search conditions

**Expected Results**:
1. Support fuzzy search
2. Return matching search results
3. Display empty state when no match
4. Exact query results accurate
5. Filter condition combination effective
6. Restore default list after clear

---

### TC_FUNC_LIST_001 Verify List Pagination Function

**Test Type**: Functional Testing - List Functions  
**Function Module**: List Display  
**Test Case Level**: P1

**Preconditions**: 
1. List data exceeds one page

**Test Steps**:
1. View first page data
2. Click "Next Page"
3. Check second page data
4. Enter page number to jump
5. Modify items per page
6. Check data update

**Expected Results**:
1. Default display first page
2. Pagination info correct
3. Second page data not duplicate
4. Jump page number correct
5. Items per page switch effective
6. Total count statistics correct

---

### TC_FUNC_LIST_002 Verify List Sorting Function

**Test Type**: Functional Testing - List Functions  
**Function Module**: List Display  
**Test Case Level**: P1

**Preconditions**: 
1. List has sortable columns

**Test Steps**:
1. Click ascending sort
2. Check data order
3. Click descending sort again
4. Check data order
5. Switch sort column
6. Check new column sort

**Expected Results**:
1. Ascending icon displays
2. Data arranged small to large
3. Descending icon displays
4. Data arranged large to small
5. Different column sorts don't affect each other
6. Sort state can be saved

---

### TC_FUNC_FORM_001 Verify Form Required Validation

**Test Type**: Functional Testing - Form Validation  
**Function Module**: Form Validation  
**Test Case Level**: P0

**Preconditions**: 
1. Form has required fields

**Test Steps**:
1. Directly click save (without filling any content)
2. Check required prompt
3. Fill some required fields
4. Submit check
5. Fill all required fields
6. Submit check

**Expected Results**:
1. Display required field prompt
2. Unfilled fields highlighted prompt
3. Cannot submit with only partial fill
4. Pass validation with all fields filled
5. Prompt message clear and explicit
6. Error prompt disappears after correction

---

### TC_FUNC_FORM_002 Verify Form Format Validation

**Test Type**: Functional Testing - Form Validation  
**Function Module**: Form Validation  
**Test Case Level**: P1

**Preconditions**: 
1. Form has format validation fields

**Test Steps**:
1. Enter phone format error (e.g., 123)
2. Check format error prompt
3. Enter email format error (e.g., abc)
4. Check format error prompt
5. Enter correct format data
6. Check validation pass

**Expected Results**:
1. Phone format validation effective
2. Display correct format prompt (e.g., 11 digits)
3. Email format validation effective
4. Display correct format prompt
5. Correct format passes validation
6. Real-time validation or validation on submit

---

### TC_FUNC_STATUS_001 Verify State Switch Function

**Test Type**: Functional Testing - State Management  
**Function Module**: State Control  
**Test Case Level**: P1

**Preconditions**: 
1. Data has state field
2. Support state switching

**Test Steps**:
1. View data current state
2. Execute enable operation
3. Check state change
4. Execute disable operation
5. Check state change
6. Refresh page check state persistence

**Expected Results**:
1. Initial state displays correctly
2. Enable operation successful
3. State updates immediately
4. Disable operation successful
5. State updates immediately
6. State persists after refresh

---

### TC_FUNC_STATUS_002 Verify Data Persistence

**Test Type**: Functional Testing - State Management  
**Function Module**: Data Storage  
**Test Case Level**: P0

**Preconditions**: 
1. Exists savable data

**Test Steps**:
1. Fill form data
2. Click save
3. Close page
4. Reopen
5. Check if data retained

**Expected Results**:
1. Save operation successful
2. Page closes normally
3. Re-enter page
4. Data complete retention
5. No data loss

---

---

## Part 3: Linkage Testing

### TC_LINKAGE_001 Verify Province-City-District Three-Level Linkage

**Test Type**: Linkage Testing - Functional Testing  
**Function Module**: Address Selection  
**Test Case Level**: P1

**Preconditions**: 
1. Address selection form normally loaded

**Test Steps**:
1. Select province (e.g., "Guangdong Province")
2. Check city dropdown options
3. Select city (e.g., "Shenzhen City")
4. Check district dropdown options
5. Select district (e.g., "Nanshan District")
6. Check complete address
7. Modify province to "Zhejiang Province"
8. Check if city and district reset

**Expected Results**:
1. City list changes with province (Guangdong→Guangzhou, Shenzhen, etc.)
2. District list changes with city (Shenzhen→Nanshan, Futian, etc.)
3. Data correctly corresponds
4. Modify parent option, child automatically resets
5. Address data complete on submit

---

### TC_LINKAGE_002 Verify Search Box Real-time Suggestion

**Test Type**: Linkage Testing - Interaction Testing  
**Function Module**: Search  
**Test Case Level**: P1

**Preconditions**: 
1. Search page
2. Support real-time suggestion

**Test Steps**:
1. Enter "ph" in search box
2. Check suggestion word list
3. Continue entering "phone"
4. Check suggestion word update
5. Click suggestion word "Apple Phone"
6. Check search results
7. Quickly delete input
8. Check suggestion word disappears

**Expected Results**:
1. Real-time display suggestion words during input
2. Suggestion words accurately match
3. Click suggestion word to execute search
4. Suggestion words disappear when input cleared
5. Debounce processing (avoid frequent requests)

---

## Part 4: Routing Testing

### TC_ROUTING_001 Verify Direct Access to Detail Page URL

**Test Type**: Routing Testing - Functional Testing  
**Function Module**: Page Navigation  
**Test Case Level**: P1

**Preconditions**: 
1. User logged in
2. Product detail page URL known

**Test Steps**:
1. Enter product detail page URL in browser address bar
2. Press Enter to access
3. Check page load

**Expected Results**:
1. Page loads normally
2. Display correct product information
3. URL matches page content
4. Page title correct

---

### TC_ROUTING_002 Verify Access to Non-existent Route

**Test Type**: Routing Testing - Error Handling  
**Function Module**: Error Page  
**Test Case Level**: P2

**Test Steps**:
1. Access non-existent route `/product/999999`
2. Press Enter

**Expected Results**:
1. Display 404 page
2. Provide link to return to homepage
3. Provide search function
4. Page status code is 404

---

### TC_ROUTING_003 Verify Access to Route Requiring Authentication Without Login

**Test Type**: Routing Testing - Security Testing  
**Function Module**: Route Guard  
**Test Case Level**: P0

**Preconditions**: 
1. User not logged in
2. Order detail page requires authentication

**Test Steps**:
1. Access order detail page `/order/123`
2. Check jump behavior

**Expected Results**:
1. Redirect to login page
2. Return to original page after login
3. Or display friendly not logged in prompt

---

## Part 5: UI Visual Testing

### TC_UI_LAYOUT_001 Verify Page Element Alignment

**Test Type**: UI Testing - Layout Testing  
**Function Module**: Page Layout  
**Test Case Level**: P2
**Test Dimension**: UI Visual

**Preconditions**: 
1. Page normally loaded

**Test Steps**:
1. Check page margin consistency
2. Check element alignment (left/center alignment)
3. Check element spacing uniform
4. Check grid system
5. Check responsive breakpoints

**Expected Results**:
1. Margins conform to design (e.g., 16px/24px)
2. Same level elements align consistently
3. Spacing uniform (e.g., 8px multiples)
4. Grid system correct
5. Layout correct at each breakpoint

---

### TC_UI_DARK_001 Verify Dark Mode Adaptation

**Test Type**: UI Testing - Theme Testing  
**Function Module**: Dark Mode  
**Test Case Level**: P2
**Test Dimension**: UI Visual

**Preconditions**: 
1. Application supports dark mode switching

**Test Steps**:
1. System switch to dark mode
2. Check application background color
3. Check text color
4. Check icon color
5. Check image adaptation

**Expected Results**:
1. Background color adapts to dark theme
2. Text contrast sufficient
3. Icon color coordinated
4. Images display normally
5. No white flash screen

---

## Part 6: API Testing

### TC_API_GET_001 Verify Get User Info API

**Test Type**: API Testing - Functional Testing  
**Function Module**: User API  
**Test Case Level**: P1

**API Info**:
- Method: GET
- URL: `/api/v1/users/{userId}`
- Authentication: Bearer Token

**Request Parameters**:
- userId: 12345 (path parameter)

**Test Steps**:
1. Set request header Authorization: Bearer {token}
2. Send GET request
3. Check response status code
4. Check response data structure
5. Check field values

**Expected Results**:
1. Status code 200
2. Return user object
3. Fields complete (id, name, email, etc.)
4. Data consistent with database
5. Sensitive information masked

---

### TC_API_POST_001 Verify Create Order API

**Test Type**: API Testing - Functional Testing  
**Function Module**: Order API  
**Test Case Level**: P0

**API Info**:
- Method: POST
- URL: `/api/v1/orders`
- Authentication: Bearer Token
- Content-Type: application/json

**Request Body**:
```json
{
  "userId": 12345,
  "items": [
    {"productId": 1001, "quantity": 2}
  ],
  "address": "Beijing Chaoyang District"
}
```

**Test Steps**:
1. Set request header and authentication
2. Construct request body
3. Send POST request
4. Check response
5. Verify database record

**Expected Results**:
1. Status code 201
2. Return order object (with order number)
3. Database creates corresponding record
4. Inventory deduction
5. Trigger order creation event

---

## Part 7: Security Testing

### TC_SEC_SQL_001 Verify SQL Injection Protection

**Test Type**: Security Testing - Injection Attack  
**Function Module**: Input Validation  
**Test Case Level**: P0

**Test Steps**:
1. Enter `' OR '1'='1` in search box
2. Enter `admin' --` in login box
3. Enter `1; DROP TABLE users--` in URL parameter
4. Check response
5. Check database log

**Expected Results**:
1. Query returns empty or normal result
2. Cannot bypass authentication
3. Database table not deleted
4. Log records attack attempt
5. Use parameterized queries

---

### TC_SEC_XSS_001 Verify Cross-Site Script Attack Protection

**Test Type**: Security Testing - XSS Attack  
**Function Module**: Input Output  
**Test Case Level**: P0

**Test Steps**:
1. Enter `<script>alert('xss')</script>` in comment box
2. Enter `<img src=x onerror=alert(1)>` in username
3. Submit and view page
4. Check if script executes
5. Check output encoding

**Expected Results**:
1. Script does not execute
2. Special characters escaped
3. Display as plain text
4. Content-Type correct
5. Set HttpOnly flag

---

### TC_SEC_AUTH_001 Verify Unauthorized Access Protection

**Test Type**: Security Testing - Authentication Authorization  
**Function Module**: Permission Control  
**Test Case Level**: P0

**Test Steps**:
1. Access interface requiring authentication without login
2. Normal user access administrator interface
3. User A access user B data
4. Access with expired Token
5. Check response

**Expected Results**:
1. Return 401 not authenticated
2. Return 403 no permission
3. Data isolation correct
4. Token invalid reject access
5. Error information not sensitive
