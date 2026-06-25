param(
    [switch]$SkipNotepad
)

$ErrorActionPreference = "Stop"
$ProjectRoot = Resolve-Path (Join-Path $PSScriptRoot "..\..")
$JarvisBat = Join-Path $ProjectRoot "Jarvis.bat"
$GeneratedDir = Join-Path (Resolve-Path (Join-Path $ProjectRoot "..\..")).Path "Documents\Generated"

function Write-Step {
    param([string]$Text)
    Write-Host ""
    Write-Host "== $Text ==" -ForegroundColor Cyan
}

function Write-Fix {
    param([string]$Cause, [string]$Fix)
    Write-Host "실패 원인 후보: $Cause" -ForegroundColor Yellow
    Write-Host "해결 방법: $Fix" -ForegroundColor Yellow
}

function Invoke-JarvisStep {
    param(
        [string]$Name,
        [string]$Arguments,
        [string]$Cause,
        [string]$Fix
    )
    Write-Step $Name
    & $JarvisBat $Arguments
    if ($LASTEXITCODE -ne 0) {
        Write-Host "실패: $Name" -ForegroundColor Red
        Write-Fix $Cause $Fix
        return $false
    }
    Write-Host "성공: $Name" -ForegroundColor Green
    return $true
}

$allPassed = $true

Write-Step "사전 확인"
if (-not (Test-Path $JarvisBat)) {
    Write-Host "실패: Jarvis.bat을 찾지 못했습니다." -ForegroundColor Red
    Write-Fix "현재 폴더가 WindowsJarvisAssistant가 아닙니다." "Jarvis\Projects\WindowsJarvisAssistant 폴더에서 실행하세요."
    exit 1
}

try {
    $pythonVersion = python --version 2>&1
    Write-Host "Python 확인: $pythonVersion" -ForegroundColor Green
} catch {
    Write-Host "실패: Python을 실행할 수 없습니다." -ForegroundColor Red
    Write-Fix "Python이 설치되어 있지 않거나 PATH에 없습니다." "Python 3.11 이상을 설치하고 `python -m pip install -e .`를 실행하세요."
    exit 1
}

if (-not $SkipNotepad) {
    $allPassed = (Invoke-JarvisStep `
        -Name "메모장 열기 테스트" `
        -Arguments 'run notepad' `
        -Cause "notepad 실행이 차단되었거나 Windows 기본 앱 실행에 실패했습니다." `
        -Fix "명령 프롬프트에서 `notepad`를 직접 실행해 보고, 보안 프로그램 차단 여부를 확인하세요.") -and $allPassed
}

$beforePdfCount = 0
if (Test-Path $GeneratedDir) {
    $beforePdfCount = @(Get-ChildItem $GeneratedDir -Filter "*.pdf" -File -ErrorAction SilentlyContinue).Count
}
$allPassed = (Invoke-JarvisStep `
    -Name "PDF 생성 테스트" `
    -Arguments 'pdf "Windows 실행 테스트"' `
    -Cause "문서 생성 폴더에 쓰기 권한이 없거나 경로 생성에 실패했습니다." `
    -Fix "`Jarvis\Documents\Generated` 폴더 권한을 확인하고 다시 실행하세요.") -and $allPassed
$afterPdfCount = 0
if (Test-Path $GeneratedDir) {
    $afterPdfCount = @(Get-ChildItem $GeneratedDir -Filter "*.pdf" -File -ErrorAction SilentlyContinue).Count
}
if ($afterPdfCount -le $beforePdfCount) {
    Write-Host "실패: PDF 파일 증가를 확인하지 못했습니다." -ForegroundColor Red
    Write-Fix "PDF 생성 명령은 성공했지만 파일 확인에 실패했습니다." "`Jarvis\Documents\Generated` 폴더에 PDF가 생성되었는지 확인하세요."
    $allPassed = $false
}

$allPassed = (Invoke-JarvisStep `
    -Name "다운로드 폴더 정리 테스트" `
    -Arguments 'organize' `
    -Cause "Downloads 폴더 생성 또는 파일 이동 권한이 부족합니다." `
    -Fix "`Jarvis\Downloads` 폴더 권한을 확인하세요.") -and $allPassed

$allPassed = (Invoke-JarvisStep `
    -Name "인터넷 검색 테스트" `
    -Arguments 'web "Jarvis Windows 테스트"' `
    -Cause "기본 브라우저가 설정되어 있지 않거나 URL 열기가 차단되었습니다." `
    -Fix "Windows 기본 브라우저 설정을 확인하고 `start https://www.google.com`을 실행해 보세요.") -and $allPassed

$allPassed = (Invoke-JarvisStep `
    -Name "장기 기억 저장/불러오기 테스트" `
    -Arguments 'memory' `
    -Cause "SQLite Memory DB 생성 또는 읽기에 실패했습니다." `
    -Fix "`Jarvis\Memory` 폴더 쓰기 권한을 확인하고, 잠긴 DB 파일이 있으면 Jarvis를 종료한 뒤 다시 실행하세요.") -and $allPassed

Write-Step "결과"
if ($allPassed) {
    Write-Host "모든 Windows 실행 테스트가 통과했습니다." -ForegroundColor Green
    exit 0
}

Write-Host "일부 Windows 실행 테스트가 실패했습니다. 위의 원인과 해결 방법을 확인하세요." -ForegroundColor Red
exit 1
