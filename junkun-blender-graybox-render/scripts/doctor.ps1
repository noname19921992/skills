param(
    [string]$BridgeDir
)

$pythonCandidates = @()
foreach ($name in @('python', 'python3', 'py')) {
    $command = Get-Command $name -ErrorAction SilentlyContinue
    if ($command) {
        $version = & $command.Source --version 2>&1 | Out-String
        if ($LASTEXITCODE -eq 0) {
            $pythonCandidates += [ordered]@{ command = $command.Source; version = $version.Trim() }
        }
    }
}

$blenderCandidates = @()
$blenderCommand = Get-Command blender -ErrorAction SilentlyContinue
if ($blenderCommand) { $blenderCandidates += $blenderCommand.Source }
$commonRoot = Join-Path $env:ProgramFiles 'Blender Foundation'
if (Test-Path -LiteralPath $commonRoot) {
    $blenderCandidates += Get-ChildItem -LiteralPath $commonRoot -Filter blender.exe -File -Recurse -ErrorAction SilentlyContinue |
        ForEach-Object { $_.FullName }
}
$blenderCandidates = @($blenderCandidates | Sort-Object -Unique)

$ffmpegCommand = Get-Command ffmpeg -ErrorAction SilentlyContinue
$processes = @(Get-Process blender -ErrorAction SilentlyContinue | ForEach-Object {
    [ordered]@{ pid = $_.Id; path = $_.Path }
})

$bridge = $null
if ($BridgeDir) {
    $resolved = [System.IO.Path]::GetFullPath($BridgeDir)
    $exists = Test-Path -LiteralPath $resolved
    $queued = @()
    $responses = @()
    $unresolved = @()
    $inflight = $null
    $clientLock = $null
    $writable = $false
    $writeError = $null
    $aclOwner = $null
    $broadWriteAcl = @()
    if ($exists) {
        $queued = @(Get-ChildItem -LiteralPath (Join-Path $resolved 'requests') -Filter '*.json' -File -ErrorAction SilentlyContinue)
        $responses = @(Get-ChildItem -LiteralPath (Join-Path $resolved 'responses') -Filter '*.json' -File -ErrorAction SilentlyContinue)
        foreach ($stateFile in @(Get-ChildItem -LiteralPath (Join-Path $resolved 'states') -Filter '*.json' -File -ErrorAction SilentlyContinue)) {
            try {
                $state = Get-Content -Raw -LiteralPath $stateFile.FullName | ConvertFrom-Json
                if ($state.state -notin @('completed', 'failed', 'cancelled')) {
                    $unresolved += [ordered]@{ id = $state.id; state = $state.state; updated_at = $state.updated_at }
                }
            } catch {}
        }
        $inflightPath = Join-Path $resolved 'inflight.json'
        if (Test-Path -LiteralPath $inflightPath) {
            try { $inflight = Get-Content -Raw -LiteralPath $inflightPath | ConvertFrom-Json } catch {}
        }
        $clientLockPath = Join-Path $resolved 'client.lock'
        if (Test-Path -LiteralPath $clientLockPath) {
            try { $clientLock = Get-Content -Raw -LiteralPath $clientLockPath | ConvertFrom-Json } catch {}
        }
        try {
            $acl = Get-Acl -LiteralPath $resolved
            $aclOwner = $acl.Owner
            $broadSids = @('S-1-1-0', 'S-1-5-11', 'S-1-5-32-545')
            foreach ($rule in $acl.Access) {
                $sid = $null
                try { $sid = $rule.IdentityReference.Translate([System.Security.Principal.SecurityIdentifier]).Value } catch {}
                $writeMask = [System.Security.AccessControl.FileSystemRights]::WriteData -bor
                    [System.Security.AccessControl.FileSystemRights]::CreateFiles -bor
                    [System.Security.AccessControl.FileSystemRights]::Modify -bor
                    [System.Security.AccessControl.FileSystemRights]::FullControl
                if ($rule.AccessControlType -eq 'Allow' -and $sid -in $broadSids -and ($rule.FileSystemRights -band $writeMask)) {
                    $broadWriteAcl += [ordered]@{ identity = $rule.IdentityReference.Value; sid = $sid; rights = $rule.FileSystemRights.ToString() }
                }
            }
        } catch {}
        $probe = Join-Path $resolved ('.doctor-' + [guid]::NewGuid().ToString('N') + '.tmp')
        try {
            [System.IO.File]::WriteAllText($probe, 'probe')
            Remove-Item -LiteralPath $probe -Force
            $writable = $true
        } catch { $writeError = $_.Exception.Message }
    }
    $lowered = $resolved.ToLowerInvariant()
    $syncLabel = $null
    foreach ($label in @('onedrive', 'dropbox', 'google drive', 'icloud')) {
        if ($lowered.Contains($label)) { $syncLabel = $label; break }
    }
    $networkDrive = $false
    try { $networkDrive = ([System.IO.DriveInfo]::new([System.IO.Path]::GetPathRoot($resolved))).DriveType -eq 'Network' } catch {}
    $bridge = [ordered]@{
        path = $resolved
        exists = $exists
        writable = $writable
        write_error = $writeError
        network_share = $resolved.StartsWith('\\') -or $networkDrive
        sync_directory_warning = $syncLabel
        acl_owner = $aclOwner
        broad_write_acl = $broadWriteAcl
        queued_files = $queued.Count
        response_files = $responses.Count
        inflight = $inflight
        client_lock = $clientLock
        unresolved_states = $unresolved
    }
}

$problems = @()
$warnings = @()
if ($pythonCandidates.Count -eq 0) { $problems += 'No runnable Python command found' }
if ($blenderCandidates.Count -eq 0) { $problems += 'Blender executable not found' }
if (-not $ffmpegCommand) { $warnings += 'FFmpeg not found; PNG review frames still work, but video/contact-sheet helpers are unavailable' }
if ($bridge) {
    if ($bridge.network_share -or $bridge.sync_directory_warning) { $problems += 'Bridge path is not a private local directory' }
    if ($bridge.exists -and -not $bridge.writable) { $problems += 'Bridge directory is not writable' }
    if ($bridge.broad_write_acl.Count -gt 0) { $problems += 'Bridge directory ACL grants broad write access' }
    if ($bridge.client_lock) { $problems += 'Bridge has a client lock; inspect its PID before removing it' }
    if ($bridge.inflight -or $bridge.unresolved_states.Count -gt 0 -or $bridge.queued_files -gt 0) {
        $problems += 'Bridge has unresolved work'
    }
}

[ordered]@{
    ok = $problems.Count -eq 0
    python = $pythonCandidates
    blender_executables = $blenderCandidates
    blender_processes = $processes
    ffmpeg = if ($ffmpegCommand) { $ffmpegCommand.Source } else { $null }
    bridge = $bridge
    problems = $problems
    warnings = $warnings
} | ConvertTo-Json -Depth 8

if ($problems.Count -gt 0) { exit 1 }
