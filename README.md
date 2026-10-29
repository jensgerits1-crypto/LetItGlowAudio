# Let It Glow Audio — FPP 10.3 LAN test (v0.2)

**Experimental; not tested on a Raspberry Pi/FPP. Back up FPP first.**

## What it does
- Reads `http://127.0.0.1/api/fppd/status` every 1.2 seconds.
- Detects a current `mediaName`, looks for the matching file in `/home/fpp/media/music`.
- Serves that file using HTTP byte ranges to smartphones on the same LAN.
- The visitor taps Start once; browser seeks to FPP's reported elapsed time.
- No internet needed **during playback**. Installation from GitHub requires internet.
- No soundcard required. Does not alter FPP's audio or network settings.

## Important limitations
- This is **not a continuous live capture stream**; it is synchronized file playback.
- Browser autoplay, phone sleep, Bluetooth and Wi-Fi latency may cause noticeable sync drift.
- FPP 10.3 API status fields may differ; test with `/api/status` and report output if media is missing.
- A few phones may work; many simultaneous visitors have not been load-tested.
- Audio is served unencrypted to anyone on the same LAN. Use a dedicated visitor Wi-Fi/VLAN only if clients can reach FPP and are restricted from FPP admin pages.
- Do not expose port 8098 to the internet. Music copyright/public performance permissions remain your responsibility.

## Install through FPP Plugin Manager
1. Create your own **public GitHub repository** named `LetItGlowAudio` and upload **the contents of this ZIP** to its root (not a nested folder).
2. Edit `pluginInfo.json`: replace `REPLACE_WITH_YOUR_USERNAME` in `srcURL` and `homeURL` with your GitHub username. Branch must be `main`.
3. In FPP v10.3 enable **Developer UI** under FPP Settings → UI.
4. Go to Content Setup → Plugin Manager; paste `https://github.com/YOUR_USERNAME/LetItGlowAudio` into the search field. Install the plugin.
5. From a phone on the same Wi-Fi open `http://192.168.100.157:8098` (if the FPP address has not changed).
6. Start a sequence with an attached MP3 and tap **Start luisteren**.
7. For diagnostics open `http://192.168.100.157:8098/api/status`. If media is null, FPP status shape or media folder needs adjustment.

## Rollback
Uninstall from FPP Plugin Manager. The uninstall script stops and removes only the Let It Glow service.

## Optional local standalone smoke test (not FPP integration)
Run `python3 server.py` on a computer. Status will report FPP API unavailable unless configured.

## Safety
Installer creates only a systemd service on port 8098, does not run package managers, and does not modify existing FPP network/audio configurations. `sudo` privileges are needed for service installation.
