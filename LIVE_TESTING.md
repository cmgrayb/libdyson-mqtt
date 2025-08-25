# Live Device Testing Guide

This directory contains test scripts to validate the paho-mqtt 2.1.0 upgrade works with real Dyson devices.

## Prerequisites

1. **Dyson Device Setup**: Your Dyson device must be connected to WiFi and have MQTT enabled
2. **Network Access**: Your computer must be able to reach the device's IP address
3. **Device Credentials**: You need the MQTT username, password, and MQTT root topic

## Test Scripts

### 1. Simple Test (`simple_test.py`)
**Recommended for most users**

A user-friendly interactive test that validates the basic functionality:

```bash
python simple_test.py
```

The script will prompt you for:
- Device IP address (e.g., `192.168.1.100`)
- MQTT username 
- MQTT password
- MQTT root topic (e.g., `475`)

**What it tests:**
- ✅ Connection to device using paho-mqtt 2.1.0 
- ✅ VERSION2 callback API functionality
- ✅ Message publishing and receiving
- ✅ Automatic connection cleanup

### 2. Comprehensive Test (`test_live_device.py`)
**For thorough validation**

A detailed test suite that runs multiple scenarios:

```bash
python test_live_device.py --host 192.168.1.100 --username your_user --password your_pass --serial 475
```

**Options:**
- `--quick`: Run only basic connection test
- `--host`: Device IP address
- `--username`: MQTT username  
- `--password`: MQTT password
- `--serial`: MQTT root topic (e.g., '475')

**What it tests:**
- ✅ Basic connection establishment
- ✅ Message publishing and receiving
- ✅ VERSION2 callback API validation
- ✅ Stress testing with rapid connections
- ✅ Connection status monitoring
- ✅ Error handling

## Getting Device Information

### Finding Your Device IP
```bash
# On Windows
arp -a | findstr "dyson"

# On macOS/Linux
arp -a | grep -i dyson

# Or check your router's connected devices page
```

### Finding MQTT Credentials
The MQTT credentials are typically:
- **Username**: Often the device serial number or WiFi network name
- **Password**: Usually found on a sticker on the device or in the Dyson app
- **MQTT Root Topic**: Usually a 3-4 digit number like `475`, `527`, etc. (used as prefix for MQTT topics)

## Expected Output

### Successful Test Output
```
🎉 ALL TESTS PASSED - paho-mqtt 2.1.0 upgrade is working correctly with live device

📊 Test Results Summary
============================================================
test_1_basic_connection           ✅ PASSED
test_2_message_publishing         ✅ PASSED  
test_3_callback_api_validation    ✅ PASSED
test_4_stress_test               ✅ PASSED

Overall: 4/4 tests passed

📨 Message Summary: Received 3 messages
  1. 475/status/current: {"msg":"CURRENT-STATE","product-state":{"fmod":"FAN"...
  2. 475/status/connection: {"msg":"STATE-CHANGE","connected":true...
  3. 475/status/summary: {"msg":"ENVIRONMENTAL-CURRENT-SENSOR-DATA"...
```

### Common Issues

#### Connection Timeout
```
❌ Connection timeout
💡 Please check:
   - Device IP address is correct
   - Device is powered on and connected to WiFi
   - MQTT credentials are correct
   - Your computer can reach the device (try ping)
```

**Solutions:**
- Verify device IP with `ping <device_ip>`
- Check device is on and connected to same network
- Confirm MQTT credentials in Dyson app settings
- Try connecting directly via ethernet if WiFi is unstable

#### Authentication Failed
```
❌ Connection lost: Failed to connect to MQTT broker: Connection Refused: not authorised.
```

**Solutions:**
- Double-check MQTT username and password
- Ensure MQTT root topic matches device
- Some devices require the username to match the device's WiFi network name

#### No Messages Received
```
⚠️ Test 2 WARNING: No response received (device might be off/unresponsive)
```

**This is often normal:**
- Device might be in standby mode
- Some devices only respond to specific commands
- Connection was successful, device just didn't send data

## Troubleshooting

### Enable Debug Logging
Add this to the top of either test script:

```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

### Network Connectivity Check
```bash
# Test basic connectivity
ping <device_ip>

# Test MQTT port
telnet <device_ip> 1883
# or
nc -v <device_ip> 1883
```

### Manual MQTT Test
You can also test with a generic MQTT client:

```bash
# Install mosquitto client tools
# Windows: Download from https://mosquitto.org/download/
# macOS: brew install mosquitto  
# Ubuntu: apt-get install mosquitto-clients

# Test connection
mosquitto_sub -h <device_ip> -u <username> -P <password> -t "<serial>/status/+"
```

## What This Validates

These tests specifically validate that:

1. **paho-mqtt 2.1.0** works correctly (vs. older versions <2.0.0)
2. **VERSION2 callback API** functions properly (vs. deprecated VERSION1)
3. **Real-world connectivity** works (vs. mocked tests)
4. **Message handling** works with actual device protocols
5. **Connection management** is robust
6. **Error handling** works with real network conditions

## Support

If you encounter issues:

1. Run with `--quick` first to isolate connection problems
2. Check the troubleshooting section above  
3. Enable debug logging for detailed output
4. Verify basic network connectivity with ping/telnet
5. Test with generic MQTT tools to isolate libdyson-mqtt issues

The upgrade to paho-mqtt 2.1.0 with VERSION2 callbacks should be transparent to end users - if these tests pass, your Dyson integration will work correctly with the new library version.
