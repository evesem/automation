$ErrorActionPreference = 'Stop'

$labDir = Split-Path -Parent $PSScriptRoot
$secretsDir = Join-Path $labDir 'secrets'
New-Item -ItemType Directory -Force -Path $secretsDir | Out-Null

function New-KeyPair {
    param([string]$FileName, [string]$Comment)

    $privatePath = Join-Path $secretsDir $FileName
    if (Test-Path $privatePath) {
        Write-Host "$FileName already exists, reusing it."
    } else {
        & ssh-keygen -q -t ed25519 -N '""' -C $Comment -f $privatePath
        if ($LASTEXITCODE -ne 0) { throw "Failed to generate $FileName" }
    }
    return (Get-Content -Path "$privatePath.pub" -Raw).Trim()
}

$phpKey = New-KeyPair -FileName 'id_ed25519_jenkins_php' -Comment 'jenkins-php'
$ansibleAgentKey = New-KeyPair -FileName 'id_ed25519_jenkins_ansible' -Comment 'jenkins-ansible'
$ansibleToServerKey = New-KeyPair -FileName 'id_ed25519_ansible' -Comment 'ansible-to-test-server'

$envContent = @"
JENKINS_AGENT_SSH_PUBKEY=$phpKey
JENKINS_ANSIBLE_AGENT_SSH_PUBKEY=$ansibleAgentKey
ANSIBLE_PUBLIC_KEY=$ansibleToServerKey
ANSIBLE_PRIVATE_KEY_PATH=./secrets/id_ed25519_ansible
"@

$envPath = Join-Path $labDir '.env'
Set-Content -Path $envPath -Value $envContent -Encoding UTF8
Write-Host "Created $envPath and SSH keys in $secretsDir"
Write-Host 'Private keys are ignored by Git. Never commit them.'
