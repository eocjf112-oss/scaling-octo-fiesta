param(
    [Parameter(Mandatory = $true)]
    [string]$Prompt,

    [ValidateSet("auto", "chatgpt", "claude", "open_interpreter")]
    [string]$Provider = "auto",

    [switch]$ConfirmLocalExecution
)

$ErrorActionPreference = "Stop"

$arguments = @("-m", "jarvis_assistant", "--provider", $Provider)
if ($ConfirmLocalExecution) {
    $arguments += "--confirm-local-execution"
}
$arguments += $Prompt

python @arguments
