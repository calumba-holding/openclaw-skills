# Mini Program Test Examples

This file provides test case examples for mini program specific scenarios.

## Example 1: Lifecycle Test

**Test Case ID**: TC_MP_LIFECYCLE_001  
**Test Title**: Verify cold start and hot start  
**Test Type**: Functional Testing  
**Function Module**: Lifecycle  
**Test Case Level**: P1

**Preconditions**: 
1. Mini program not launched or in background

**Test Steps**:
1. First launch mini program (cold start)
2. Check loading performance
3. Switch to background
4. Re-enter mini program (hot start)
5. Check page state

**Expected Results**:
1. Cold start: Full initialization, loading time < 3 seconds
2. Loading indicator displays
3. Mini program switches to background
4. Hot start: Quick recovery, page state persists
5. User operation state not lost

---

## Example 2: Authorization Management Test

**Test Case ID**: TC_MP_AUTH_001  
**Test Title**: Verify location authorization process  
**Test Type**: Functional Testing  
**Function Module**: Authorization  
**Test Case Level**: P1

**Preconditions**: 
1. First use location function
2. No location authorization

**Test Steps**:
1. Click location button
2. Check authorization request
3. Click deny
4. Check function degradation
5. Click re-request
6. Click agree

**Expected Results**:
1. Trigger location authorization request
2. Authorization popup displays, explains purpose
3. User denies, function degrades, prompts to enable
4. Re-request authorization
5. User agrees
6. Location function normally uses

---

## Example 3: Share Function Test

**Test Case ID**: TC_MP_SHARE_001  
**Test Title**: Verify share to friend  
**Test Type**: Functional Testing  
**Function Module**: Share  
**Test Case Level**: P1

**Preconditions**: 
1. Enter page that can be shared

**Test Steps**:
1. Click top-right menu
2. Select "Share to Friend"
3. Select friend
4. Send share
5. Friend receives share card
6. Friend clicks share card

**Expected Results**:
1. Top-right menu opens
2. Enter share interface
3. Select target friend
4. Share sent
5. Friend receives share card, displays title, description, image
6. Jump to mini program specified page

---

## Example 4: Mini Program Code Test

**Test Case ID**: TC_MP_CODE_001  
**Test Title**: Verify scan code open mini program  
**Test Type**: Functional Testing  
**Function Module**: Mini Program Code  
**Test Case Level**: P1

**Preconditions**: 
1. Have valid mini program code

**Test Steps**:
1. Open WeChat scan
2. Scan mini program code
3. Check recognition result
4. Enter mini program
5. Check page jump

**Expected Results**:
1. Scan interface opens
2. Successfully recognizes mini program code
3. Displays mini program name and entry
4. Jump to mini program
5. Jump to specified page based on code parameters

---

## Example 5: Subscription Message Test

**Test Case ID**: TC_MP_SUBSCRIBE_001  
**Test Title**: Verify subscription message authorization and send  
**Test Type**: Functional Testing  
**Function Module**: Subscription Message  
**Test Case Level**: P1

**Preconditions**: 
1. User not authorized subscription message

**Test Steps**:
1. Trigger subscription message authorization
2. Check authorization popup
3. Click agree
4. Trigger message send
5. User receives message
6. Click message

**Expected Results**:
1. Subscription authorization popup displays
2. Displays message type and purpose
3. User agrees to authorization
4. Backend sends subscription message
5. User receives WeChat service notification
6. Click message jumps to mini program specified page

---

## Example 6: Mini Program Jump Test

**Test Case ID**: TC_MP_JUMP_001  
**Test Title**: Verify jump to other mini program  
**Test Type**: Functional Testing  
**Function Module**: Mini Program Jump  
**Test Case Level**: P1

**Preconditions**: 
1. Current mini program has jump permission

**Test Steps**:
1. Click jump button
2. Check target mini program info
3. Confirm jump
4. Enter target mini program
5. Return to original mini program

**Expected Results**:
1. Trigger jump
2. Displays target mini program name and icon
3. User confirms jump
4. Jump to target mini program specified page
5. Can return to original mini program
