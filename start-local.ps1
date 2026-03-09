# Local Development Startup Script
# Run this to start all services for local testing (without Docker)

Write-Host "=== Investment Portfolio Management System ===" -ForegroundColor Cyan
Write-Host ""

# Check if PostgreSQL and Redis are running
Write-Host "Checking prerequisites..." -ForegroundColor Yellow

# Function to check if a port is available
function Test-Port {
    param($Port)
    $connection = New-Object System.Net.Sockets.TcpClient
    try {
        $connection.Connect("localhost", $Port)
        $connection.Close()
        return $true
    }
    catch {
        return $false
    }
}

# Check PostgreSQL (port 5432)
if (Test-Port 5432) {
    Write-Host "✓ PostgreSQL is running on port 5432" -ForegroundColor Green
} else {
    Write-Host "✗ PostgreSQL is NOT running on port 5432" -ForegroundColor Red
    Write-Host "  Please start PostgreSQL before running services" -ForegroundColor Yellow
    Write-Host "  Create databases: asset_db, transaction_db, portfolio_db" -ForegroundColor Yellow
}

# Check Redis (port 6379)
if (Test-Port 6379) {
    Write-Host "✓ Redis is running on port 6379" -ForegroundColor Green
} else {
    Write-Host "✗ Redis is NOT running on port 6379" -ForegroundColor Red
    Write-Host "  Please start Redis before running Asset Service" -ForegroundColor Yellow
}

Write-Host ""
Write-Host "=== Quick Setup Instructions ===" -ForegroundColor Cyan
Write-Host ""
Write-Host "Option 1: Use Docker Compose (Recommended)" -ForegroundColor Yellow
Write-Host "  docker-compose up --build" -ForegroundColor White
Write-Host ""
Write-Host "Option 2: Run Locally" -ForegroundColor Yellow
Write-Host "  1. Start PostgreSQL and create databases:" -ForegroundColor White
Write-Host "     CREATE DATABASE asset_db;" -ForegroundColor Gray
Write-Host "     CREATE DATABASE transaction_db;" -ForegroundColor Gray
Write-Host "     CREATE DATABASE portfolio_db;" -ForegroundColor Gray
Write-Host ""
Write-Host "  2. Start Redis" -ForegroundColor White
Write-Host ""
Write-Host "  3. Open 4 separate PowerShell windows and run:" -ForegroundColor White
Write-Host ""
Write-Host "     Window 1 (Asset Service):" -ForegroundColor Cyan
Write-Host "     cd asset-service" -ForegroundColor Gray
Write-Host "     `$env:DATABASE_URL=`"postgresql+asyncpg://postgres:postgres@localhost:5432/asset_db`"" -ForegroundColor Gray
Write-Host "     `$env:REDIS_URL=`"redis://localhost:6379/0`"" -ForegroundColor Gray
Write-Host "     ..\.venv\Scripts\Activate.ps1" -ForegroundColor Gray
Write-Host "     python main.py" -ForegroundColor Gray
Write-Host ""
Write-Host "     Window 2 (Transaction Service):" -ForegroundColor Cyan
Write-Host "     cd transaction-service" -ForegroundColor Gray
Write-Host "     `$env:DATABASE_URL=`"postgresql+asyncpg://postgres:postgres@localhost:5432/transaction_db`"" -ForegroundColor Gray
Write-Host "     ..\.venv\Scripts\Activate.ps1" -ForegroundColor Gray
Write-Host "     python main.py" -ForegroundColor Gray
Write-Host ""
Write-Host "     Window 3 (Portfolio Service):" -ForegroundColor Cyan
Write-Host "     cd portfolio-service" -ForegroundColor Gray
Write-Host "     `$env:DATABASE_URL=`"postgresql+asyncpg://postgres:postgres@localhost:5432/portfolio_db`"" -ForegroundColor Gray
Write-Host "     ..\.venv\Scripts\Activate.ps1" -ForegroundColor Gray
Write-Host "     python main.py" -ForegroundColor Gray
Write-Host ""
Write-Host "     Window 4 (Analytics Service):" -ForegroundColor Cyan
Write-Host "     cd analytics-service" -ForegroundColor Gray
Write-Host "     ..\.venv\Scripts\Activate.ps1" -ForegroundColor Gray
Write-Host "     python main.py" -ForegroundColor Gray
Write-Host ""
Write-Host "=== Service URLs ===" -ForegroundColor Cyan
Write-Host "  Asset Service:       http://localhost:8001" -ForegroundColor White
Write-Host "  Transaction Service: http://localhost:8002" -ForegroundColor White
Write-Host "  Portfolio Service:   http://localhost:8003" -ForegroundColor White
Write-Host "  Analytics Service:   http://localhost:8004" -ForegroundColor White
Write-Host ""
Write-Host "=== API Documentation ===" -ForegroundColor Cyan
Write-Host "  Asset Service:       http://localhost:8001/docs" -ForegroundColor White
Write-Host "  Transaction Service: http://localhost:8002/docs" -ForegroundColor White
Write-Host "  Portfolio Service:   http://localhost:8003/docs" -ForegroundColor White
Write-Host "  Analytics Service:   http://localhost:8004/docs" -ForegroundColor White
Write-Host ""
Write-Host "Press any key to exit..." -ForegroundColor Gray
$null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")
