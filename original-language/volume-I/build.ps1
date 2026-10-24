$ErrorActionPreference='Stop'
$compiler=(Get-Command xelatex -ErrorAction Stop).Source
$mutex=[System.Threading.Mutex]::new($false,'Global\InterlanguageTeXSlotV1')
$owned=$false
try {
 try {$owned=$mutex.WaitOne(0)} catch [System.Threading.AbandonedMutexException] {$owned=$true}
 if(-not $owned){Write-Output 'TeX slot occupied; source editing can continue.';return}
 Push-Location -LiteralPath $PSScriptRoot
 try {
  $output=Join-Path $PSScriptRoot ('build_'+[DateTime]::UtcNow.ToString('yyyyMMddTHHmmssfffZ'))
  New-Item -ItemType Directory -Path $output | Out-Null
  foreach($pass in @(1,2)){
   & $compiler '-interaction=nonstopmode' '-halt-on-error' '-file-line-error' '-recorder' '-jobname=gauss_i_editable_full' ('-output-directory='+$output) 'source.tex'
   if($LASTEXITCODE -ne 0){throw ('XeLaTeX failed on pass '+$pass)}
  }
 } finally {Pop-Location}
} finally {if($owned){$mutex.ReleaseMutex()};$mutex.Dispose()}
