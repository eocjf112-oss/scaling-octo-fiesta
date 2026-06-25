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
$script:NotifyIcon = $null

Add-Type -AssemblyName System.Windows.Forms
Add-Type -AssemblyName System.Drawing
[System.Windows.Forms.Application]::EnableVisualStyles()

function Start-JarvisConsole {
    param([string]$Arguments)

    $command = "`"$JarvisBat`" $Arguments"
    Start-Process -FilePath "cmd.exe" -ArgumentList "/c $command & pause"
}

function Start-JarvisGui {
    param([switch]$Settings)

    $args = "-NoProfile -ExecutionPolicy Bypass -STA -File `"$GuiScript`""
    if ($Settings) {
        $args = "$args -Settings"
    }
    Start-Process -FilePath "powershell.exe" -ArgumentList $args
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

function New-MenuItem {
    param(
        [string]$Text,
        [scriptblock]$Action
    )

    $item = New-Object System.Windows.Forms.ToolStripMenuItem
    $item.Text = $Text
    $item.add_Click($Action)
    return $item
}

function Add-MenuItem {
    param(
        [System.Windows.Forms.ToolStripItemCollection]$Items,
        [string]$Text,
        [scriptblock]$Action
    )

    $item = New-MenuItem -Text $Text -Action $Action
    [void]$Items.Add($item)
    return $item
}

function Add-Separator {
    param([System.Windows.Forms.ToolStripItemCollection]$Items)

    $separator = New-Object System.Windows.Forms.ToolStripSeparator
    [void]$Items.Add($separator)
}

function Stop-JarvisTray {
    Stop-VoiceListener
    if ($script:NotifyIcon) {
        $script:NotifyIcon.Visible = $false
        $script:NotifyIcon.Dispose()
    }
    [System.Windows.Forms.Application]::Exit()
}

$menu = New-Object System.Windows.Forms.ContextMenuStrip

Add-MenuItem -Items $menu.Items -Text "Open Control Panel" -Action { Start-JarvisGui } | Out-Null
Add-MenuItem -Items $menu.Items -Text "Open Settings" -Action { Start-JarvisGui -Settings } | Out-Null
Add-Separator -Items $menu.Items

Add-MenuItem -Items $menu.Items -Text "Status" -Action { Start-JarvisConsole "test" } | Out-Null
Add-MenuItem -Items $menu.Items -Text "Memory Status" -Action { Start-JarvisConsole "memory" } | Out-Null
Add-MenuItem -Items $menu.Items -Text "Start Voice Listener" -Action { Start-VoiceListener } | Out-Null
Add-MenuItem -Items $menu.Items -Text "Stop Voice Listener" -Action { Stop-VoiceListener } | Out-Null
Add-Separator -Items $menu.Items

$testMenu = New-Object System.Windows.Forms.ToolStripMenuItem
$testMenu.Text = "Test Menu"
Add-MenuItem -Items $testMenu.DropDownItems -Text "Open Notepad" -Action { Start-JarvisConsole "run notepad" } | Out-Null
Add-MenuItem -Items $testMenu.DropDownItems -Text "Open Calculator" -Action { Start-JarvisConsole "calc" } | Out-Null
Add-MenuItem -Items $testMenu.DropDownItems -Text "Create PDF" -Action { Start-JarvisConsole "pdf tray-test" } | Out-Null
Add-MenuItem -Items $testMenu.DropDownItems -Text "Create Excel" -Action { Start-JarvisConsole "excel tray-test" } | Out-Null
Add-MenuItem -Items $testMenu.DropDownItems -Text "Create Word" -Action { Start-JarvisConsole "word tray-test" } | Out-Null
Add-MenuItem -Items $testMenu.DropDownItems -Text "Organize Downloads" -Action { Start-JarvisConsole "organize" } | Out-Null
Add-MenuItem -Items $testMenu.DropDownItems -Text "Web Search" -Action { Start-JarvisConsole "web Jarvis usage" } | Out-Null
Add-MenuItem -Items $testMenu.DropDownItems -Text "Save Memory Test" -Action { Start-JarvisConsole "memory test from tray" } | Out-Null
Add-MenuItem -Items $testMenu.DropDownItems -Text "Check Memory" -Action { Start-JarvisConsole "memory" } | Out-Null
[void]$menu.Items.Add($testMenu)
Add-Separator -Items $menu.Items

Add-MenuItem -Items $menu.Items -Text "Enable Startup" -Action {
    Start-Process -FilePath "powershell.exe" -ArgumentList "-NoProfile -ExecutionPolicy Bypass -File `"$StartupScript`" -Action install"
} | Out-Null
Add-MenuItem -Items $menu.Items -Text "Disable Startup" -Action {
    Start-Process -FilePath "powershell.exe" -ArgumentList "-NoProfile -ExecutionPolicy Bypass -File `"$StartupScript`" -Action remove"
} | Out-Null
Add-Separator -Items $menu.Items

Add-MenuItem -Items $menu.Items -Text "Exit Jarvis" -Action { Stop-JarvisTray } | Out-Null

$script:NotifyIcon = New-Object System.Windows.Forms.NotifyIcon
$script:NotifyIcon.Icon = [System.Drawing.SystemIcons]::Application
$script:NotifyIcon.Text = "Jarvis - Ready"
$script:NotifyIcon.ContextMenuStrip = $menu
$script:NotifyIcon.Visible = $true
$script:NotifyIcon.ShowBalloonTip(3000, "Jarvis", "Jarvis is running in the system tray.", [System.Windows.Forms.ToolTipIcon]::Info)
$script:NotifyIcon.add_DoubleClick({ Start-JarvisGui })

if (-not $NoVoice) {
    Start-VoiceListener
}

[System.Windows.Forms.Application]::Run()
