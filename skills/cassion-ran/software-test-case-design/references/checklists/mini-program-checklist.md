# Mini Program Testing Checklist

## Lifecycle (10 items)
- [ ] Cold start
- [ ] Hot start
- [ ] Page onLoad
- [ ] Page onShow
- [ ] Page onReady
- [ ] Page onHide
- [ ] Page onUnload
- [ ] Switch to background
- [ ] Switch to foreground
- [ ] Destroy after long time background

## Authorization Management (12 items)
- [ ] User info authorization
- [ ] Phone number authorization
- [ ] Location authorization
- [ ] Camera authorization
- [ ] Photo album authorization
- [ ] Bluetooth authorization
- [ ] Recording authorization
- [ ] Authorization agree
- [ ] Authorization deny
- [ ] Re-guide after deny
- [ ] Open permission in settings page
- [ ] Authorization state persistence

## Share Function (14 items)
- [ ] Top-right menu share
- [ ] Share button share
- [ ] Share title
- [ ] Share description
- [ ] Share cover image
- [ ] Share path
- [ ] Share to friend
- [ ] Share to group chat
- [ ] Share to moments
- [ ] Share success callback
- [ ] Share failure handling
- [ ] Open from share card
- [ ] Share parameter passing
- [ ] Share open specified page

## Platform Difference Adaptation (10 items)
- [ ] WeChat mini program API
- [ ] Alipay mini program API
- [ ] Baidu mini program API
- [ ] Douyin mini program API
- [ ] Component compatibility
- [ ] Style compatibility
- [ ] Login difference
- [ ] Payment difference
- [ ] Share difference
- [ ] Review specification difference

## Mini Program Code & QR Code (8 items)
- [ ] Mini program code generate
- [ ] Mini program code style
- [ ] QR code generate
- [ ] Scan code open mini program
- [ ] Scan code parameter parsing
- [ ] Scan code permission control
- [ ] Mini program code jump
- [ ] QR code jump

## Subscription Message & Template Message (8 items)
- [ ] Subscription message authorization
- [ ] Subscription message send
- [ ] Subscription message open
- [ ] Template message send
- [ ] Template message open
- [ ] Subscription count limit
- [ ] Subscription permission revoke
- [ ] Message push setting

## Mini Program Jump (10 items)
- [ ] Jump to other mini program
- [ ] Jump carry parameters
- [ ] Return from other mini program
- [ ] web-view open H5
- [ ] H5 jump to mini program
- [ ] Open mini program from App
- [ ] Open App from mini program
- [ ] Jump count limit
- [ ] Half-screen mini program
- [ ] Mini program mutual jump

## Local Storage (8 items)
- [ ] Storage store
- [ ] Storage read
- [ ] Storage clear
- [ ] Capacity limit
- [ ] Cache update
- [ ] Cache cleanup
- [ ] Temp file storage
- [ ] File management system

## Network Request (10 items)
- [ ] Domain whitelist
- [ ] Request concurrency limit
- [ ] Request timeout
- [ ] Request retry
- [ ] Sensitive data encryption
- [ ] File upload
- [ ] File download
- [ ] Upload download progress
- [ ] Weak network request
- [ ] Offline request

## Performance Optimization (10 items)
- [ ] First screen load time
- [ ] Page render smooth
- [ ] Long list optimization
- [ ] Memory usage
- [ ] Main package size
- [ ] Sub-package load
- [ ] Image lazy loading
- [ ] Data cache
- [ ] Skeleton screen
- [ ] Performance monitoring

## Payment Function (8 items)
- [ ] WeChat payment
- [ ] Alipay payment
- [ ] Payment callback
- [ ] Payment success page
- [ ] Payment failure handling
- [ ] Order state synchronization
- [ ] Refund process
- [ ] Payment security

## Customer Service Function (6 items)
- [ ] Customer service button display
- [ ] Customer service session open
- [ ] Customer service message send
- [ ] Customer service message receive
- [ ] Customer service session close
- [ ] Customer service evaluation
