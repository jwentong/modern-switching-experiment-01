$ErrorActionPreference = 'Stop'
$env:PYTHONUTF8 = '1'
$repoRoot = Split-Path -Parent $PSScriptRoot
$projectPython = Join-Path $repoRoot '.venv\Scripts\python.exe'
if (-not (Test-Path -LiteralPath $projectPython)) {
    throw 'Create .venv and install student_tests/requirements-lock.txt first; see REPORT.md.'
}
Push-Location -LiteralPath $repoRoot
try {
    & $projectPython src/test_environment.py
    if ($LASTEXITCODE -ne 0) { throw 'Environment check failed' }
    & $projectPython -m pytest grading student_tests -q
    if ($LASTEXITCODE -ne 0) { throw 'Tests failed' }
    & $projectPython src/performance_test.py
    if ($LASTEXITCODE -ne 0) { throw 'Baseline simulation failed' }
    & $projectPython student_tests/run_extra.py
    if ($LASTEXITCODE -ne 0) { throw 'Parameter scans failed' }
    & $projectPython student_tests/verify_artifacts.py
    if ($LASTEXITCODE -ne 0) { throw 'Artifact verification failed' }
    & $projectPython grading/calculate_grade.py
    if ($LASTEXITCODE -ne 0) { throw 'Local grading failed' }
    Copy-Item -LiteralPath 'grade_report.json' -Destination 'results/extra/local_grade_report.json' -Force
    Copy-Item -LiteralPath 'grade_result.txt' -Destination 'results/extra/local_grade_result.txt' -Force
}
finally {
    Pop-Location
}
