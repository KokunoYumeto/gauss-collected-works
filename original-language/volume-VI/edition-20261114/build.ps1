$ErrorActionPreference='Stop'
$gaussMutex=[Threading.Mutex]::new($false,'Global\InterlanguageTeXSlotV1')
$gaussHeld=$false
try {
 try {$gaussHeld=$gaussMutex.WaitOne(0)} catch [Threading.AbandonedMutexException] {$gaussHeld=$true}
 if (-not $gaussHeld) {Write-Output 'TeX slot occupied; no compilation or polling.';return}
 Push-Location $PSScriptRoot
 try {
  foreach ($gaussPass in 1,2) {
   & xelatex '-no-shell-escape' '-interaction=nonstopmode' '-halt-on-error' 'source.tex'
   if ($LASTEXITCODE -ne 0) {throw 'XeLaTeX failed.'}
  }
 } finally {Pop-Location}
} finally {if ($gaussHeld) {$gaussMutex.ReleaseMutex()};$gaussMutex.Dispose()}
