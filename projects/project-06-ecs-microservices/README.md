# Project 06 — Containerized Microservices with ECS Fargate and Service Discovery

**Architecture:** Containers / microservices  
**Goal:** Split a demo application into Auth, Orders, and Notifications services and deploy them on ECS Fargate.

## Target architecture

~~~mermaid
flowchart TD
    User --> ALB[Application Load Balancer]
    ALB --> Auth[Auth service]
    ALB --> Orders[Orders service]
    ALB --> Notify[Notifications service]
    Auth <--> Orders
    Orders --> Notify
    Auth --> CM[Cloud Map]
    Orders --> CM
    Notify --> CM
    Auth --> Redis[(ElastiCache Redis)]
    Orders --> DB[(Data store)]
    ECR[Amazon ECR] --> ECS[ECS Fargate]
    SM[Secrets Manager] --> ECS
    CP[CodePipeline] --> CD[CodeDeploy blue/green]
    CD --> ECS
    ECS --> CW[CloudWatch / X-Ray]
~~~

## Phase 1 — Split the application

1. Define service boundaries and API contracts.
2. Keep each service independently buildable and deployable.
3. Keep containers stateless; durable data belongs in external storage.
4. Define health endpoints and graceful shutdown.
5. Decide how authentication context is passed between services.
6. Add correlation IDs and structured logs.

## Phase 2 — Containerize locally

1. Create a Dockerfile for each service.
2. Pin runtime and dependency versions.
3. Run containers locally and test service-to-service calls.
4. Add health checks and a non-root user.
5. Scan images for vulnerabilities.
6. Keep secrets out of build arguments and image layers.

## Phase 3 — ECR and ECS foundation

1. Create one ECR repository per service.
2. Enable image scanning and immutable tags where appropriate.
3. Push versioned images to ECR.
4. Create an ECS cluster with Fargate capacity.
5. Create task definitions with CPU, memory, ports, logs, and health checks.
6. Create an execution role for image pulls and log delivery.
7. Create a separate task role for application AWS API access.
8. Deploy services into private subnets with narrow security groups.

## Phase 4 — ALB and service discovery

1. Create an ALB in public subnets.
2. Create target groups using IP target type for Fargate tasks.
3. Configure path rules such as /api/orders/* and /api/notifications/*.
4. Create a Cloud Map namespace and service registrations.
5. Configure private DNS discovery between services.
6. Restrict internal ports to the required service security groups.
7. Test external ALB routing and internal Cloud Map discovery.

## Phase 5 — Secrets and shared state

1. Store database passwords and API secrets in Secrets Manager.
2. Grant the ECS task execution role permission to retrieve only injected secrets.
3. Rotate secrets where dependent services support rotation.
4. Use Redis for shared ephemeral session/cache data only.
5. Use durable storage for business records.
6. Confirm secrets do not appear in task definitions, source, logs, or images.

## Phase 6 — Blue/green delivery

1. Configure the ECS service with CodeDeploy deployment controller.
2. Create a blue/green deployment group and required target groups.
3. Configure listener traffic shifting.
4. Create CodePipeline to build, test, scan, and publish images.
5. Deploy a new task-definition revision through CodeDeploy.
6. Add a post-deployment smoke test.
7. Test rollback with a deliberately failing lab deployment.

## Phase 7 — Observability and tests

1. Send container logs to CloudWatch Logs.
2. Enable X-Ray/OpenTelemetry instrumentation where supported by the chosen runtime.
3. Create dashboards for errors, latency, CPU, memory, task count, and ALB health.
4. Test task restart, replacement, and scaling.
5. Test downstream service failure and timeout/retry policies.
6. Confirm no service relies on another service's local filesystem or in-memory state.

## Cleanup

Delete CodePipeline/CodeDeploy resources, ECS services and cluster, Cloud Map services/namespace, ALB/listeners/target groups, ECR images/repositories, ElastiCache, secrets, IAM roles, and CloudWatch log groups. Observe secret deletion recovery windows and data-retention requirements.

## Definition of done

Three independently deployed services communicate through documented APIs and private service discovery; secrets are injected at runtime; deployments support traffic shifting and rollback; and tracing/logging are demonstrable.
