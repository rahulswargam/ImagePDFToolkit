# Code signing

FileForge Toolkit's build produces two files that Windows treats specially:
`dist\ImagePDFToolkit.exe` (the app) and `dist\ImagePDFToolkit-Setup.exe` (the
installer). Both already carry correct publisher metadata (`CompanyName` /
`ProductName` = "FileForge Toolkit", author "Rahul Swargam" — see the
`version_info` block in `ImagePDFToolkit.spec` and the `AppPublisher`/
`VersionInfoCompany` settings in `installer/setup.iss`), which is why Windows
no longer shows "Unknown Publisher" when you inspect the file properties.

That metadata is **not** the same thing as Authenticode signing. Signing adds
a cryptographic signature backed by a certificate from a trusted Certificate
Authority (CA), which is what lets Windows attribute the file to a verified
identity rather than an unverified string embedded in the exe.

**No certificate is checked into this repository, and none should ever be.**
This document describes the infrastructure for signing once you have one —
it does not itself produce a signed build.

## What signing does and does not do

- It **does** let Windows show "Verified publisher: Rahul Swargam" instead of
  "Unknown publisher" in the UAC / SmartScreen prompt, once a certificate is
  installed and used.
- It does **not**, by itself, guarantee SmartScreen stops warning on first
  run. Standard (OV) code-signing certificates still need to build up
  download reputation with Microsoft over time before SmartScreen's
  application-reputation check stops flagging new releases. An Extended
  Validation (EV) certificate gets that reputation immediately, but costs
  more and requires hardware-token-backed key storage. Signing is necessary
  for a trusted publisher identity; it is not sufficient on its own to
  eliminate every warning immediately.

## Provisioning a certificate

1. Buy a code-signing certificate from a CA (e.g. DigiCert, Sectigo, SSL.com).
   For an individual publisher, a standard OV certificate is the usual
   starting point; EV is optional and pricier.
2. You'll receive either a `.pfx`/`.p12` file (private key + cert bundled,
   password-protected) or a hardware token (EV certs are usually
   token-based, in which case `sign.ps1`'s `/f` + `/p` args are replaced with
   token-specific `signtool` flags per your CA's instructions).
3. Store the `.pfx` somewhere outside the repo. `.gitignore` already blocks
   `*.pfx`, `*.p12`, `*.cer`, `*.crt`, `*.pem`, `*.key` from being committed
   by accident, but the real safeguard is simply never putting it in the
   project folder.

## Signing a build locally

```powershell
$env:CODE_SIGN_CERT_PATH = "C:\path\to\your-cert.pfx"
$env:CODE_SIGN_CERT_PASSWORD = "your-certificate-password"

python -m PyInstaller ImagePDFToolkit.spec --noconfirm
ISCC installer\setup.iss
.\installer\sign.ps1
```

`sign.ps1` signs both `dist\ImagePDFToolkit.exe` and
`dist\ImagePDFToolkit-Setup.exe` (skipping either if it isn't present),
timestamps the signature (so it stays valid after the certificate expires),
and verifies each signature afterward. Requires `signtool.exe`, which ships
with the Windows SDK / Visual Studio Build Tools.

If the environment variables aren't set, `sign.ps1` prints a message and
exits `0` — it's a deliberate no-op, not a build failure, so the normal
unsigned build/release flow this project already uses keeps working exactly
as before.

## Signing in CI

No CI workflow exists in this repo yet — releases are currently created
manually via `gh release create` (see the git history for the pattern). If
that changes, the equivalent step is:

```yaml
- name: Sign build
  env:
    CODE_SIGN_CERT_PATH: ${{ secrets.CODE_SIGN_CERT_PATH }}
    CODE_SIGN_CERT_PASSWORD: ${{ secrets.CODE_SIGN_CERT_PASSWORD }}
  run: pwsh installer/sign.ps1
```

with `CODE_SIGN_CERT_PATH` pointing at a certificate written to a temp file
from a base64 repository secret during the job (never checked into the repo
itself), and `CODE_SIGN_CERT_PASSWORD` as a separate secret. Neither secret
should ever appear in a workflow file, a log line, or a commit.
