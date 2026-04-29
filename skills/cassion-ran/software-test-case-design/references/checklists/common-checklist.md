# General Testing Checklist

This document integrates checklists for functional testing, linkage testing, routing testing, UI visual testing, API testing, and security testing, applicable to test case execution across all platforms.

## Table of Contents

| Line | Chapter |
|------|------|
| 19 | Part 1: Functional Testing Checklist |
| 65 | Part 2: Linkage Testing Checklist |
| 110 | Part 3: Routing Testing Checklist |
| 161 | Part 4: UI Visual Testing Checklist |
| 232 | Part 5: API Testing Checklist |
| 307 | Part 6: Security Testing Checklist |
| 410 | Check Completion Record |

---

## Part 1: Functional Testing Checklist

### Test Coverage
- [ ] All function points covered
- [ ] Normal process covered
- [ ] Exception process covered
- [ ] Boundary conditions covered
- [ ] Special scenarios covered

### Function Correctness
- [ ] Functions implemented according to requirements
- [ ] Business logic correct
- [ ] Data processing correct
- [ ] State transition correct
- [ ] Permission control correct

### Input Validation
- [ ] Valid input handled correctly
- [ ] Invalid input prompts friendly
- [ ] Boundary values handled correctly
- [ ] Special characters handled correctly
- [ ] Empty values handled correctly

### Output Validation
- [ ] Display content correct
- [ ] Data format correct
- [ ] Sorting correct
- [ ] Filtering correct
- [ ] Statistics correct

### Interaction Testing
- [ ] User operation process smooth
- [ ] Page jumps correct
- [ ] Button functions correct
- [ ] Form submission correct
- [ ] List operations correct

### Data Consistency
- [ ] Frontend and backend data consistent
- [ ] Multi-device data consistent
- [ ] Cache and database consistent
- [ ] History records correct
- [ ] Real-time data correct

---

## Part 2: Linkage Testing Checklist

### Form Linkage
- [ ] Province-City-District linkage
- [ ] Category selection linkage
- [ ] Conditional show/hide
- [ ] Data cascade
- [ ] Form validation linkage
- [ ] Submit button state linkage

### List Linkage
- [ ] Master-detail list linkage
- [ ] Filter condition linkage
- [ ] Sorting linkage
- [ ] Pagination linkage
- [ ] Selection state linkage

### Search Linkage
- [ ] Search keyword suggestion
- [ ] Search result linkage
- [ ] Search history linkage
- [ ] Popular search linkage

### State Linkage
- [ ] Button state linkage
- [ ] Menu state linkage
- [ ] Tab state linkage
- [ ] Icon state linkage
- [ ] Color state linkage

### Data Linkage
- [ ] Real-time data synchronization
- [ ] Multi-device data synchronization
- [ ] Cache and database synchronization
- [ ] Local and remote synchronization
- [ ] Two-way data binding

### Page Linkage
- [ ] Page parameter passing
- [ ] Page state synchronization
- [ ] Multi-window linkage
- [ ] iframe linkage

---

## Part 3: Routing Testing Checklist

### Direct Access
- [ ] Direct access to homepage URL
- [ ] Direct access to detail page URL
- [ ] Direct access to list page URL
- [ ] Direct access to personal center page URL

### Navigation Jump
- [ ] Navigation bar click jump
- [ ] Breadcrumb navigation jump
- [ ] Bottom navigation jump
- [ ] Sidebar navigation jump
- [ ] Tab switching
- [ ] Button click jump

### Browser Navigation
- [ ] Browser back
- [ ] Browser forward
- [ ] Browser refresh
- [ ] History records

### Deep Links
- [ ] External link open App specified page
- [ ] Push notification open specified page
- [ ] Share link open specified page

### Error Pages
- [ ] 404 page display
- [ ] 403 page display
- [ ] 500 page display

### Routing Parameters
- [ ] URL parameter passing
- [ ] URL parameter parsing
- [ ] Missing parameter handling
- [ ] Wrong parameter handling

### Route Guards
- [ ] Login verification
- [ ] Permission verification
- [ ] Not logged in redirect to login page
- [ ] No permission redirect to 403

### Routing Performance
- [ ] Route switching smooth
- [ ] Page loading fast
- [ ] Route animation smooth

---

## Part 4: UI Visual Testing Checklist

### Layout Testing
- [ ] Alignment correct
- [ ] Spacing consistent
- [ ] Hierarchy structure clear
- [ ] Responsive layout adaptation
- [ ] Elements not overlapping
- [ ] Content not overflowing
- [ ] Whitespace reasonable
- [ ] Visual balance

### Color Testing
- [ ] Brand color correct
- [ ] Auxiliary color correct
- [ ] State color correct (success/failure/warning)
- [ ] Contrast conforms to WCAG standards
- [ ] Dark mode adaptation
- [ ] Light mode adaptation
- [ ] Color semantics correct
- [ ] Color blind friendly

### Font Testing
- [ ] Font family correct
- [ ] Font size hierarchy clear
- [ ] Line height appropriate
- [ ] Font weight correct
- [ ] Font color contrast sufficient
- [ ] Text not truncated
- [ ] Multi-language font adaptation
- [ ] Special characters display normal

### Icon Testing
- [ ] Icon style consistent
- [ ] Icon size uniform
- [ ] Icon semantics clear
- [ ] Icon states correct (default/hover/click/disabled)
- [ ] Icon clarity sufficient
- [ ] Icon loading normal

### Image Testing
- [ ] Image quality clear
- [ ] Image ratio correct
- [ ] Loading state displays placeholder
- [ ] Error state displays error image
- [ ] Image lazy loading normal
- [ ] Image compression appropriate

### Animation Testing
- [ ] Animation curve natural
- [ ] Animation duration appropriate
- [ ] Animation performance smooth (≥50fps)
- [ ] Animation semantics clear
- [ ] Animation interruptible
- [ ] No animation flickering

### Interaction State Testing
- [ ] Default state correct
- [ ] Hover state correct
- [ ] Click state correct
- [ ] Disabled state correct
- [ ] Focus state correct

### Multi-theme Testing
- [ ] Light theme normal
- [ ] Dark theme normal
- [ ] Theme switching smooth
- [ ] Theme memory correct

---

## Part 5: API Testing Checklist

### Usage Instructions
- ✅ Check item by item to ensure coverage
- 🔴 Record issues immediately when found
- 📝 Add business-specific check items

---

### Functional Testing
- [ ] GET request returns normally
- [ ] POST creates resource successfully
- [ ] PUT/PATCH updates successfully
- [ ] DELETE deletes successfully
- [ ] Batch operations correct
- [ ] Status code conforms to specification
- [ ] Error response clear

### Data Validation
- [ ] Required field validation
- [ ] Field type validation
- [ ] Field format validation
- [ ] Field length validation
- [ ] Field range validation
- [ ] Uniqueness validation
- [ ] Business rule validation

### Authentication & Authorization
- [ ] Token authentication normal
- [ ] Unauthenticated access denied
- [ ] Unauthorized access denied
- [ ] Token expiration handling
- [ ] Token refresh normal
- [ ] Permission isolation correct

### Performance Testing
- [ ] Response time meets standard (P95 < 500ms)
- [ ] Concurrency test passed
- [ ] Stress test passed
- [ ] No memory leak
- [ ] Connection pool normal

### Error Handling
- [ ] Error code specification
- [ ] Error message clear
- [ ] Exception capture
- [ ] Log recording
- [ ] Retry mechanism
- [ ] Idempotency guarantee

### Pagination & Sorting
- [ ] Pagination parameters normal
- [ ] Total count correct
- [ ] Sorting function normal
- [ ] Default sorting reasonable

### Search & Filtering
- [ ] Exact search normal
- [ ] Fuzzy search normal
- [ ] Multi-condition combination correct
- [ ] Filtering function normal

### Version Management
- [ ] Version control correct
- [ ] Backward compatible
- [ ] Version documentation complete

### API Documentation
- [ ] Swagger/OpenAPI specification
- [ ] Parameter description complete
- [ ] Examples clear
- [ ] Error code documentation

---

## Part 6: Security Testing Checklist

### Usage Instructions
- ✅ Check item by item to ensure coverage
- 🔴 Report security issues immediately when found
- 📝 Test in authorized environment
- ⚠️ Follow OWASP Top 10

---

### Injection Attack Protection
- [ ] SQL injection protection (parameterized queries)
- [ ] NoSQL injection protection
- [ ] Command injection protection
- [ ] Path traversal protection
- [ ] File inclusion protection

### XSS Protection
- [ ] Reflected XSS protection
- [ ] Stored XSS protection
- [ ] DOM-based XSS protection
- [ ] Input filtering
- [ ] Output encoding
- [ ] CSP policy setting
- [ ] HttpOnly flag

### Authentication Security
- [ ] Password strength validation
- [ ] Password encrypted storage
- [ ] Password transmission encryption
- [ ] Multi-factor authentication
- [ ] Login failure limit
- [ ] Account lockout mechanism
- [ ] CAPTCHA mechanism

### Session Management
- [ ] Session ID secure generation
- [ ] Session timeout setting
- [ ] Session fixation attack protection
- [ ] Cookie security flags (Secure, HttpOnly)
- [ ] Single sign-on security

### Access Control
- [ ] Horizontal privilege escalation protection
- [ ] Vertical privilege escalation protection
- [ ] Data permission isolation
- [ ] Sensitive data masking

### Sensitive Information Protection
- [ ] API does not return sensitive fields
- [ ] No hardcoded keys in frontend
- [ ] Log desensitization processing
- [ ] Error information not exposed
- [ ] HTTPS enforced
- [ ] TLS version latest
- [ ] Database encryption

### CSRF Protection
- [ ] CSRF Token validation
- [ ] Referer validation
- [ ] SameSite Cookie setting
- [ ] Key operations secondary confirmation

### File Upload Security
- [ ] File type whitelist
- [ ] File content validation
- [ ] File size limit
- [ ] Virus scanning
- [ ] Upload directory permissions
- [ ] File access control

### Business Logic Security
- [ ] Payment amount tampering protection
- [ ] Duplicate payment protection
- [ ] Concurrent competition handling
- [ ] Inventory overselling protection
- [ ] Coupon abuse protection
- [ ] Business process step skipping protection

### API Security
- [ ] Token security protection
- [ ] API rate limiting
- [ ] API quota limiting
- [ ] Operation log audit
- [ ] Abnormal detection alarm

### Security Configuration
- [ ] Directory listing disabled
- [ ] Error page customization
- [ ] HTTP method restriction
- [ ] Security header setting (X-Frame-Options etc.)
- [ ] Framework vulnerability repair
- [ ] Dependency library vulnerability repair
- [ ] Database minimum permissions

### Compliance Check
- [ ] GDPR compliance (if applicable)
- [ ] Cybersecurity Law compliance
- [ ] Level protection compliance
- [ ] Privacy policy complete

---

## Check Completion Record

| Check Item | Check Result | Issue Record | Fix Status |
|-------|---------|---------|---------|
| Functional Testing | ✅ Passed | - | - |
| Linkage Testing | Pending Check | - | - |
| Routing Testing | Pending Check | - | - |
| UI Visual Testing | Pending Check | - | - |
| API Testing | Pending Check | - | - |
| Security Testing | Pending Check | - | - |
