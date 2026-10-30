<# Reads only the specified mods directory. Emits JSON to stdout; never writes source files. #>
[CmdletBinding()]
param(
    [Parameter(Mandatory = $true)]
    [string]$ModsPath
)
$ErrorActionPreference = 'Stop'
$directory = Get-Item -LiteralPath $ModsPath
if (-not $directory.PSIsContainer) { throw 'ModsPath must be a directory.' }
if ($directory.Attributes -band [IO.FileAttributes]::ReparsePoint) { throw 'Symlink/junction mods directory is not accepted.' }
$files = @()
foreach ($file in (Get-ChildItem -LiteralPath $directory.FullName -File | Sort-Object Name)) {
    if ($file.Name -notmatch '(?i)\.jar(?:\.disabled)?$') { continue }
    if ($file.Attributes -band [IO.FileAttributes]::ReparsePoint) { throw 'Symlink JAR is not accepted.' }
    $before = Get-Item -LiteralPath $file.FullName
    $length = $before.Length
    $stamp = $before.LastWriteTimeUtc.Ticks
    $sha256 = (Get-FileHash -LiteralPath $file.FullName -Algorithm SHA256).Hash.ToLowerInvariant()
    $sha1 = (Get-FileHash -LiteralPath $file.FullName -Algorithm SHA1).Hash.ToLowerInvariant()
    $after = Get-Item -LiteralPath $file.FullName
    if ($length -ne $after.Length -or $stamp -ne $after.LastWriteTimeUtc.Ticks) {
        throw 'A JAR changed during inspection. Close the launcher/game and repeat.'
    }
    $files += [PSCustomObject]@{
        name = $file.Name
        length = $length
        sha256 = $sha256
        sha1 = $sha1
        enabled = -not $file.Name.EndsWith('.disabled', [StringComparison]::OrdinalIgnoreCase)
    }
}
# Do not emit source absolute paths, Windows usernames, secrets, or JAR contents.
[PSCustomObject]@{ schema = 1; files = @($files) } | ConvertTo-Json -Depth 5
