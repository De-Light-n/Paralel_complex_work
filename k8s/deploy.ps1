# ============================================================
# deploy.ps1 — Повний скрипт розгортання Kubernetes кластеру
# Лабораторна робота №6: Orchestration with Kubernetes
# Запускати з кореня репозиторію
# ============================================================

$ErrorActionPreference = "Stop"
$PROJECT_ROOT = $PSScriptRoot

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  Kubernetes Deployment - Lab #6" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan

# ── Крок 1: Запуск Minikube ──────────────────────────────────
Write-Host "`n[STEP 1/8] Starting Minikube..." -ForegroundColor Yellow
minikube start --driver=docker --cpus=4 --memory=8192
Write-Host "✓ Minikube started" -ForegroundColor Green

# ── Крок 2: Переключення Docker daemon на Minikube ────────────
Write-Host "`n[STEP 2/8] Switching Docker daemon to Minikube..." -ForegroundColor Yellow
minikube -p minikube docker-env --shell powershell | Invoke-Expression
Write-Host "✓ Docker daemon switched" -ForegroundColor Green

# ── Крок 3: Збірка образів ───────────────────────────────────
Write-Host "`n[STEP 3/8] Building Docker images inside Minikube..." -ForegroundColor Yellow
docker build -f docker/Dockerfile --build-arg SERVICE_DIR=asset-service       -t asset-service:latest       .
docker build -f docker/Dockerfile --build-arg SERVICE_DIR=transaction-service  -t transaction-service:latest  .
docker build -f docker/Dockerfile --build-arg SERVICE_DIR=portfolio-service    -t portfolio-service:latest    .
docker build -f docker/Dockerfile --build-arg SERVICE_DIR=analytics-service    -t analytics-service:latest    .
Write-Host "✓ All images built" -ForegroundColor Green

# ── Крок 4: Застосування маніфестів ──────────────────────────
Write-Host "`n[STEP 4/8] Applying Kubernetes manifests..." -ForegroundColor Yellow

# Інфраструктура (БД та кеш)
kubectl apply -f k8s/postgres.yaml
kubectl apply -f k8s/redis.yaml

Write-Host "  Waiting for postgres and redis to be ready..." -ForegroundColor Gray
kubectl wait --for=condition=available deployment/postgres --timeout=180s
kubectl wait --for=condition=available deployment/redis    --timeout=120s

# Мікросервіси
kubectl apply -f k8s/asset-service-configmap.yaml
kubectl apply -f k8s/asset-service-deployment.yaml
kubectl apply -f k8s/asset-service-service.yaml
kubectl apply -f k8s/portfolio-service.yaml
kubectl apply -f k8s/transaction-service.yaml
kubectl apply -f k8s/analytics-service.yaml

# NodePort services для зовнішнього доступу
kubectl apply -f k8s/nodeport-services.yaml

Write-Host "✓ All manifests applied" -ForegroundColor Green

# ── Крок 5: Очікування готовності ─────────────────────────────
Write-Host "`n[STEP 5/8] Waiting for all deployments to be ready..." -ForegroundColor Yellow
kubectl wait --for=condition=available deployment/asset-service       --timeout=180s
kubectl wait --for=condition=available deployment/portfolio-service   --timeout=180s
kubectl wait --for=condition=available deployment/transaction-service --timeout=180s
kubectl wait --for=condition=available deployment/analytics-service   --timeout=180s
Write-Host "✓ All services are ready" -ForegroundColor Green

# ── Крок 6: Поточний стан кластеру ───────────────────────────
Write-Host "`n[STEP 6/8] Current cluster state:" -ForegroundColor Yellow
Write-Host "`n--- Deployments ---" -ForegroundColor Cyan
kubectl get deployments -o wide
Write-Host "`n--- Pods ---" -ForegroundColor Cyan
kubectl get pods -o wide
Write-Host "`n--- Services ---" -ForegroundColor Cyan
kubectl get services

# ── Крок 7: Масштабування ─────────────────────────────────────
Write-Host "`n[STEP 7/8] Scaling asset-service to 3 replicas..." -ForegroundColor Yellow
kubectl scale deployment asset-service --replicas=3
Start-Sleep -Seconds 5
kubectl get pods -l app=asset-service
Write-Host "✓ Scaled to 3 replicas" -ForegroundColor Green

# ── Крок 8: Rolling Update (оновлення версії) ─────────────────
Write-Host "`n[STEP 8/8] Performing rolling update of asset-service..." -ForegroundColor Yellow
# Оновлюємо анотацію, щоб запустити rolling update без зміни образу
kubectl patch deployment asset-service --patch '{"spec":{"template":{"metadata":{"annotations":{"kubectl.kubernetes.io/restartedAt":"' + (Get-Date -Format "yyyy-MM-ddTHH:mm:ssZ") + '"}}}}}'
kubectl rollout status deployment/asset-service --timeout=120s
Write-Host "✓ Rolling update completed" -ForegroundColor Green

# ── Підсумок ──────────────────────────────────────────────────
Write-Host "`n========================================" -ForegroundColor Cyan
Write-Host "  Deployment Complete!" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "`nTo access services, run: .\k8s\port-forward.ps1"
Write-Host "Or use minikube service URLs:"
Write-Host "  minikube service asset-service-nodeport --url"
Write-Host "  minikube service portfolio-service-nodeport --url"
Write-Host "  minikube service transaction-service-nodeport --url"
Write-Host "  minikube service analytics-service-nodeport --url"
