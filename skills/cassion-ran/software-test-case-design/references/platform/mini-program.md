# Mini Program Specific Test Points

## 1. Lifecycle

### What to Test
- Cold start, hot start
- Page onLoad, onShow, onReady, onHide, onUnload
- Switch to background, switch to foreground
- Destroy after long time background

### Why Test
- Mini program lifecycle is special, different from H5 and App
- Lifecycle function execution order affects page initialization and data loading

### Common Pitfalls
- Data reloads every time enter page, doesn't use cache
- Background switch after page state lost
- Long time background destroy, return after data lost

---

## 2. Authorization Management

### What to Test
- User info, phone number, location, camera, album authorization
- Authorization agree, deny, re-guide
- Open permission in settings page
- Authorization state persistence

### Why Test
- Mini program authorization mechanism is special, need user active trigger
- Authorization denial shouldn't cause function unavailable

### Common Pitfalls
- Authorization request without explanation, user doesn't know why
- Authorization denied then function directly unavailable
- "Don't ask again" after no guidance, user doesn't know how to enable

---

## 3. Share Function

### What to Test
- Top-right menu share, share button share
- Share title, description, cover image, path
- Share to friend, group chat, moments
- From share card open specified page

### Why Test
- Share is the core spread method of mini programs, affects user growth
- Share parameters need to correctly pass to target page

### Common Pitfalls
- Share cover image not displayed or displayed incompletely
- From share card open doesn't jump to specified page
- Share parameters lost, page data loading failure

---

## 4. Platform Difference Adaptation

### What to Test
- WeChat, Alipay, Baidu, Douyin mini program API differences
- Component compatibility, style compatibility
- Login, payment, share differences
- Review specification differences

### Why Test
- Multi-platform mini programs need to adapt to different platform characteristics
- Review specifications are different, need to ensure pass review

### Common Pitfalls
- API doesn't exist on specific platform, function unavailable
- Style displays differently on different platforms
- Review rejected, doesn't conform to platform specification

---

## 5. Mini Program Code and QR Code

### What to Test
- Mini program code, QR code generate
- Scan code open mini program
- Scan code parameter parsing
- Mini program code jump

### Why Test
- Mini program code and QR code are important entry points, need to ensure normal use
- Scan code parameters need to correctly parse and pass

### Common Pitfalls
- Mini program code scan failure
- Scan code parameters parsing error, page data loading failure
- QR code expired, can't open

---

## 6. Subscription Message and Template Message

### What to Test
- Subscription message authorization, send, open
- Template message send, open
- Subscription count limit, permission revoke

### Why Test
- Subscription message is important channel for mini program to reach users
- Subscription count is limited, need reasonable use

### Common Pitfalls
- Subscription authorization not triggered, can't send message
- Subscription count used up, can't send important message
- Message click doesn't jump to specified page

---

## 7. Mini Program Jump

### What to Test
- Jump to other mini program
- Jump carry parameters, return from other mini program
- web-view open H5, H5 jump to mini program
- From App open mini program, from mini program open App

### Why Test
- Mini program ecosystem supports mutual jump, extends usage scenarios
- Jump parameters need to correctly pass

### Common Pitfalls
- Jump to other mini program failure
- Jump parameters lost
- web-view open H5 page abnormal

---

## 8. Local Storage

### What to Test
- Storage store, read, clear
- Capacity limit (10MB per mini program)
- Cache update, cleanup
- Temp file storage, file management system

### Why Test
- Mini program storage capacity is limited, need reasonable use
- Cache update not timely leads to user using old version

### Common Pitfalls
- Storage exceeds capacity, data storage failure
- Cache doesn't update, user always uses old version
- Temp file not cleaned, occupy storage

---

## 9. Network Request

### What to Test
- Domain whitelist configuration
- Request concurrency limit (10 concurrent)
- Request timeout, retry
- Sensitive data encryption
- File upload, download

### Why Test
- Mini program network request has restrictions, need to adapt
- Sensitive data needs encryption transmission

### Common Pitfalls
- Domain not in whitelist, request blocked
- Request concurrency exceeds limit, request failure
- Large file upload timeout

---

## 10. Performance Optimization

### What to Test
- First screen load time, page render smoothness
- Main package size, sub-package loading
- Image lazy loading, data cache
- Skeleton screen, performance monitoring

### Why Test
- Mini program performance affects user experience and review
- Main package size exceeds limit can't upload

### Common Pitfalls
- First screen load too slow, user loses patience
- Main package too large, exceeds 2MB limit
- Image not lazy loaded, page scroll lag

---

## 11. Payment Function

### What to Test
- WeChat payment, Alipay payment
- Payment callback, payment success page
- Payment failure handling
- Order state synchronization, refund process

### Why Test
- Payment is core function of e-commerce mini programs, needs to ensure safety
- Payment result callback is critical, affecting order state

### Common Pitfalls
- Payment success but callback failure, order shows unpaid
- Payment failure no prompt, user doesn't know reason
- Order state not synchronized, display error

---

## 12. Customer Service Function

### What to Test
- Customer service button display, session open
- Customer service message send, receive
- Customer service session close, evaluation

### Why Test
- Customer service is important channel for user feedback, needs to ensure normal
- Message send receive needs to be timely

### Common Pitfalls
- Customer service button not displayed or click no response
- Message send failure or delay
- Session close after can't re-enter
