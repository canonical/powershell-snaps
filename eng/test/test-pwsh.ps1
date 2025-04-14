# Set error action preference to stop on errors
$ErrorActionPreference = 'Stop'
try {
    cd pwsh-repo

    Import-Module ./build.psm1
    Restore-PSOptions -PSOptionsPath /snap/powershell*/current/opt/powershell/psoptions.json

    $options = (Get-PSOptions)
    $options.Output = (find /snap/powershell*/current/opt/powershell -type f -name pwsh)

    Set-PSOptions $options
    Start-PSPester -ThrowOnFailure
} catch {
    Write-Error "An error occurred: $_"
    exit 1
}
