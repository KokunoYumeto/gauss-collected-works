param([string]$Python = 'python', [string]$XeLaTeX = 'xelatex')
$ErrorActionPreference = 'Stop'
$editionRoot = $PSScriptRoot
$mutex = [System.Threading.Mutex]::new($false, 'Global\InterlanguageTeXSlotV1')
$acquired = $false
try {
    try { $acquired = $mutex.WaitOne(0) } catch [System.Threading.AbandonedMutexException] { $acquired = $true }
    if (-not $acquired) { throw 'TeX slot occupied. No compiler started.' }
    $volume = Get-Content -Raw -LiteralPath (Join-Path $editionRoot 'volume.json') | ConvertFrom-Json
    foreach ($part in $volume.parts) {
        $partRoot = Join-Path (Join-Path $editionRoot 'parts') $part.id
        $buildRoot = Join-Path $partRoot 'build'
        New-Item -ItemType Directory -Force -Path $buildRoot | Out-Null
        Push-Location -LiteralPath $partRoot
        try {
            foreach ($pass in 1..2) {
                & $XeLaTeX '-interaction=nonstopmode' '-halt-on-error' '-no-shell-escape' '-output-directory=build' '-jobname=source' $part.main *> (Join-Path $buildRoot "pass$pass.txt")
                if ($LASTEXITCODE -ne 0) { throw "XeLaTeX failed in $($part.id), pass $pass. See its build log." }
            }
        } finally { Pop-Location }
    }
    $stamp = [DateTime]::UtcNow.ToString('yyyyMMddTHHmmssZ')
    $readerPath = Join-Path $editionRoot "Gauss_Werke_VIII_$stamp.pdf"
    & $Python (Join-Path $editionRoot 'assemble_reader.py') '--output' $readerPath
    if ($LASTEXITCODE -ne 0) { throw 'Reader assembly failed.' }
} finally {
    if ($acquired) { $mutex.ReleaseMutex() }
    $mutex.Dispose()
}
