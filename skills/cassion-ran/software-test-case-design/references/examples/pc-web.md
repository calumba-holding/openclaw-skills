# PC Web Test Examples

This file provides test case examples for PC Web specific scenarios.

## Example 1: Keyboard Navigation Test

**Test Case ID**: TC_WEB_KEYBOARD_001  
**Test Title**: Verify Tab key focus order  
**Test Type**: Accessibility Testing  
**Function Module**: Keyboard Navigation  
**Test Case Level**: P1

**Preconditions**: 
1. Page normally loaded

**Test Steps**:
1. Press Tab key
2. Check focus position
3. Continue pressing Tab
4. Check focus order
5. Press Shift+Tab

**Expected Results**:
1. First focusable element gets focus
2. Focus indicator clearly visible
3. Focus moves to next element in order
4. Focus order conforms to page structure
5. Shift+Tab moves focus to previous element

---

## Example 2: Form Interaction Test

**Test Case ID**: TC_WEB_FORM_001  
**Test Title**: Verify form auto-complete  
**Test Type**: Functional Testing  
**Function Module**: Form  
**Test Case Level**: P1

**Preconditions**: 
1. User has saved form data in browser

**Test Steps**:
1. Click input field
2. Check auto-complete suggestion
3. Select suggested value
4. Check form fill

**Expected Results**:
1. Input field gets focus
2. Browser displays auto-complete suggestion
3. User selects suggestion
4. Form automatically fills corresponding fields

---

## Example 3: Multi-window Test

**Test Case ID**: TC_WEB_WINDOW_001  
**Test Title**: Verify cross-window data synchronization  
**Test Type**: Functional Testing  
**Function Module**: Multi-window  
**Test Case Level**: P1

**Preconditions**: 
1. Page opened in two tabs

**Test Steps**:
1. Modify data in Tab A
2. Switch to Tab B
3. Check data display
4. Refresh Tab B

**Expected Results**:
1. Tab A data modification successful
2. Switch to Tab B
3. Tab B data synchronizes update (if using real-time sync)
4. After refresh, Tab B data consistent with Tab A

---

## Example 4: Routing Test

**Test Case ID**: TC_WEB_ROUTING_001  
**Test Title**: Verify route guard redirect when not logged in  
**Test Type**: Security Testing  
**Function Module**: Routing  
**Test Case Level**: P0

**Preconditions**: 
1. User not logged in

**Test Steps**:
1. Enter authenticated page URL in address bar
2. Press Enter
3. Check page jump
4. Check URL change

**Expected Results**:
1. Enter URL
2. Page loads
3. Route guard detects not logged in, redirects to login page
4. URL changes to login page address

---

## Example 5: Drag Interaction Test

**Test Case ID**: TC_WEB_DRAG_001  
**Test Title**: Verify drag sort function  
**Test Type**: Functional Testing  
**Function Module**: Drag  
**Test Case Level**: P1

**Preconditions**: 
1. Page has sortable list

**Test Steps**:
1. Mouse press list item
2. Drag to target position
3. Release mouse
4. Check list order
5. Refresh page

**Expected Results**:
1. Item follows mouse movement
2. Drag process has visual feedback
3. Release after item drops to new position
4. List order updates
5. After refresh, order persists

---

## Example 6: Rich Text Editor Test

**Test Case ID**: TC_WEB_EDITOR_001  
**Test Title**: Verify paste from Word  
**Test Type**: Functional Testing  
**Function Module**: Rich Text Editor  
**Test Case Level**: P1

**Preconditions**: 
1. Rich text editor normally loaded
2. Word document has formatted content

**Test Steps**:
1. Copy content from Word
2. Paste into editor
3. Check content format
4. Check style cleanup

**Expected Results**:
1. Content copied
2. Successfully pasted into editor
3. Text content complete
4. Redundant styles cleaned, conform to editor specifications

---

## Example 7: Print Function Test

**Test Case ID**: TC_WEB_PRINT_001  
**Test Title**: Verify print preview content  
**Test Type**: Functional Testing  
**Function Module**: Print  
**Test Case Level**: P2

**Preconditions**: 
1. Page has print button

**Test Steps**:
1. Click print button
2. Check print preview
3. Check page settings
4. Cancel print

**Expected Results**:
1. Print preview window opens
2. Preview content complete, hides unnecessary elements
3. Page settings (A4, margins) correct
4. Cancel print, return to page

---

## Example 8: Dark Mode Test

**Test Case ID**: TC_WEB_DARK_001  
**Test Title**: Verify dark mode color contrast  
**Test Type**: UI Testing  
**Function Module**: Dark Mode  
**Test Case Level**: P2

**Preconditions**: 
1. Page supports dark mode

**Test Steps**:
1. Switch system to dark mode
2. Check page background
3. Check text color
4. Check icon color
5. Use contrast detection tool

**Expected Results**:
1. Page switches to dark theme
2. Background color is dark
3. Text color is light, contrast sufficient
4. Icon color adapts to dark theme
5. Contrast ratio ≥4.5:1
