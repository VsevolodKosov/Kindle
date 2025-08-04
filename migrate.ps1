param(
    [ValidateSet("prod", "test")]
    [string]$env = "prod",

    [ValidateSet("upgrade", "downgrade", "revision")]
    [string]$action = "upgrade",

    [string]$revisionMessage = "auto revision"
)

$env:APP_ENV = $env

Write-Host "Using environment: $env"
Write-Host "Action: $action"

switch ($action) {
    "revision" {
        Write-Host "Generating new revision with message: $revisionMessage"
        alembic revision --autogenerate -m $revisionMessage
        break
    }
    "upgrade" {
        Write-Host "Upgrading database to head"
        alembic upgrade head
        break
    }
    "downgrade" {
        Write-Host "Downgrading database by one revision"
        alembic downgrade -1
        break
    }
    default {
        Write-Host "Unknown action. Supported actions: revision, upgrade, downgrade"
        break
    }
}
