# Mobile Web Specific Test Points

## 1. Responsive Layout

### What to Test
- Layout adaptation at different screen widths (320px-768px)
- Touch area size (minimum 44×44px)
- Font size adaptation (respect system font size settings)
- Image adaptive display (not stretched, not cropped)

### Why Test
- Mobile devices have various screen sizes, need to ensure layout normal at all sizes
- Touch area too small leads to misoperation, affecting user experience

### Common Pitfalls
- Layout disorder on small screen, content overlap
- Button too small, user hard to click
- Font size doesn't adapt, user sets large font but page unchanged

---

## 2. Touch Interaction

### What to Test
- Click, double-click, long press, swipe gesture response
- Pull-down refresh, pull-up load more trigger
- Zoom, drag gesture support
- Touch and mouse event compatibility

### Why Test
- Mobile Web mainly relies on touch interaction, gesture experience directly affects user satisfaction
- Some components need to support both touch and mouse (e.g., tablet with keyboard)

### Common Pitfalls
- Click delay (300ms), user feels lag
- Pull-down refresh and page scroll conflict
- Gesture response not sensitive, user needs multiple attempts

---

## 3. Browser Compatibility

### What to Test
- iOS Safari, Android Chrome mainstream versions
- WeChat built-in browser, QQ Browser, UC Browser, etc.
- Private/incognito mode
- WebView compatibility (WKWebView, X5 Kernel)

### Why Test
- Mobile browsers have various kernels, compatibility issues are common
- WeChat built-in browser has special restrictions (e.g., autoplay)

### Common Pitfalls
- Function abnormal on specific browser
- WeChat built-in browser video autoplay failure
- WebView page white screen or crash

---

## 4. Viewport and Safe Area

### What to Test
- Viewport settings correct (width=device-width, initial-scale=1)
- Notch screen, punch hole screen safe area adaptation
- Keyboard popup page layout adjustment
- Orientation switch layout adaptation

### Why Test
- Notch screen, punch hole screen need to avoid blocking content
- Keyboard popup may block input field, need automatic adjustment

### Common Pitfalls
- Content blocked by notch on notch screen
- Keyboard popup blocks input field, user can't see input content
- Orientation switch after layout disorder

---

## 5. H5 Specific Features

### What to Test
- tel:, sms:, mailto: link jump
- Map link open
- Add to home screen (PWA)
- Web Share API share

### Why Test
- H5 needs to interact with system functions (call, SMS, email, map)
- PWA provides near-native app experience

### Common Pitfalls
- tel: link doesn't jump to dial interface on some browsers
- Add to home screen prompt not displayed
- Share API not supported, no fallback scheme

---

## 6. Third-party Login and Payment

### What to Test
- WeChat H5 login, Alipay H5 login
- WeChat H5 payment, Alipay H5 payment
- Login state persistence and synchronization
- Payment result callback and query

### Why Test
- H5 usually integrates third-party login and payment
- Payment result callback is critical, affecting order state

### Common Pitfalls
- Login callback failure, can't get user info
- Payment success but callback failure, order shows unpaid
- Login state lost after refresh

---

## 7. WebView Specific

### What to Test
- JSBridge communication normal
- Native capability call (camera, album, location, scan)
- Physical back button handling
- Page loading progress display

### Why Test
- H5 in WebView needs to interact with native
- Native capabilities need to be called through JSBridge

### Common Pitfalls
- JSBridge call failure, native function unavailable
- Back button directly exits app, doesn't return to previous page
- Page loading white screen, no progress prompt

---

## 8. Cache and Offline

### What to Test
- Service Worker offline cache
- LocalStorage, SessionStorage use
- Cache update strategy (version control)
- Offline state prompt and handling

### Why Test
- Offline cache improves user experience, reduces loading time
- Cache update not timely leads to user using old version

### Common Pitfalls
- Service Worker registration failure, offline function unavailable
- Cache doesn't update, user always uses old version
- LocalStorage exceeds capacity, data storage failure
