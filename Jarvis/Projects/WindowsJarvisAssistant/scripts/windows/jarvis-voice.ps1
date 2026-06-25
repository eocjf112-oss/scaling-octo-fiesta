param(
    [switch]$Once
)

$ErrorActionPreference = "Stop"
$ProjectRoot = Resolve-Path (Join-Path $PSScriptRoot "..\..")
$JarvisBat = Join-Path $ProjectRoot "Jarvis.bat"

Add-Type -AssemblyName System.Speech

function New-Recognizer {
    $recognizer = New-Object System.Speech.Recognition.SpeechRecognitionEngine
    $recognizer.SetInputToDefaultAudioDevice()
    return $recognizer
}

function Speak-Jarvis {
    param([string]$Text)
    $speaker = New-Object System.Speech.Synthesis.SpeechSynthesizer
    $speaker.SpeakAsync($Text) | Out-Null
}

function Wait-WakeWord {
    $recognizer = New-Recognizer
    $choices = New-Object System.Speech.Recognition.Choices
    $choices.Add("자비스") | Out-Null
    $choices.Add("jarvis") | Out-Null
    $grammarBuilder = New-Object System.Speech.Recognition.GrammarBuilder
    $grammarBuilder.Append($choices)
    $grammar = New-Object System.Speech.Recognition.Grammar($grammarBuilder)
    $recognizer.LoadGrammar($grammar)
    Write-Host "Jarvis 음성 대기 중입니다. '자비스'라고 말하세요."
    $result = $recognizer.Recognize()
    $recognizer.Dispose()
    return $null -ne $result
}

function Wait-Command {
    $recognizer = New-Recognizer
    $grammar = New-Object System.Speech.Recognition.DictationGrammar
    $recognizer.LoadGrammar($grammar)
    Write-Host "명령을 말씀하세요."
    Speak-Jarvis "네, 말씀하세요."
    $result = $recognizer.Recognize([TimeSpan]::FromSeconds(10))
    $recognizer.Dispose()
    if ($null -eq $result) {
        return ""
    }
    return $result.Text
}

function Invoke-JarvisVoiceCommand {
    param([string]$Command)

    $normalized = $Command.ToLowerInvariant()
    if ($normalized -match "메모장|notepad") {
        & $JarvisBat run notepad
        return
    }
    if ($normalized -match "엑셀|excel") {
        & $JarvisBat excel $Command
        return
    }
    if ($normalized -match "워드|word") {
        & $JarvisBat word $Command
        return
    }
    if ($normalized -match "pdf|피디에프") {
        & $JarvisBat pdf $Command
        return
    }
    if ($normalized -match "다운로드.*정리|정리.*다운로드|organize") {
        & $JarvisBat organize
        return
    }
    if ($normalized -match "인터넷|검색|web|google|구글") {
        & $JarvisBat web $Command
        return
    }

    & $JarvisBat $Command
}

do {
    if (Wait-WakeWord) {
        $command = Wait-Command
        if ($command) {
            Write-Host "Jarvis 명령: $command"
            Invoke-JarvisVoiceCommand $command
        } else {
            Write-Host "음성 명령을 인식하지 못했습니다."
            Speak-Jarvis "명령을 인식하지 못했습니다."
        }
    }
} while (-not $Once)
