# Kubernetes Deployment Guide
# Investment Portfolio Management System

## Prerequisites
- Kubernetes cluster (Minikube, Docker Desktop, or cloud provider)
- kubectl CLI tool installed
- Docker images built for all services

## Build Docker Images

Before deploying to Kubernetes, build all Docker images:

```bash
# Build Asset Service
cd asset-service
docker build -t asset-service:latest -f ../docker/Dockerfile .

# Build Transaction Service  
cd ../transaction-service
docker build -t transaction-service:latest -f ../docker/Dockerfile .

# Build Portfolio Service
cd ../portfolio-service
docker build -t portfolio-service:latest -f ../docker/Dockerfile .

# Build Analytics Service
cd ../analytics-service
docker build -t analytics-service:latest -f ../docker/Dockerfile .
```

## Deploy to Kubernetes

### Option 1: Deploy All at Once

```bash
# From the project root
kubectl apply -f k8s/
```

### Option 2: Deploy Step by Step

```bash
# 1. Deploy database and cache
kubectl apply -f k8s/postgres.yaml
kubectl apply -f k8s/redis.yaml

# Wait for PostgreSQL and Redis to be ready
kubectl wait --for=condition=ready pod -l app=postgres --timeout=120s
kubectl wait --for=condition=ready pod -l app=redis --timeout=60s

# 2. Deploy Asset Service (needs Redis)
kubectl apply -f k8s/asset-service-configmap.yaml
kubectl apply -f k8s/asset-service-deployment.yaml
kubectl apply -f k8s/asset-service-service.yaml

# Wait for Asset Service
kubectl wait --for=condition=ready pod -l app=asset-service --timeout=120s

# 3. Deploy Portfolio Service
kubectl apply -f k8s/portfolio-service.yaml

# Wait for Portfolio Service
kubectl wait --for=condition=ready pod -l app=portfolio-service --timeout=120s

# 4. Deploy Transaction Service (depends on Asset and Portfolio)
kubectl apply -f k8s/transaction-service.yaml

# Wait for Transaction Service
kubectl wait --for=condition=ready pod -l app=transaction-service --timeout=120s

# 5. Deploy Analytics Service (depends on all others)
kubectl apply -f k8s/analytics-service.yaml
```

## Verify Deployment

```bash
# Check all pods are running
kubectl get pods

# Check services
kubectl get services

# Check deployments
kubectl get deployments

# View logs for a specific service
kubectl logs -l app=asset-service --tail=50
kubectl logs -l app=transaction-service --tail=50
kubectl logs -l app=portfolio-service --tail=50
kubectl logs -l app=analytics-service --tail=50
```

## Access Services

### Port Forwarding (for local testing)

```bash
# Asset Service
kubectl port-forward service/asset-service 8001:8000

# Transaction Service
kubectl port-forward service/transaction-service 8002:8000

# Portfolio Service
kubectl port-forward service/portfolio-service 8003:8000

# Analytics Service
kubectl port-forward service/analytics-service 8004:8000
```

Now access services at:
- Asset Service: http://localhost:8001
- Transaction Service: http://localhost:8002
- Portfolio Service: http://localhost:8003
- Analytics Service: http://localhost:8004

## Scaling

Lab #6 Requirement: Services are deployed with 2 replicas by default.

To scale manually:
```bash
kubectl scale deployment asset-service --replicas=3
kubectl scale deployment transaction-service --replicas=3
kubectl scale deployment portfolio-service --replicas=3
kubectl scale deployment analytics-service --replicas=3
```

## Rolling Updates

Lab #6 Requirement: All services support rolling updates.

To update a service:
```bash
# Build new image with tag
docker build -t asset-service:v2 -f docker/Dockerfile ./asset-service

# Update deployment
kubectl set image deployment/asset-service asset-service=asset-service:v2

# Watch rollout
kubectl rollout status deployment/asset-service
```

## Troubleshooting

```bash
# Describe a pod
kubectl describe pod <pod-name>

# Get logs
kubectl logs <pod-name>

# Execute command in pod
kubectl exec -it <pod-name> -- /bin/sh

# Check events
kubectl get events --sort-by='.lastTimestamp'
```

## Clean Up

```bash
# Delete all resources
kubectl delete -f k8s/

# Or delete specific resources
kubectl delete deployment --all
kubectl delete service --all
kubectl delete pvc --all
```

## Architecture Overview

```
┌─────────────────────────────────────────────────────┐
│                  Kubernetes Cluster                 │
│                                                     │
│  ┌──────────────┐  ┌──────────────┐               │
│  │  PostgreSQL  │  │    Redis     │               │
│  │  (Database)  │  │   (Cache)    │               │
│  └──────┬───────┘  └──────┬───────┘               │
│         │                  │                        │
│  ┌──────┴─────────────────┴───────┐               │
│  │                                  │               │
│  │  ┌────────────┐  ┌────────────┐│               │
│  │  │   Asset    │  │ Portfolio  ││               │
│  │  │  Service   │  │  Service   ││               │
│  │  │ (2 pods)   │  │ (2 pods)   ││               │
│  │  └──────┬─────┘  └──────┬─────┘│               │
│  │         │                │       │               │
│  │  ┌──────┴────────────────┴─────┐│               │
│  │  │    Transaction Service      ││               │
│  │  │        (2 pods)              ││               │
│  │  └──────┬──────────────────────┘│               │
│  │         │                        │               │
│  │  ┌──────┴──────────┐            │               │
│  │  │   Analytics     │            │               │
│  │  │    Service      │            │               │
│  │  │   (2 pods)      │            │               │
│  │  └─────────────────┘            │               │
│  └──────────────────────────────────┘               │
└─────────────────────────────────────────────────────┘
```

## Lab Requirements Compliance

### Lab #6 Requirements:
✅ **Kubernetes Deployment**: All services deployed as Deployments
✅ **Replicas**: 2 replicas per service for high availability
✅ **Rolling Updates**: RollingUpdate strategy configured
✅ **Health Checks**: Liveness and readiness probes
✅ **Service Discovery**: ClusterIP services for inter-service communication
✅ **Resource Management**: CPU and memory limits/requests defined
✅ **Persistent Storage**: PVC for PostgreSQL data

### Architecture Pattern:
✅ **Microservices**: Each service independent
✅ **Database per Service**: Separate databases for each service
✅ **Service Communication**: HTTP/REST between services
✅ **Caching**: Redis for Asset Service
