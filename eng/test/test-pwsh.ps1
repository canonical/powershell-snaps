# Set error action preference to stop on errors
$ErrorActionPreference = 'Stop'
try {
    Set-Location pwsh-repo

    Import-Module ./build.psm1
    Restore-PSOptions -PSOptionsPath "/snap/powershell*/current/opt/powershell/psoptions.json"

    $options = (Get-PSOptions)
    $options.Output = (Get-ChildItem -Path "/snap/powershell*/current/opt/powershell" -Recurse -Filter "pwsh").FullName

    # PSPester runs on a noble machine and PowerShell builds on core22 (jammy).
    # Therefore, we need to override the runtime from the options file to match that of the runner
    # to avoid 'nuget restore' issues, since packages like Microsoft.NETCore.App.Runtime targeting
    # linux-s390x and linux-ppc64el are not available on NuGet.org.
    if ($options.Runtime -match 's390x') {
        $options.Runtime = 'ubuntu.24.04-s390x'
    } elseif ($options.Runtime -match 'ppc64le') {
        $options.Runtime = 'ubuntu.24.04-ppc64le'
    }

    Set-PSOptions $options
    Start-PSPester
} catch {
    Write-Error "An error occurred: $_"
    exit 1
}
