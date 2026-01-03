# Android Simulator App (Demo)

This folder contains a simple Python (Kivy) Android simulator app that sends UDP
payloads to the `altrus run` scanner. Each button starts a loop that sends normal
payloads for 5 seconds, then anomaly payloads continuously until you press **Stop**.

## What it does

- Buttons: Tachycardia, Bradycardia, Fever, Heart Attack, Cardiac Arrest
- Each button starts a loop (0.5s interval) sending UDP JSON data
- The last payload is shown in the UI
- Stop button halts the loop

## Build APK (step-by-step)

> This uses **buildozer** (Python tool for packaging Kivy apps). You can run this
> on Linux or Windows (via WSL). Buildozer is simplest on Linux.

### 1) Install build dependencies

**Ubuntu / WSL**:

```bash
sudo apt update
sudo apt install -y python3-pip git zip unzip openjdk-17-jdk
pip install --user buildozer
```

### 2) Build the APK

```bash
cd android_app
buildozer android debug
```

The APK will be generated at:

```
android_app/bin/*.apk
```

### 3) Copy APK to your phone

- Transfer the APK to your Android device
- Enable “Install unknown apps” in Android settings
- Install and open the app

## Using the app

1. Start scanner on your PC:
   ```bash
   altrus run --host 0.0.0.0 --port 5055
   ```
2. Enter the PC IP and port in the app
3. Press a simulator button
4. Watch `altrus run` output
5. Press **Stop** to end the loop

## Notes

- The app sends **UDP** packets only (fast and simple)
- Ensure phone and PC are on the same Wi‑Fi network
- Open port 5055 in Windows firewall if needed
