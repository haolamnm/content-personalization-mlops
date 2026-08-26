---
title: "Messaging Design — Facts, Commands, and Workflows"
id: architecture-messaging
date: 2026-08-26
type: comparison
status: draft
tags: [architecture, messaging, kafka, rabbitmq, temporal]
related:
  - ./system-flow.md
  - ./domain-contracts.md
  - ./decision-gates.md
---

# Messaging Design — Facts, Commands, and Workflows

This page answers one question: which mechanism carries a fact, a work item, or a multi-step workflow?

## Semantic split

| Mechanism | Carries | Strength | Boundary in this platform |
|:---|:---|:---|:---|
| Kafka | Facts and durable event streams | Retention, fan-out, replay, partitioned ordering | Impressions, clicks, CDC, derived streams |
| RabbitMQ | Work items and commands | Routing, acknowledgements, retries, worker backpressure | Training and operational task experiments |
| Temporal | Durable workflow state | Long-running steps, retries, timers, and recovery | Candidate for training/promotion workflows |
| Dagster | Data/ML asset orchestration | Asset dependencies, materializations, lineage, and schedules | Candidate for feature/backfill pipelines |
| NATS JetStream | Lightweight streams and messaging | Small operational footprint and simple transport | Broker comparison only |
| Redpanda | Kafka-compatible event streaming | Broker alternative with Kafka client compatibility | Kafka comparison only |

## Canonical rule

Kafka remains the event backbone. RabbitMQ does not replace it, and a RabbitMQ queue is not the historical record of a recommendation outcome.

The RabbitMQ experiment uses commands such as `train_model`, `materialize_features`, `rebuild_candidates`, or `send_notification`. Workers use manual acknowledgements, bounded prefetch, retry limits, dead-letter handling, and idempotency keys.

Worker lifecycle facts can be emitted to Kafka or stored in MLflow. RabbitMQ transports the command; it does not own the system history.

## RabbitMQ learning slice

```text
POST /training-jobs → dispatcher → RabbitMQ exchange → training-worker
                                                        ↓
                                              ack / retry / dead letter
```

The experiment must observe worker death before acknowledgement, duplicate delivery, poison-message handling, publisher confirmation, prefetch fairness, and the difference between broker acceptance and task completion.

## Temporal versus RabbitMQ versus Dagster

RabbitMQ answers “which worker should receive this task?” Temporal answers “where is this multi-step workflow after a crash or timeout?” Dagster answers “which data and ML assets must be materialized, and in what dependency order?”

They may interact, but they are not interchangeable. Choosing all three without separate ownership boundaries would create orchestration sprawl.

## Read next

- [Data platform](./data-platform.md) for Kafka Connect, schemas, and storage.
- [ML platform](./ml-platform.md) for training and evaluation workflows.
- [Decision gates](./decision-gates.md) before adopting another broker or orchestrator.

## Primary references

- [Apache Kafka documentation](https://kafka.apache.org/documentation/)
- [RabbitMQ reliability](https://www.rabbitmq.com/docs/reliability)
- [RabbitMQ consumers](https://www.rabbitmq.com/docs/consumers)
- [Temporal workflows](https://docs.temporal.io/workflows)
- [Dagster documentation](https://docs.dagster.io/)
