# Mobile Web Test Examples

This file provides test case examples for mobile Web specific scenarios.

## Example 1: Responsive Layout Test

**Test Case ID**: TC_H5_LAYOUT_001  
**Test Title**: Verify page layout at different screen widths  
**Test Type**: UI Testing  
**Function Module**: Page Layout  
**Test Case Level**: P1

**Preconditions**: 
1. Page normally loaded

**Test Steps**:
1. View page at 320px width
2. View page at 375px width
3. View page at 414px width
4. View page at 768px width
5. Check element arrangement

**Expected Results**:
1. 320px: Content normally displays, no horizontal scroll
2. 375px: Layout reasonable, elements not crowded
3. 414px: Layout comfortable, spacing appropriate
4. 768px: May switch to tablet layout
5. Element arrangement conforms to responsive design

---

## Example 2: Touch Interaction Test

**Test Case ID**: TC_H5_TOUCH_001  
**Test Title**: Verify pull-down refresh trigger  
**Test Type**: Functional Testing  
**Function Module**: List Page  
**Test Case Level**: P1

**Preconditions**: 
1. Page normally loaded
2. At top of list

**Test Steps**:
1. Pull down at top of page
2. Check refresh indicator
3. Release finger
4. Check list refresh

**Expected Results**:
1. Pull-down distance reaches threshold, indicator displays
2. Indicator animation smooth
3. Release triggers refresh
4. List data updates

---

## Example 3: Browser Compatibility Test

**Test Case ID**: TC_H5_BROWSER_001  
**Test Title**: Verify function normal in WeChat built-in browser  
**Test Type**: Compatibility Testing  
**Function Module**: Browser Compatibility  
**Test Case Level**: P1

**Preconditions**: 
1. Open page in WeChat

**Test Steps**:
1. Browse page content
2. Click button
3. Submit form
4. Play video
5. Use share function

**Expected Results**:
1. Page content displays normally
2. Button click effective
3. Form submits normally
4. Video plays normally (note: autoplay may be restricted)
5. Share function normally calls WeChat share

---

## Example 4: Viewport Configuration Test

**Test Case ID**: TC_H5_VIEWPORT_001  
**Test Title**: Verify notch screen safe area adaptation  
**Test Type**: UI Testing  
**Function Module**: Viewport  
**Test Case Level**: P2

**Preconditions**: 
1. Use notch screen device
2. Page normally loaded

**Test Steps**:
1. View page in portrait
2. Check top navigation bar position
3. Check bottom button position
4. Switch to landscape
5. Check content display

**Expected Results**:
1. Page normally displays
2. Navigation bar not blocked by notch
3. Bottom button not blocked by home indicator
4. Landscape layout normal
5. Content not blocked by notch

---

## Example 5: H5 Specific Features Test

**Test Case ID**: TC_H5_FEATURE_001  
**Test Title**: Verify tel: link jump to dial  
**Test Type**: Functional Testing  
**Function Module**: H5 Features  
**Test Case Level**: P1

**Preconditions**: 
1. Page has tel: link

**Test Steps**:
1. Click phone number link
2. Check system response
3. Confirm dial

**Expected Results**:
1. Click link
2. System dial interface pops up, number filled
3. User can confirm dial

---

## Example 6: Third-party Login Test

**Test Case ID**: TC_H5_LOGIN_001  
**Test Title**: Verify WeChat H5 login process  
**Test Type**: Functional Testing  
**Function Module**: Third-party Login  
**Test Case Level**: P0

**Preconditions**: 
1. User not logged in
2. In WeChat environment

**Test Steps**:
1. Click login button
2. Authorize WeChat login
3. Check callback
4. Check login state

**Expected Results**:
1. Jump to WeChat authorization page
2. User clicks agree
3. Callback returns to page, carries code
4. Login successful, user info displays

---

## Example 7: WebView Specific Test

**Test Case ID**: TC_H5_WEBVIEW_001  
**Test Title**: Verify JSBridge call native camera  
**Test Type**: Functional Testing  
**Function Module**: WebView  
**Test Case Level**: P1

**Preconditions**: 
1. Page in App WebView
2. JSBridge normally configured

**Test Steps**:
1. Click camera button
2. Check JSBridge call
3. Native camera opens
4. Take photo
5. Check callback

**Expected Results**:
1. Trigger JSBridge call
2. Native camera interface opens
3. User takes photo
4. Photo returns to H5
5. H5 displays photo
