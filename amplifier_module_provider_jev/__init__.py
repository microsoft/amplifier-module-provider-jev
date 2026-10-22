"""Decision-only provider. Never inserted into an ordinary chat fallback chain."""
__amplifier_module_type__ = 'provider'

import os
import httpx


class JevProvider:
    name = 'jev'
    def __init__(self, api_key=None, config=None, *, client=None):
        self.config = config or {}
        self._api_key = api_key or self.config.get('api_key') or os.environ.get('TYPESAFE_API_KEY')
        self._client, self._owned_client = client, client is None

    @property
    def client(self):
        if self._client is None:
            self._client = httpx.AsyncClient(follow_redirects=False, trust_env=False)
        return self._client

    @staticmethod
    def get_info():
        from amplifier_core import ProviderInfo, ConfigField
        return ProviderInfo(id='jev', display_name='TypeSafe Jev', credential_env_vars=['TYPESAFE_API_KEY'],
                            capabilities=['decisions'], defaults={'chat_enabled': False}, config_fields=[
            ConfigField(id='api_key', display_name='API key', field_type='secret',
                        prompt='TypeSafe API key', env_var='TYPESAFE_API_KEY')])

    @staticmethod
    def get_decision_info():
        return {'schema_version': 1, 'provider': 'jev', 'available': True,
                'requires_explicit_enable': True, 'kinds': ['predicate', 'choice', 'score'],
                'images': False, 'models': ['jev-1.14.0', 'jev-latest'], 'configuration_key': 'decisions'}

    async def list_models(self):
        return []  # No chat models. Decision metadata is separate.

    def decision_backend(self, config, coordinator=None):
        from amplifier_decisions.config import endpoint
        from amplifier_decisions.runtime import SystemOneBackend, DecisionFailure
        from amplifier_decisions.response import read_json
        target = endpoint(config.get('endpoint') or self.config.get('base_url') or 'https://api.typesafe.ai/v1/systemone')
        async def send(content, timeout):
            if not self._api_key:
                raise DecisionFailure('unavailable', 'missing_credential')
            try:
                async with self.client.stream('POST', target, content=content, timeout=timeout,
                    headers={'Authorization': 'Bearer '+self._api_key, 'Content-Type': 'application/json'}) as response:
                    return await read_json(response)
            except httpx.TimeoutException:
                raise DecisionFailure('unavailable', 'timeout') from None
            except httpx.HTTPError:
                raise DecisionFailure('unavailable', 'transport_error') from None
        return SystemOneBackend('jev', config['model'], send, coordinator=coordinator)

    async def close(self):
        if self._owned_client and self._client is not None:
            await self._client.aclose()
            self._client = None


async def mount(coordinator, config=None):
    config = config or {}
    row = config.get('decisions') or {}
    if row.get('enabled') is not True:
        return None
    from amplifier_decisions.runtime import register
    from amplifier_decisions.config import configured_backends
    provider = JevProvider(config=config)
    removals = []
    try:
        for identity, row in configured_backends(config, 'jev-decisions').items():
            removals.append(register(coordinator, identity, provider.decision_backend(row, coordinator)))
    except Exception:
        for remove in removals: await remove()
        await provider.close()
        raise
    async def cleanup():
        for remove in removals: await remove()
        await provider.close()
    return cleanup
