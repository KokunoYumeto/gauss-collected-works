$ErrorActionPreference = 'Stop'
$slot = [System.Threading.Mutex]::new($false, 'Global\InterlanguageTeXSlotV1')
$held = $false
try {
    $held = $slot.WaitOne(0)
    if (-not $held) { throw 'TeX slot occupied; no compiler started.' }
    Push-Location $PSScriptRoot
    try {
        for ($pass = 1; $pass -le 2; $pass++) {
            & xelatex -interaction=nonstopmode -halt-on-error -file-line-error source.tex
            if ($LASTEXITCODE -ne 0) { throw "XeLaTeX pass $pass failed." }
        }
    } finally { Pop-Location }
} finally {
    if ($held) { $slot.ReleaseMutex() }
    $slot.Dispose()
}
