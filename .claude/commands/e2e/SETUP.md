# E2E Testing Setup Requirements

## Prerequisites for Browser Automation

E2E tests use Playwright for browser automation, which requires system-level dependencies to run browsers in WSL or Linux environments.

### Required System Dependencies

- `libnspr4` - Netscape Portable Runtime
- `libnss3` - Network Security Service libraries
- `libasound2t64` - ALSA sound library
- Additional libraries for full browser support

### Installation

#### Quick Setup (Recommended)

Run the provided setup script:

```bash
./scripts/setup_playwright.sh
```

This script will:
1. Install all required system dependencies
2. Install Playwright browsers (Chromium)

**Note**: This script requires `sudo` access to install system packages.

#### Manual Installation

If you prefer to install dependencies manually:

```bash
# Update package list
sudo apt-get update

# Install core dependencies
sudo apt-get install -y libnspr4 libnss3 libasound2t64

# Install additional browser dependencies
sudo apt-get install -y libatk1.0-0 libatk-bridge2.0-0 libcups2 libdrm2 \
    libxkbcommon0 libxcomposite1 libxdamage1 libxfixes3 libxrandr2 \
    libgbm1 libpango-1.0-0 libcairo2

# Install Playwright browsers
playwright install chromium
```

## Troubleshooting

### "Host system is missing dependencies" Error

If you see this error when running E2E tests:

```
Host system is missing dependencies to run browsers.
Please install them with the following command:
    sudo playwright install-deps
```

This means the system dependencies are not installed. Run `./scripts/setup_playwright.sh` or follow the manual installation steps above.

### Permission Issues

If you don't have `sudo` access:
- Contact your system administrator to install the dependencies
- Use the API-based testing alternative (see below)
- Run tests in a Docker container with dependencies pre-installed

### Alternative: API-Based Testing

If you cannot install browser dependencies, you can validate functionality using API-based tests:

```bash
# This tests the same functionality without browser automation
python test_sql_injection_api.py
```

Note: API tests validate the backend protection but don't test the full user interface flow.

## Verifying Setup

After installation, verify Playwright is working:

```bash
# Check installed browsers
playwright install --help

# Test browser launch (should not show dependency errors)
playwright codegen http://localhost:5173
```

## WSL-Specific Notes

- WSL 2 is recommended over WSL 1 for better Linux compatibility
- X11 forwarding is not required for headed mode in WSL 2
- Some features may require WSLg (GUI support in WSL 2)
