# Desktop Specific Test Points

## 1. Window Management

### What to Test
- Window size adjustment (drag border, maximize, minimize, restore)
- Multi-window management (switch, arrange, close)
- Window always on top, full screen mode
- Window state persistence (position, size)

### Why Test
- Desktop application window management is core function, affecting user multi-task operation
- Window state persistence improves user experience

### Common Pitfalls
- Window size adjustment not smooth
- Multi-window switch confusion
- Window position not saved, restart returns to default

---

## 2. Keyboard Shortcuts

### What to Test
- Common shortcuts (Ctrl+C/V, Ctrl+Z/Y, Ctrl+S)
- Application custom shortcuts
- Shortcut conflict handling
- Shortcut hint and custom settings

### Why Test
- Desktop users rely on keyboard shortcuts to improve efficiency
- Shortcut conflict leads to function abnormality

### Common Pitfalls
- Shortcuts conflict with system or other applications
- No shortcut hint, user doesn't know available shortcuts
- Custom shortcut settings not saved

---

## 3. File Operations

### What to Test
- File open, save, save as
- Drag file open
- Auto save and recovery
- File association (double-click open with this application)
- Recent files

### Why Test
- File operation is the core function of desktop applications
- Auto save prevents data loss

### Common Pitfalls
- Large file open slow or crash
- Auto save interval too long, data lost after crash
- File association failure, double-click can't open

---

## 4. System Integration

### What to Test
- System tray icon and right-click menu
- Notification center message push
- Auto start on boot
- Right-click menu integration (Windows Explorer)
- Menu bar integration (macOS)

### Why Test
- System integration improves application availability
- Notification center is important channel for user recall

### Common Pitfalls
- Tray icon not displayed or click no response
- Notification not pushed or click no jump
- Auto start setting invalid

---

## 5. Multi-monitor Adaptation

### What to Test
- Single monitor, dual screen extend, multi-screen extend
- Duplicate mode
- Different resolution and DPI zoom
- Window cross-screen drag

### Why Test
- Multi-monitor is common configuration of desktop, need to adapt to various modes
- Window cross-screen drag needs to ensure position correct

### Common Pitfalls
- Window displays on disconnected monitor, user can't find
- Different resolution causes window size abnormality
- Full screen mode displays on wrong monitor

---

## 6. Peripheral Support

### What to Test
- Mouse operation (left button, right button, wheel, side button)
- Touchpad gesture (two-finger scroll, zoom)
- Touch screen operation (if supported)
- Printer, scanner and other peripherals

### Why Test
- Desktop applications need to support various input devices
- Peripherals extend application capabilities

### Common Pitfalls
- Touchpad gesture not recognized
- High DPI mouse movement not smooth
- Print function abnormal

---

## 7. System Compatibility

### What to Test
- Windows 10, Windows 11
- macOS different versions
- Intel chip, ARM64 chip (Apple Silicon)
- Light mode, dark mode, high contrast mode

### Why Test
- Desktop operating systems have various versions, need to ensure compatibility
- New chip architecture (ARM64) needs special adaptation

### Common Pitfalls
- Function abnormal on specific system version
- ARM64 architecture application can't run or performance poor
- Dark mode adaptation incomplete

---

## 8. Installation and Update

### What to Test
- Installer download and installation wizard
- Installation location selection and shortcut creation
- First run initialization
- Uninstall and residue cleanup
- Auto update detection and download
- Forced update vs optional update

### Why Test
- Installation and update are the first step of user contact with application, experience affects retention
- Timely updates fix vulnerabilities and add features

### Common Pitfalls
- Installation process error, can't complete installation
- Uninstall not clean,残留 files and registry
- Update download failure no retry mechanism
- Forced update interrupts user operation

---

## 9. Performance and Resources

### What to Test
- Cold start time, hot start time
- Memory usage, CPU usage
- Interface response speed
- Long time running stability

### Why Test
- Desktop application performance affects user experience, need to ensure smooth
- Resource usage too high affects other applications

### Common Pitfalls
- Start too slow, user loses patience
- Memory leak, long time use causes application crash
- Interface response lag, operation not smooth

---

## 10. Security and Permissions

### What to Test
- Administrator permission request (Windows)
- File read-write permission
- Network access permission
- Data encryption and sensitive information protection

### Why Test
- Desktop applications have higher permissions, need to ensure security
- Sensitive data needs encryption protection

### Common Pitfalls
- Permission request too frequent, user experience poor
- Sensitive data stored in plain text, security risk
- No security audit log
