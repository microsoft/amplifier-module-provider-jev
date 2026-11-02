# TypeSafe Jev provider

**Status: experimental.** Interfaces may change. See [SUPPORT.md](SUPPORT.md) for the support policy.

This optional package exposes Jev decisions through a genuine Amplifier hook
module. It has no chat models and never enters the ordinary chat fallback chain.
Keep an ordinary chat provider configured. No decision call occurs until both
the account and a consumer explicitly enable it. The hook and account metadata
ship in the same wheel; no separate credential store is introduced.

```yaml
hooks:
  - module: hooks-jev-decisions
    source: git+https://github.com/microsoft/amplifier-module-provider-jev@main
    config:
      api_key: ${TYPESAFE_API_KEY}
      decisions:
        enabled: true
        backends:
          jev-ui:
            enabled: true
            model: jev-1.14.0
```

A host that supports credential references may expand them in the hook config.
For other hosts, omit `api_key` and set `TYPESAFE_API_KEY` in the process environment. Multiple backend IDs share the account.
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

## Hook lifecycle and saved accounts

The direct `hooks:` composition above uses Core's existing hook contract. The
wheel contains both `provider-jev` for account metadata and the separate
`hooks-jev-decisions` runtime package, declared with module type `hook`.
It requires the shared library revision providing
`amplifier_decisions.hooks.mount_account`; qualify these dependency revisions
together. Installing a key or package alone never selects a decision model.

| Composition on Core 2.0.2 | Result |
| --- | --- |
| Genuine hook, decisions enabled | Registers only named decision backends; teardown removes and closes them. |
| Genuine hook, decisions disabled | No account transport or backend is created. |
| Direct `provider-jev` row, enabled or disabled | Unsupported: Core requires a chat provider mount. Do not depend on residual capability state after rejection. |
| Saved logical provider account in a host with the decision-account adapter | Host resolves that account's existing auth and exact source, then projects the genuine hook for this runtime. |

Unified's saved-account projection is a host integration, not a Core feature or
an automatic behavior of every CLI/host. Other hosts can use the direct hook
example. Ordinary chat providers remain strict, and omitting these hooks leaves
ordinary execution unchanged. The earlier proposed capability-only Core change
([Core #124](https://github.com/microsoft/amplifier-core/pull/124)) is not required
by this hook implementation and is not claimed to be implemented.

Account mounting unwinds every owned registration and transport on a partial
failure. Another account's backend or replacement is preserved. A projecting
host must verify the private lifecycle receipt before execution; only explicit
host acceptance after complete rollback permits ordinary-model fallback.
Cancellation and incomplete rollback abort initialization. The hook preserves
cancellation; Core 2.0.2's Rust session boundary wraps it as an initialization
error. No decision or UI action is replayed.

Offline qualification covers built-wheel entrypoints, the real Core 2.0.2 hook
validator/session, disabled and multiple accounts, partial failure, callback
failure, cancellation and teardown. A separate source-selection check uses the
real Foundation resolver and host account adapter. These checks use synthetic
keys and no model, API inference or device calls; they do not claim new live
inference, hardware or general website reliability results.

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
