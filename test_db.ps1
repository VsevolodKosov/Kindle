param(
    [string]$task = ""
)

$composeFile = "./docker/docker-compose.test-db.yml"

switch ($task) {
    "up" {
        Write-Host "Starting test database..."
        docker-compose -f $composeFile up -d kindle_db_test
        break
    }
    "down" {
        Write-Host "Stopping and removing test database container..."
        docker-compose -f $composeFile down -v --remove-orphans
        break
    }
    "logs" {
        Write-Host "Showing logs for test database..."
        docker-compose -f $composeFile logs -f kindle_db_test
        break
    }
    default {
        Write-Host "Available commands:"
        Write-Host "  up    - Start test database"
        Write-Host "  down  - Stop and delete test database with volume"
        Write-Host "  logs  - Show logs for test database"
    }
}
