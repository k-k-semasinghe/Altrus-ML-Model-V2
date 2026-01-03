# Mobile Web Simulator (Browser)

This folder contains a mobile-friendly web page that sends simulation payloads to
`altrus run`. Because browsers cannot send UDP directly, the page sends HTTP requests
to a tiny relay server, and the relay forwards them to UDP.

## 1) Start the relay server (on your PC)

```bash
python mobile_web/relay_server.py
```

This listens on:

```
http://<PC-IP>:8080/send
```

## 2) Start the Altrus scanner

```bash
altrus run --host 0.0.0.0 --port 5055
```

## 3) Open the mobile web UI

- Copy `mobile_web/index.html` to your phone or open it with any local file viewer.
- Update the **Relay URL** to match your PC IP, e.g.:
  `http://192.168.1.45:8080/send`
- Update the **UDP Host** to your PC IP and port (default 5055).
- Tap any simulation button to start sending data every 0.5s.
- Tap **Stop** to stop the loop.

## Notes

- Phone and PC must be on the same Wi‑Fi network.
- Windows firewall must allow port 8080 (HTTP) and 5055 (UDP).
- The payload being sent is shown on the page.
