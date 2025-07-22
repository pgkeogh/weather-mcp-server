"""
Azure Key Vault service for secure API key retrieval.
Provides a clean abstraction over Azure Key Vault operations.
"""
# services/key_vault_service.py
import logging
from typing import Optional
import sys
from pathlib import Path
from azure.keyvault.secrets import SecretClient
from azure.identity import DefaultAzureCredential, ChainedTokenCredential, ManagedIdentityCredential, AzureCliCredential
from config.settings import Settings

# Add parent directory to path for settings import
# sys.path.append(str(Path(__file__).parent.parent))

logger = logging.getLogger(__name__)

class KeyVaultService:
    """Professional Key Vault service using settings configuration."""
    
    def __init__(self):
        # Validate required settings
        Settings.validate_required_settings()
        
        self.key_vault_name = Settings.KEY_VAULT_NAME
        self.key_vault_url = f"https://{self.key_vault_name}.vault.azure.net/"
        self._client: Optional[SecretClient] = None
        
    def _get_client(self) -> SecretClient:
        """Get authenticated Key Vault client with fallback credentials."""
        if self._client is None:
            try:
                # Use your Azure credential configuration
                credential = ChainedTokenCredential(
                    ManagedIdentityCredential(),
                    AzureCliCredential(),
                    DefaultAzureCredential(**Settings.get_azure_credential_config())
                )
                
                self._client = SecretClient(
                    vault_url=self.key_vault_url,
                    credential=credential
                )
                logger.info("Key Vault client initialized for vault: %s", self.key_vault_name)
                
            except Exception as e:
                logger.error("Failed to initialize Key Vault client: %s", e)
                raise
                
        return self._client
    
    async def get_secret(self, secret_name: str) -> str:
        """Retrieve secret from Key Vault."""
        try:
            client = self._get_client()
            secret = client.get_secret(secret_name)
            logger.info("Successfully retrieved secret: %s", secret_name)
            return secret.value
            
        except Exception as e:
            logger.error("Failed to retrieve secret %s: %s", secret_name, e)
            raise RuntimeError(f"Unable to retrieve secret {secret_name}") from e    
    def get_openweather_api_key(self) -> str:
        """Get the OpenWeatherMap API key."""
        return self.get_secret(Settings.OPENWEATHER_API_KEY_SECRET)
    
    def get_openai_api_key(self) -> str:
        """Get the OpenAI API key."""
        return self.get_secret(Settings.OPENAI_API_KEY_SECRET)