# WSL Audio Fix Guide

**Problem:** Can't hear audio when running Liquid ASCII in WSL (Windows Subsystem for Linux).

**Cause:** WSL doesn't have native audio support - it can't directly access Windows audio hardware.

---

## 🎯 Quick Solutions (Choose One)

### Option 1: Use Windows PowerShell (Easiest) ⭐

**Just run the project directly in Windows - no WSL needed!**

```powershell
# In Windows PowerShell (not WSL)
cd path\to\liquid-ascii
.\scripts\dev.ps1 setup
.\scripts\dev.ps1 run --speak "Audio works in Windows!"
```

**Why this works:** Runs natively on Windows, has direct audio access.

---

### Option 2: Use WSLg (Easy - Windows 11 Only)

**If you have Windows 11 and WSL2, audio might already work!**

```bash
# In WSL
# Update WSL to latest version
wsl --update

# Install audio tools
sudo apt update
sudo apt install pulseaudio alsa-utils

# Test it
./dev.sh run --speak "Testing WSLg audio"
```

**Requirements:** Windows 11 + WSL2 with WSLg support.

---

### Option 3: PulseAudio Bridge (Medium - Works on Windows 10/11)

**Create a bridge between WSL and Windows audio.**

#### Automated Setup (Recommended)

**Step 1: Setup Windows (in PowerShell)**

```powershell
# In Windows PowerShell - NOT in WSL!
cd path\to\liquid-ascii
.\scripts\setup_windows_audio_for_wsl.ps1
```

This script will:
- ✓ Install PulseAudio for Windows
- ✓ Configure it for WSL access
- ✓ Start the audio server

**Step 2: Setup WSL**

```bash
# In WSL terminal
cd /path/to/liquid-ascii
./scripts/fix_wsl_audio.sh
```

This script will:
- ✓ Install PulseAudio client tools
- ✓ Configure environment variables
- ✓ Connect to Windows audio server

**Step 3: Restart and Test**

```bash
# Close and reopen WSL terminal
./dev.sh run --speak "Testing audio bridge!"
```

#### Manual Setup (If scripts don't work)

<details>
<summary>Click to expand manual setup instructions</summary>

**Windows Side:**

1. **Install PulseAudio for Windows**
   ```powershell
   # Option A: Using winget
   winget install --id=PulseAudio.PulseAudio -e

   # Option B: Manual download
   # Visit: https://www.freedesktop.org/wiki/Software/PulseAudio/Ports/Windows/Support/
   # Download and extract to C:\PulseAudio
   ```

2. **Configure PulseAudio**

   Create file: `C:\PulseAudio\etc\pulse\default.pa`
   ```
   load-module module-native-protocol-tcp auth-ip-acl=127.0.0.1;172.16.0.0/12
   load-module module-esound-protocol-tcp auth-ip-acl=127.0.0.0/8
   load-module module-waveout sink_name=output source_name=input record=0
   ```

3. **Start PulseAudio**
   ```powershell
   cd C:\PulseAudio\bin
   .\pulseaudio.exe
   ```

**WSL Side:**

1. **Install PulseAudio client**
   ```bash
   sudo apt update
   sudo apt install pulseaudio pulseaudio-utils alsa-utils
   ```

2. **Configure environment**
   ```bash
   # Add to ~/.bashrc
   export HOST_IP=$(cat /etc/resolv.conf | grep nameserver | awk '{print $2}')
   export PULSE_SERVER=tcp:$HOST_IP
   ```

3. **Reload configuration**
   ```bash
   source ~/.bashrc
   ```

4. **Test**
   ```bash
   # Test audio system
   speaker-test -c 2 -t wav -D pulse

   # Test Liquid ASCII
   ./dev.sh run --speak "Testing audio"
   ```

</details>

---

## 🧪 Testing Audio

### Test 1: Check Audio System

```bash
# In WSL
speaker-test -c 2 -t wav -D pulse
```

You should hear white noise. Press Ctrl+C to stop.

### Test 2: Test Liquid ASCII

```bash
./dev.sh run --speak "Hello from WSL with audio!"
```

You should see the animated head AND hear the speech.

### Test 3: Check Devices

```bash
python -c "import sounddevice; print(sounddevice.query_devices())"
```

Should list available audio devices.

---

## 🔧 Troubleshooting

### Issue: "No audio output"

**Check Windows PulseAudio is running:**

```powershell
# In PowerShell
Get-Process pulseaudio
```

If not running:
```powershell
cd C:\PulseAudio\bin
.\pulseaudio.exe
```

**Check WSL can connect:**

```bash
# In WSL
echo $PULSE_SERVER  # Should show tcp:172.x.x.x
echo $HOST_IP       # Should show 172.x.x.x
```

If empty:
```bash
export HOST_IP=$(cat /etc/resolv.conf | grep nameserver | awk '{print $2}')
export PULSE_SERVER=tcp:$HOST_IP
```

### Issue: "Connection refused"

**Check Windows Firewall:**

1. Open Windows Defender Firewall
2. Click "Allow an app through firewall"
3. Find "pulseaudio.exe"
4. Allow both Private and Public networks

**Try alternate port:**

```bash
export PULSE_SERVER=tcp:$HOST_IP:4713
```

### Issue: "No module named sounddevice"

```bash
./dev.sh install  # Reinstall dependencies
```

### Issue: "PortAudio not found"

```bash
sudo apt install portaudio19-dev python3-dev
./dev.sh update
```

### Issue: Audio is choppy/delayed

**Adjust buffer settings in `~/.pulse/daemon.conf`:**

```bash
mkdir -p ~/.pulse
cat > ~/.pulse/daemon.conf << EOF
default-fragments = 5
default-fragment-size-msec = 2
EOF
```

Then restart:
```bash
pulseaudio --kill
# PulseAudio will auto-restart
```

### Issue: "Still no sound!"

Try restarting everything:

```powershell
# In Windows PowerShell
Stop-Process -Name pulseaudio
cd C:\PulseAudio\bin
.\pulseaudio.exe
```

```bash
# In WSL - close and reopen terminal
./dev.sh run --speak "Testing again"
```

---

## 🚀 Make PulseAudio Start Automatically (Optional)

**To start PulseAudio when Windows boots:**

1. Press `Win + R`
2. Type: `shell:startup`
3. Press Enter
4. Create a shortcut:
   - Right-click → New → Shortcut
   - Target: `C:\PulseAudio\bin\pulseaudio.exe`
   - Name: "PulseAudio Server"

Now PulseAudio starts automatically when you log into Windows.

---

## 📊 Comparison of Solutions

| Solution | Difficulty | Compatibility | Quality |
|----------|-----------|---------------|---------|
| **Windows PowerShell** | ⭐ Easy | All Windows | Perfect |
| **WSLg** | ⭐⭐ Medium | Win 11 + WSL2 | Perfect |
| **PulseAudio Bridge** | ⭐⭐⭐ Hard | Win 10/11 | Good |

**Recommendation:**
- **For most users:** Use Windows PowerShell (easiest, always works)
- **For Windows 11 users:** Try WSLg first (built-in)
- **For WSL enthusiasts:** Use PulseAudio bridge (more setup)

---

## 💡 Best Practices

### Use Windows for Audio Tasks

```powershell
# In Windows PowerShell
.\scripts\dev.ps1 run --speak "Your text"
.\scripts\dev.ps1 voices
```

### Use WSL for Development

```bash
# In WSL
./dev.sh test        # Run tests
./dev.sh status      # Check status
./dev.sh update      # Update dependencies
```

### Hybrid Approach

- **Development:** Use WSL (better Linux tools, faster)
- **Audio/TTS:** Switch to Windows PowerShell when needed
- **Testing:** Use Windows for full integration tests

---

## 🆘 Still Having Issues?

1. **Check environment:**
   ```bash
   ./dev.sh status
   ```

2. **View detailed logs:**
   ```bash
   ./dev.sh logs
   ```

3. **Try the simpler solution:**
   ```powershell
   # Just use Windows!
   .\scripts\dev.ps1 run --speak "This works!"
   ```

4. **Ask for help:**
   - Include output of `./dev.sh status`
   - Include output of `echo $PULSE_SERVER`
   - Mention your Windows version (10 or 11)
   - Mention your WSL version (WSL1 or WSL2)

---

## 📚 Additional Resources

- [WSL Audio Guide](https://github.com/microsoft/WSL/issues/4856)
- [PulseAudio Windows](https://www.freedesktop.org/wiki/Software/PulseAudio/Ports/Windows/)
- [WSLg Documentation](https://github.com/microsoft/wslg)

---

**Remember:** If WSL audio is too complicated, just use Windows PowerShell directly! The project works perfectly in native Windows. 🎉
