# Mobile Web Testing Checklist

## Browser Compatibility (12 items)
- [ ] iOS Safari latest version normal
- [ ] iOS Safari mainstream version compatible
- [ ] Android Chrome normal
- [ ] Android Chrome mainstream version compatible
- [ ] WeChat built-in browser normal
- [ ] QQ Browser normal
- [ ] UC Browser normal
- [ ] Quark Browser normal
- [ ] Samsung Internet normal
- [ ] Privacy/Incognito mode normal
- [ ] WebView (WKWebView/Android) compatible
- [ ] JavaScript features compatible

## Touch Interaction (14 items)
- [ ] Single click normal response
- [ ] Double-click zoom function
- [ ] Long press trigger context menu
- [ ] Left-right swipe switch
- [ ] Up-down swipe scroll
- [ ] Two-finger zoom function
- [ ] Pull-down refresh function
- [ ] Pull-up load more
- [ ] Click state visual feedback
- [ ] Touch disabled setting effective
- [ ] Nested scroll no conflict
- [ ] Rubber band effect normal
- [ ] Inertial scroll smooth
- [ ] Gesture conflict handling correct

## Responsive Layout (12 items)
- [ ] 320px width normal
- [ ] 375px width normal
- [ ] 414px width normal
- [ ] 768px (iPad) width normal
- [ ] Long screen (19.5:9) adaptation
- [ ] Notch screen content not blocked
- [ ] Media query breakpoints correct
- [ ] Image width adaptive
- [ ] Font size adaptation
- [ ] Horizontal scroll list normal
- [ ] Fixed position elements normal
- [ ] Landscape layout correct

## Viewport Configuration (8 items)
- [ ] Viewport setting correct
- [ ] Notch screen safe area adaptation
- [ ] Punch hole screen adaptation
- [ ] Viewport recalculation on screen rotation
- [ ] Layout adjustment when keyboard pops up
- [ ] Layout recovery when keyboard closes
- [ ] Zoom limit effective
- [ ] Split screen mode adaptation

## Keyboard & Input (10 items)
- [ ] Input field focus normal
- [ ] Keyboard popup animation smooth
- [ ] Keyboard not block input field
- [ ] Number/email keyboard type correct
- [ ] Chinese input method normal
- [ ] Auto-correction function normal
- [ ] Password show/hide switch
- [ ] Form auto-fill normal
- [ ] Max length limit effective
- [ ] Input format regex validation

## H5 Specific Features (10 items)
- [ ] tel: link dial phone normal
- [ ] sms: link send SMS normal
- [ ] mailto: link open email normal
- [ ] Map link open normal
- [ ] Web Share API share normal
- [ ] Add to home screen function
- [ ] Launch screen display normal
- [ ] Full screen mode normal
- [ ] PWA offline function normal
- [ ] Notification push function normal

## Third-party Login & Payment (10 items)
- [ ] WeChat H5 login normal
- [ ] Alipay H5 login normal
- [ ] QQ H5 login normal
- [ ] Weibo H5 login normal
- [ ] WeChat H5 payment normal
- [ ] Alipay H5 payment normal
- [ ] Login state persistence normal
- [ ] Multi-account switch normal
- [ ] Authorization callback normal
- [ ] Payment result query normal

## WebView Specific (12 items)
- [ ] JSBridge call normal
- [ ] Camera call function normal
- [ ] Photo album call function normal
- [ ] Location call function normal
- [ ] Scan code function normal
- [ ] Physical back button handling correct
- [ ] Navigation bar customization normal
- [ ] Loading progress bar display normal
- [ ] Error page display normal
- [ ] Pull-down refresh function normal
- [ ] Share function normal
- [ ] Login state synchronization normal

## Network & Cache (10 items)
- [ ] WiFi network normal
- [ ] 4G/5G network normal
- [ ] Weak network environment prompt friendly
- [ ] Offline prompt friendly
- [ ] Network recovery auto reconnection
- [ ] Service Worker offline cache
- [ ] LocalStorage normal use
- [ ] SessionStorage normal use
- [ ] Image lazy loading normal
- [ ] Cache update strategy normal

## Performance Optimization (10 items)
- [ ] First screen load < 3 seconds
- [ ] FCP time < 1.8 seconds
- [ ] LCP time < 2.5 seconds
- [ ] Image compression optimization
- [ ] Code splitting effective
- [ ] Rendering no obvious lag
- [ ] No memory leak
- [ ] Skeleton screen display normal
- [ ] CDN resource loading normal
- [ ] First screen monitoring data normal

## SEO & Sharing (10 items)
- [ ] Meta tags complete
- [ ] Page title optimization
- [ ] WeChat share card content correct
- [ ] QQ share card content correct
- [ ] Weibo share card content correct
- [ ] OG tags complete
- [ ] Twitter Card complete
- [ ] Structured data correct
- [ ] Share callback normal
- [ ] Anti-blocking handling normal
