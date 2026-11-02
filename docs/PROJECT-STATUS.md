# Project Delivery Status

This file distinguishes the published learning guides from deployable implementations.

| Project | Architecture guide | Infrastructure code | Application code | Automated tests | AWS deployment verified |
|---|---|---|---|---|---|
| 01 — Scalable web app | Complete | Pending | Pending | Pending | Not deployed |
| 02 — Image processing | Complete | Pending | Pending | Pending | Not deployed |
| 03 — Cognito REST API | Complete | Pending | Pending | Pending | Not deployed |
| 04 — Hybrid connectivity | Complete | Pending | Pending | Pending | Not deployed |
| 05 — Multi-region DR | Complete | Pending | Pending | Pending | Not deployed |
| 06 — ECS microservices | Complete | Pending | Pending | Pending | Not deployed |
| 07 — Serverless data lake | Complete | Pending | Pending | Pending | Not deployed |

## Acceptance gates for each project

A project is not considered complete until all applicable gates pass:

1. **Code:** infrastructure and application source are committed; versions are pinned.
2. **Static checks:** formatting, linting, security scanning, and unit tests pass.
3. **Deployment:** a clean environment can be deployed by following the README.
4. **Validation:** success cases, negative cases, and failure/recovery scenarios pass.
5. **Evidence:** architecture, test outputs, screenshots/log excerpts with secrets removed, and known limitations are documented.
6. **Teardown:** resources are removed and remaining billable resources are checked.

## Suggested sequence

Build and validate one project end-to-end before starting the next. Project 01 provides the network, IAM, compute, load balancing, and monitoring foundation. Projects 02 and 03 then add serverless patterns. Project 04 is a separate network lab requiring an actual VPN peer for live tunnel testing. Project 05 builds on the web application. Projects 06 and 07 introduce containers and data engineering.

**Important:** The current repository seed is a documentation milestone. No AWS infrastructure has been deployed by this repository initialization.
