# TypeSafe Jev provider

This optional Amplifier provider exposes Jev decisions using a saved provider
account. It has no chat models and never enters the ordinary chat fallback chain.
Keep an ordinary chat provider configured. No decision call occurs until both
the provider and a consumer explicitly enable it.

```yaml
providers:
  - module: provider-jev
    source: git+https://github.com/microsoft/amplifier-module-provider-jev@main
    config:
      chat_enabled: false
      api_key: ${TYPESAFE_API_KEY}
      decisions:
        enabled: true
        backends:
          jev-ui:
            enabled: true
            model: jev-1.14.0
```

The host expands credential references from its private settings. The provider
also supports `TYPESAFE_API_KEY` directly. Multiple backend IDs share the account.
An optional account `base_url` or decision `endpoint` sets an HTTPS service URL;
otherwise it uses `https://api.typesafe.ai/v1/systemone`. Endpoints containing
credentials, fragments or query strings are rejected.

The shared `amplifier-lib-decisions` contract normalizes predicate, fixed choice
and ordinal score answers. This provider owns HTTP transport and credential use.
Requests have bounded time/body sizes, no automatic retries or redirects, and
redacted errors. Cancellation propagates. Images and Box execution are disabled.

UI use binds `selection.browser` or `selection.computer` to
`{mode: decision, backend: jev-ui, allow_external_state: true}`. The ordinary
model remains the default and the configured fallback. Consent to transfer an
observation does not approve an action on a browser or desktop.

The shared library is a branch-tracking dependency on its canonical Git repository.
For direct installation into a host-managed Python environment:

```sh
uv pip install 'amplifier-module-provider-jev @ git+https://github.com/microsoft/amplifier-module-provider-jev@main'
```

Hosts should record installed revisions and qualify updates before activation.
Run `pytest` with the `test` extra for offline transport/lifecycle tests.
Wire reference: [TypeSafe API](https://docs.typesafe.ai/api).
