"""
Admin Authentication Module

Handles password verification for admin access.
"""

import anvil.server
import anvil.secrets


@anvil.server.callable
def check_admin_password(password):
    """
    Check if the provided password matches the admin password.
    
    Args:
        password: Password provided by user
        
    Returns:
        bool: True if password matches, False otherwise
    """
    try:
        admin_password = anvil.secrets.get_secret('ADMIN_PASSWORD')
        
        if not admin_password:
            print("Warning: ADMIN_PASSWORD secret is not set!")
            return False
        
        return password == admin_password
    
    except Exception as e:
        print(f"Error checking admin password: {e}")
        return False

