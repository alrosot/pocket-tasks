# RaspberryPi Deployment Guide

This document explains how to deploy Pocket Tasks to a RaspberryPi with an e-paper display.

## Current State

The application currently supports:
- **Development**: `make test-emulator` - pygame emulator window on Mac
- **Fallback**: dummy device (no visual output, runs silently)

## Deploying to RaspberryPi

### Step 1: Identify Your E-Paper Display

Common Waveshare e-paper displays:
- **2.13" Touch Display**: `epd2in13_V4`
- **2.9" Display**: `epd2in9`
- **4.2" Display**: `epd4in2`
- **7.5" Display**: `epd7in5`

Check your display specifications or the documentation included with your HAT.

### Step 2: Update Device Initialization

Edit `src/app.py` and find the `get_device()` function (around line 84-96).

Replace the commented-out hardware initialization section with your display model:

```python
else:
    # Try to initialize actual hardware device (for RaspberryPi)
    try:
        # Import and initialize your e-paper display
        from waveshare_epd import epd2in13_V4  # Replace with your model
        device = epd2in13_V4.EPD()
        device.init()
        device.clear()
        return device
    except ImportError:
        # Fallback to dummy device for development
        from luma.core.device import dummy
        return dummy(width=width, height=height)
```

### Step 3: Install Dependencies on RaspberryPi

1. Update `requirements.txt` to include the waveshare driver:

```bash
pip install waveshare-epd
```

Or add to `requirements.txt`:
```
waveshare-epd==4.0.0
```

2. Install production dependencies:

```bash
make install
```

### Step 4: Deploy and Run

On the RaspberryPi, run the application:

```bash
python3 src/app.py
```

Or to run in the background:

```bash
nohup python3 src/app.py > /tmp/pocket-tasks.log 2>&1 &
```

## Testing Before Full Deployment

1. **Test locally with emulator** (development machine):
   ```bash
   make test-emulator
   ```

2. **Test on RaspberryPi without hardware** (to verify code logic):
   ```bash
   python3 src/app.py
   ```
   This will use the dummy device and run silently without visual output.

3. **Test with actual hardware** (once configured):
   ```bash
   python3 src/app.py
   ```
   The display should update and show the home screen.

## Troubleshooting

### Display not showing anything
- Check that your display model is correctly specified
- Verify the e-paper HAT is properly connected
- Check GPIO pins are not being used by other services

### ImportError: No module named waveshare_epd
- Install: `pip install waveshare-epd`
- May need to use repository version on some RaspberryPi configurations

### Permission errors
- The GPIO interface may require root privileges
- Run with: `sudo python3 src/app.py`

## Notes

- The `LUMA_EMULATOR` environment variable is automatically ignored on RaspberryPi
- Always test with `make test-emulator` on your development machine first
- The dummy device fallback ensures the app won't crash if hardware is unavailable
- Touch events are already implemented in the `handle_touch()` method and will work with compatible displays

## References

- [Waveshare E-Paper GitHub](https://github.com/waveshare/e-Paper)
- [RaspberryPi GPIO Documentation](https://www.raspberrypi.com/documentation/computers/gpio.html)
