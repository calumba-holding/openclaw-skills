# Test Case General Rules

This document integrates core specifications for test case design, including test case templates, test type classifications, priority rules, and numbering rules.

## Table of Contents

| Line | Chapter |
|------|------|
| 16 | Part 1: Test Case Template |
| 59 | Part 2: Test Type Classification |
| 133 | Part 3: Priority Determination Rules |
| 175 | Part 4: Test Case Numbering Rules |

---

## Part 1: Test Case Template

### Standard Fields

| Field | Description | Required |
|-----|------|------|
| Test Case ID | Unique identifier | Yes |
| Test Title | Concise description of test purpose | Yes |
| Test Type | Functional/Security/Compatibility/UI etc. | Yes |
| Function Module | Belonging function module | Yes |
| Sub-function | Specific sub-function point | No |
| Test Case Level | P0/P1/P2/P3 | Yes |
| Test Dimension | Gesture/Screen/Network etc. | No |
| Preconditions | Environment and state before execution | Yes |
| Test Steps | Detailed operation steps | Yes |
| Expected Results | Expected system response | Yes |
| Actual Results | Actual test results | Fill during execution |
| Test Status | Pass/Fail/Block | Fill during execution |

### Example

**Test Case ID**: TC_LOGIN_001

**Test Title**: Verify correct username and password can login

**Test Type**: Functional Testing

**Function Module**: User Login

**Test Case Level**: P0

**Preconditions**: User registered, account password correct

**Test Steps**:
1. Open login page
2. Enter correct username
3. Enter correct password
4. Click login button

**Expected Results**: Login successful, redirect to homepage

---

## Part 2: Test Type Classification

### 1. Functional Testing
Verify functions work according to requirements specifications, ensuring all function points are correctly implemented.

**Sub-types**: Unit testing, integration testing, system testing, end-to-end testing

**Examples**: Login function, form submission, data query

---

### 2. Security Testing
Verify system security mechanisms are effective, preventing unauthorized access and data leakage.

**Sub-types**: Identity authentication, authorization control, data security, vulnerability scanning

**Examples**: Unauthorized access, sensitive data exposure, API misuse

---

### 3. Compatibility Testing
Verify system compatibility in different environments, ensuring consistent experience.

**Sub-types**: Platform compatibility, browser compatibility, device compatibility, version compatibility

**Examples**: Different device adaptations, different browser layouts, version upgrade compatibility

---

### 4. UI Testing
Verify interface display and interactions are correct, ensuring user experience.

**Sub-types**: Layout testing, style testing, interaction testing, theme testing

**Examples**: Page misalignment, style inconsistency, animation lag

---

### 5. Performance Testing
Verify system performance indicators meet standards, ensuring smooth experience.

**Sub-types**: Response time, concurrency capability, resource usage, stability

**Examples**: Slow first screen load, lag/crash, high concurrency crash

---

### 6. Usability Testing
Verify system usability and user experience, ensuring easy to learn and use.

**Sub-types**: Navigation testing, form testing, help testing, accessibility

**Examples**: Tedious operations, unclear prompts, unable to keyboard operate

---

### 7. Linkage Testing
Verify data synchronization and state linkage between different modules/components.

**Sub-types**: Form linkage, list linkage, search linkage, state linkage, data linkage

**Examples**: Province-city linkage, filter condition linkage, cross-page state synchronization

---

### 8. Routing Testing
Verify page routing jumps, parameter passing, and permission control.

**Sub-types**: Navigation jump, browser navigation, routing parameters, deep links

**Examples**: Direct URL access, 404 handling, login interception

---

## Part 3: Priority Determination Rules

### P0 - Critical
- Core functions
- Affect main process
- Cause system crash
- Data loss
- Security vulnerabilities

**Handling**: Fix immediately, block release

---

### P1 - Major
- Important functions
- Affect user experience
- Function errors
- Serious interface issues

**Handling**: Fix as soon as possible, affect release

---

### P2 - Minor
- Secondary functions
- Minor experience issues
- Minor interface issues
- Inaccurate prompt information

**Handling**: Schedule fix, can release with issues

---

### P3 - Trivial
- Optimization suggestions
- Interface beautification
- Does not affect function

**Handling**: Fix when available

---

## Part 4: Test Case Numbering Rules

### Numbering Format

```
[Platform]_[Module]_[Dimension]_[Sequence]
```

### Platform Prefix

| Platform | Prefix |
|-----|------|
| Mobile App | APP |
| Desktop | DESKTOP |
| Mini Program | MP |
| Mobile Web | H5 |
| PC Web | WEB |
| General Functional Testing | FUNC |
| General Linkage Testing | LINKAGE |
| General Routing Testing | ROUTING |

### Dimension Abbreviation

| Dimension | Abbreviation |
|-----|------|
| Gesture Operation | GESTURE |
| Screen Adaptation | SCREEN |
| Interruption Recovery | INTERRUPT |
| Network Switching | NETWORK |
| Device Compatibility | COMPAT |
| Permission Management | PERMISSION |
| System Interaction | SYSTEM |
| Performance Experience | PERFORMANCE |
| Lifecycle | LIFECYCLE |
| API Testing | API |
| Security Testing | SEC |
| UI Visual | UI |
| Linkage Testing | LINKAGE |
| Routing Testing | ROUTING |
| Payment Testing | PAYMENT |
| Data Sync | SYNC |
| Authorization Management | AUTH |
| Browser Compatibility | BROWSER |

### Examples (Full Format)

```
APP_LOGIN_GESTURE_001   - Mobile login function gesture operation test case 1
APP_ORDER_NETWORK_005   - Mobile order function network switching test case 5
MP_SHARE_LIFECYCLE_003  - Mini program sharing function lifecycle test case 3
WEB_LOGIN_BROWSER_001   - PC Web login function browser compatibility test case 1
LINKAGE_FORM_001        - Linkage testing form linkage test case 1
ROUTING_NAV_001         - Routing testing navigation jump test case 1
```

### Simplified Format (General Test Cases)

For general test cases, simplified format can be used:

```
TC_[Test Type Prefix]_[Scenario Keyword]_[Sequence]
```

Simplified prefix comparison:

| Full Prefix | Simplified Prefix | Applicable Scenario |
|---------|---------|---------|
| FUNC_CRUD | FUNC | Functional Testing - CRUD |
| FUNC_LIST | FUNC | Functional Testing - List Functions |
| FUNC_FORM | FUNC | Functional Testing - Form Validation |
| FUNC_STATUS | FUNC | Functional Testing - State Management |
| LINKAGE | LINKAGE | Linkage Testing |
| ROUTING | ROUTING | Routing Testing |
| API | API | API Testing |
| SEC | SEC | Security Testing |
| UI | UI | UI Testing |

Simplified format examples:

```
TC_FUNC_CRUD_001     - Functional Testing - Create data test case 1
TC_FUNC_FORM_001     - Functional Testing - Form validation test case 1
TC_LINKAGE_CITY_001  - Linkage Testing - City selection test case 1
TC_ROUTING_URL_001   - Routing Testing - URL access test case 1
TC_API_GET_001       - API Testing - GET request test case 1
TC_SEC_SQL_001       - Security Testing - SQL injection test case 1
TC_UI_LAYOUT_001     - UI Testing - Layout alignment test case 1
```
