# Mobile App Specific Test Points

## 1. Gesture Operations

### What to Test
- Pull-down refresh, pull-up load trigger area and animation
- Long press trigger context menu vs long press enter edit mode (conflict handling)
- Two-finger zoom boundaries (min/max zoom ratio)
- Swipe delete vs swipe switch conflict
- Gesture and page scroll event conflict (nested scroll)

### Why Test
- Mobile devices rely on gesture interaction, poor gesture experience directly affects user satisfaction
- Gesture conflicts lead to user confusion and reduced efficiency

### Common Pitfalls
- Pull-down refresh trigger area too small, user hard to trigger
- Long press and swipe gesture conflict, user accidentally triggers wrong function
- Zoom animation not smooth, user experience lag

---

## 2. Interruption Recovery

### What to Test
- Form data retention after call/SMS/alarm interruption
- Order state consistency after payment process interruption
- Return after long time background (cold start vs hot start)
- Recovery after permission popup interruption

### Why Test
- Mobile scenarios are fragmented, users frequently switch apps, data loss causes user complaints
- Payment interruption may cause order state inconsistency, affecting user rights

### Common Pitfalls
- Form data lost after background return, user needs to re-enter
- Payment interrupted then returned, order shows unpaid but deducted
- Permission popup interrupts operation flow, user doesn't know how to continue

---

## 3. Network Switching

### What to Test
- Handling of in-progress requests during WiFi↔4G/5G switching
- Submit operations under weak network (high latency/low bandwidth/high packet loss)
- Reconnection mechanism after airplane mode switching
- Data auto-sync after network recovery

### Why Test
- Mobile network environment is complex, users frequently switch networks, app needs to adapt
- Weak network environment is common, poor handling leads to operation failure

### Common Pitfalls
- Network switching causes request failure, user needs to retry
- Submit under weak network no response, user doesn't know if successful
- Network recovery doesn't auto-sync, data shows old version

---

## 4. Permission Management

### What to Test
- First permission request needs to explain purpose
- Function degradation + guide to enable after denial
- Handling after permission revocation
- Guide after "Don't ask again"

### Why Test
- Mobile permissions are sensitive, unreasonable requests lead to user rejection
- Permission denial shouldn't cause app unusable, need graceful degradation

### Common Pitfalls
- Permission request without explanation, user doesn't know why
- Permission denied then function directly unavailable, user experience poor
- "Don't ask again" after no guidance, user doesn't know how to enable

---

## 5. Push Notifications

### What to Test
- Cold start vs hot start when clicking push
- Push parameter passing and page data loading
- Handling of multiple push clicks

### Why Test
- Push is important channel for user recall, click behavior affects conversion
- Push parameter passing error leads to wrong page or data loading failure

### Common Pitfalls
- Click push opens app but doesn't jump to specified page
- Push carries parameters but page data loading error
- Multiple push clicks only process the first one

---

## 6. Device Compatibility

### What to Test
- Different screen sizes and resolutions adaptation
- Notch screen, punch hole screen, waterfall screen adaptation
- Different iOS/Android versions compatibility
- Different manufacturer ROM compatibility

### Why Test
- Mobile device fragmentation is severe, need to ensure experience consistency
- New device features (notch, punch hole) need special adaptation

### Common Pitfalls
- Content blocked by notch on notch screen
- Button too small on small screen, hard to click
- Function abnormal on specific ROM

---

## 7. Performance Experience

### What to Test
- Cold start time, first screen load time
- Page scroll smoothness, animation frame rate
- Memory usage, power consumption

### Why Test
- Mobile device performance is limited, poor performance leads to lag, heat, power consumption
- Users are sensitive to start speed and operation smoothness

### Common Pitfalls
- Cold start too slow, user loses patience
- List scroll lag, frame rate below 50fps
- Long time use causes phone heat and power consumption

---

## 8. Storage and Data

### What to Test
- Local data storage and reading
- Cache cleanup and update
- Data migration and version compatibility

### Why Test
- Mobile storage is limited, need reasonable cache strategy
- Data migration errors cause user data loss

### Common Pitfalls
- Cache too large, occupy too much storage
- App update after data lost or abnormal
- Cache cleanup causes important data lost

---

## 9. Updates and Versions

### What to Test
- In-app update detection and download
- Forced update vs optional update
- Update progress and installation

### Why Test
- Timely updates fix vulnerabilities and add features
- Forced update strategy affects user experience

### Common Pitfalls
- Update detection not timely, user uses old version for long time
- Forced update interrupts user operation, experience poor
- Update download failure no retry mechanism
