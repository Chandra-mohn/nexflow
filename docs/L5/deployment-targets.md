# L5: Deployment Targets

> **Source**: Native Nexflow specification
> **Status**: Complete Specification

---

## Overview

Deployment targets configure how Nexflow processes are deployed to execution environments. L5 supports multiple deployment models to match different infrastructure requirements.

---

## Supported Deployment Targets

| Target | Use Case | Features |
|--------|----------|----------|
| **Kubernetes** | Cloud-native | Auto-scaling, self-healing, portable |
| **YARN** | Hadoop ecosystem | Resource sharing, existing clusters |
| **Standalone** | Simple deployments | Direct control, minimal overhead |
| **Docker Compose** | Development | Local testing, easy setup |

---

## Kubernetes Deployment

### Basic Configuration

```yaml
deployment:
  type: kubernetes
  namespace: credit-card-processing
```

### Complete Configuration

```yaml
deployment:
  type: kubernetes
  namespace: credit-card-processing

  # Kubernetes connection
  kubernetes:
    context: production-cluster  # kubectl context
    config_file: ~/.kube/config  # Optional

  # Service account
  service_account: nexflow-runner

  # Image configuration
  image:
    repository: company/flink
    tag: 1.17.1
    pull_policy: IfNotPresent
    pull_secrets:
      - docker-registry-secret

  # Job Manager
  job_manager:
    replicas: 1  # For HA, use 2+
    resources:
      cpu: 2
      memory: 4gb

  # Task Manager
  task_manager:
    replicas: 4
    resources:
      cpu: 4
      memory: 8gb

  # Pod template customization
  pod_template:
    metadata:
      labels:
        team: credit-card
        env: production
      annotations:
        prometheus.io/scrape: "true"
        prometheus.io/port: "9249"

    spec:
      # Node selection
      node_selector:
        workload-type: streaming
        disk-type: ssd

      # Tolerations
      tolerations:
        - key: dedicated
          operator: Equal
          value: streaming
          effect: NoSchedule

      # Affinity rules
      affinity:
        pod_anti_affinity:
          preferred:
            - weight: 100
              pod_affinity_term:
                label_selector:
                  match_labels:
                    app: flink
                topology_key: topology.kubernetes.io/zone

      # Security context
      security_context:
        run_as_user: 9999
        run_as_group: 9999
        fs_group: 9999

      # Volumes
      volumes:
        - name: flink-config
          config_map:
            name: flink-config
        - name: hadoop-config
          config_map:
            name: hadoop-config

      # Volume mounts
      volume_mounts:
        - name: flink-config
          mount_path: /opt/flink/conf
        - name: hadoop-config
          mount_path: /etc/hadoop/conf

  # High Availability
  ha:
    enabled: true
    type: kubernetes  # kubernetes, zookeeper

  # Ingress for Web UI
  ingress:
    enabled: true
    host: flink.company.com
    tls:
      enabled: true
      secret_name: flink-tls

  # Service configuration
  service:
    type: ClusterIP  # ClusterIP, LoadBalancer, NodePort
    rest_port: 8081
    blob_port: 6124
    query_port: 6125

  # Scaling configuration
  scaling:
    type: horizontal
    min_replicas: 2
    max_replicas: 20
    metrics:
      - type: cpu
        target_utilization: 70
      - type: kafka_lag
        target_value: 10000
```

### Kubernetes Native Mode

```yaml
deployment:
  type: kubernetes
  mode: native  # native or application

  # Native mode specific
  native:
    # Pod resources requested on-demand
    pod_template_file: /path/to/pod-template.yaml

    # Resource quotas
    quotas:
      cpu: 100
      memory: 200gb
```

### Kubernetes Application Mode

```yaml
deployment:
  type: kubernetes
  mode: application

  # Application mode specific
  application:
    main_class: com.company.FlinkJob
    args:
      - "--process=authorization_enrichment"
      - "--environment=production"

    # Job artifacts
    artifacts:
      - s3://artifacts/nexflow-jobs.jar
      - s3://artifacts/udfs.jar
```

---

## YARN Deployment

### Basic Configuration

```yaml
deployment:
  type: yarn
  queue: streaming
```

### Complete Configuration

```yaml
deployment:
  type: yarn
  queue: credit-card-streaming

  # YARN connection
  yarn:
    resource_manager: yarn-rm.company.com:8032
    config_dir: /etc/hadoop/conf

  # Application configuration
  application:
    name: authorization-enrichment
    type: flink
    tags:
      - credit-card
      - production

  # Application Master
  application_master:
    memory: 2gb
    vcores: 2

  # Container configuration
  container:
    memory: 4gb
    vcores: 2
    count: 32

  # Resource allocation
  resource:
    # Dynamic allocation
    dynamic:
      enabled: true
      min_containers: 8
      max_containers: 64
      idle_timeout: 5m

  # YARN-specific settings
  yarn_settings:
    # Ship files to containers
    ship_files:
      - /opt/flink/lib/*.jar
      - /etc/ssl/certs/ca-bundle.crt

    # Application classpath
    provided_lib_dirs:
      - hdfs:///flink/lib

    # Log aggregation
    log_aggregation:
      enabled: true
      rolling_interval: 3600

  # Kerberos authentication
  kerberos:
    enabled: true
    principal: flink/_HOST@REALM
    keytab: /etc/security/keytabs/flink.keytab
    renew_interval: 1h
```

### YARN Session Mode

```yaml
deployment:
  type: yarn
  mode: session

  session:
    name: flink-session-cluster
    # Pre-allocate resources
    task_managers: 16
    slots_per_task_manager: 4
```

### YARN Per-Job Mode

```yaml
deployment:
  type: yarn
  mode: per_job

  per_job:
    # Resources allocated for this job only
    detached: true
    shutdown_on_completion: true
```

---

## Standalone Deployment

### Basic Configuration

```yaml
deployment:
  type: standalone
  job_manager: localhost:8081
```

### Complete Configuration

```yaml
deployment:
  type: standalone

  # Cluster configuration
  cluster:
    job_manager:
      host: flink-jm.company.com
      port: 6123
      web_port: 8081

    task_managers:
      - host: flink-tm-1.company.com
        port: 6122
        slots: 4
      - host: flink-tm-2.company.com
        port: 6122
        slots: 4
      - host: flink-tm-3.company.com
        port: 6122
        slots: 4

  # High Availability
  ha:
    enabled: true
    type: zookeeper
    zookeeper:
      quorum: zk1:2181,zk2:2181,zk3:2181
      root_path: /flink
    storage_dir: hdfs:///flink/ha/

  # Security
  security:
    ssl:
      enabled: true
      internal:
        enabled: true
        keystore: /etc/ssl/flink-keystore.jks
        truststore: /etc/ssl/flink-truststore.jks
      rest:
        enabled: true
        cert_file: /etc/ssl/flink-rest.pem
        key_file: /etc/ssl/flink-rest-key.pem
```

---

## Docker Compose (Development)

```yaml
deployment:
  type: docker_compose

  # Compose configuration
  compose:
    project_name: nexflow-dev

    # Services
    services:
      job_manager:
        image: flink:1.17.1
        ports:
          - "8081:8081"
        environment:
          - JOB_MANAGER_RPC_ADDRESS=job_manager

      task_manager:
        image: flink:1.17.1
        replicas: 2
        environment:
          - JOB_MANAGER_RPC_ADDRESS=job_manager
        depends_on:
          - job_manager

    # Supporting services
    kafka:
      image: confluentinc/cp-kafka:7.4.0
      ports:
        - "9092:9092"

    mongodb:
      image: mongo:6.0
      ports:
        - "27017:27017"

  # Volume mounts for development
  volumes:
    - ./jobs:/opt/flink/usrlib
    - ./conf:/opt/flink/conf
```

---

## Deployment Strategy

### Rolling Update

```yaml
deployment:
  strategy:
    type: rolling_update

    rolling:
      max_unavailable: 1
      max_surge: 1
      partition: 0  # For canary

    # Pre/post hooks
    hooks:
      pre_upgrade:
        - action: savepoint
          timeout: 5m
      post_upgrade:
        - action: verify_health
          timeout: 2m
```

### Blue-Green Deployment

```yaml
deployment:
  strategy:
    type: blue_green

    blue_green:
      # Both versions run simultaneously
      switch_traffic_after: verify_health
      keep_old_version: 1h

      # Traffic switching
      traffic:
        type: instant  # instant, gradual
```

### Canary Deployment

```yaml
deployment:
  strategy:
    type: canary

    canary:
      # Gradual rollout
      steps:
        - weight: 10
          duration: 10m
          metrics:
            - error_rate < 0.01
            - latency_p99 < 100ms
        - weight: 50
          duration: 30m
        - weight: 100

      # Automatic rollback
      rollback:
        enabled: true
        on_metrics_failure: true
```

---

## Savepoint Management

```yaml
deployment:
  savepoint:
    # Automatic savepoint on upgrade/stop
    auto_savepoint: true
    directory: s3://savepoints/authorization-enrichment/

    # Restore from savepoint
    restore:
      path: s3://savepoints/authorization-enrichment/savepoint-abc123
      allow_non_restored: false

    # Periodic savepoints
    periodic:
      enabled: true
      interval: 1h
      retention:
        count: 24  # Keep last 24 savepoints
```

---

## Environment-Specific Deployment

```yaml
# development.infra
deployment:
  type: docker_compose
  compose:
    project_name: nexflow-dev

# staging.infra
deployment:
  type: kubernetes
  namespace: credit-card-staging
  task_manager:
    replicas: 2

# production.infra
deployment:
  type: kubernetes
  namespace: credit-card-production
  task_manager:
    replicas: 16
  ha:
    enabled: true
```

---

## CI/CD Integration

### GitHub Actions

```yaml
deployment:
  ci_cd:
    type: github_actions

    workflow:
      on_push:
        branches: [main]
      on_pull_request:
        types: [opened, synchronize]

    jobs:
      validate:
        - procdsl validate
      compile:
        - procdsl compile --target flink-sql
      test:
        - procdsl test --integration
      deploy:
        environment: production
        needs: [validate, compile, test]
```

### GitLab CI

```yaml
deployment:
  ci_cd:
    type: gitlab_ci

    stages:
      - validate
      - compile
      - test
      - deploy

    deploy_production:
      stage: deploy
      environment: production
      when: manual
      only:
        - main
```

### ArgoCD

```yaml
deployment:
  ci_cd:
    type: argocd

    application:
      name: authorization-enrichment
      project: credit-card
      source:
        repo_url: https://github.com/company/nexflow-apps
        path: kubernetes/authorization-enrichment
        target_revision: main

    sync_policy:
      automated:
        prune: true
        self_heal: true
      sync_options:
        - CreateNamespace=true
```

---

## Related Documents

- [L5-Infrastructure-Binding.md](../L5-Infrastructure-Binding.md) - Overview
- [resource-allocation.md](./resource-allocation.md) - Resource configuration
- [state-checkpoints.md](./state-checkpoints.md) - Checkpointing
