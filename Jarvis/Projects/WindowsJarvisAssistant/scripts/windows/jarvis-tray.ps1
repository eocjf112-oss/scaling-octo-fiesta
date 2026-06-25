param(
    [switch]$NoVoice
)

$ErrorActionPreference = "Stop"
$ProjectRoot = Resolve-Path (Join-Path $PSScriptRoot "..\..")
$JarvisBat = Join-Path $ProjectRoot "Jarvis.bat"
$GuiScript = Join-Path $PSScriptRoot "jarvis-gui.ps1"
$VoiceScript = Join-Path $PSScriptRoot "jarvis-voice.ps1"
$StartupScript = Join-Path $PSScriptRoot "install-startup.ps1"
$script:VoiceProcess = $null

Add-Type -AssemblyName System.Windows.Forms
Add-Type -AssemblyName System.Drawing
[System.Windows.Forms.Application]::EnableVisualStyles()

function Start-JarvisConsole {
    param([string]$Arguments)
    Start-Process -FilePath "cmd.exe" -ArgumentList "/c `"`"$JarvisBat`" $Arguments & pause`""
}

function Start-JarvisGui {
    param([switch]$Settings)
    $arguments = "-NoProfile -ExecutionPolicy Bypass -STA -File `"$GuiScript`""
    if ($Settings) {
        $arguments = "$arguments -Settings"
    }
    Start-Process -FilePath "powershell.exe" -ArgumentList $arguments
}

function Start-VoiceListener {
    if ($script:VoiceProcess -and -not $script:VoiceProcess.HasExited) {
        return
    }
    $script:VoiceProcess = Start-Process `
        -FilePath "powershell.exe" `
        -ArgumentList "-NoProfile -ExecutionPolicy Bypass -File `"$VoiceScript`"" `
        -WindowStyle Minimized `
        -PassThru
}

function Stop-VoiceListener {
    if ($script:VoiceProcess -and -not $script:VoiceProcess.HasExited) {
        $script:VoiceProcess.Kill()
        $script:VoiceProcess.WaitForExit()
    }
}

function Add-TrayItem {
    param(
        [System.Windows.Forms.ContextMenuStrip]$Menu,
        [string]$Text,
        [scriptblock]$Action
    )
    $item = New-Object System.Windows.Forms.ToolStripMenuItem
    $item.Text = $Text
    $item.Add_Click($Action)
    [void]$Menu.Items.Add($item)
    return $item
}

$menu = New-Object System.Windows.Forms.ContextMenuStrip
[void](Add-TrayItem $menu "Jarvis 제어판 열기" { Start-JarvisGui })
[void](Add-TrayItem $menu "설정 열기" { Start-JarvisGui -Settings })
[void]$menu.Items.Add((New-Object System.Windows.Forms.ToolStripSeparator))
[void](Add-TrayItem $menu "Jarvis 상태 보기" { Start-JarvisConsole "test" })
[void](Add-TrayItem $menu "Memory 상태 보기" { Start-JarvisConsole "memory" })
[void](Add-TrayItem $menu "음성 리스너 시작" { Start-VoiceListener })
[void](Add-TrayItem $menu "음성 리스너 중지" { Stop-VoiceListener })
[void]$menu.Items.Add((New-Object System.Windows.Forms.ToolStripSeparator))
$testMenu = New-Object System.Windows.Forms.ToolStripMenuItem
$testMenu.Text = "테스트 메뉴"
[void]$testMenu.DropDownItems.Add("메모장 열기", $null, { Start-JarvisConsole "run notepad" })
[void]$testMenu.DropDownItems.Add("계산기 열기", $null, { Start-JarvisConsole "calc" })
[void]$testMenu.DropDownItems.Add("PDF 생성", $null, { Start-JarvisConsole "pdf `"트레이 테스트`"" })
[void]$testMenu.DropDownItems.Add("엑셀 생성", $null, { Start-JarvisConsole "excel `"트레이 테스트`"" })
[void]$testMenu.DropDownItems.Add("Word 문서 생성", $null, { Start-JarvisConsole "word `"트레이 테스트`"" })
[void]$testMenu.DropDownItems.Add("다운로드 정리", $null, { Start-JarvisConsole "organize" })
[void]$testMenu.DropDownItems.Add("인터넷 검색", $null, { Start-JarvisConsole "web `"Jarvis 사용법`"" })
[void]$testMenu.DropDownItems.Add("장기기억 저장 테스트", $null, { Start-JarvisConsole "`"장기 기억 트레이 테스트`"" })
[void]$testMenu.DropDownItems.Add("장기 기억 확인", $null, { Start-JarvisConsole "memory" })
[void]$menu.Items.Add($testMenu)
[void]$menu.Items.Add((New-Object System.Windows.Forms.ToolStripSeparator))
[void](Add-TrayItem $menu "시작 자동 실행 등록" {
    Start-Process -FilePath "powershell.exe" -ArgumentList "-NoProfile -ExecutionPolicy Bypass -File `"$StartupScript`" -Action install"
})
[void](Add-TrayItem $menu "시작 자동 실행 제거" {
    Start-Process -FilePath "powershell.exe" -ArgumentList "-NoProfile -ExecutionPolicy Bypass -File `"$StartupScript`" -Action remove"
})
[void]$menu.Items.Add((New-Object System.Windows.Forms.ToolStripSeparator))
[void](Add-TrayItem $menu "Jarvis 종료" {
    Stop-VoiceListener
    $notifyIcon.Visible = $false
    $notifyIcon.Dispose()
    [System.Windows.Forms.Application]::Exit()
})

$notifyIcon = New-Object System.Windows.Forms.NotifyIcon
$notifyIcon.Icon = [System.Drawing.SystemIcons]::Application
$notifyIcon.Text = "Jarvis - 자비스 대기 중"
$notifyIcon.ContextMenuStrip = $menu
$notifyIcon.Visible = $true
$notifyIcon.ShowBalloonTip(3000, "Jarvis", "자비스가 시스템 트레이에서 대기 중입니다.", [System.Windows.Forms.ToolTipIcon]::Info)
$notifyIcon.Add_DoubleClick({ Start-JarvisGui })

if (-not $NoVoice) {
    Start-VoiceListener
}

[System.Windows.Forms.Application]::Run()
