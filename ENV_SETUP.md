# Environment Variables Setup Guide

This guide explains how to configure the `.env` file for the Policy Navigator Agent.

---

## Quick Setup

Create a file named `.env` in the project root directory and add the following:

```env
AIXPLAIN_API_KEY=ada6267c2fbef32d4178f00df6462c7b1558d161790894ce51725f62309b3aa3
```

That's it! This is the only required variable to run the application.

---

## Complete .env File Template

For a full configuration with all optional settings, copy this:

```env
# ============================================
# REQUIRED: aiXplain API Configuration
# ============================================
# Your aiXplain API key from https://platform.aixplain.com/api-keys
AIXPLAIN_API_KEY=ada6267c2fbef32d4178f00df6462c7b1558d161790894ce51725f62309b3aa3

# ============================================
# OPTIONAL: Flask Configuration
# ============================================
# Port for the web server (default: 5000)
# PORT=5000

# Enable debug mode (default: True)
# DEBUG=True

# ============================================
# OPTIONAL: External API Keys
# ============================================
# Federal Register API (no key required, but can be added for rate limit increases)
# FEDERAL_REGISTER_API_KEY=your_key_here

# CourtListener API for case law (future integration)
# COURTLISTENER_API_KEY=your_key_here

# ============================================
# OPTIONAL: Notification Integration
# ============================================
# Slack webhook for notifications
# SLACK_WEBHOOK_URL=https://hooks.slack.com/services/YOUR/WEBHOOK/URL

# Slack bot token for advanced integrations
# SLACK_BOT_TOKEN=xoxb-your-bot-token
```

---

## Step-by-Step Instructions

### 1. Create the .env file

**On Linux/Mac:**
```bash
cd policy-navigator-agent
touch .env
nano .env
```

**On Windows:**
```cmd
cd policy-navigator-agent
notepad .env
```

### 2. Add your API key

Copy and paste this line into the file:

```env
AIXPLAIN_API_KEY=ada6267c2fbef32d4178f00df6462c7b1558d161790894ce51725f62309b3aa3
```

### 3. Save the file

- **nano:** Press `Ctrl+X`, then `Y`, then `Enter`
- **notepad:** Click File → Save

### 4. Verify the file

```bash
cat .env
```

You should see:
```
AIXPLAIN_API_KEY=ada6267c2fbef32d4178f00df6462c7b1558d161790894ce51725f62309b3aa3
```

---

## How to Get Your Own API Key

If you need to generate a new API key:

1. Go to https://platform.aixplain.com/login
2. Log in with your credentials:
   - Email: `omar.qasem@menadevs.io`
   - Password: `GAj8qtK6g.X2mLn`
3. Click on your profile icon (top right)
4. Select "API Keys" or go to https://platform.aixplain.com/api-keys
5. Click "Manage" next to an existing key, or "Create New Key"
6. Copy the full key (not the masked version)
7. Paste it into your `.env` file

---

## Security Notes

⚠️ **IMPORTANT:**

- **Never commit `.env` to git** - It's already in `.gitignore`
- **Never share your API key publicly** - It gives full access to your aiXplain account
- **Rotate keys regularly** - Generate new keys periodically for security
- **Use different keys for dev/prod** - Create separate keys for different environments

---

## Troubleshooting

### Error: "AIXPLAIN_API_KEY not found"

**Problem:** The application can't find your API key.

**Solution:**
1. Make sure the file is named exactly `.env` (with the dot at the start)
2. Make sure it's in the project root directory (same level as `README.md`)
3. Check for typos in the variable name (must be `AIXPLAIN_API_KEY`)
4. Make sure there are no spaces around the `=` sign

### Error: "API key is not valid"

**Problem:** The API key is incorrect or expired.

**Solution:**
1. Copy the full key from the aiXplain platform (not the masked version)
2. Make sure there are no extra spaces or line breaks
3. Generate a new key if the old one has been revoked

### The .env file is not being read

**Problem:** Environment variables are not loading.

**Solution:**
1. Make sure `python-dotenv` is installed: `pip3 install python-dotenv`
2. Check that the code includes: `from dotenv import load_dotenv` and `load_dotenv()`
3. Try restarting the application

---

## Example: Complete Working .env File

Here's a real example that will work immediately:

```env
AIXPLAIN_API_KEY=ada6267c2fbef32d4178f00df6462c7b1558d161790894ce51725f62309b3aa3
PORT=5000
DEBUG=True
```

This configuration:
- ✅ Sets the aiXplain API key
- ✅ Runs the web server on port 5000
- ✅ Enables debug mode for development

---

## Testing Your Configuration

After creating the `.env` file, test it:

```bash
# Test 1: Check if the file exists
ls -la .env

# Test 2: View the contents (be careful not to share this output!)
cat .env

# Test 3: Run the agent builder to verify API key works
python3 src/agents/build_agents.py

# Test 4: Start the web demo
cd demo
python3 app.py
```

If everything is configured correctly, you should see:
```
============================================================
Policy Navigator Agent - Web Demo
============================================================
Server starting on http://localhost:5000
Debug mode: True
============================================================
```

---

## Need Help?

If you're still having issues:

1. Check the [SETUP_GUIDE.md](SETUP_GUIDE.md) for detailed setup instructions
2. Review the [AIXPLAIN_TECHNICAL_DOCUMENTATION.md](AIXPLAIN_TECHNICAL_DOCUMENTATION.md) for technical details
3. Open an issue on GitHub: https://github.com/omar-qasem/policy-navigator-agent/issues

---

**Last Updated:** October 31, 2025
