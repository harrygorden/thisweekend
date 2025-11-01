# Admin Access Setup Guide

## ✅ What Was Added

I've added a secure, password-protected admin link to the bottom of your MainApp form.

## 🔐 Features

- **🔒 Secure Login**: Password field is masked (type="password")
- **🛡️ Server-Side Verification**: Password is checked on the server, never exposed to client
- **🚫 Access Control**: Only users with the correct password can access AdminForm
- **💬 User-Friendly**: Clear error messages and prompts

## 📋 Setup Instructions

### Step 1: Set Your Admin Password

1. In Anvil editor, click **Settings** (gear icon)
2. Go to **Secrets** section
3. You should already have created a secret named **`ADMIN_PASSWORD`**
4. Set it to your desired admin password (e.g., `MySecurePassword123!`)

### Step 2: Pull Latest Code

1. Click **Version History** (clock icon)
2. Click **"Pull from origin"**
3. Wait for sync to complete

### Step 3: Open Forms in Designer

Since we modified `MainApp/form_template.yaml`, you need to refresh it:

1. **Close** the MainApp tab if it's open
2. **Click on MainApp** in the forms list to reopen it
3. You should see the new admin link at the bottom

### Step 4: Test It!

1. Click **Run** to launch your app
2. Scroll to the **bottom of the page**
3. You should see a small **"🔒 Admin"** link
4. Click it to test the password prompt

## 🎯 How It Works

### User Experience:

1. User clicks the **"Admin"** link at the bottom of MainApp
2. A password prompt appears:
   ```
   🔒 Admin Access
   [Enter admin password]
   [Login] [Cancel]
   ```
3. User enters password (masked with bullets: •••••)
4. If **correct**: Opens AdminForm
5. If **incorrect**: Shows "Access Denied" error

### Technical Flow:

```
MainApp (Client)
    ↓
admin_link_click() handler
    ↓
Shows password TextBox in alert
    ↓
Calls: anvil.server.call('check_admin_password', password)
    ↓
Server: admin_auth.py
    ↓
Retrieves: anvil.secrets.get_secret('ADMIN_PASSWORD')
    ↓
Compares: user_password == admin_password
    ↓
Returns: True/False
    ↓
If True: open_form(AdminForm())
If False: Shows error
```

## 📁 Files Created/Modified

### New File:
- **`server_code/admin_auth.py`** - Password verification module
  - `check_admin_password(password)` - Server function

### Modified Files:
- **`client_code/MainApp/__init__.py`**
  - Imported `AdminForm`
  - Added `admin_link_click()` event handler
  
- **`client_code/MainApp/form_template.yaml`**
  - Added footer panel with admin link

## 🔧 Customization

### Change Link Appearance

Edit in `form_template.yaml`:

```yaml
- type: Link
  properties:
    text: Admin        # Change text
    font_size: 12      # Change size
    foreground: '#999999'  # Change color
    icon: 'fa:lock'    # Change icon
```

### Change Link Position

Currently centered at bottom. To move:
- Change `align: center` to `align: left` or `align: right`
- Adjust `spacing_above: large` to control spacing

### Add More Security

Add IP restrictions in `admin_auth.py`:

```python
@anvil.server.callable
def check_admin_password(password):
    import anvil.http
    
    # Get client IP
    client_ip = anvil.http.request.origin
    
    # Only allow from certain IPs
    allowed_ips = ['192.168.1.100', '10.0.0.1']
    if client_ip not in allowed_ips:
        print(f"Access attempt from unauthorized IP: {client_ip}")
        return False
    
    # ... rest of password check
```

## 🎨 UI Preview

Bottom of MainApp will show:

```
┌─────────────────────────────────────────┐
│                                         │
│  [Event Cards Listed Above]             │
│                                         │
└─────────────────────────────────────────┘
              
              🔒 Admin
         (centered, small, gray)
```

When clicked:

```
┌────────────────────────────────┐
│      🔒 Admin Access           │
├────────────────────────────────┤
│                                │
│  Enter admin password:         │
│  [••••••••••••••]              │
│                                │
│  [Login]        [Cancel]       │
└────────────────────────────────┘
```

## 🚨 Security Best Practices

1. ✅ **Use a strong password** - Mix of letters, numbers, symbols
2. ✅ **Don't share the password** - Keep it confidential
3. ✅ **Change periodically** - Update password every 90 days
4. ✅ **Use Anvil secrets** - Never hardcode passwords in code
5. ✅ **Monitor access** - Check server logs for failed attempts

## 🐛 Troubleshooting

**Link doesn't appear:**
- Pull from GitHub
- Reopen MainApp in designer
- Check footer_panel is visible

**Password always fails:**
- Verify `ADMIN_PASSWORD` secret is set in Anvil
- Check for extra spaces in password
- Password is case-sensitive

**Error opening AdminForm:**
- Make sure AdminForm exists
- Check import statement in MainApp

**Can't find admin link:**
- Scroll to bottom of page
- It's a small gray link with lock icon
- Centered below all events

## ✨ Next Steps

Once working, you can:

1. **Add audit logging** - Track who accesses admin panel
2. **Add session timeout** - Auto-logout after inactivity
3. **Add 2FA** - Extra security with email codes
4. **Add user roles** - Different admin levels

Your admin access is now secure and ready to use! 🎉

