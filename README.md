# TypeSafe Jev provider

**Status: experimental.** Interfaces may change. See [SUPPORT.md](SUPPORT.md) for the support policy.

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

## Contributing

Most contributions require you to agree to a
Contributor License Agreement (CLA) declaring that you have the right to, and actually do, grant us
the rights to use your contribution. For details, visit [Contributor License Agreements](https://cla.opensource.microsoft.com).

When you submit a pull request, a CLA bot will automatically determine whether you need to provide
a CLA and decorate the PR appropriately (e.g., status check, comment). Simply follow the instructions
provided by the bot. You will only need to do this once across all repos using our CLA.

This project has adopted the [Microsoft Open Source Code of Conduct](https://opensource.microsoft.com/codeofconduct/).
For more information see the [Code of Conduct FAQ](https://opensource.microsoft.com/codeofconduct/faq/) or
contact [opencode@microsoft.com](mailto:opencode@microsoft.com) with any additional questions or comments.

## Trademarks

This project may contain trademarks or logos for projects, products, or services. Authorized use of Microsoft
trademarks or logos is subject to and must follow
[Microsoft's Trademark & Brand Guidelines](https://www.microsoft.com/legal/intellectualproperty/trademarks/usage/general).
Use of Microsoft trademarks or logos in modified versions of this project must not cause confusion or imply Microsoft sponsorship.
Any use of third-party trademarks or logos are subject to those third-party's policies.
