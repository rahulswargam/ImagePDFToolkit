<#
.SYNOPSIS
    Authenticode-signs the FileForge Toolkit exe and installer.

.DESCRIPTION
    Reads the signing certificate path and password from environment
    variables only - never from source, never from a committed file.
    Intended to run locally (with the vars set for that shell session) or
    as a step in a CI job that injects them from a secret store.

    Required environment variables:
      CODE_SIGN_CERT_PATH      Path to a .pfx/.p12 certificate file.
      CODE_SIGN_CERT_PASSWORD  Password for that certificate.

    If either variable is missing, this script prints a message and exits
    0 (a no-op) rather than failing the build - signing is optional
    infrastructure until a real certificate is provisioned; see SIGNING.md.

.PARAMETER Files
    Files to sign. Defaults to the exe and installer produced by the
    standard build (dist\FileForgeToolkit.exe, dist\FileForgeToolkit-Setup.exe),
    skipping any that don't exist yet.

.EXAMPLE
    $env:CODE_SIGN_CERT_PATH = "C:\secure\rahul-swargam.pfx"
    $env:CODE_SIGN_CERT_PASSWORD = "..."
    .\installer\sign.ps1
#>

param(
    [string[]]$Files
)

$ErrorActionPreference = "Stop"

$RepoRoot = Split-Path -Parent $PSScriptRoot
if (-not $Files) {
    $Files = @(
        (Join-Path $RepoRoot "dist\FileForgeToolkit.exe"),
        (Join-Path $RepoRoot "dist\FileForgeToolkit-Setup.exe")
    )
}
$Files = $Files | Where-Object { Test-Path $_ }

if (-not $env:CODE_SIGN_CERT_PATH -or -not $env:CODE_SIGN_CERT_PASSWORD) {
    Write-Host "Code signing skipped: CODE_SIGN_CERT_PATH / CODE_SIGN_CERT_PASSWORD not set." -ForegroundColor Yellow
    Write-Host "This is a no-op, not a failure - see SIGNING.md to provision a certificate." -ForegroundColor Yellow
    exit 0
}

if (-not (Test-Path $env:CODE_SIGN_CERT_PATH)) {
    Write-Error "CODE_SIGN_CERT_PATH is set but the file does not exist: $env:CODE_SIGN_CERT_PATH"
    exit 1
}

if ($Files.Count -eq 0) {
    Write-Host "Nothing to sign - no built exe/installer found under dist folder. Build first." -ForegroundColor Yellow
    exit 0
}

$signtoolCandidates = @(
    (Get-Command signtool.exe -ErrorAction SilentlyContinue).Source
) + (Get-ChildItem -Path "C:\Program Files (x86)\Windows Kits\10\bin" -Recurse -Filter "signtool.exe" -ErrorAction SilentlyContinue |
        Where-Object { $_.FullName -match "x64" } | Select-Object -ExpandProperty FullName)

$signtool = $signtoolCandidates | Where-Object { $_ } | Select-Object -First 1

if (-not $signtool) {
    Write-Error "signtool.exe not found. Install the Windows SDK (or Visual Studio Build Tools) to get it."
    exit 1
}

$timestampUrl = "http://timestamp.digicert.com"

foreach ($file in $Files) {
    Write-Host "Signing $file ..."
    & $signtool sign `
        /f $env:CODE_SIGN_CERT_PATH `
        /p $env:CODE_SIGN_CERT_PASSWORD `
        /fd sha256 `
        /td sha256 `
        /tr $timestampUrl `
        /d "FileForge Toolkit" `
        $file

    if ($LASTEXITCODE -ne 0) {
        Write-Error "signtool failed for $file (exit $LASTEXITCODE)"
        exit $LASTEXITCODE
    }

    Write-Host "Verifying signature on $file ..."
    & $signtool verify /pa /v $file
}

Write-Host "All files signed successfully." -ForegroundColor Green
