param(
    [string]$task = ""
)

$composeFile = "./docker/docker-compose.db.yml"

switch ($task) {
    "up_all_db" {
        Write-Host "Starting all database services..."
        docker-compose -f $composeFile up -d
        break
    }
    "down_all_db" {
        Write-Host "Stopping all database services..."
        docker-compose -f $composeFile stop
        Write-Host "Removing only test database container..."
        docker-compose -f $composeFile rm -f kindle_db_test
        break
    }
    "up_prod_db" {
        Write-Host "Starting production database..."
        docker-compose -f $composeFile up -d kindle_db_prod
        break
    }
    "down_prod_db" {
        Write-Host "Stopping production database..."
        docker-compose -f $composeFile stop kindle_db_prod
        break
    }
    "remove_prod_container" {
        Write-Host "Removing production database container (volume will be kept)..."
        docker-compose -f $composeFile rm -f kindle_db_prod
        break
    }
    "up_test_db" {
        Write-Host "Starting test database..."
        docker-compose -f $composeFile up -d kindle_db_test
        break
    }
    "down_test_db" {
        Write-Host "Stopping and removing test database container..."
        docker-compose -f $composeFile down -v --remove-orphans
        break
    }
    "logs_all_db" {
        Write-Host "Showing logs for all databases..."
        docker-compose -f $composeFile logs -f
        break
    }
    "logs_prod_db" {
        Write-Host "Showing logs for production database..."
        docker-compose -f $composeFile logs -f kindle_db_prod
        break
    }
    "logs_test_db" {
        Write-Host "Showing logs for test database..."
        docker-compose -f $composeFile logs -f kindle_db_test
        break
    }
    default {
        Write-Host "Available commands:"
        Write-Host "  up_all_db             - Start all database services"
        Write-Host "  down_all_db           - Stop all services, remove only test DB"
        Write-Host "  up_prod_db            - Start production database"
        Write-Host "  down_prod_db          - Stop production database"
        Write-Host "  remove_prod_container - Remove production DB container (keep data)"
        Write-Host "  up_test_db            - Start test database"
        Write-Host "  down_test_db          - Stop and delete test database with volume"
        Write-Host "  logs_all_db           - Show logs for all databases"
        Write-Host "  logs_prod_db          - Show logs for production database"
        Write-Host "  logs_test_db          - Show logs for test database"
    }
}
