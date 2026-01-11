# 🔊 WSL Audio Issue - Quick Fix

**You're running in WSL and can't hear audio?** This is normal - WSL doesn't support audio by default.

---

## ⚡ Quick Solutions

### 1. Use Windows PowerShell (Easiest) ⭐

**Forget WSL for audio - just run in Windows!**

```powershell
# Open Windows PowerShell
# Navigate to project (Windows path)
cd C:\path\to\liquid-ascii

# Run it
.\scripts\dev.ps1 setup
.\scripts\dev.ps1 run --speak "Audio works in Windows!"
```

**Done!** This works immediately, no configuration needed.

---

### 2. Fix WSL Audio (More Complex)

If you really want audio in WSL:

**Step 1: In Windows PowerShell**
```powershell
cd C:\path\to\liquid-ascii
.\scripts\setup_windows_audio_for_wsl.ps1
```

**Step 2: In WSL**
```bash
cd /path/to/liquid-ascii
./scripts/fix_wsl_audio.sh
```

**Step 3: Restart WSL terminal and test**
```bash
./dev.sh run --speak "Testing WSL audio!"
```

**Full guide:** [docs/WSL_AUDIO_FIX.md](docs/WSL_AUDIO_FIX.md)

---

### 3. Use WSL Without Audio

WSL works great for development, just no audio:

```bash
# All these work fine in WSL:
./dev.sh setup              # Setup environment
./dev.sh test               # Run tests
./dev.sh run --static       # Show visual only
./dev.sh status             # Check status
./dev.sh update             # Update packages

# For audio features, switch to Windows:
# (Open PowerShell)
.\scripts\dev.ps1 run --speak "Your text"
```

---

## 🎯 Recommended Workflow

**Best of both worlds:**

1. **Use WSL for development:**
   - Writing code
   - Running tests
   - Git operations
   - Package management

2. **Use Windows for audio:**
   - TTS demos
   - Full integration tests
   - Showing off the project

---

## 🆘 Still Stuck?

```bash
# Check if you're in WSL
uname -a  # Should show "Microsoft" if WSL

# Check environment
./dev.sh status

# See detailed guide
cat docs/WSL_AUDIO_FIX.md

# Or just use Windows!
# Exit WSL, open PowerShell:
.\scripts\dev.ps1 run --speak "Problem solved!"
```

---

## 📋 Quick Command Reference

### In WSL (No Audio)
```bash
./dev.sh setup          # Setup
./dev.sh test           # Tests
./dev.sh run --static   # Visual demo
```

### In Windows PowerShell (With Audio)
```powershell
.\scripts\dev.ps1 setup             # Setup
.\scripts\dev.ps1 run --speak "Hi"  # TTS demo
.\scripts\dev.ps1 voices            # List voices
```

---

**Bottom line:** WSL is great for development, but for audio features just use Windows PowerShell. It's easier! 🎉
