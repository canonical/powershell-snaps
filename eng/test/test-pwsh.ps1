# Set error action preference to stop on errors
$ErrorActionPreference = 'Stop'
try {
    Set-Location pwsh-repo

    Import-Module ./build.psm1
    Restore-PSOptions -PSOptionsPath /snap/powershell*/current/opt/powershell/psoptions.json

    $options = (Get-PSOptions)
    $architecture = [System.Runtime.InteropServices.RuntimeInformation]::OSArchitecture

    if ($architecture -eq 'S390x') {
        $options.Runtime = 'ubuntu.24.04-s390x'
        $options.Output = (find /snap/powershell*/current/opt/powershell -type f -name pwsh.dll)
    } elseif ($architecture -eq 'Ppc64le') {
        $options.Runtime = 'ubuntu.24.04-ppc64le'
        $options.Output = (find /snap/powershell*/current/opt/powershell -type f -name pwsh.dll)
    } else {
        $options.Output = (find /snap/powershell*/current/opt/powershell -type f -name pwsh)
    }

    Set-PSOptions $options
    Start-PSPester
} catch {
    Write-Error "An error occurred: $_"
    exit 1
}
