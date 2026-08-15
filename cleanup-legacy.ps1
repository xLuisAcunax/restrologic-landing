<#
  RestroLogic landing — remove files superseded by the redesign.

  The redesign was written into the repo as new files. This script deletes the
  ones it replaced. Nothing here is imported by the new code, so the site
  builds correctly either way — but leaving them behind means `npm run check`
  fails (the old components reference translation keys that no longer exist)
  and ~27 MB of unused PNGs stay in git.

  Run from the repo root:
      pwsh -File .\cleanup-legacy.ps1            # preview what would be deleted
      pwsh -File .\cleanup-legacy.ps1 -Confirm   # actually delete
#>

[CmdletBinding()]
param(
    [switch]$Confirm
)

$ErrorActionPreference = 'Stop'

$targets = @(
    # Replaced by src/components/{layout,sections,ui}/.
    # These still reference removed i18n keys and daisyUI classes.
    'src/components/Hero.astro',
    'src/components/Features.astro',
    'src/components/Modules.astro',
    'src/components/Pricing.astro',
    'src/components/Contact.astro',
    'src/components/LanguagePicker.astro',
    'src/components/Welcome.astro',

    # Astro starter leftovers, never referenced.
    'src/assets/astro.svg',
    'src/assets/background.svg',

    # Replaced by src/assets/screens/*.webp (340 KB total, down from 21 MB)
    # and public/images/og-cover.jpg.
    'public/images/admin.png',
    'public/images/domicilios.png',
    'public/images/facturacion.png',
    'public/images/inventarios.png',
    'public/images/hero-bg.png',

    # The four AI-rendered marketing images, replaced by real product captures
    # (dashboard / pos-mesas / pos-ordenes / inventario / productos / caja /
    # reportes-ordenes / reportes-caja). Nothing imports these any more.
    'src/assets/screens/admin.webp',
    'src/assets/screens/domicilios.webp',
    'src/assets/screens/facturacion.webp',
    'src/assets/screens/inventarios.webp',
    'preview/assets/screens/admin.webp',
    'preview/assets/screens/domicilios.webp',
    'preview/assets/screens/facturacion.webp',
    'preview/assets/screens/inventarios.webp',

    # Scratch output from an earlier icon-extraction experiment.
    'build_log.txt',
    'build_log_2.txt',
    'extract_icons.mjs',
    'icons_data.txt',
    'icons_data_2.txt'
)

$found   = @()
$missing = @()
$bytes   = 0

foreach ($rel in $targets) {
    $path = Join-Path $PSScriptRoot $rel
    if (Test-Path -LiteralPath $path -PathType Leaf) {
        $item   = Get-Item -LiteralPath $path
        $bytes += $item.Length
        $found += [pscustomobject]@{ Path = $rel; SizeKB = [math]::Round($item.Length / 1KB, 1) }
    }
    else {
        $missing += $rel
    }
}

if ($found.Count -eq 0) {
    Write-Host 'Nothing to clean up — already done.' -ForegroundColor Green
    exit 0
}

$found | Format-Table -AutoSize
Write-Host ("{0} file(s), {1:N1} MB" -f $found.Count, ($bytes / 1MB)) -ForegroundColor Cyan

if ($missing.Count -gt 0) {
    Write-Host ("(already absent: {0})" -f ($missing -join ', ')) -ForegroundColor DarkGray
}

if (-not $Confirm) {
    Write-Host ''
    Write-Host 'Dry run. Re-run with -Confirm to delete:' -ForegroundColor Yellow
    Write-Host '    pwsh -File .\cleanup-legacy.ps1 -Confirm'
    exit 0
}

foreach ($entry in $found) {
    Remove-Item -LiteralPath (Join-Path $PSScriptRoot $entry.Path) -Force
    Write-Host "deleted  $($entry.Path)" -ForegroundColor DarkGray
}

Write-Host ''
Write-Host ("Removed {0} file(s), freed {1:N1} MB." -f $found.Count, ($bytes / 1MB)) -ForegroundColor Green
Write-Host 'Next:  npm install  &&  npm run dev'
