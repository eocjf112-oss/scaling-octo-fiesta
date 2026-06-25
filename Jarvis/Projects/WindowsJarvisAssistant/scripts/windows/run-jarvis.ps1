param(
    [string]$Prompt,

    [ValidateSet("auto", "local", "windows_automation", "chatgpt", "claude", "open_interpreter")]
    [string]$Provider = "auto",

    [switch]$ConfirmLocalExecution,

    [switch]$VoiceStatus
)

$ErrorActionPreference = "Stop"

if ($VoiceStatus) {
    python -m jarvis_assistant --voice-status
    exit $LASTEXITCODE
}

if (-not $Prompt) {
    $Prompt = "Jarvis 현재 상태를 알려줘"
}

$arguments = @("-m", "jarvis_assistant", "--provider", $Provider)
if ($ConfirmLocalExecution) {
    $arguments += "--confirm-local-execution"
}
$arguments += $Prompt

python @arguments
