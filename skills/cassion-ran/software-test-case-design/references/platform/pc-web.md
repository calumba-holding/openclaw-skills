# PC Web Specific Test Points

## 1. Browser Compatibility

### What to Test
- Chrome, Firefox, Safari, Edge mainstream versions
- Different versions of same browser (e.g., Chrome 90/100/110)
- JavaScript, CSS features compatibility
- Developer tools no error output

### Why Test
- PC users use various browsers, need to ensure compatibility
- New features may not be supported by old browsers

### Common Pitfalls
- CSS Grid layout abnormal on old browsers
- ES6+ syntax error on old browsers
- Specific browser plugin causes page error

---

## 2. Page Layout

### What to Test
- Layout at different resolutions (1366×768, 1920×1080, 2K, 4K)
- Different DPI zoom (100%, 125%, 150%)
- Window maximize and custom size
- Scrollbar display and scroll smoothness

### Why Test
- PC screen sizes vary greatly, need to adapt to various resolutions
- High DPI screen needs zoom adaptation, otherwise text and icons are too small

### Common Pitfalls
- Layout disorder on high resolution
- Content too small after zoom, hard to read
- Window size change after element overlap

---

## 3. Keyboard Navigation

### What to Test
- Tab key focus order
- Enter key trigger button
- Space key operate checkbox
- Arrow key navigation
- Esc key close dialog
- Global shortcut keys (Ctrl+C/V, Ctrl+S, etc.)

### Why Test
- PC users are accustomed to keyboard operation, need to support complete keyboard navigation
- Accessibility requires keyboard operability

### Common Pitfalls
- Tab order illogical, user jumps disorderly
- Can't trigger button with Enter key
- No focus indicator, user doesn't know current focus position

---

## 4. Form Interaction

### What to Test
- Various input types (text, number, date, file, etc.)
- Form validation (required, format, length)
- Auto-complete, input suggestion
- Copy paste function
- Form submit and reset

### Why Test
- Form is core interaction method of PC Web, experience directly affects conversion
- Form validation error leads to user submission failure

### Common Pitfalls
- Date picker style inconsistent
- Auto-complete covers input field
- Form submit no response, user doesn't know if successful

---

## 5. Authentication and Session

### What to Test
- Login, logout function
- Session expiration handling
- Remember login function
- Password retrieve and modify
- Multi-device login conflict

### Why Test
- Authentication is the foundation of Web applications, security and experience are equally important
- Session expiration handling affects user continuous operation

### Common Pitfalls
- Session expires but no prompt, user operation fails
- Remember login invalid, user needs to login every time
- Multi-device login kicks out without prompt

---

## 6. Multi-window and Tabs

### What to Test
- New window, new tab open page
- Cross-window communication (localStorage, BroadcastChannel)
- Browser forward/back, refresh
- Tab switch state persistence

### Why Test
- PC users are accustomed to multi-tab operation, need to support state synchronization
- Cross-window communication is needed for some scenarios (e.g., payment callback)

### Common Pitfalls
- Data not synchronized between tabs
- Refresh after form data lost
- Cross-window communication failure

---

## 7. Routing and Navigation

### What to Test
- SPA route path correct match
- Nested route level correct
- Dynamic route parameter parsing
- Route guard (login, permission verification)
- 404 page display
- Deep link direct access

### Why Test
- SPA routing is the core of page navigation, error leads to page not found
- Route guard is the foundation of security, need to ensure effective

### Common Pitfalls
- Route parameter parsing error, page data loading failure
- Not logged in access authenticated page, no redirect to login
- 404 page not displayed, user sees white screen

---

## 8. Data Linkage

### What to Test
- Parent-child component data synchronization
- Cross-component state sharing
- List click jump detail, detail modify then list refresh
- Multi-condition filter linkage

### Why Test
- Complex applications have multi-level data linkage, need to ensure data consistency
- Data not synchronized leads to user seeing old data

### Common Pitfalls
- Parent component data modify, child component not updated
- List and detail data inconsistent
- Filter condition linkage error, data doesn't match

---

## 9. Drag Interaction

### What to Test
- Element drag function
- Drag sort position
- Drag upload file
- Drag not exceed boundary
- Undo drag (Ctrl+Z)

### Why Test
- Drag is common interaction method of PC Web, need to support mouse drag
- Drag sort is common function, need to ensure position correct

### Common Pitfalls
- Drag process element position offset
- Drag sort position error
- No undo function, user misoperation can't recover

---

## 10. Rich Text Editor

### What to Test
- Basic text input
- Style settings (bold, italic, underline, color)
- Insert link, image, table
- Undo redo (Ctrl+Z/Y)
- Paste from external (Word, Excel)

### Why Test
- Rich text editor is complex component, need to ensure function complete
- Paste from external may bring format pollution

### Common Pitfalls
- Paste from Word brings redundant styles
- Undo redo history lost
- Image upload failure

---

## 11. File Operations

### What to Test
- File download, preview, save
- File import, export
- Drag file upload
- File type and size limit

### Why Test
- File operation is common function of PC Web, need to support various formats
- File upload needs to limit type and size, prevent security risks

### Common Pitfalls
- Large file download timeout
- File preview format not supported
- File upload no progress prompt

---

## 12. Internationalization and Localization

### What to Test
- Language switch function
- Static text and dynamic content translation
- Number, date time, currency format
- RTL layout (Arabic, Hebrew)

### Why Test
- Multi-language support is the foundation of internationalization
- Different regions have different format habits

### Common Pitfalls
- Language switch after page not fully refreshed
- Date format doesn't conform to region habit
- RTL layout text direction error

---

## 13. Print Function

### What to Test
- Click print button trigger print
- Print preview content correct
- Print style correct (hide unnecessary elements)
- Header footer display correct
- Cross-page table title repeat

### Why Test
- Print is common requirement of PC Web, need to ensure print effect
- Print style may be different from screen display

### Common Pitfalls
- Print preview content incomplete
- Background color, image not printed
- Table cross-page title not repeated

---

## 14. Dark Mode

### What to Test
- Manual switch dark mode
- Follow system dark mode
- Color contrast sufficient after switch
- Image, icon adaptation dark

### Why Test
- Dark mode reduces eye fatigue, improves user experience
- Need to ensure dark mode color contrast sufficient

### Common Pitfalls
- Dark mode text color too light, hard to read
- Image doesn't adapt dark, display too bright
- Mode switch has white flash
