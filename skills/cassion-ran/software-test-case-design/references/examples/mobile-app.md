# Mobile App Test Examples

This file provides test case examples for mobile App specific scenarios.

## Example 1: Gesture Operation Test

**Test Case ID**: TC_APP_GESTURE_001  
**Test Title**: Verify pull-down refresh function  
**Test Type**: Functional Testing  
**Function Module**: List Page  
**Test Case Level**: P1

**Preconditions**: 
1. App normally launched
2. Enter list page

**Test Steps**:
1. Pull down at top of list
2. Check refresh indicator display
3. Release finger
4. Check list data refresh
5. Check refresh time display

**Expected Results**:
1. Pull-down distance reaches threshold, refresh indicator displays
2. Indicator animation smooth
3. Release after trigger refresh
4. List data updates, displays latest
5. Refresh time updates to current time

---

## Example 2: Interruption Recovery Test

**Test Case ID**: TC_APP_INTERRUPT_001  
**Test Title**: Verify form data retention after incoming call interruption  
**Test Type**: Functional Testing  
**Function Module**: Form Page  
**Test Case Level**: P1

**Preconditions**: 
1. App normally launched
2. Enter form filling page
3. Partially filled form

**Test Steps**:
1. Fill some form fields
2. Simulate incoming call
3. Answer call and wait 10 seconds
4. Hang up call
5. Return to App

**Expected Results**:
1. Form fields display filled content
2. Incoming call interface displays
3. Call normally answered
4. Call ended
5. Form data complete retention, no loss

---

## Example 3: Network Switching Test

**Test Case ID**: TC_APP_NETWORK_001  
**Test Title**: Verify request handling during WiFi to 4G switching  
**Test Type**: Functional Testing  
**Function Module**: Network Request  
**Test Case Level**: P1

**Preconditions**: 
1. App connected to WiFi
2. Enter page with network request

**Test Steps**:
1. Trigger network request
2. During request, switch to 4G network
3. Check request result
4. Check page display

**Expected Results**:
1. Request sent
2. Network switching successful
3. Request normally returns or auto retry
4. Page data displays normally, no error

---

## Example 4: Permission Management Test

**Test Case ID**: TC_APP_PERMISSION_001  
**Test Title**: Verify camera permission request and handling  
**Test Type**: Functional Testing  
**Function Module**: Permission Management  
**Test Case Level**: P1

**Preconditions**: 
1. App first install, no camera permission
2. Enter page requiring camera

**Test Steps**:
1. Click camera button
2. Check permission request popup
3. Click deny
4. Check function degradation
5. Click re-request
6. Click agree

**Expected Results**:
1. Permission request popup displays, explains purpose
2. User clicks deny
3. Function gracefully degrades, prompts user to enable
4. Re-request permission
5. User clicks agree
6. Camera function normally uses

---

## Example 5: Push Notification Test

**Test Case ID**: TC_APP_PUSH_001  
**Test Title**: Verify click push notification jump to specified page  
**Test Type**: Functional Testing  
**Function Module**: Push Notification  
**Test Case Level**: P1

**Preconditions**: 
1. App has push permission
2. User logged in
3. App in background

**Test Steps**:
1. Send push notification with specified page parameters
2. User clicks push notification
3. Check App launch
4. Check jump page
5. Check page data loading

**Expected Results**:
1. Push notification received
2. App launches
3. Jump to specified page
4. Page parameters correctly passed
5. Page data loads normally

---

## Example 6: Accessibility Test

**Test Case ID**: TC_APP_ACCESSIBILITY_001  
**Test Title**: Verify VoiceOver/TalkBack compatibility  
**Test Type**: Accessibility Testing  
**Function Module**: Accessibility  
**Test Case Level**: P2

**Preconditions**: 
1. App normally launched
2. System VoiceOver/TalkBack enabled

**Test Steps**:
1. Use VoiceOver/TalkBack browse page
2. Click button
3. Input text
4. Check voice feedback

**Expected Results**:
1. Voice correctly reads element labels
2. Button click has voice feedback
3. Input content has voice feedback
4. All functions can be completed through voice
