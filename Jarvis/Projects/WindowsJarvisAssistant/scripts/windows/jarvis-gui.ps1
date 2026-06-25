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
    if ((-not (Test-Path -Path $EnvFile)) -and (Test-Path -Path $EnvExample)) {
        Copy-Item -Path $EnvExample -Destination $EnvFile -Force
    }
}

function Read-EnvMap {
    Ensure-EnvFile
    $map = @{}

    if (Test-Path -Path $EnvFile) {
        $lines = [System.IO.File]::ReadAllLines($EnvFile)
        foreach ($line in $lines) {
            $trimmed = $line.Trim()
            if ($trimmed.Length -eq 0) { continue }
            if ($trimmed.StartsWith("#")) { continue }
            if (-not $line.Contains("=")) { continue }

            $parts = $line.Split(@("="), 2, [System.StringSplitOptions]::None)
            $key = $parts[0].Trim()
            $value = ""
            if ($parts.Length -gt 1) {
                $value = $parts[1].Trim()
            }
            if ($key.Length -gt 0) {
                $map[$key] = $value
            }
        }
    }

    return $map
}

function Write-EnvMap {
    param(
        [hashtable]$Updates
    )

    Ensure-EnvFile
    $known = @{}
    $output = New-Object System.Collections.Generic.List[string]

    if (Test-Path -Path $EnvFile) {
        $lines = [System.IO.File]::ReadAllLines($EnvFile)
        foreach ($line in $lines) {
            $trimmed = $line.Trim()
            if ($trimmed.StartsWith("#") -or (-not $line.Contains("="))) {
                $output.Add($line)
                continue
            }

            $parts = $line.Split(@("="), 2, [System.StringSplitOptions]::None)
            $key = $parts[0].Trim()
            if ($Updates.ContainsKey($key)) {
                $output.Add(("{0}={1}" -f $key, $Updates[$key]))
                $known[$key] = $true
            } else {
                $output.Add($line)
            }
        }
    }

    foreach ($key in $Updates.Keys) {
        if (-not $known.ContainsKey($key)) {
            $output.Add(("{0}={1}" -f $key, $Updates[$key]))
        }
    }

    $utf8NoBom = New-Object System.Text.UTF8Encoding($false)
    [System.IO.File]::WriteAllLines($EnvFile, $output.ToArray(), $utf8NoBom)
}

function Invoke-JarvisCommand {
    param(
        [string]$Arguments
    )

    $cmd = "`"$JarvisBat`" $Arguments"
    Start-Process -FilePath "cmd.exe" -ArgumentList "/c $cmd & pause"
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

function Add-Button {
    param(
        [System.Windows.Forms.Form]$Form,
        [string]$Text,
        [int]$X,
        [int]$Y,
        [scriptblock]$Action
    )

    $button = New-Button -Text $Text -X $X -Y $Y -Action $Action
    [void]$Form.Controls.Add($button)
}

function Select-Folder {
    param(
        [System.Windows.Forms.TextBox]$Target
    )

    $dialog = New-Object System.Windows.Forms.FolderBrowserDialog
    if ($Target.Text -and (Test-Path -Path $Target.Text)) {
        $dialog.SelectedPath = $Target.Text
    }

    if ($dialog.ShowDialog() -eq [System.Windows.Forms.DialogResult]::OK) {
        $Target.Text = $dialog.SelectedPath
    }
}

function Select-MemoryDb {
    param(
        [System.Windows.Forms.TextBox]$Target
    )

    $dialog = New-Object System.Windows.Forms.SaveFileDialog
    $dialog.Filter = "SQLite DB (*.sqlite3)|*.sqlite3|All files (*.*)|*.*"
    $dialog.FileName = "jarvis_memory.sqlite3"

    if ($Target.Text) {
        $parent = Split-Path -Path $Target.Text -Parent
        $leaf = Split-Path -Path $Target.Text -Leaf
        if ($parent -and (Test-Path -Path $parent)) {
            $dialog.InitialDirectory = $parent
        }
        if ($leaf) {
            $dialog.FileName = $leaf
        }
    }

    if ($dialog.ShowDialog() -eq [System.Windows.Forms.DialogResult]::OK) {
        $Target.Text = $dialog.FileName
    }
}

function Show-SettingsForm {
    $envMap = Read-EnvMap

    $form = New-Object System.Windows.Forms.Form
    $form.Text = "Jarvis Settings"
    $form.Size = New-Object System.Drawing.Size(720, 330)
    $form.StartPosition = "CenterScreen"
    $form.FormBorderStyle = "FixedDialog"
    $form.MaximizeBox = $false

    $memoryLabel = New-Object System.Windows.Forms.Label
    $memoryLabel.Text = "Memory DB"
    $memoryLabel.Location = New-Object System.Drawing.Point(20, 30)
    $memoryLabel.Size = New-Object System.Drawing.Size(110, 24)
    [void]$form.Controls.Add($memoryLabel)

    $memoryText = New-Object System.Windows.Forms.TextBox
    $memoryText.Location = New-Object System.Drawing.Point(140, 30)
    $memoryText.Size = New-Object System.Drawing.Size(430, 24)
    $memoryText.Text = $envMap["JARVIS_MEMORY_DB_PATH"]
    [void]$form.Controls.Add($memoryText)

    $memoryBrowse = New-Object System.Windows.Forms.Button
    $memoryBrowse.Text = "Browse"
    $memoryBrowse.Location = New-Object System.Drawing.Point(585, 28)
    $memoryBrowse.Size = New-Object System.Drawing.Size(80, 28)
    $memoryBrowse.Add_Click({ Select-MemoryDb -Target $memoryText })
    [void]$form.Controls.Add($memoryBrowse)

    $downloadLabel = New-Object System.Windows.Forms.Label
    $downloadLabel.Text = "Downloads"
    $downloadLabel.Location = New-Object System.Drawing.Point(20, 90)
    $downloadLabel.Size = New-Object System.Drawing.Size(110, 24)
    [void]$form.Controls.Add($downloadLabel)

    $downloadText = New-Object System.Windows.Forms.TextBox
    $downloadText.Location = New-Object System.Drawing.Point(140, 90)
    $downloadText.Size = New-Object System.Drawing.Size(430, 24)
    $downloadText.Text = $envMap["JARVIS_DOWNLOADS_DIR"]
    [void]$form.Controls.Add($downloadText)

    $downloadBrowse = New-Object System.Windows.Forms.Button
    $downloadBrowse.Text = "Browse"
    $downloadBrowse.Location = New-Object System.Drawing.Point(585, 88)
    $downloadBrowse.Size = New-Object System.Drawing.Size(80, 28)
    $downloadBrowse.Add_Click({ Select-Folder -Target $downloadText })
    [void]$form.Controls.Add($downloadBrowse)

    $projectLabel = New-Object System.Windows.Forms.Label
    $projectLabel.Text = "Projects"
    $projectLabel.Location = New-Object System.Drawing.Point(20, 150)
    $projectLabel.Size = New-Object System.Drawing.Size(110, 24)
    [void]$form.Controls.Add($projectLabel)

    $projectText = New-Object System.Windows.Forms.TextBox
    $projectText.Location = New-Object System.Drawing.Point(140, 150)
    $projectText.Size = New-Object System.Drawing.Size(430, 24)
    $projectText.Text = $envMap["JARVIS_PROJECTS_DIR"]
    [void]$form.Controls.Add($projectText)

    $projectBrowse = New-Object System.Windows.Forms.Button
    $projectBrowse.Text = "Browse"
    $projectBrowse.Location = New-Object System.Drawing.Point(585, 148)
    $projectBrowse.Size = New-Object System.Drawing.Size(80, 28)
    $projectBrowse.Add_Click({ Select-Folder -Target $projectText })
    [void]$form.Controls.Add($projectBrowse)

    $hint = New-Object System.Windows.Forms.Label
    $hint.Text = "Leave blank to use defaults. Changes apply to newly started Jarvis commands."
    $hint.Location = New-Object System.Drawing.Point(20, 205)
    $hint.Size = New-Object System.Drawing.Size(650, 24)
    [void]$form.Controls.Add($hint)

    $save = New-Object System.Windows.Forms.Button
    $save.Text = "Save"
    $save.Location = New-Object System.Drawing.Point(420, 240)
    $save.Size = New-Object System.Drawing.Size(110, 36)
    $save.Add_Click({
        $updates = @{}
        $updates["JARVIS_MEMORY_DB_PATH"] = $memoryText.Text
        $updates["JARVIS_DOWNLOADS_DIR"] = $downloadText.Text
        $updates["JARVIS_PROJECTS_DIR"] = $projectText.Text
        Write-EnvMap -Updates $updates
        [System.Windows.Forms.MessageBox]::Show("Settings saved.", "Jarvis", [System.Windows.Forms.MessageBoxButtons]::OK, [System.Windows.Forms.MessageBoxIcon]::Information) | Out-Null
        $form.Close()
    })
    [void]$form.Controls.Add($save)

    $cancel = New-Object System.Windows.Forms.Button
    $cancel.Text = "Cancel"
    $cancel.Location = New-Object System.Drawing.Point(550, 240)
    $cancel.Size = New-Object System.Drawing.Size(110, 36)
    $cancel.Add_Click({ $form.Close() })
    [void]$form.Controls.Add($cancel)

    [void]$form.ShowDialog()
}

function Show-MainForm {
    $form = New-Object System.Windows.Forms.Form
    $form.Text = "Jarvis Control Panel"
    $form.Size = New-Object System.Drawing.Size(650, 540)
    $form.StartPosition = "CenterScreen"
    $form.FormBorderStyle = "FixedSingle"
    $form.MaximizeBox = $false

    $title = New-Object System.Windows.Forms.Label
    $title.Text = "Jarvis Control Panel"
    $title.Location = New-Object System.Drawing.Point(20, 20)
    $title.Size = New-Object System.Drawing.Size(560, 28)
    $title.Font = New-Object System.Drawing.Font("Segoe UI", 12, [System.Drawing.FontStyle]::Bold)
    [void]$form.Controls.Add($title)

    Add-Button -Form $form -Text "Run Self Test" -X 20 -Y 70 -Action { Invoke-JarvisCommand "selftest" }
    Add-Button -Form $form -Text "Open Notepad" -X 220 -Y 70 -Action { Invoke-JarvisCommand "run notepad" }
    Add-Button -Form $form -Text "Open Calculator" -X 420 -Y 70 -Action { Invoke-JarvisCommand "calc" }

    Add-Button -Form $form -Text "Create PDF" -X 20 -Y 130 -Action { Invoke-JarvisCommand "pdf GUI-test" }
    Add-Button -Form $form -Text "Create Excel" -X 220 -Y 130 -Action { Invoke-JarvisCommand "excel GUI-test" }
    Add-Button -Form $form -Text "Create Word" -X 420 -Y 130 -Action { Invoke-JarvisCommand "word GUI-test" }

    Add-Button -Form $form -Text "Organize Downloads" -X 20 -Y 190 -Action { Invoke-JarvisCommand "organize" }
    Add-Button -Form $form -Text "Web Search" -X 220 -Y 190 -Action { Invoke-JarvisCommand "web Jarvis usage" }
    Add-Button -Form $form -Text "Memory Status" -X 420 -Y 190 -Action { Invoke-JarvisCommand "memory" }

    Add-Button -Form $form -Text "Save Memory Test" -X 20 -Y 250 -Action { Invoke-JarvisCommand "memory test from GUI" }
    Add-Button -Form $form -Text "Start Voice" -X 220 -Y 250 -Action { Invoke-JarvisCommand "listen" }
    Add-Button -Form $form -Text "Settings" -X 420 -Y 250 -Action { Show-SettingsForm }

    Add-Button -Form $form -Text "Enable Startup" -X 20 -Y 310 -Action { Invoke-JarvisCommand "startup install" }
    Add-Button -Form $form -Text "Disable Startup" -X 220 -Y 310 -Action { Invoke-JarvisCommand "startup remove" }

    $commandLabel = New-Object System.Windows.Forms.Label
    $commandLabel.Text = "Command:"
    $commandLabel.Location = New-Object System.Drawing.Point(20, 375)
    $commandLabel.Size = New-Object System.Drawing.Size(100, 24)
    [void]$form.Controls.Add($commandLabel)

    $commandBox = New-Object System.Windows.Forms.TextBox
    $commandBox.Location = New-Object System.Drawing.Point(135, 372)
    $commandBox.Size = New-Object System.Drawing.Size(340, 24)
    $commandBox.Text = "jarvis"
    [void]$form.Controls.Add($commandBox)

    $runCommand = New-Object System.Windows.Forms.Button
    $runCommand.Text = "Run"
    $runCommand.Location = New-Object System.Drawing.Point(490, 368)
    $runCommand.Size = New-Object System.Drawing.Size(110, 32)
    $runCommand.Add_Click({
        $command = $commandBox.Text.Trim()
        if ($command.Length -eq 0) {
            [System.Windows.Forms.MessageBox]::Show("Enter a command first.", "Jarvis", [System.Windows.Forms.MessageBoxButtons]::OK, [System.Windows.Forms.MessageBoxIcon]::Warning) | Out-Null
            return
        }
        if (($command -eq "jarvis") -or ($command -eq "Jarvis")) {
            [System.Windows.Forms.MessageBox]::Show("Jarvis is ready. Click a button or enter a command.", "Jarvis", [System.Windows.Forms.MessageBoxButtons]::OK, [System.Windows.Forms.MessageBoxIcon]::Information) | Out-Null
            return
        }
        Invoke-JarvisCommand ("`"{0}`"" -f $command)
    })
    [void]$form.Controls.Add($runCommand)

    $close = New-Object System.Windows.Forms.Button
    $close.Text = "Close"
    $close.Location = New-Object System.Drawing.Point(480, 440)
    $close.Size = New-Object System.Drawing.Size(120, 36)
    $close.Add_Click({ $form.Close() })
    [void]$form.Controls.Add($close)

    [void]$form.ShowDialog()
}

if ($Settings) {
    Show-SettingsForm
} else {
    Show-MainForm
}
