"""
Vault management for ipscanner
Wrapper around Jeyriku Vault for credential management
"""

import os
from typing import Optional

try:
    from jeyriku_vault import VaultManager as JeyrikuVault
except ImportError:
    raise ImportError(
        "jeyriku-vault is required for credential management. "
        "Install it with: pip install git+http://jeysrv12:8090/jeyriku/jeyriku-vault.git"
    )


class VaultManager:
    """Manages credentials using Jeyriku Vault"""

    def __init__(self, vault_path: str = None):
        """
        Initialize vault manager and auto-unlock using JEYRIKU_VAULT_PASSWORD env var.

        Env vars:
            JEYRIKU_VAULT_PASSWORD: Master password to auto-unlock.
            JEYRIKU_VAULT_PATH:     Vault path (without extension).
            JEYRIKU_VAULT_BACKEND:  Backend type ('sqlcipher' or 'encrypted_file').
        """
        if vault_path is None:
            vault_path = os.environ.get('JEYRIKU_VAULT_PATH') or None

        backend = os.environ.get('JEYRIKU_VAULT_BACKEND', 'sqlcipher')
        self.vault = JeyrikuVault(vault_path=vault_path, backend=backend)
        password = os.environ.get('JEYRIKU_VAULT_PASSWORD')
        self.vault.unlock(password)

    def _get(self, service: str):
        return self.vault.get_credential(service)

    def get_secret_key(self) -> str:
        """Get Django secret key from vault (ipscanner service)."""
        try:
            cred = self._get("ipscanner")
            return cred.password or cred.token
        except Exception:
            # Fallback: try web_app service
            try:
                cred = self._get("web_app")
                return cred.password or cred.token
            except Exception:
                return None

    def lock(self):
        """Lock the vault"""
        self.vault.lock()

    def is_initialized(self) -> bool:
        """Check if vault is initialized"""
        return self.vault.is_initialized()


# Global vault instance
_vault_instance: Optional[VaultManager] = None


def get_vault() -> VaultManager:
    """Get or create the global vault instance."""
    global _vault_instance
    if _vault_instance is None:
        _vault_instance = VaultManager()
    return _vault_instance
