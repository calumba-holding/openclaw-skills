# PC Web Testing Checklist

## Browser Compatibility (12 items)
- [ ] Chrome latest version normal
- [ ] Chrome mainstream version compatible
- [ ] Firefox latest version normal
- [ ] Firefox mainstream version compatible
- [ ] Safari browser compatible
- [ ] Edge browser compatible
- [ ] Multi-core browser compatible
- [ ] JavaScript features compatible
- [ ] CSS features compatible
- [ ] Privacy mode access normal
- [ ] Developer tools no errors
- [ ] Browser extension compatibility

## Page Layout (10 items)
- [ ] 1366×768 resolution normal
- [ ] 1920×1080 resolution normal
- [ ] 2K/4K resolution normal
- [ ] 100% DPI zoom normal
- [ ] 125% DPI zoom normal
- [ ] 150% DPI zoom normal
- [ ] Window maximize layout correct
- [ ] Window custom size layout correct
- [ ] Scrollbar display correct
- [ ] Responsive breakpoints correct

## Keyboard Navigation (10 items)
- [ ] Tab key focus order correct
- [ ] Enter key can trigger button
- [ ] Space key can operate checkbox
- [ ] Arrow keys can navigate
- [ ] Global shortcuts normal
- [ ] Esc key close dialog
- [ ] F5 refresh page
- [ ] Ctrl+C/V copy paste
- [ ] Focus indicator clearly visible
- [ ] Accessibility jump link available

## Form Interaction (12 items)
- [ ] Text input normal
- [ ] Number input validation
- [ ] Date picker available
- [ ] Dropdown selection normal
- [ ] File upload function
- [ ] Form required validation
- [ ] Form submit success
- [ ] Prevent duplicate submit
- [ ] Form reset function
- [ ] Input suggestion/auto-complete
- [ ] Copy paste function
- [ ] Form disabled state

## Authentication & Session (10 items)
- [ ] Normal login success
- [ ] Wrong password prompt friendly
- [ ] Session expiration handling
- [ ] Remember login function
- [ ] Normal logout
- [ ] Password retrieve process
- [ ] Password modify function
- [ ] Two-factor authentication (if applicable)
- [ ] Multi-device login conflict handling
- [ ] Timeout auto logout

## Multi-window & Tabs (8 items)
- [ ] New window open normal
- [ ] New tab open normal
- [ ] Cross-window communication normal
- [ ] Close window confirmation
- [ ] Tab switch state persistence
- [ ] Browser forward/back normal
- [ ] Page refresh data persistence
- [ ] Window state memory

## Routing & Navigation (12 items)
- [ ] SPA route path correct match
- [ ] Nested route level correct
- [ ] Dynamic route parameter parsing correct
- [ ] URL and page state synchronization
- [ ] Route guard redirect when not logged in
- [ ] Route jump when insufficient permission
- [ ] 404 page display normal
- [ ] Deep link direct access normal
- [ ] Browser forward/back state correct
- [ ] After refresh URL and page state consistent
- [ ] Breadcrumb navigation level correct
- [ ] Anchor positioning function normal

## Data Linkage (10 items)
- [ ] Parent-child component data sync
- [ ] Cross-component state share correct
- [ ] List click jump detail
- [ ] Detail modify then list refresh
- [ ] Multi-condition filter linkage correct
- [ ] Pagination switch data correct
- [ ] Sorting switch display correct
- [ ] Modal submit then page refresh
- [ ] Linkage field dependency correct
- [ ] Tab switch data load

## Drag Interaction (10 items)
- [ ] Element drag function normal
- [ ] Drag sort position correct
- [ ] Drag upload file success
- [ ] Drag disabled state normal
- [ ] Drag keyboard operation available
- [ ] Drag not exceed boundary
- [ ] Ctrl+Z undo drag
- [ ] Drag guide line alignment
- [ ] Large amount element drag smooth
- [ ] After drag data save correct

## Rich Text Editor (10 items)
- [ ] Basic text input normal
- [ ] Bold/italic/underline effective
- [ ] Heading level switch correct
- [ ] Unordered/ordered list normal
- [ ] Insert link/image/table normal
- [ ] Ctrl+Z undo normal
- [ ] Ctrl+Y redo normal
- [ ] Paste from external format保留
- [ ] Markdown edit preview normal
- [ ] Word count accurate

## File Operations (8 items)
- [ ] File download normal
- [ ] File preview normal
- [ ] File save normal
- [ ] File import normal
- [ ] File export normal
- [ ] File delete confirmation
- [ ] Drag file upload
- [ ] File type limit

## Network & Cache (10 items)
- [ ] Normal network access
- [ ] Offline prompt friendly
- [ ] Network recovery handling
- [ ] Weak network load prompt
- [ ] Strong cache effective
- [ ] Negotiation cache effective
- [ ] Cookie normal use
- [ ] LocalStorage normal use
- [ ] SessionStorage normal use
- [ ] Request retry mechanism

## Internationalization & Localization (10 items)
- [ ] Language switch function normal
- [ ] Static text translation correct
- [ ] Dynamic content translation correct
- [ ] Number format conforms to region habit
- [ ] Date time format conforms to region habit
- [ ] Currency format correct
- [ ] RTL layout normal (if applicable)
- [ ] Language selection persistence
- [ ] After refresh language persistence
- [ ] Cross-page language consistent

## Print Function (8 items)
- [ ] Click print button trigger print
- [ ] Print preview content correct
- [ ] Print style correct (hide unnecessary elements)
- [ ] Header footer display correct
- [ ] Cross-page table title repeat
- [ ] Image print clear
- [ ] A4/Letter paper layout correct
- [ ] Chrome/Firefox/Edge print consistent

## Dark Mode (8 items)
- [ ] Manual switch dark mode
- [ ] Follow system dark mode
- [ ] After switch color contrast sufficient
- [ ] Image/icon adaptation dark
- [ ] Form control style correct
- [ ] Code block highlight readable
- [ ] Mode persistence (refresh persistence)
- [ ] Cross-page mode consistent

## Performance Optimization (8 items)
- [ ] First screen load < 3 seconds
- [ ] White screen time < 1 second
- [ ] Image lazy loading normal
- [ ] Animation smooth 60fps
- [ ] No memory leak
- [ ] Long list load normal
- [ ] Code splitting effective
- [ ] Resource compression effective
