---
title: "ML Platform Design — Features, Workflows, and Serving"
id: architecture-ml-platform
date: 2026-08-26
type: architecture
status: draft
tags: [architecture, mlops, features, serving]
related:
  - ./system-flow.md
  - ./domain-contracts.md
  - ./messaging.md
  - ./production-bar.md
---

# ML Platform Design — Features, Workflows, and Serving

This page answers one question: how does historical data become a measured model and a safe online recommendation?

## Feature plane

Feast owns feature definitions and the contract between historical training and online serving. Iceberg is the offline store for point-in-time-correct values; Redis or Valkey is the online store for fresh low-latency values.

A feature is not complete if it works only in one store. The offline and online definitions need parity, freshness rules, missing-value behavior, and tests.

## Training plane

Ray Train and Tune provide the training and tuning runtime. MLflow tracks experiments, artifacts, model versions, and promotion state.

The model evaluation job is a first-class component: it computes offline metrics, slice metrics, calibration or ranking quality, and promotion evidence before a model reaches serving.

## Workflow plane

Dagster is a candidate for asset-oriented feature, backfill, and training orchestration. Temporal is a candidate for durable multi-step workflows with retries, timers, and recovery. Airflow, Prefect, Flyte, Kubeflow Pipelines, and Argo Workflows are alternatives to compare, not a shopping list.

The choice depends on the dominant unit: data asset dependencies, durable business workflow state, or Kubernetes-native job execution.

## Serving plane

FastAPI and Ray Serve are the current target for model inference. KServe is the Kubernetes-native alternative when declarative model resources, traffic management, autoscaling, and standardized inference protocols matter more than the current simple runtime.

BentoML is a developer-focused serving alternative. NVIDIA Triton is a specialized option when multi-framework CPU/GPU throughput is the bottleneck.

The Rust retrieval service owns candidate retrieval, feature joining, and ranking. It calls model serving through a stable contract and returns a ranked feed to the Go BFF.

## Model monitoring

Evidently is a candidate for evaluating data quality, drift, prediction behavior, and model performance after deployment. Monitoring is part of the model lifecycle, not an observability afterthought.

## Selection rule

Do not adopt Dagster, Temporal, Airflow, Prefect, Flyte, Kubeflow Pipelines, and Argo Workflows together. Do not adopt Ray Serve, KServe, BentoML, and Triton together without separate model-runtime requirements.

## Read next

- [Data platform](./data-platform.md) for offline data and table contracts.
- [Messaging](./messaging.md) for command and workflow transport.
- [Production bar](./production-bar.md) for evaluation and rollback proof.

## Primary references

- [Feast documentation](https://docs.feast.dev/)
- [Dagster documentation](https://docs.dagster.io/)
- [KServe documentation](https://kserve.github.io/website/docs/intro)
