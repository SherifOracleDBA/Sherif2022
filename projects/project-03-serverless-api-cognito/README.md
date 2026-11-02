# Project 03 — Serverless REST API with Cognito, DynamoDB, and WAF

**Architecture:** Serverless REST API  
**Goal:** Build a CRUD API protected by Cognito authentication and instrumented for security and tracing.

## Target request flow

~~~mermaid
sequenceDiagram
    participant User
    participant Cognito
    participant APIGW as API Gateway
    participant Lambda
    participant DDB as DynamoDB
    User->>Cognito: Sign up / sign in
    Cognito-->>User: JWT tokens
    User->>APIGW: HTTPS request + Bearer token
    APIGW->>Cognito: Validate token with User Pool authorizer
    Cognito-->>APIGW: Authorization result
    APIGW->>Lambda: Invoke authorized route
    Lambda->>DDB: Query / write with IAM role
    DDB-->>Lambda: Result
    Lambda-->>User: JSON response
~~~

## Phase 1 — API and data model

1. Choose a resource such as todos or customer records.
2. Define CRUD routes and request/response shapes.
3. Define access patterns before designing DynamoDB.
4. Define partition/sort keys and add GSIs only for demonstrated query needs.
5. Store an owner/user identifier in each item so the application can enforce per-user access.
6. Define validation, pagination, and error response conventions.

## Phase 2 — Cognito

1. Create a Cognito User Pool.
2. Configure sign-up, verification, password policy, and MFA settings for the lab.
3. Create an app client. Do not create a client secret for a browser-only public client.
4. Configure a hosted UI/domain if using hosted sign-in.
5. Configure callback and sign-out URLs for the exact frontend origin.
6. Test sign-up, verification, sign-in, refresh, and sign-out.
7. Inspect claims and token expiration. Access and ID tokens are different token types; send the type expected by the API Gateway authorizer.

## Phase 3 — API Gateway and Lambda

1. Create an API Gateway REST API.
2. Implement Lambda handlers for list, create, read, update, and delete.
3. Give the Lambda role only the required actions on the intended table.
4. Add a Cognito User Pool authorizer to protected methods.
5. Read identity from verified authorizer claims; never trust a user ID supplied only in the request body.
6. Enforce ownership in every read/update/delete operation.
7. Add request validation, CORS, throttling, and consistent error responses.

## Phase 4 — DynamoDB

1. Create the table with on-demand capacity for the learning workload.
2. Add a GSI only when a query pattern needs it.
3. Enable point-in-time recovery for the data-retention exercise.
4. Enable Streams only for a defined downstream use case.
5. Test conditional writes and pagination.
6. Add alarms for throttling and system errors.

## Phase 5 — WAF and CloudFront

1. Associate AWS WAF with the API Gateway REST API stage.
2. Start managed rules in count mode and inspect logs before blocking.
3. Add rate-based protection and a safe request-size limit.
4. Host the static frontend in private S3 behind CloudFront with Origin Access Control.
5. If CloudFront also fronts API routes, create separate cache behaviors.
6. Disable caching for authenticated user-specific API responses by default. Never share cached responses through an incomplete cache key.

## Phase 6 — Observability and caching

1. Enable API Gateway access/execution logging with sensitive values redacted.
2. Enable X-Ray tracing for API Gateway and Lambda.
3. Add structured logs and request/correlation IDs.
4. Create CloudWatch dashboards and alarms.
5. Use API Gateway caching only for responses proven safe to share. Test authorization headers, query strings, cache keys, and user isolation first.
6. Use API keys only for consumer metering or quotas; an API key is not user authentication.

## Phase 7 — Security tests

- Unauthenticated request is rejected.
- A valid user can access only their own records.
- A user cannot access another user's item by changing an ID.
- Invalid or expired tokens are rejected.
- WAF rate-based protection activates under controlled load.
- X-Ray shows API Gateway → Lambda → DynamoDB.
- Tokens and personal data do not appear in logs.

## Cleanup

Delete CloudFront, WAF association, API Gateway, Lambda functions, DynamoDB, Cognito app client/User Pool, log groups, and IAM roles. Empty and delete the frontend bucket.

## Definition of done

The API uses Cognito; application logic enforces record ownership; WAF and tracing are demonstrable; caching is safe; and security tests are recorded.
