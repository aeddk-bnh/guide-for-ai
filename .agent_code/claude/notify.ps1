param(
    [string]$EventName = "Notification"
)

# Determine message based on event
if ($EventName -eq "Stop") {
    $msg = "Task completed."
} else {
    $msg = "Needs your attention."
}

# 1. Play Sound (System standard notification sound)
try {
    $player = New-Object System.Media.SoundPlayer("C:\Windows\Media\Windows Notify System Generic.wav")
    $player.PlaySync()
} catch {
    # Fallback beep if wav file missing
    [console]::beep(880, 250)
}

# 2. Show UI (MessageBox with Information icon for cleaner look)
[System.Reflection.Assembly]::LoadWithPartialName("System.Windows.Forms") | Out-Null
[System.Windows.Forms.MessageBox]::Show($msg, "Claude Code", [System.Windows.Forms.MessageBoxButtons]::OK, [System.Windows.Forms.MessageBoxIcon]::Information) | Out-Null
