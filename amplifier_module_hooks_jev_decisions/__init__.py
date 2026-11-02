"""Optional Jev decisions through the supported Amplifier hook lifecycle."""
from amplifier_decisions.hooks import mount_account
from amplifier_module_provider_jev import JevProvider

__amplifier_module_type__ = 'hook'


async def mount(coordinator, config=None):
    return await mount_account(coordinator, config, provider_factory=JevProvider,
                               default_id='jev-decisions', hook_module='hooks-jev-decisions')
