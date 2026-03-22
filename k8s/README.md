# Kubernetes Deployment Guide (Minikube)

## 1. Передумови
- Встановлений Docker Desktop.
- Встановлений `kubectl`.
- Встановлений `minikube`.

Перевірка:

```powershell
kubectl version --client
minikube version
```

## 2. Встановлення Minikube на Windows
Якщо Minikube відсутній, встановіть одним із способів:

```powershell
winget install Kubernetes.minikube
```

або

```powershell
choco install minikube -y
```

Після інсталяції перезапустіть термінал.

Якщо команда `minikube` не знаходиться після інсталяції:

```powershell
where.exe minikube
```

Якщо шлях не знайдено, закрийте VS Code і відкрийте знову, або додайте шлях до `minikube.exe` у змінну середовища `Path` вручну.

Тимчасовий запуск за повним шляхом (приклад):

```powershell
& "C:\Program Files\Kubernetes\Minikube\minikube.exe" version
```

## 3. Підйом локального Kubernetes-кластера

```powershell
minikube start --driver=docker --cpus=4 --memory=8192
kubectl config current-context
kubectl get nodes
```

Очікування: `STATUS=Ready` для вузла `minikube`.

## 4. Збірка образів у середовищі Minikube
Щоб Kubernetes бачив локальні образи без зовнішнього registry:

```powershell
minikube -p minikube docker-env --shell powershell | Invoke-Expression

cd <project-root>
docker build -f docker/Dockerfile --build-arg SERVICE_DIR=asset-service -t asset-service:latest .
docker build -f docker/Dockerfile --build-arg SERVICE_DIR=transaction-service -t transaction-service:latest .
docker build -f docker/Dockerfile --build-arg SERVICE_DIR=portfolio-service -t portfolio-service:latest .
docker build -f docker/Dockerfile --build-arg SERVICE_DIR=analytics-service -t analytics-service:latest .
```

## 5. Розгортання ресурсів Kubernetes
У каталозі `k8s` уже підготовлено:
- Deployment для кожного мікросервісу.
- Service (ClusterIP) для міжсервісного доступу.
- Deployment для Redis і PostgreSQL.
- PVC для PostgreSQL.

Застосування маніфестів:

```powershell
cd <project-root>
kubectl apply -f k8s/postgres.yaml
kubectl apply -f k8s/redis.yaml

kubectl wait --for=condition=available deployment/postgres --timeout=180s
kubectl wait --for=condition=available deployment/redis --timeout=120s

kubectl apply -f k8s/asset-service-configmap.yaml
kubectl apply -f k8s/asset-service-deployment.yaml
kubectl apply -f k8s/asset-service-service.yaml
kubectl apply -f k8s/portfolio-service.yaml
kubectl apply -f k8s/transaction-service.yaml
kubectl apply -f k8s/analytics-service.yaml
```

Перевірка стану:

```powershell
kubectl get deployments
kubectl get pods -o wide
kubectl get services
```

## 6. Доступність сервісів і міжсервісна взаємодія
Для локального тестування використовуйте port-forward:

```powershell
kubectl port-forward service/asset-service 8001:8000
kubectl port-forward service/portfolio-service 8003:8000
kubectl port-forward service/transaction-service 8002:8000
kubectl port-forward service/analytics-service 8004:8000
```

Базові перевірки:

```powershell
curl http://localhost:8001/health
curl http://localhost:8003/health
curl http://localhost:8002/health
curl http://localhost:8004/health
```

## 7. Перевірка Redis-підключення
Оскільки кеш інтегровано в `asset-service`, перевіряємо запит читання двічі та дивимось логи:

```powershell
curl http://localhost:8001/assets/1
curl http://localhost:8001/assets/1
kubectl logs -l app=asset-service --tail=100
```

У логах має з’явитися `Cache MISS` на першому виклику і `Cache HIT` на повторному.

## 8. Масштабування і балансування навантаження
За замовчуванням сервіси в маніфестах мають 2 репліки. Для демонстрації масштабування:

```powershell
kubectl scale deployment asset-service --replicas=4
kubectl get pods -l app=asset-service
kubectl get endpoints asset-service
```

Перевірка балансування: зробіть серію запитів до `service/asset-service` і перевірте, що запити обробляються різними pod (за логами кількох pod).

## 9. Перевірка самовідновлення після видалення Pod

```powershell
kubectl get pods -l app=asset-service
kubectl delete pod <one-asset-pod-name>
kubectl get pods -l app=asset-service -w
```

Очікування: Deployment автоматично створює новий pod, а кількість реплік повертається до заданого значення.

## 10. Rolling Update сервісу

```powershell
# Приклад нового тегу
docker build -f docker/Dockerfile --build-arg SERVICE_DIR=asset-service -t asset-service:v2 .

kubectl set image deployment/asset-service asset-service=asset-service:v2
kubectl rollout status deployment/asset-service
kubectl rollout history deployment/asset-service
```

За потреби відкат:

```powershell
kubectl rollout undo deployment/asset-service
```

## 11. Демонстраційний сценарій для захисту
1. Показати `kubectl get deployments,pods,svc`.
2. Показати 2+ репліки `asset-service`.
3. Через port-forward викликати `/health` та `GET /assets/{id}` двічі.
4. Показати в логах cache miss/hit.
5. Збільшити репліки `asset-service` до 4.
6. Видалити один pod і показати автозаміщення.
7. Запустити rolling update до нового тегу й показати `rollout status`.

## 12. Щоденне керування Minikube

Старт/стоп/стан кластера:

```powershell
minikube start --driver=docker
minikube status
minikube stop
minikube delete
```

Робота з профілями Minikube:

```powershell
minikube profile list
minikube start -p lab-k8s --driver=docker
minikube profile lab-k8s
```

Корисні діагностичні команди:

```powershell
kubectl get nodes
kubectl get pods -A
kubectl get events --sort-by=.metadata.creationTimestamp
kubectl describe pod <pod-name>
kubectl logs <pod-name>
minikube logs
```

Доступ до Kubernetes Dashboard:

```powershell
minikube dashboard
```

Доступ до сервісу без ручного port-forward:

```powershell
minikube service asset-service --url
```

Очищення тільки застосунку (без видалення кластера):

```powershell
kubectl delete -f k8s/
kubectl get all
```

## 13. Команди очищення

```powershell
kubectl delete -f k8s/
minikube stop
```

Для повного скидання даних PostgreSQL у Minikube:

```powershell
kubectl delete pvc postgres-pvc
```

Важливо: ініціалізаційний SQL для `asset_db`, `transaction_db`, `portfolio_db` виконується лише на першому старті PostgreSQL-контейнера (коли volume порожній).
