# Hum2Song

Helps users find songs by humming or describing melodies, using available music recognition tools and services.

---

## Overview

This skill assists users in identifying songs when they can only remember part of the melody or have a humming recording. It provides guidance on using various music recognition services and tools.

---

## Triggers

Use this skill when the user:
- Hums or describes a melody (e.g., "dun dun dun dun")
- Has an audio recording of humming and wants to find the song
- Asks "what song is this?" with melodic description
- Wants to identify music from a partial memory

---

## Methods

### 1. Music Recognition Apps

**Recommended Apps:**

| App | Platform | Best For | How to Use |
|-----|----------|----------|------------|
| **SoundHound** | iOS/Android | Humming/singing recognition | Tap mic → Hum or sing |
| **Shazam** | iOS/Android | Playing music recognition | Tap to listen to playing audio |
| **Google Hum to Search** | Android/Web | Humming recognition | Google app → Hum |
| **Musixmatch** | iOS/Android | Lyrics-based search | Type lyrics you remember |

### 2. Online Services

**Midomi** (midomi.com)
- Website-based humming recognition
- Click "Click and Sing or Hum"
- Allow microphone access
- Hum for 10+ seconds

**AHA Music** (Chrome Extension)
- Browser extension for music recognition
- Works with any audio playing in browser

### 3. Manual Search Techniques

When automated recognition fails:

**Describe the melody:**
- Use "dun", "dee", "doo" to represent notes
- Indicate rhythm (fast/slow, pauses)
- Mention approximate pitch changes (up/down)

**Search by lyrics:**
- Type any words you remember
- Use quotes for exact phrases
- Add "lyrics" to search query

**Search by context:**
- Where did you hear it? (movie, ad, radio)
- Approximate era/genre
- Language of the song

---

## Response Format

### If User Hums/Describes Melody

```
🎵 I'll help you identify that song!

Here are the best options:

1️⃣ **SoundHound** (Best for humming)
   - Download: iOS/Android app store
   - Tap the orange button
   - Hum or sing for 10+ seconds

2️⃣ **Google Hum to Search**
   - Open Google app
   - Tap microphone → "Search a song"
   - Hum the melody

3️⃣ **Midomi** (Web-based)
   - Visit: midomi.com
   - Click "Click and Sing or Hum"
   - Allow microphone access

💡 **Tip:** Hum clearly for at least 10 seconds for best results.

Would you like me to help you describe the melody better for searching?
```

### If User Has Audio File

```
🎵 I can guide you through identifying the song from your audio file.

**Option 1: Use Your Phone**
- Play the audio on one device
- Open Shazam or SoundHound on another device
- Let it listen and identify

**Option 2: Online Tools**
- Upload to: https://www.midomi.com
- Or use AHA Music browser extension

**Option 3: Manual Description**
If the above doesn't work, you can:
- Describe the melody ("dun-dun-dun" style)
- Tell me any lyrics you remember
- Share where you heard it (movie, ad, etc.)
```

---

## Example Interactions

### Example 1: User Hums
```
User: dun dun dun dun dun dun dun

AI: 🎵 I see you're trying to hum a melody!

That rhythm pattern sounds familiar. To identify it:

1. Try **SoundHound** app - it's the best at recognizing hummed melodies
2. Or use **Google Hum to Search** in the Google app
3. You can also try **Midomi.com** on your computer

Would you like to:
- Describe the song more (genre, where you heard it)?
- Tell me any lyrics you remember?
- Get help with a specific recognition app?
```

### Example 2: User Has Recording
```
User: I have a recording of me humming a song, how do I find it?

AI: 🎵 Great! Here's how to identify it:

**Method 1: Two-Device Method**
- Play your recording on phone/computer #1
- Open **SoundHound** or **Shazam** on phone #2
- Let the app listen and identify

**Method 2: Upload to Midomi**
- Go to midomi.com on your computer
- You may be able to play the audio near your mic

**Method 3: Describe It**
If apps don't work, tell me:
- Any lyrics you remember (even just a few words)
- The genre/style (pop, rock, classical, etc.)
- Where you might have heard it

Which method would you like to try?
```

### Example 3: Partial Lyrics
```
User: I remember "something something love you" from the chorus

AI: 🎵 Let me help you find that song!

With partial lyrics like "...love you", here are some approaches:

1. **Search the lyrics directly:**
   - Google: "lyrics love you" + any other words you remember
   - Try Musixmatch app for lyrics search

2. **Add more context:**
   - Is it a male or female singer?
   - Approximate year/decade?
   - Genre (pop, rock, R&B, country)?
   - Fast or slow tempo?

3. **Describe the melody:**
   - Use "dun/da/dee" to show the rhythm
   - Example: "dun-da-dun-da-love-you"

Can you share any additional details?
```

---

## Tips for Better Recognition

### For Humming:
- Hum for at least 10 seconds
- Try to match the rhythm accurately
- Hum the most distinctive part (usually chorus)
- Avoid background noise

### For Describing:
- Focus on the chorus/hook
- Note the approximate tempo (fast/medium/slow)
- Mention any instruments you remember
- Describe the singer's voice (male/female, solo/group)

### Common Patterns:
- "Dun dun dun duuun" → Often Beethoven's 5th or similar
- "Doo doo doo doo doo" → Could be many songs, need more context
- "De-de-de-de-de" → Fast rhythm suggests dance/pop

---

## Limitations

- This skill provides guidance on using external tools
- Actual song recognition requires third-party apps/services
- Success rate varies based on humming accuracy and song popularity
- Some obscure or new songs may not be in recognition databases

---

## Technical Information

| Attribute | Value |
|-----------|-------|
| **Name** | Hum2Song |
| **Slug** | hum2song |
| **Version** | 2.0.0 |
| **Category** | Utility / Entertainment |
| **Tags** | music, song-recognition, humming, search |

---

## Related Skills

- `music-search` - General music search and discovery
- `lyrics-search` - Finding songs by lyrics

---

**Note:** This skill provides guidance and recommendations for music recognition. It does not perform audio analysis directly but directs users to appropriate tools and services.
