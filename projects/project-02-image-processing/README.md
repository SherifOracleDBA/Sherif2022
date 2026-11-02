# Project 02 — Serverless Image Processing Pipeline

**Architecture:** Event-driven serverless  
**Goal:** Accept image uploads, process them asynchronously, store derived images, and expose processing status.

## Target architecture

~~~mermaid
flowchart TD
    Client --> API[API Gateway]
    API --> Upload[Lambda: presigned URL]
    Upload --> Meta[(DynamoDB metadata)]
    Client --> Source[S3 source bucket]
    Source --> Queue[SQS queue]
    Queue --> Worker[Lambda worker]
    Worker --> SFN[Step Functions]
    SFN --> Validate[Validate image]
    Validate --> Resize[Resize and watermark]
    Resize --> Dest[S3 destination bucket]
    SFN --> Meta
    SFN --> Notify[SNS]
    CF[CloudFront] --> Dest
~~~

S3 sends object-created events to SQS. Lambda polls SQS through an event-source mapping. The worker starts a Step Functions execution for each message or small batch. Make processing idempotent using bucket, object key, and version/ETag as the job identity.

## Phase 1 — Buckets and metadata

1. Choose a Region and globally unique bucket names.
2. Create separate source and destination buckets with Block Public Access enabled.
3. Enable versioning where replay/recovery is useful.
4. Choose SSE-S3 for a simple lab or SSE-KMS for customer-managed-key practice.
5. Define lifecycle rules for originals, generated images, and incomplete multipart uploads.
6. Design a DynamoDB metadata table with image ID, source key, output keys, status, dimensions, timestamp, and error details.

## Phase 2 — Upload API

1. Create API Gateway endpoint POST /uploads.
2. Add Lambda to validate content type and requested file size.
3. Generate a short-lived presigned PUT URL for one source object.
4. Return the object key and URL to the client.
5. Write a PENDING_UPLOAD metadata record.
6. Configure CORS only for the demo frontend origin.
7. Test valid uploads and reject unsupported content types.

Do not make the source bucket public. The presigned URL grants time-limited access to one object operation.

## Phase 3 — SQS and failure handling

1. Create a processing queue and a dead-letter queue.
2. Set retention and visibility timeout based on expected processing duration.
3. Configure a redrive policy with a bounded retry count.
4. Configure an S3 ObjectCreated notification targeting SQS.
5. Add a queue policy allowing only the intended source bucket to publish.
6. Configure Lambda event-source mapping and partial batch failure handling where supported.
7. Alert on DLQ messages or excessive queue age.

## Phase 4 — Image processing

1. Choose Python/Pillow or Node.js/Sharp.
2. Package native dependencies in a Lambda Layer or deployment artifact built for the Lambda runtime and architecture.
3. Validate file content, dimensions, and size; do not trust only extension or client content type.
4. Generate thumbnail and full-size outputs.
5. Apply watermark only to intended variants.
6. Write results to deterministic destination keys.
7. Update DynamoDB status to COMPLETED or FAILED.
8. Make retries safe so duplicate events do not duplicate work.

## Phase 5 — Step Functions orchestration

1. Create a Standard workflow with validation, resize, watermark, store, metadata update, and notification states.
2. Configure retry/catch behavior for transient and permanent errors.
3. Pass object identifiers rather than large image payloads between states.
4. Set execution timeouts and log retention.
5. Have the queue-triggered worker start the workflow and store its execution ARN.
6. Test with an intentionally invalid image.

## Phase 6 — Delivery and notification

1. Create CloudFront with the destination bucket as a private origin using Origin Access Control.
2. Define cache behavior for generated images and versioned object paths.
3. Create SNS topic for success/failure notifications.
4. Publish completion only after output objects and metadata are consistent.
5. Add a status endpoint reading DynamoDB.

## Phase 7 — Test

- Valid upload creates expected variants.
- Invalid and oversized images are rejected.
- Duplicate events do not create duplicate outputs.
- A transient failure retries.
- Permanent failure reaches DLQ and triggers an alarm.
- Generated image is available through CloudFront.
- Both buckets remain private.

## Cleanup

Remove CloudFront, API, event notifications, Lambda functions/layers, Step Functions, SQS, SNS, DynamoDB, and finally empty and delete both S3 buckets. Remove log groups if no longer required.

## Definition of done

The pipeline is asynchronous, retryable, observable, idempotent, and private by default. Document a sample upload, processing status, output URL, tests, and cleanup.
