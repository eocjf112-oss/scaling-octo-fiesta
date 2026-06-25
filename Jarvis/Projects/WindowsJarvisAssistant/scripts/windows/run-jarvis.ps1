param(
    [Parameter(Mandatory = $true)]
    [string]$Prompt,

    [ValidateSet("auto", "chatgpt", "claude", "open_interpreter")]
    [string]$Provider = "auto"
)

$ErrorActionPreference = "Stop"

python -m jarvis_assistant --provider $Provider $Prompt
