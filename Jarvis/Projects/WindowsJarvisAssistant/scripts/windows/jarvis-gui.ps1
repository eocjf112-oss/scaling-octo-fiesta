param(
    [switch]$Settings
)

$ErrorActionPreference = "Stop"
$ProjectRoot = Resolve-Path (Join-Path $PSScriptRoot "..\..")
$WorkspaceRoot = Resolve-Path (Join-Path $ProjectRoot "..\..")
$JarvisBat = Join-Path $ProjectRoot "Jarvis.bat"
$EnvFile = Join-Path $ProjectRoot ".env"
$EnvExample = Join-Path $ProjectRoot ".env.example"

Add-Type -AssemblyName System.Windows.Forms
Add-Type -AssemblyName System.Drawing
[System.Windows.Forms.Application]::EnableVisualStyles()

function Ensure-EnvFile {
    if (-not (Test-Path $EnvFile) -and (Test-Path $EnvExample)) {
        Copy-Item $EnvExample $EnvFile
    }
}

function Read-EnvMap {
    Ensure-EnvFile
    $map = @{}
    if (Test-Path $EnvFile) {
        foreach ($line in Get-Content $EnvFile -Encoding UTF8) {
            if ($line.Trim().StartsWith("#") -or -not $line.Contains("=")) {
                continue
            }
            $parts = $line.Split("=", 2)
            $map[$parts[0].Trim()] = $parts[1].Trim()
        }
    }
    return $map
}

function Write-EnvMap {
    param([hashtable]$Updates)
    Ensure-EnvFile
    $known = @{}
    $lines = New-Object System.Collections.Generic.List[string]
    foreach ($line in Get-Content $EnvFile -Encoding UTF8) {
        if ($line.Trim().StartsWith("#") -or -not $line.Contains("=")) {
            $lines.Add($line)
            continue
        }
        $parts = $line.Split("=", 2)
        $key = $parts[0].Trim()
        if ($Updates.ContainsKey($key)) {
            $lines.Add("$key=$($Updates[$key])")
            $known[$key] = $true
        } else {
            $lines.Add($line)
        }
    }
    foreach ($key in $Updates.Keys) {
        if (-not $known.ContainsKey($key)) {
            $lines.Add("$key=$($Updates[$key])")
        }
    }
    Set-Content -Path $EnvFile -Value $lines -Encoding UTF8
}

function Invoke-JarvisCommand {
    param([string]$Arguments)
    Start-Process -FilePath "cmd.exe" -ArgumentList "/c `"`"$JarvisBat`" $Arguments & pause`""
}

function New-Button {
    param(
        [string]$Text,
        [int]$X,
        [int]$Y,
        [scriptblock]$Action
    )
    $button = New-Object System.Windows.Forms.Button
    $button.Text = $Text
    $button.Location = New-Object System.Drawing.Point($X, $Y)
    $button.Size = New-Object System.Drawing.Size(180, 42)
    $button.Add_Click($Action)
    return $button
}

function Select-Folder {
    param([System.Windows.Forms.TextBox]$Target)
    $dialog = New-Object System.Windows.Forms.FolderBrowserDialog
    if ($Target.Text) {
        $dialog.SelectedPath = $Target.Text
    }
    if ($dialog.ShowDialog() -eq [System.Windows.Forms.DialogResult]::OK) {
        $Target.Text = $dialog.SelectedPath
    }
}

function Select-MemoryDb {
    param([System.Windows.Forms.TextBox]$Target)
    $dialog = New-Object System.Windows.Forms.SaveFileDialog
    $dialog.Filter = "SQLite DB (*.sqlite3)|*.sqlite3|All files (*.*)|*.*"
    $dialog.FileName = "jarvis_memory.sqlite3"
    if ($Target.Text) {
        $dialog.InitialDirectory = Split-Path $Target.Text -Parent
        $dialog.FileName = Split-Path $Target.Text -Leaf
    }
    if ($dialog.ShowDialog() -eq [System.Windows.Forms.DialogResult]::OK) {
        $Target.Text = $dialog.FileName
    }
}

function Show-SettingsForm {
    $envMap = Read-EnvMap
    $form = New-Object System.Windows.Forms.Form
    $form.Text = "Jarvis 설정"
    $form.Size = New-Object System.Drawing.Size(720, 330)
    $form.StartPosition = "CenterScreen"

    $labels = @(
        @("Memory DB", "JARVIS_MEMORY_DB_PATH", 20, 30),
        @("다운로드 폴더", "JARVIS_DOWNLOADS_DIR", 20, 90),
        @("프로젝트 폴더", "JARVIS_PROJECTS_DIR", 20, 150)
    )
    $textBoxes = @{}
    foreach ($item in $labels) {
        $label = New-Object System.Windows.Forms.Label
        $label.Text = $item[0]
        $label.Location = New-Object System.Drawing.Point($item[2], $item[3])
        $label.Size = New-Object System.Drawing.Size(110, 24)
        $form.Controls.Add($label)

        $textBox = New-Object System.Windows.Forms.TextBox
        $textBox.Location = New-Object System.Drawing.Point(140, $item[3])
        $textBox.Size = New-Object System.Drawing.Size(430, 24)
        $textBox.Text = $envMap[$item[1]]
        $form.Controls.Add($textBox)
        $textBoxes[$item[1]] = $textBox

        $browse = New-Object System.Windows.Forms.Button
        $browse.Text = "찾기"
        $browse.Location = New-Object System.Drawing.Point(585, $item[3] - 2)
        $browse.Size = New-Object System.Drawing.Size(80, 28)
        if ($item[1] -eq "JARVIS_MEMORY_DB_PATH") {
            $browse.Add_Click({ Select-MemoryDb $textBoxes["JARVIS_MEMORY_DB_PATH"] })
        } else {
            $key = $item[1]
            $browse.Add_Click({ Select-Folder $textBoxes[$key] }.GetNewClosure())
        }
        $form.Controls.Add($browse)
    }

    $hint = New-Object System.Windows.Forms.Label
    $hint.Text = "비워 두면 기본값을 사용합니다. 저장 후 새로 실행되는 Jarvis 명령부터 적용됩니다."
    $hint.Location = New-Object System.Drawing.Point(20, 205)
    $hint.Size = New-Object System.Drawing.Size(650, 24)
    $form.Controls.Add($hint)

    $save = New-Object System.Windows.Forms.Button
    $save.Text = "저장"
    $save.Location = New-Object System.Drawing.Point(420, 240)
    $save.Size = New-Object System.Drawing.Size(110, 36)
    $save.Add_Click({
        Write-EnvMap @{
            "JARVIS_MEMORY_DB_PATH" = $textBoxes["JARVIS_MEMORY_DB_PATH"].Text
            "JARVIS_DOWNLOADS_DIR" = $textBoxes["JARVIS_DOWNLOADS_DIR"].Text
            "JARVIS_PROJECTS_DIR" = $textBoxes["JARVIS_PROJECTS_DIR"].Text
        }
        [System.Windows.Forms.MessageBox]::Show("설정을 저장했습니다.", "Jarvis", "OK", "Information") | Out-Null
        $form.Close()
    })
    $form.Controls.Add($save)

    $cancel = New-Object System.Windows.Forms.Button
    $cancel.Text = "취소"
    $cancel.Location = New-Object System.Drawing.Point(550, 240)
    $cancel.Size = New-Object System.Drawing.Size(110, 36)
    $cancel.Add_Click({ $form.Close() })
    $form.Controls.Add($cancel)

    [void]$form.ShowDialog()
}

function Show-MainForm {
    $form = New-Object System.Windows.Forms.Form
    $form.Text = "Jarvis 제어판"
    $form.Size = New-Object System.Drawing.Size(650, 430)
    $form.StartPosition = "CenterScreen"

    $title = New-Object System.Windows.Forms.Label
    $title.Text = "Jarvis 제어판 - 명령어를 몰라도 버튼으로 실행하세요"
    $title.Location = New-Object System.Drawing.Point(20, 20)
    $title.Size = New-Object System.Drawing.Size(560, 28)
    $title.Font = New-Object System.Drawing.Font("맑은 고딕", 11, [System.Drawing.FontStyle]::Bold)
    $form.Controls.Add($title)

    $buttons = @(
        @("전체 테스트", 20, 70, { Invoke-JarvisCommand "selftest" }),
        @("메모장 열기", 220, 70, { Invoke-JarvisCommand "run notepad" }),
        @("PDF 생성", 420, 70, { Invoke-JarvisCommand "pdf `"GUI 테스트`"" }),
        @("엑셀 생성", 20, 130, { Invoke-JarvisCommand "excel `"GUI 테스트`"" }),
        @("워드 생성", 220, 130, { Invoke-JarvisCommand "word `"GUI 테스트`"" }),
        @("다운로드 정리", 420, 130, { Invoke-JarvisCommand "organize" }),
        @("인터넷 검색", 20, 190, { Invoke-JarvisCommand "web `"Jarvis 사용법`"" }),
        @("장기 기억 보기", 220, 190, { Invoke-JarvisCommand "memory" }),
        @("음성 대기 시작", 420, 190, { Invoke-JarvisCommand "listen" }),
        @("시작 자동 실행 등록", 20, 250, { Invoke-JarvisCommand "startup install" }),
        @("시작 자동 실행 제거", 220, 250, { Invoke-JarvisCommand "startup remove" }),
        @("설정 열기", 420, 250, { Show-SettingsForm })
    )
    foreach ($entry in $buttons) {
        $form.Controls.Add((New-Button $entry[0] $entry[1] $entry[2] $entry[3]))
    }

    $close = New-Object System.Windows.Forms.Button
    $close.Text = "닫기"
    $close.Location = New-Object System.Drawing.Point(480, 330)
    $close.Size = New-Object System.Drawing.Size(120, 36)
    $close.Add_Click({ $form.Close() })
    $form.Controls.Add($close)

    [void]$form.ShowDialog()
}

if ($Settings) {
    Show-SettingsForm
} else {
    Show-MainForm
}
