# ============================================================
# port-forward.ps1 — Відкрити port-forward для всіх сервісів
# Запускати після deploy.ps1
# ============================================================

Write-Host "Starting port-forwarding for all services..." -ForegroundColor Cyan
Write-Host "Services will be available at:"
Write-Host "  Asset Service:       http://localhost:8001"
Write-Host "  Transaction Service: http://localhost:8002"
Write-Host "  Portfolio Service:   http://localhost:8003"
Write-Host "  Analytics Service:   http://localhost:8004"
Write-Host ""
Write-Host "Press Ctrl+C to stop all port-forwards" -ForegroundColor Yellow

# Start all port-forwards in background jobs
$jobs = @(
    Start-Job { kubectl port-forward service/asset-service 8001:8000 }
    Start-Job { kubectl port-forward service/portfolio-service 8003:8000 }
    Start-Job { kubectl port-forward service/transaction-service 8002:8000 }
    Start-Job { kubectl port-forward service/analytics-service 8004:8000 }
)

Write-Host "Port-forwarding started (background jobs: $($jobs.Id -join ', '))"
Write-Host ""
Write-Host "Quick health checks:"
Start-Sleep -Seconds 3

try {
    $checks = @(
        @{ Name="Asset Service";       Url="http://localhost:8001/health" }
        @{ Name="Portfolio Service";   Url="http://localhost:8003/health" }
        @{ Name="Transaction Service"; Url="http://localhost:8002/health" }
        @{ Name="Analytics Service";   Url="http://localhost:8004/health" }
    )
    foreach ($check in $checks) {
        try {
            $response = Invoke-WebRequest -Uri $check.Url -TimeoutSec 5 -UseBasicParsing
            Write-Host "  ✓ $($check.Name): $($response.StatusCode)" -ForegroundColor Green
        } catch {
            Write-Host "  ✗ $($check.Name): Not ready yet" -ForegroundColor Red
        }
    }
} catch {}

Write-Host ""
Write-Host "Waiting... Press Ctrl+C to stop." -ForegroundColor Gray
try {
    Wait-Job $jobs | Out-Null
} finally {
    $jobs | Stop-Job
    $jobs | Remove-Job
}
