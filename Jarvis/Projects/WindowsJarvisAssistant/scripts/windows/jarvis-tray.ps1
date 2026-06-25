param(
    [switch]$NoVoice
)

$ErrorActionPreference = "Stop"
$ProjectRoot = Resolve-Path (Join-Path $PSScriptRoot "..\..")
$JarvisBat = Join-Path $ProjectRoot "Jarvis.bat"
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
[void](Add-TrayItem $menu "Jarvis 상태 보기" { Start-JarvisConsole "test" })
[void](Add-TrayItem $menu "Memory 상태 보기" { Start-JarvisConsole "memory" })
[void](Add-TrayItem $menu "음성 리스너 시작" { Start-VoiceListener })
[void](Add-TrayItem $menu "음성 리스너 중지" { Stop-VoiceListener })
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
$notifyIcon.Add_DoubleClick({ Start-JarvisConsole "test" })

if (-not $NoVoice) {
    Start-VoiceListener
}

[System.Windows.Forms.Application]::Run()
