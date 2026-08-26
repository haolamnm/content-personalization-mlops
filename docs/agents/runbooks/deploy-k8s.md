---
title: "Runbook: Operate the k3s Cluster"
id: agents-runbook-deploy-k8s
date: 2026-08-26
type: runbook
status: active
tags: [kubernetes, k3s, helm, thinkbook, deploy]
related:
  - ../../adr/0007-kubernetes-adoption-k3s-helm.md
  - deploy-thinkbook.md
  - ../../../.computers/THINKBOOK.md
---

# Runbook: Operate the k3s Cluster (THINKBOOK)

Single-node k3s per [ADR 0007](../../adr/0007-kubernetes-adoption-k3s-helm.md). All root operations go through **`mlops-sudo`** — the only NOPASSWD surface; everything else stays password-gated. Box-specific values (tailnet IP, kubeconfig paths, measured costs) live in `.computers/THINKBOOK.md` §6, never here.

## Integrity gate (run after any change to either copy)

The box copy of the helper must stay byte-identical to the tracked source:

```bash
ssh thinkbook 'sha256sum ~/.local/bin/mlops-sudo | cut -d" " -f1'
shasum -a 256 platform/infra/thinkbook/mlops-sudo | cut -d' ' -f1   # must match
```

If they diverge: `git pull` on the box, then reinstall from the repo copy (`install -m 0755 platform/infra/thinkbook/mlops-sudo ~/.local/bin/mlops-sudo`) — never hand-edit the box copy.

## Bootstrap from scratch (reproducible sequence)

Order matters; each gate before the next step:

```bash
# 1. dependencies + firewall (API scoped to tailnet, pod/service CIDRs trusted)
ssh thinkbook 'sudo -n ~/.local/bin/mlops-sudo pkg-install container-selinux selinux-policy-base policycoreutils-python-utils curl'
ssh thinkbook 'bash -c "TS=\$(tailscale ip -4); sudo -n ~/.local/bin/mlops-sudo firewall --permanent --add-rich-rule=\"rule family=ipv4 source address=\$TS port port=6443 protocol=tcp accept\" && sudo -n ~/.local/bin/mlops-sudo firewall --permanent --zone=trusted --add-source=10.42.0.0/16 && sudo -n ~/.local/bin/mlops-sudo firewall --permanent --zone=trusted --add-source=10.43.0.0/16 && sudo -n ~/.local/bin/mlops-sudo firewall-reload"'

# 2. install + export kubeconfig to the account
ssh thinkbook 'bash -c "sudo -n ~/.local/bin/mlops-sudo k3s-install && sudo -n ~/.local/bin/mlops-sudo kubeconfig-export"'
sleep 25

# 3. tailnet SAN + cert rotation (remote kubectl fails x509 without it)
ssh thinkbook 'bash -c "sudo -n ~/.local/bin/mlops-sudo tls-san-sync && sudo -n ~/.local/bin/mlops-sudo service restart k3s"'
sleep 25

# 4. gates: node Ready on-box AND remote TLS handshake from the authoring box
ssh thinkbook 'KUBECONFIG=$HOME/.kube/config kubectl get nodes'
export KUBECONFIG=~/.kube/config && kubectl get nodes
```

Authoring-box kubeconfig is the exported copy with `server:` rewritten from loopback to the tailnet address (see §6 for the value); regenerate that edit whenever the SAN changes.

## Day-2 operations

| Task | Command |
|:---|:---|
| Restart control plane | `ssh thinkbook 'sudo -n ~/.local/bin/mlops-sudo service restart k3s'` |
| Tailscale re-assigned IP → cert invalid | rerun `tls-san-sync` + restart (idempotent), then redo the authoring-box server rewrite |
| Install cluster packages | `pkg-install …` (dnf) — node-level packages only; in-cluster software ships as charts/images |
| Full teardown | `mlops-sudo k3s-uninstall` (also removes the SELinux package cleanly) |

## Image flow (the migration gotcha)

k3s embeds its own containerd — **images built/pulled by Docker are invisible to it** (`ErrImagePull` despite `docker images` showing them). Two paths when migrating services off compose:

1. Push to a registry the cluster can reach, or
2. One-shot import through the helper: `docker save <image> | ssh thinkbook 'sudo -n ~/.local/bin/mlops-sudo image-import'`

Avoid `:latest` tags — its default `imagePullPolicy: Always` defeats locally imported images.

## Data-plane cutover

The standing data-plane assets live in [`platform/infra/k8s/`](../../../platform/infra/k8s/README.md). Apply the operator resources before the owned-service values, restore the captured data before stopping Compose, and preserve the old named volumes as rollback evidence. The final gate is one Strimzi Kafka cluster, one Strimzi KafkaConnect/Debezium connector, healthy CNPG/MongoDB/MinIO, and zero `data-*` or `cdc-connect` containers on THINKBOOK.

## Verification habits

- Node + workload health: `kubectl get nodes`, `kubectl get pods -A`
- Control-plane cost check before/after big changes: `free -h` deltas recorded in `.computers/THINKBOOK.md` §5/§6
- Never bypass the helper with ad-hoc root shells — if a needed capability is missing, extend `platform/infra/thinkbook/mlops-sudo` through review instead
