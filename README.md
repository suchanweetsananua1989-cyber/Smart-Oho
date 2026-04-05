# Smart Footing Central Values

## Calculation Status

- Engineering calculation features are temporarily disabled while the calculation engine is being rebuilt.
- Disabled scope includes the FEM analysis flow, geotechnical UBC/ABC helpers, and calculator-driven result generation.
- UI/data contracts remain in place so the calculation layer can be rebuilt without reworking project storage and page wiring.

This project already has several shared modules that act as the source of truth for defaults, load rules, and cross-page data contracts. This file documents those modules so future work can extend the right place instead of duplicating rules.

## Environment Setup

The launch scripts expect the project to run from the parent virtual environment at `../.venv312`.

Recommended setup from the parent folder:

```powershell
python -m venv .venv312
.\.venv312\Scripts\python.exe -m pip install -r .\footing_rebuild\requirements.txt
```

Then start the app from [run_footing_rebuild.ps1](run_footing_rebuild.ps1) or [run_footing_rebuild.bat](run_footing_rebuild.bat).

Note:
- `cryptography` is required for HWID license verification
- some 3D analysis paths also expect an internal `fea_viewer` package that is not bundled in this repository

## Central Modules

## UI Package Layout

Related UI modules are now grouped by domain instead of staying flat under `ui/`:

- `ui/licensing/` for license activation, HWID, and offline verification
- `ui/project/` for `.sfpj` document storage and recent projects
- `ui/setup/` for project setup tabs and setup window orchestration
- `ui/topview/` for top-view canvas interaction, transforms, preview, and selection helpers
- `ui/view3d/` for 3D monitor rendering, camera/navigation helpers, and orientation cube code
- `ui/piles/` for pile layout/deviation pages, pile rendering, and pile type settings

### [ui/footing_defaults.py](ui/footing_defaults.py)
Owns default footing geometry and form startup values.

Use it for:
- default footing dimensions
- default column dimensions
- default pile diameter
- common numeric ranges
- `default_footing_data()`
- triangular footing helper geometry

### [ui/load_catalog.py](ui/load_catalog.py)
Owns project-level load-definition and load-combination rules.

Use it for:
- supported load types
- load-type labels
- reserved load names like `SWL`
- default project loads
- load-combination source files
- combination summary formatting
- combination source loading
- normalized catalog snapshot for analysis/design

Important API:
- `normalize_load_definition(...)`
- `normalize_load_combination(...)`
- `build_combination_summary(...)`
- `build_load_catalog_snapshot(...)`
- `load_combination_source_payload(...)`

### [ui/load_case_targets.py](ui/load_case_targets.py)
Owns the target-key format for mapping a load case row to a specific column.

Current format:
- `main_column:0` — for the main column (C1)
- `column_id:<uuid>` — for extra columns (C2, C3, …), uses a stable UUID that survives add/remove/reorder
- Legacy `column:0`, `column:1` — old index-based format, auto-migrated on project load

Use it for:
- parsing/storing load targets
- syncing workspace load rows with selected columns
- future analysis/design code that needs per-column applied loads
- `generate_column_stable_id()` to mint a new UUID for a column
- `make_column_id_target_key(column_id)` / `parse_column_id_target_key(key)` for the stable format
- `load_case_column_key(entry)` to resolve any legacy or current key format

### [ui/project/project_document.py](ui/project/project_document.py)
Owns the project-file schema and custom Smart Footing file extension.

Current document extension:
- `.sfpj`

Security:
- `.sfpj` is stored as a standard JSON project file
- project save/open goes directly through [ui/project/project_document.py](ui/project/project_document.py) without password protection
- legacy password-protected `.sfpj` files are not rewritten automatically; resave them from an older build first if needed

Use it for:
- project document schema versioning
- project export/import payloads
- future Save/Open Project actions
- keeping project-level load catalog and footing items in one document format

### [styles.py](styles.py)
Owns app-wide visual tokens and stylesheet rules.

Use it for:
- shared widget styling
- global visual consistency
- cross-page UI refinements that should not be duplicated inline

## Setup UI Notes

- Soil setup currently focuses on spread-footing inputs: soil type, $\gamma$, $c$, $\phi$, groundwater, and bearing-related factors.
- The Soil-tab SPT UI/data model is intentionally kept in code but hidden from the visible layout for now.
- Reason: SPT is expected to be more useful for future pile/deep-foundation workflows than for the current spread-footing scope.
- If future pile/deep-soil features need a shared borehole source, the hidden Soil SPT widgets/data can be re-enabled instead of rebuilt.

## Setup Load Contract

Setup load editing lives in [ui/setup/setup_load_tab.py](ui/setup/setup_load_tab.py).

Top-level access should come through [ui/setup/setup_window.py](ui/setup/setup_window.py):
- `load_definitions()`
- `load_combinations()`
- `load_catalog_snapshot()`

Signals:
- `loadsChanged`
  - fire when load definitions change
  - intended for pages that only need refreshed load names
- `catalogChanged`
  - fire when either load definitions or combinations change
  - intended for future analysis/design synchronization

Recommended future integration:
- analysis should read `setup_window.load_catalog_snapshot()`
- design should read `setup_window.load_catalog_snapshot()`
- avoid rebuilding load/combo rules inside those modules

Workspace placeholder for that sync now exists in [ui/workspace_page.py](ui/workspace_page.py):
- `current_analysis_placeholder_context()`

It currently exposes:
- project name
- current project load catalog snapshot
- active footing item payload

That is the intended handoff point before a real analysis engine is added.

## Working Load Contract

Working-mode load editing lives in [ui/workspace_load_page.py](ui/workspace_load_page.py).

Current row schema:
```python
{
    'columnKey': 'main_column:0',
    'loadName': 'DL',
    'fx': None,
    'fy': None,
    'fz': 12.5,
    'mx': None,
    'my': 1.2,
    'mz': None,
}
```

Rules:
- `loadName` must come from Setup load definitions
- `SWL` is reserved and not selectable in working mode
- `columnKey` is the stable link between a load row and a real column on the footing
- rows targeting a deleted/unknown column are **dropped**, never silently remapped to another column

## FEM Payload Contract

Use `build_fem_payload(item, load_catalog)` from [ui/footing_models.py](ui/footing_models.py) to assemble a self-contained FEM payload from any footing item.

Returned keys:
- `name` — item display name
- `mode` — `'parametric'`, `'dxf'`, or `'drawing'`
- `footing_data` — dict that is fully self-contained (includes `column_x/y`, `extra_columns`, `pile_points`, `pile_deviations`, `cover`, `pile_length`)
- `footing` — `FootingData` object ready for geometry/analysis queries
- `load_cases` — list of per-column load rows
- `pile_type` — pile type name
- `load_catalog` — project-level load definitions and combinations
- `materials` — concrete & rebar properties (`fc_ksc`, `fy_ksc`, `ec_ksc`, `unit_weight_kg_m3`, `beta1`, `eps_cu`, `lambda_factor`, `fu_ksc`, `es_ksc`, `eps_y`)
- `pile_capacity` — resolved pile settings (`va_tonf`, `ha_tonf`, `ua_tonf`, `length`, `dimensions`, `group_efficiency`, `n_piles`)
- `geometry` — section properties (`area`, `centroid`, `Ix`, `Iy`, `Sx`, `Sy`, `bounds`, `vertices`, `column_edge_distances`)
- `soil` — soil engineering properties (`bearing_capacity_tonf_sqm`, `subgrade_modulus_tonf_m3`, `unit_weight_tonf_m3`)

Example batch-calc from home:
```python
from ui.footing_models import build_fem_payload
from ui.load_catalog import resolve_factored_loads

catalog = workspace.setup_window.load_catalog_snapshot()
for item in workspace.footing_items:
    payload = build_fem_payload(item, catalog)
    footing = payload['footing']        # FootingData with all columns/piles
    loads = payload['load_cases']       # per-column load rows
    combos = payload['load_catalog']    # definitions + combinations
    mat = payload['materials']          # fc, fy, Ec, unit weight, ...
    geom = payload['geometry']          # Ix, Iy, Sx, Sy, edge distances
    soil = payload['soil']              # qa, ks, gamma_soil
    pile = payload['pile_capacity']     # Va, Ha, Ua, group efficiency

    # Resolve factored loads for all combinations
    factored = resolve_factored_loads(loads, combos)
    for combo in factored:
        for col_key, forces in combo['column_results'].items():
            # forces = {'fx': ..., 'fy': ..., 'fz': ..., 'mx': ..., 'my': ..., 'mz': ...}
            pass  # → send to FEM solver
```

### FootingGeometry Section Properties

```python
from ui.footing_geometry import FootingGeometry

geom = FootingGeometry.from_footing_data(footing_data)
ix, iy = geom.moment_of_inertia   # m⁴
sx, sy = geom.section_modulus      # m³
edges = geom.edge_distances(col_x, col_y)  # left/right/bottom/top/min (m)
```

## 3D / Future Analysis Split

Keep these two responsibilities separate:

1. Project load catalog
   - source: `setup_window.load_catalog_snapshot()`
   - contains project load definitions and combinations

2. Footing applied load rows
   - source: `load_cases` stored on each footing item / `FootingData.extras`
   - contains which real column receives which load row

3. Project document payload
  - source: `workspace_page.export_project_document_payload()`
    - normalized by [ui/project/project_document.py](ui/project/project_document.py)
  - intended to be saved as `.sfpj`

That split is intentional:
- Setup answers what load definitions and combinations exist
- Workspace answers which column on this footing has which applied loads

## Rules To Keep

1. Do not hardcode load types in new files. Import from [ui/load_catalog.py](ui/load_catalog.py).
2. Do not duplicate `SWL` logic. Use helpers from [ui/load_catalog.py](ui/load_catalog.py).
3. Do not invent a new per-column load-target format. Use [ui/load_case_targets.py](ui/load_case_targets.py).
4. Do not duplicate footing startup defaults. Use [ui/footing_defaults.py](ui/footing_defaults.py).
5. If a rule is shared by Setup, Workspace, Analysis, or Design, move it into a central module first.

## Commercial License / HWID Contract

The application now has a client-side licensing foundation for machine-bound commercial distribution.

Central modules:
- [ui/licensing/license_hwid.py](ui/licensing/license_hwid.py)
- [ui/licensing/license_manager.py](ui/licensing/license_manager.py)
- [ui/licensing/license_activation_dialog.py](ui/licensing/license_activation_dialog.py)

What the app now does:
- computes a machine fingerprint (`HWID`) from multiple machine claims instead of a single ID
- requires a signed `.sflic` license before `New` or `Open` can be used
- verifies licenses with an Ed25519 public key embedded in the client or overridden by a production PEM file
- re-reads the `.sflic` file directly on every license check and rejects licenses for the wrong machine, wrong product, expired license, or bad signature
- supports a signed revocation list so specific license IDs can be blocked in later updates

Current license file model:
- extension: `.sflic`
- signed JSON document with a `payload` object and `signature`
- payload includes `productCode`, `licenseId`, `licenseType`, `customerName`, `issuedAt`, optional `expiresAt`, machine `hwid`, and `features`

License types:
- `full`
- `trial`

Default feature policy:
- `full`
  - all features enabled via `full`
- `trial`
  - limited by default to `project-save` and `trial`
  - current UI locks `Smart Cad` and `Setup`

Current activation flow:
1. App starts on [ui/start_page.py](ui/start_page.py)
2. If no valid activation exists, `New` and `Open` stay locked
3. User opens the activation dialog and copies the HWID
4. Vendor signs a full or trial `.sflic` license for that HWID
5. User either imports the `.sflic` manually or places it next to the installed program
6. App verifies signature and HWID match from the `.sflic` file itself on every check

Trial tamper protection:
- trial licenses rely on signed `expiresAt` timestamps
- signed expiry is still enforced directly from the license payload
- there is no local activation cache anymore; the app state follows the current `.sflic` file on disk

Recommended customer delivery flow:
- send the customer a `.sflic` file back
- ask them to place it in the same folder as the installed app executable
- preferred file name: `smart_footing_license.sflic`
- on startup the app now searches the install folder first and auto-activates from that file if it is valid
- manual import still exists as a fallback

Vendor-side tooling:
- [tools/generate_license_keypair.py](tools/generate_license_keypair.py)
  - generate an Ed25519 private/public keypair
- [tools/sign_license.py](tools/sign_license.py)
  - sign a HWID-bound license file using the vendor private key
- [tools/license_generator_ui.py](tools/license_generator_ui.py)
  - vendor-side UI for loading a `.sfreq`, choosing `full` or `trial`, setting `days` or `lifetime`, and generating a signed `.sflic`
- [tools/sign_revocations.py](tools/sign_revocations.py)
  - sign a revocation list for blocked license IDs using the vendor private key
- [tools/customer_hwid_reader.py](tools/customer_hwid_reader.py)
  - lightweight customer-side utility for reading HWID and exporting a `.sfreq` request file

Customer-side request options:
- customers can export a `.sfreq` request file directly from the in-app License Activation dialog without filling in extra fields
- the default saved request filename is now `smart_footing_request.sfreq`
- customers can still use [tools/customer_hwid_reader.py](tools/customer_hwid_reader.py) as a separate standalone utility when needed

Vendor UI generator workflow:
1. Run [run_license_generator.ps1](run_license_generator.ps1) or [run_license_generator.bat](run_license_generator.bat).
2. Put `smart_footing_license_private_key.pem` under the vendor key folder or set `SMART_FOOTING_LICENSE_PRIVATE_KEY`.
3. Paste the customer HWID manually, load the customer `.sfreq` file, or use both together.
4. Choose `Full` or `Trial`.
5. Choose `Days` or `Lifetime`.
6. Click `Generate License File` to write the `.sflic`.

Generator behavior:
- `Trial` requires `Days`
- `Full` supports `Days` or `Lifetime`
- `HWID` and `Request File` are both optional inputs, but at least one of them must be provided before generating
- if both `HWID` and `Request File` are provided, the typed `HWID` overrides the `hwid` inside the request file
- the default output filename is now short and simple: `smart_footing_trial.sflic` or `smart_footing_full.sflic`
- the UI auto-detects the vendor private key and does not ask the operator to browse for it manually
- the generated file still uses the same Ed25519 signing flow as [tools/sign_license.py](tools/sign_license.py)

Customer request file model:
- extension: `.sfreq`
- plain JSON request document created on the customer machine
- contains `hwid`, `hwidShort`, machine label, and machine claims

Recommended offline sales flow:
1. Build or package [tools/customer_hwid_reader.py](tools/customer_hwid_reader.py) as a small customer utility.
2. Customer runs it, or uses the in-app License Activation dialog, then copies the HWID or saves a `.sfreq` file.
3. Customer sends the HWID or `.sfreq` file back to you.
4. You sign a `.sflic` with [tools/sign_license.py](tools/sign_license.py).
5. You send the `.sflic` back to the customer.
6. Customer places the `.sflic` beside the installed program, then starts the app.

Offline production-like pre-release flow:
1. Generate the signing keypair outside the repository and keep the private key there.
2. Copy only the public key into `data/license_public_key.pem`.
3. Ship a fail-closed `data/license_policy.json` that requires the custom public key, requires a signed revocation list, and pins the SHA-256 fingerprint of the shipped public key.
4. Ship a signed `data/license_revocations.json` even if it only contains a harmless placeholder revoked ID at first.
5. Sign a trial or full `.sflic` for the target HWID.
6. Place the `.sflic` next to the executable or source-run parent folder and verify startup, open/save, and revocation behavior before release.

License auto-discovery locations:
- packaged build: folder containing the application executable
- source/developer run: project root folder [footing_rebuild](README.md)
- fallback: current working directory when the process starts
- supported auto-detected filenames: `smart_footing_license.sflic` and `license.sflic`

License file enforcement:
- the application now re-reads the supported `.sflic` file from the auto-discovery locations on every license check
- if no supported `.sflic` file is present in those locations, the app treats the machine as unlicensed immediately
- importing a license copies it to the standard auto-discovery location so the runtime can keep reading the same real file directly
- deleting that discovered `.sflic` file immediately removes the activated state on the next license check
- generic extra `.sflic` files are ignored during auto-discovery so an old full license file cannot silently override the current intended file

Signing from a request file:
- `tools/sign_license.py` can now read `--request-file path/to/customer.sfreq`
- if the request file already contains `customerName` or `customerEmail`, the signer can reuse them
- you can still override values explicitly with command-line flags
- use `--trial-days 7` or `--trial-days 14` to issue a signed trial license automatically
- use `--features` if you want a custom feature list instead of the default features for that license type

Example vendor command:
```powershell
python -m footing_rebuild.tools.sign_license \
  --private-key C:\secure\smart_footing_license_private_key.pem \
  --request-file C:\incoming\customer_request.sfreq \
  --customer-name "Customer Name" \
  --trial-days 14 \
  --out C:\outgoing\customer_license.sflic
```

Current trial gating in the desktop UI:
- trial licenses can still open and save projects
- `Smart Cad` is disabled for trial by default
- `Setup` is disabled for trial by default
- future contributors should add any new premium restrictions through the centralized `features` payload instead of hardcoding random UI checks

Revocation flow:
- ship a signed `data/license_revocations.json` with the app or with updates
- the revocation file uses the same Ed25519 trust chain as licenses
- if a license ID appears in the signed revocation list, the app rejects it even if the original license signature is valid
- this is the current offline path for emergency license blocking without adding a server

License policy hardening:
- the app now supports an optional `data/license_policy.json`
- this policy requires a shipped custom public key, requires a revocation list, and pins the SHA-256 fingerprint of `data/license_public_key.pem`
- a production release should fail closed by shipping both `data/license_public_key.pem` and `data/license_policy.json`
- see [data/license_policy.example.json](data/license_policy.example.json) for the expected shape

## Release Hardening

If you are preparing a commercial release, package the application and the customer HWID reader as separate executables.

Recommended build strategy:
- prefer Nuitka over plain source distribution so shipped binaries are harder to inspect and patch
- build the main app and the customer HWID reader separately
- ship only the public verification key and the signed revocation list with the app
- never ship private signing keys, request signing scripts, or vendor-only key folders to customers

Build helper:
- [tools/build_release.ps1](tools/build_release.ps1)
  - `-Target App` builds the main desktop application
  - `-Target HWIDReader` builds the customer HWID reader utility

Example build commands:
```powershell
pwsh ./footing_rebuild/tools/build_release.ps1 -Target App -PythonExe C:\Python312\python.exe -PublicKeyPath C:\secure\smart_footing_license_public_key.pem -RevocationsPath C:\secure\license_revocations.json

pwsh ./footing_rebuild/tools/build_release.ps1 -Target HWIDReader -PythonExe C:\Python312\python.exe
```

Production build note:
- when `-PublicKeyPath` is provided, [tools/build_release.ps1](tools/build_release.ps1) now auto-generates `data/license_policy.json` with the shipped public key fingerprint pinned
- you can override that by supplying `-LicensePolicyPath` explicitly

Recommended release layout:
- `SmartFooting.exe`
- `data/license_public_key.pem`
- `data/license_revocations.json`
- customer-delivered license file `smart_footing_license.sflic` placed next to the executable

Pre-release checklist:
1. Ship a production `data/license_public_key.pem` (the code-embedded obfuscated key must match).
2. Ship `data/license_policy.json` so production builds fail closed if the custom key or revocation policy is missing.
3. Generate the app binary from a clean machine or controlled build environment.
4. Verify no private `.pem` key is included anywhere in the release output.
5. Verify `data/license_revocations.json` is signed and current.
6. Verify the trial build still blocks `Smart Cad` and `Setup` before shipping it.
7. Verify a revoked license ID is rejected by the packaged build.
8. Sign the final binaries with your code-signing certificate if you have one.

Production key rotation rule:
- the client contains an XOR-obfuscated production verification key embedded in source code
- before shipping commercially, generate a real keypair and keep the private key outside the application repository
- ship only the public key to the application as `data/license_public_key.pem`
- never commit or bundle the private signing key with the desktop app

Security boundary notes:
- client-side checks raise the cost of cracking but do not make piracy mathematically impossible
- authenticity must come from a private key that stays off the customer machine
- a writable source or portable install is inherently weaker than a packaged release because the local machine controls the client runtime
- if future work adds an activation server, keep the existing signed-license verification and treat the server as an additional control, not a replacement

## License Security Hardening

The licensing system uses multi-layer defense-in-depth to resist file reading, key forgery, memory scanning, and policy tampering.

### Binary license envelope (anti-read, anti-Cheat-Engine)

The `.sflic` file is no longer plain JSON. It uses a binary envelope format:

```
SFLIC (5 bytes magic)
VERSION (1 byte = 0x01)
XOR_KEY (32 bytes random)
ZLIB( XOR(JSON, XOR_KEY) )
```

- opening the file with a text editor or hex viewer shows only binary noise
- each file is encoded with a unique random XOR key, so two licenses for the same customer produce completely different file bytes
- all JSON field names (`payload`, `signature`, `customerName`, `hwid`, `issuedAt`, etc.) are invisible in the raw file
- legacy plain-JSON `.sflic` files are still accepted for backward compatibility, but importing a license always re-encodes it as a binary envelope

### Obfuscated embedded public key (anti-key-extraction)

The production Ed25519 public key is never stored as plain PEM text in source code or memory:

- the PEM is XOR-encoded at build time into two constants (`_OBF_KEY` and `_OBF_DATA`) inside `license_manager.py`
- the key is decoded only at runtime, used for verification, then scrubbed from memory
- searching the source code for `-----BEGIN PUBLIC KEY-----` will not reveal the production key
- the disk PEM file (`data/license_public_key.pem`) is cross-checked against the embedded key; if they differ, the app rejects both

### Dual key verification (anti-fake-key)

Verifying a license requires passing three independent checks:

1. **Code-embedded key** — the obfuscated key decoded at runtime must match the code-pinned SHA-256 fingerprint (`_CODE_PINNED_PUBLIC_KEY_SHA256`)
2. **Disk PEM** — if `data/license_public_key.pem` exists, it must be byte-identical to the embedded key
3. **Signature chain** — the license file must carry a valid Ed25519 signature from the matching keypair

An attacker who replaces the disk PEM gets: *"On-disk public key does not match the embedded verification key."*
An attacker who deletes the disk PEM gets: *"A custom license public key is required by license policy."*
An attacker who signs with their own key gets: *"License signature is invalid."*

### Code-level policy floor (anti-policy-tamper)

Even if an attacker edits or deletes `data/license_policy.json`:

- `requireCustomPublicKey` is always forced to `True`
- `requireRevocationsFile` is always forced to `True`
- `pinnedPublicKeySha256` is always forced to the code-pinned constant

These overrides are applied unconditionally in `load_license_policy()`, regardless of whether the JSON file exists, is missing, or contains malicious values.

The `allowEmbeddedDemoKey` field was fully removed in round 3 — there is no demo key concept in the codebase.

### Memory scrubbing (anti-memory-scan)

After each license verification:

- PEM key bytes are zeroed with `ctypes.memset` via `_scrub_bytes()`
- Ed25519 signature bytes are zeroed
- canonical JSON bytes are zeroed
- the obfuscated key buffer is zeroed after recovery

This prevents Cheat Engine or similar memory scanners from finding `-----BEGIN PUBLIC KEY-----` or license JSON in process memory.

### Anti-clock-rollback

- `issuedAt` is mandatory in every license payload
- if the system clock is more than 5 minutes before `issuedAt`, the license is rejected
- expired trials cannot be extended by rolling the clock forward past `expiresAt`

### Anti-time-freeze (Registry marker)

An attacker can bypass expiry by freezing the system clock at a date when the trial is still valid. To counter this:

- every successful license validation writes the current UTC timestamp to `HKCU\SOFTWARE\SmartFooting\License` (value `rt`)
- the timestamp is XOR-obfuscated with a hardcoded mask so it cannot be trivially read or edited with regedit
- on the next validation, if the current time is more than 5 minutes *before* the stored last-runtime, the check fails with `"System clock appears to have moved backward since the last run."`
- first launch (no Registry entry) is accepted gracefully

### Anti-import caller guard

`_recover_obfuscated_public_key()` uses `sys._getframe(1)` to verify the caller module is `license_manager` itself. External scripts attempting:
```python
from footing_rebuild.ui.licensing.license_manager import _recover_obfuscated_public_key
print(_recover_obfuscated_public_key())
```
receive `RuntimeError: Access denied.` This forces an attacker to patch the source file rather than using a one-liner.

### Fail-closed revocation

`_revoked_license_ids()` raises `LicenseBindingError` unconditionally when the revocation file is missing — there is no fallback `return set()` path. Deleting `data/license_revocations.json` crashes license validation immediately.

### Payload RAM scrubbing

After `verify_license_bytes()` completes validation, only a safe subset of payload fields (customerName, licenseId, licenseType, expiresAt, features) is copied into the returned `LicenseStatus`. The full payload dict — containing hwid, schemaVersion, productCode, issuedAt, and all other fields — is scrubbed via `_scrub_dict()` before the function returns.

### Demo dead-code removal

All references to the embedded demo public key have been removed:
- `LICENSE_EMBEDDED_DEMO_PUBLIC_KEY_PEM` constant → deleted
- `_HARDENED_ALLOW_EMBEDDED_DEMO_KEY` constant → deleted
- `allowEmbeddedDemoKey` policy field → deleted from source, JSON files, and build scripts
- All `'Embedded demo key'` / `'using demo verification key'` strings → deleted
- `LicenseStatus.public_key_mode` default → changed from `'demo'` to `'custom'`
- `demo_key_warning` widget in activation dialog → deleted

## Penetration Test Results

### Round 2 (26 tests, 50 checks — 50/50 passed)

One vulnerability was found during testing (**T26: policy file deletion**) and fixed immediately before final results.

| ID | Attack scenario | Checks | Result |
|----|----------------|--------|--------|
| T01 | Binary envelope — no plaintext in file | 6 | PASS |
| T02 | Tampered envelope body | 1 | PASS |
| T03 | Truncated envelope file | 1 | PASS |
| T04 | Wrong magic header | 1 | PASS |
| T05 | Wrong envelope version | 1 | PASS |
| T06 | Legacy plain JSON backward compat | 1 | PASS |
| T07 | Import auto-upgrades to binary | 2 | PASS |
| T08 | PEM file replaced with attacker key | 1 | PASS |
| T09 | PEM file deleted | 1 | PASS |
| T10 | Policy JSON tampered to enable demo key | 4 | PASS |
| T11 | Policy JSON deleted | 1 | PASS |
| T12 | Forged license — wrong HWID | 1 | PASS |
| T13 | Forged license — wrong product code | 1 | PASS |
| T14 | Forged license — attacker-signed | 1 | PASS |
| T15 | Missing `issuedAt` timestamp | 1 | PASS |
| T16 | Clock rollback (`issuedAt` in future) | 1 | PASS |
| T17 | Expired trial license | 1 | PASS |
| T18 | Revoked license ID | 1 | PASS |
| T19 | Revocation list deleted | 1 | PASS |
| T20 | Revocation list tampered signature | 1 | PASS |
| T21 | Embedded key integrity verification | 2 | PASS |
| T22 | Memory scrubbing (`bytearray` zeroed) | 2 | PASS |
| T23 | Envelope XOR key randomness | 3 | PASS |
| T24 | Full round-trip (full → trial → cleanup) | 3 | PASS |
| T25 | Anti-Cheat-Engine — 10 field names absent | 10 | PASS |
| T26 | Policy file deletion bypass | 1 | PASS |

**Round 2 vulnerability found and fixed:**

- **T26 — Policy file deletion bypassed code-level floor**: `load_license_policy()` returned early with lenient defaults when the file was missing. Fixed by moving the code-level floor enforcement outside the `if path.exists()` branch.

### Round 3 (34 tests, 65 checks — 65/65 passed)

Retested all original scenarios plus 9 new tests for the 5 logic vulnerabilities:

| ID | Attack scenario | Checks | Result |
|----|----------------|--------|--------|
| T01–T25 | All original envelope/key/policy/forge/revocation/memory tests | 55 | PASS |
| T26 | Anti-time-freeze (clock frozen after valid run) | 1 | PASS |
| T27 | Registry marker is XOR-obfuscated (not plain timestamp) | 3 | PASS |
| T28 | External import of `_recover_obfuscated_public_key` blocked | 1 | PASS |
| T29 | Revocation file missing = hard crash (fail-closed) | 1 | PASS |
| T30 | Payload RAM scrub — only safe keys returned | 2 | PASS |
| T31 | No demo references in source code | 5 | PASS |
| T32 | `LicenseStatus` default mode is `'custom'` | 1 | PASS |
| T33 | Summary lines contain no demo references | 1 | PASS |
| T34 | First run without Registry entry succeeds | 1 | PASS |

### Residual risks (acknowledged)

These risks cannot be fully mitigated without additional infrastructure:

- **Source-code patching** — an attacker with write access to the Python source can modify any check; mitigated by compiling with Nuitka/PyInstaller + code signing
- **Cython/.pyd compilation** — the cryptography functions (`_recover_obfuscated_public_key`, `verify_license_bytes`, `_OBF_DATA`) should ideally be compiled to a C extension (`.pyd`) to resist dynamic import and bytecode patching; this is not yet done
- **Revocation list rollback** — replacing `data/license_revocations.json` with an older legitimately-signed version can un-revoke licenses; full mitigation requires a server-side revocation epoch counter
- **Clock manipulation** — the 5-minute drift tolerance and Registry marker protect against obvious rollback and time-freezing, but an attacker with admin access can modify the Registry value; a network time check would be stronger but requires internet access
- **Memory forensics at C level** — Python's allocator may retain copies of scrubbed data in freed heap blocks; only a C-level secure allocator can guarantee complete erasure; payload dict scrubbing and `_scrub_dict()` are best-effort within CPython constraints
- **PyArmor / obfuscation** — runtime string obfuscation with tools like PyArmor would raise the cost of bytecode patching further; not yet integrated

Rules for future contributors:
1. Do not remove the startup license gate in [main_window.py](main_window.py) without replacing it with an equivalent stronger gate.
2. Do not store a private signing key anywhere inside the app package, repo, installer, or shipped resources.
3. Do not replace Ed25519 signatures with symmetric secrets embedded in the client.
4. Do not validate licenses by MAC address alone; keep HWID generation centralized in [ui/licensing/license_hwid.py](ui/licensing/license_hwid.py).
5. Do not bypass license verification for convenience in production builds.
6. If you add a server later, keep offline signature verification so the app still rejects forged licenses locally.
7. Keep trial and full licenses on the same verification path; differ by `licenseType`, `expiresAt`, and `features`, not by a separate ad hoc trial subsystem.
8. Do not reintroduce hidden local activation state; runtime license status must follow the actual `.sflic` file on disk.
9. Do not use an unsigned revocation file; it must stay under the same signing trust model as licenses.
10. Do not ship vendor-only tooling or private signing keys inside customer releases; package them separately from the end-user app.
11. Do not reintroduce `allowEmbeddedDemoKey`, `LICENSE_EMBEDDED_DEMO_PUBLIC_KEY_PEM`, or any code path referencing a 'demo' verification key — all dead demo code was removed in round 3.
12. Do not add `return set()` fallback paths in `_revoked_license_ids()` — the revocation file is always mandatory (fail-closed design).
13. Do not expose `_recover_obfuscated_public_key()` in `__all__` or remove its caller guard.

## Data Integrity Fixes (April 2026)

This section documents critical data-integrity bugs discovered during a full audit of the save/load/FEM pipeline and the fixes applied.

### Fixed bugs

| ID | Bug | Severity | File | Fix |
|----|-----|----------|------|-----|
| #1 | Main column (C1) load-target entry had no explicit `key` in `_build_workspace_load_columns()` — while harmless today, it was inconsistent with extra columns | LOW | `workspace_page.py` | Added `'key': MAIN_COLUMN_TARGET_KEY` to the C1 entry |
| #2 | `_normalize_row()` silently remapped loads for a deleted/unknown column to the first available column instead of dropping them | HIGH | `workspace_load_page.py` | Changed fallback: rows targeting a column that no longer exists are now dropped (empty `columnKey`) instead of silently reassigned |
| #3 | `set_available_columns()` and `set_available_loads()` called `_normalize_row()` **twice per row** (once in filter, once in map) | MEDIUM | `workspace_load_page.py` | Changed to walrus-operator list comprehension that calls `_normalize_row()` once per row |
| #4 | `set_load_cases()` used a nested-`for` pattern instead of checking both `loadName` and `columnKey` | MEDIUM | `workspace_load_page.py` | Rows with empty `loadName` or empty `columnKey` are now both filtered out |
| #5 | `footing_data` dict from `footing_form.get_data()` did not contain `column_x/y` — C1 position was stored separately in `main_column_xy` but never merged back into `footing_data` | HIGH | `workspace_page.py` | Created `_merge_footing_data_for_storage()` that injects `column_x`, `column_y`, `extra_columns`, `pile_points`, and `pile_deviations` into `footing_data` on every save |
| #6 | `extra_columns` not included in `footing_data` — `FootingData.from_dict(item['footing_data'])` would return an object with zero extra columns | HIGH | `workspace_page.py` | Same merge helper now injects `extra_columns` into `footing_data` |
| #7 | `pile_points` not included in `footing_data` for parametric mode — `FootingData.from_dict()` would return an object with zero piles | HIGH | `workspace_page.py` | Same merge helper now injects `pile_points` and `pile_deviations` |
| #8 | Pile deviations keyed by index — deleting a pile caused all deviation indices to shift and deviations to silently detach from their original pile | MEDIUM | `workspace_page.py` | `update_piles()` now matches old→new pile deviations by position coordinates instead of truncating by index |
| #9 | DXF save path (`handle_dxf_config`) did not persist `pile_deviations`, `extra_columns`, or `main_column_xy` on the item dict | HIGH | `workspace_page.py` | Added missing assignments so DXF items carry the same complete data as parametric items |
| #10 | DXF and drawing save paths stored `footing_data` from `_build_preview_footing_model()` without merging column/pile/deviation data | HIGH | `workspace_page.py` | All three save paths (`save_parametric_item`, `save_drawing_item`, `handle_dxf_config`) now call `_merge_footing_data_for_storage()` |
| #11 | No centralized function to assemble a complete FEM payload from any footing item | CRITICAL | `footing_models.py` | Created `build_fem_payload(item, load_catalog)` that returns a self-contained dict with a complete `FootingData` object, load cases, and load catalog |

### What `_merge_footing_data_for_storage()` does

Called by every save path before writing `item['footing_data']`. It injects:
- `column_x`, `column_y` ← from `main_column_xy`
- `extra_columns` ← from `self.current_columns`
- `pile_points` ← from `self.current_piles`
- `pile_deviations` + `pile_deviation_targets` ← from `self.current_pile_deviations`

This ensures `FootingData.from_dict(item['footing_data'])` always returns a **complete** object with all columns, piles, and deviations included — ready for FEM without additional assembly.

### What `build_fem_payload()` does

A standalone function in `ui/footing_models.py` for batch calculation from the home screen:
```python
payload = build_fem_payload(item, catalog)
payload['footing']       # → FootingData with all columns, piles, deviations
payload['footing_data']  # → dict form (includes cover, pile_length)
payload['load_cases']    # → per-column load rows
payload['load_catalog']  # → project-level load definitions + combinations
payload['materials']     # → {fc_ksc, fy_ksc, ec_ksc, unit_weight_kg_m3, beta1, ...}
payload['geometry']      # → {area, Ix, Iy, Sx, Sy, centroid, column_edge_distances, ...}
payload['pile_capacity'] # → {va_tonf, ha_tonf, ua_tonf, length, group_efficiency, ...}
payload['soil']          # → {bearing_capacity_tonf_sqm, subgrade_modulus_tonf_m3, unit_weight_tonf_m3}
```

### Remaining known limitations

| Item | Status | Notes |
|------|--------|-------|
| Material settings per footing item | PARTIAL | `build_fem_payload` injects project defaults; per-item override fields (`concrete_grade`, `rebar_grade`) can be stored in `footing_data.extras` but no UI yet |
| Pile length / embedment depth | DONE | `PileData.length` added; auto-populated from `pile_settings.json` |
| Load combination resolver | DONE | `resolve_factored_loads(load_cases, catalog)` in `load_catalog.py` |
| `has_main_column` toggle mid-session | LOW RISK | If C1 is toggled off, existing C1 load rows remain in `load_cases` until next column sync |

## FEM Completeness Fixes (April 2026)

All gaps identified in the FEM data pipeline audit have been resolved.

### Changes

| # | Gap | Files Changed | Fix |
|---|-----|---------------|-----|
| B1 | No moment of inertia (Ix, Iy) | `footing_geometry.py` | Added `moment_of_inertia` property using polygon shoelace formula — verified: 2×3 rect → Ix=4.5, Iy=2.0 m⁴ |
| B2 | No section modulus (Sx, Sy) | `footing_geometry.py` | Added `section_modulus` property: Sx = Ix/y_max, Sy = Iy/x_max |
| B3 | No pile embedment length | `footing_models.py`, `pile_settings.json` | Added `PileData.length` field; `build_fem_payload` auto-populates from pile_settings.json |
| B4 | No subgrade modulus (ks) | `capacity_settings.json`, `capacity_settings.py` | Added `subgradeModulusTonfPerCuM` to soil entries; new `soil_subgrade_modulus_by_name()` helper |
| B5 | No soil unit weight (γ) | `capacity_settings.json`, `capacity_settings.py` | Added `soilUnitWeightTonfPerCuM` to soil entries; new `soil_unit_weight_by_name()` helper |
| S1 | No punching shear edge distances | `footing_geometry.py` | Added `edge_distances(col_x, col_y)` → `{left, right, bottom, top, min}` for column classification |
| S2 | Material not bound to payload | `setup_material_calculations.py`, `footing_models.py` | Added `build_material_snapshot()` → `{fc_ksc, fy_ksc, ec_ksc, ...}`; injected into `build_fem_payload` |
| S3 | No concrete cover | `footing_defaults.py`, `footing_models.py` | Added `FootingData.cover` field (default 0.075 m per ACI 20.6.1) |
| S4 | No pile group efficiency | `footing_models.py` | Added Converse–Labarre group efficiency calculation in `build_fem_payload` |
| S5 | Pile capacity not resolved | `footing_models.py` | `build_fem_payload` now resolves `pile_type` → `{va_tonf, ha_tonf, ua_tonf, length, dimensions}` from pile_settings |
| M1 | Concrete unit weight not in payload | `setup_material_calculations.py` | `build_material_snapshot()` includes `unit_weight_kg_m3` from material_settings.json |
| M3 | No load combination resolver | `load_catalog.py` | Added `resolve_factored_loads(load_cases, catalog)` → factored forces per column per combination |

## Setup Soil & Pile Tabs (April 2026)

The Setup dialog now has dedicated **Soil** and **Pile** tabs, each with a **Simple / Detailed** mode toggle so users can choose between entering design values directly or providing investigation-level data.

### Tab Layout

```
[ Soil ] [ Pile ] [ Materials ] [ Load ]
```

### Soil Tab — `ui/setup/setup_soil_tab.py`

| Mode | Section | Parameters |
|------|---------|------------|
| **Simple** | Design Values (Direct Input) | qa — Bearing Capacity (tonf/m²), ks — Subgrade Modulus (tonf/m³), γ — Soil Unit Weight (tonf/m³), Groundwater Depth (m) |
| **From Investigation** | Soil Classification | Soil Type (Clay / Sand / Silt / Gravel) |
| | Strength Parameters | Cohesion c (tonf/m²), Friction Angle φ (°), SPT N-value (blows/ft) |
| | Unit Weights | γ natural (tonf/m³), γ saturated (tonf/m³) |
| | Site Conditions | Groundwater Depth (m), Factor of Safety |
| | Bearing Capacity Factors (auto) | Nc, Nq, Nγ — auto-calculated from φ via Terzaghi interpolation |

### Pile Tab — `ui/setup/setup_general_tab.py`

| Mode | Section | Parameters |
|------|---------|------------|
| **Both** | Section & Material | Pile Type (square/circle), Pile Diameter/Width (m), Material Concrete, Rebar, Tie |
| **Simple** | Allowable Capacity (Direct Input) | VA — Vertical (tonf), HA — Lateral (tonf), UA — Uplift (tonf), Auto HA/UA from VA |
| **Detailed** | Pile Geometry & Installation | Pile Class (Precast / Cast-in-place / Steel / Timber), Installation Method (Driven / Bored / Micro / CFA), Pile Length (m) |
| | Soil-Pile Interaction | Soil Friction δ (°), Soil Cohesion ca (tonf/m²), SPT N-value (blows/ft) |
| | End Bearing & Skin Friction | End Bearing qp (tonf/m²), Skin Friction fs (tonf/m²) |
| | Group & Special Effects | Group Efficiency Factor, Negative Skin Friction (tonf) |

### Files Changed

| File | Change |
|------|--------|
| `ui/setup/setup_soil_tab.py` | **New** — Soil properties tab with Simple/Investigation modes, Terzaghi Nc/Nq/Nγ auto-calc |
| `ui/setup/setup_general_tab.py` | Refactored — Removed soil card, added Simple/Detailed pile modes with SegmentedSelector |
| `ui/setup/setup_page.py` | Added Soil tab as first tab, renamed Capacity → Pile |
| `ui/setup/__init__.py` | Added `SetupSoilTab` export |
| `data/capacity_settings.json` | Extended soil entries with mode, investigation fields (cohesion, φ, SPT, γ_sat, GWT, FS) |
| `data/pile_settings.json` | Extended pile entries with mode, pileClass, installMethod, soil-pile interaction fields |