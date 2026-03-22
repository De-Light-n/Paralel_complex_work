# ============================================================
# demo-scenario.ps1 — Повний демонстраційний сценарій захисту
# Лабораторна робота №6: Kubernetes Orchestration
# Запускати з кореня репозиторію після deploy.ps1
# ============================================================

$ErrorActionPreference = "Continue"

function Write-Step($n, $text) {
    Write-Host "`n════════════════════════════════════════" -ForegroundColor Magenta
    Write-Host "  КРОК $n: $text" -ForegroundColor Cyan
    Write-Host "════════════════════════════════════════" -ForegroundColor Magenta
    Read-Host "  [Enter щоб продовжити]"
}

Write-Host @"
╔══════════════════════════════════════════════════════════╗
║   Демонстраційний сценарій — Kubernetes Lab #6          ║
║   Investment Portfolio Management System                 ║
╚══════════════════════════════════════════════════════════╝
"@ -ForegroundColor Cyan

# ── КРОК 1: Стан кластеру ────────────────────────────────────
Write-Step 1 "Поточний стан кластеру"
Write-Host "--- Deployments ---" -ForegroundColor Yellow
kubectl get deployments
Write-Host "`n--- Pods (з вузлами) ---" -ForegroundColor Yellow
kubectl get pods -o wide
Write-Host "`n--- Services ---" -ForegroundColor Yellow
kubectl get services

# ── КРОК 2: Доступність сервісів ─────────────────────────────
Write-Step 2 "Перевірка доступності сервісів (health checks)"

Write-Host "Запускаємо port-forward для asset-service..." -ForegroundColor Gray
$pf = Start-Job { kubectl port-forward service/asset-service 8001:8000 }
Start-Sleep -Seconds 3

$services = @(
    @{ Name="Asset Service";  Port=8001 }
)
foreach ($svc in $services) {
    try {
        $r = Invoke-WebRequest "http://localhost:$($svc.Port)/health" -UseBasicParsing -TimeoutSec 5
        Write-Host "  ✓ $($svc.Name) -> $($r.Content)" -ForegroundColor Green
    } catch {
        Write-Host "  ✗ $($svc.Name): $_" -ForegroundColor Red
    }
}
$pf | Stop-Job; $pf | Remove-Job

# ── КРОК 3: Перевірка Redis ───────────────────────────────────
Write-Step 3 "Перевірка підключення до Redis"
$redisPod = kubectl get pods -l app=redis -o jsonpath='{.items[0].metadata.name}'
Write-Host "Redis pod: $redisPod" -ForegroundColor Yellow
Write-Host "Ping:" -ForegroundColor Gray
kubectl exec $redisPod -- redis-cli ping
Write-Host "Ключі в кеші:" -ForegroundColor Gray
kubectl exec $redisPod -- redis-cli keys '*'
Write-Host "Інформація про Redis:" -ForegroundColor Gray
kubectl exec $redisPod -- redis-cli info server | Select-String "redis_version"

# ── КРОК 4: Міжсервісна взаємодія ────────────────────────────
Write-Step 4 "Перевірка міжсервісної взаємодії (analytics)"
$pf = Start-Job { kubectl port-forward service/analytics-service 8004:8000 }
Start-Sleep -Seconds 3
try {
    $r = Invoke-WebRequest "http://localhost:8004/health" -UseBasicParsing
    Write-Host "Analytics health: $($r.Content)" -ForegroundColor Green
} catch {
    Write-Host "Analytics not ready: $_" -ForegroundColor Red
}
$pf | Stop-Job; $pf | Remove-Job

# ── КРОК 5: Масштабування ─────────────────────────────────────
Write-Step 5 "Масштабування: asset-service 2 → 4 репліки"
Write-Host "До масштабування:" -ForegroundColor Yellow
kubectl get pods -l app=asset-service

kubectl scale deployment asset-service --replicas=4
Write-Host "Очікуємо нові pod-и..." -ForegroundColor Gray
Start-Sleep -Seconds 10

Write-Host "Після масштабування:" -ForegroundColor Yellow
kubectl get pods -l app=asset-service
Write-Host "Endpoints (IP всіх реплік):" -ForegroundColor Yellow
kubectl get endpoints asset-service

# ── КРОК 6: Видалення Pod-а (self-healing) ───────────────────
Write-Step 6 "Самовідновлення: видалення pod-а"
$podToDelete = kubectl get pods -l app=asset-service -o jsonpath='{.items[0].metadata.name}'
Write-Host "Видаляємо pod: $podToDelete" -ForegroundColor Yellow
kubectl delete pod $podToDelete

Write-Host "Спостерігаємо відновлення (15 секунд)..." -ForegroundColor Gray
for ($i = 1; $i -le 5; $i++) {
    Start-Sleep -Seconds 3
    kubectl get pods -l app=asset-service
}
Write-Host "Kubernetes автоматично відновив pod!" -ForegroundColor Green

# ── КРОК 7: Rolling Update ────────────────────────────────────
Write-Step 7 "Rolling Update asset-service"
Write-Host "Поточна версія:" -ForegroundColor Yellow
kubectl rollout history deployment/asset-service

Write-Host "Виконуємо rolling update (restart)..." -ForegroundColor Gray
kubectl rollout restart deployment/asset-service
kubectl rollout status deployment/asset-service --timeout=120s

Write-Host "Після оновлення:" -ForegroundColor Yellow
kubectl rollout history deployment/asset-service
kubectl get pods -l app=asset-service

# ── КРОК 8: Масштабування назад ──────────────────────────────
Write-Step 8 "Масштабування назад: 4 → 2 репліки"
kubectl scale deployment asset-service --replicas=2
Start-Sleep -Seconds 5
kubectl get pods -l app=asset-service

Write-Host @"

╔══════════════════════════════════════════════════════════╗
║   Демонстрація завершена успішно!                        ║
║   Всі кроки лабораторної виконані.                       ║
╚══════════════════════════════════════════════════════════╝
"@ -ForegroundColor Green
