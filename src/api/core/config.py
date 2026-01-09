#src/api/core/config.py
from fastapi import APIRouter
from azure.identity.aio import DefaultAzureCredential
from azure.appconfiguration.provider.aio import load
from azure.appconfiguration.provider import AzureAppConfigurationKeyVaultOptions

router = APIRouter()
APP_CONFIG_ENDPOINT = "https://xappconfig.azconfig.io"

@router.get("/config.json")
async def get_widget_config():
    async with DefaultAzureCredential() as credential:
        kv_options = AzureAppConfigurationKeyVaultOptions(credential=credential)
        config = await load(
            endpoint=APP_CONFIG_ENDPOINT,
            credential=credential,
            key_vault_options=kv_options,
        )
        try:
            api_base = config.get("widget-api-base") or "https://chat.zenai.co.in"
            ttl = config.get("session-ttl-minutes") or 30
            return {"API_BASE": api_base, "SESSION_TTL": ttl}
        finally:
            await config.close()
