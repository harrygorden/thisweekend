"""Admin authentication for This Weekend app."""

import anvil.server
import anvil.secrets


@anvil.server.callable
def check_admin_password(password):
    """Verify admin password against stored secret.
    
    Args:
        password: Password to verify
        
    Returns:
        bool: True if password matches
    """
    try:
        admin_password = anvil.secrets.get_secret('ADMIN_PASSWORD')
        if not admin_password:
            print("Warning: ADMIN_PASSWORD secret not set")
            return False
        return password == admin_password
    except Exception as e:
        print(f"Admin auth error: {e}")
        return False

