param(
    [string]$EventName = "Notification"
)

$statePath = Join-Path $HOME ".claude\notify-state.json"
$now = [DateTimeOffset]::UtcNow.ToUnixTimeSeconds()

if ($EventName -eq "Stop") {
    $msg = "Task completed."
    $soundPath = "C:\Windows\Media\Windows Notify System Generic.wav"
    $cooldownSeconds = 2
} else {
    $msg = "Needs your attention."
    $soundPath = "C:\Windows\Media\Windows Notify System Generic.wav"
    $cooldownSeconds = 20
}

# Suppress duplicate repeated notifications inside cooldown window
try {
    if (Test-Path $statePath) {
        $state = Get-Content $statePath -Raw | ConvertFrom-Json
        if ($state.lastEvent -eq $EventName -and (($now - [int64]$state.lastTimestamp) -lt $cooldownSeconds)) {
            exit 0
        }
    }
} catch {
    # ignore bad state file and continue
}

# Persist latest event state
try {
    @{ lastEvent = $EventName; lastTimestamp = $now } | ConvertTo-Json | Set-Content -Path $statePath -Encoding UTF8
} catch {
    # ignore state persistence failure
}

# Play sound and show auto-closing popup
try {
    $player = New-Object System.Media.SoundPlayer($soundPath)
    $player.Play()
} catch {
    [console]::beep(880, 250)
}

try {
    $wshell = New-Object -ComObject Wscript.Shell
    # 64 = Information icon. Auto-closes after 3 seconds.
    $wshell.Popup($msg, 3, "Claude Code", 64) | Out-Null
} catch {
    [System.Reflection.Assembly]::LoadWithPartialName("System.Windows.Forms") | Out-Null
    [System.Windows.Forms.MessageBox]::Show($msg, "Claude Code", [System.Windows.Forms.MessageBoxButtons]::OK, [System.Windows.Forms.MessageBoxIcon]::Information) | Out-Null
}
