
# 📦 Migrating from Python Log Shipper to Fluentd in OpenShift

## 🎯 Motivation

We initiated this migration to improve performance, maintainability, and scalability of our log shipping pipeline. Key drivers included:

- 🔧 **Replace custom Python code**: Avoid maintaining brittle scripts and one-off configurations.
- 🔁 **Dynamic log routing**: Centralize logic to route logs by source, type, or content using Fluentd’s tag/match system.
- 🚚 **Smooth migration path**: By using a **central Fluentd deployment** instead of injecting sidecars (like Fluent Bit or Filebeat) into all services, we:
  - Avoided friction or changes in other teams' services
  - Accelerated implementation without requiring DevOps coordination
  - Reduced pod sprawl and OCP resource overhead

---

## 📌 Overview

We migrated our centralized log shipping mechanism from a custom Python-based service to a more scalable, production-grade Fluentd-based solution running in OpenShift (OCP). This document summarizes the motivation, implementation details, and architectural changes.

---

## 🤖 What is Fluentd?

[Fluentd](https://www.fluentd.org/) is an open-source data collector that helps unify and route logs across various systems. It supports over 500 plugins for input, output, filtering, and formatting, making it a powerful and flexible choice for modern logging pipelines.

### Why Fluentd?

- 🔌 **Plugin-rich**: Seamless integration with Elasticsearch, Prometheus, S3, Kafka, etc.
- 🧩 **Flexible routing**: Route logs dynamically with tag-based filtering and matching.
- 🚀 **High-performance**: Handles thousands of log lines per second with buffering and retry.
- 🌐 **Cloud-native**: Ideal for Kubernetes/OpenShift environments with ConfigMap-based configs.
- 🔄 **Reliable delivery**: Built-in support for buffering, retries, and backpressure handling.

---

## ✅ Background

### 🧾 Previous Setup (Python Shipper)

- Each service logs to **stdout** and a **rotating file**.
- Logs rotate every **60 seconds** or after **1,000 lines**.
- Rotated logs are moved to a **shared NFS**.
- A Python script scanned the NFS based on a JSON config:

  ```json
  {
    "service-dir": {
      "index": "my_app",
      "index_date_pattern": "%Y.%m",
      "type": "_doc"
    }
  }
  ```

- Logs were sent to **custom Elasticsearch indices** (`my_app-2025.07`).
- **Index rollover** was handled manually via naming patterns.

---

### 🆕 New Setup (Fluentd on OCP)

- A **single Fluentd deployment** (not DaemonSet, due to limited OCP permissions) reads logs directly from the **same NFS**.
- Fluentd is configured via a **ConfigMap** using:
  - `source`, `filter`, and `match` blocks
  - `elasticsearch_data_stream` plugin
- Logs are sent to **Elasticsearch Data Streams** with an **Index Lifecycle Management (ILM)** policy.
- Logs are enriched, routed, and compressed natively via Fluentd.

---

## 🌍 Logging Best Practices

- Centralized logging is crucial for observability, troubleshooting, and compliance.
- Use **structured logs** (JSON format) when possible.
- Ensure **separation of concerns**: app writes logs; a dedicated shipper forwards them.
- Prefer **data streams** + **ILM** over manual index management.
- Use **compressed protocols**, **buffers**, and **failover** for resilience.

---

## 📘 Fluentd in Modern Log Systems — Best Practices

Fluentd is a widely adopted **Cloud Native Computing Foundation (CNCF)** project and a cornerstone of modern observability pipelines. Here's why it's considered best practice in modern log architecture:

### ✅ 1. Single Binary, Multiple Sources

Fluentd supports **over 500 input/output plugins** and can ingest logs from files, systemd, Docker, Kafka, syslog, and more — all within a single agent.  
> 🔹 *Best Practice:* Use Fluentd as a **log unifier** for all your sources.

### ✅ 2. Configurable, Not Coded

Fluentd is **declarative and config-driven**, unlike custom log shippers written in Python.  
> 🔹 *Best Practice:* Centralize log routing logic in Fluentd config.

### ✅ 3. Buffering and Retry Mechanism

Built-in support for **persistent buffering**, **exponential backoff**, and **dead-letter queues** ensures reliable delivery.  
> 🔹 *Best Practice:* Enable `buffer`, `retry`, and `flush_interval`.

### ✅ 4. Native Kubernetes/OpenShift Integration

Fluentd integrates with ConfigMaps and volumes, and fits naturally in containerized ecosystems.  
> 🔹 *Best Practice:* Use as a **Deployment** when DaemonSet isn't allowed.

### ✅ 5. Structured Logging with JSON

Parsing logs into JSON improves downstream usability in tools like Kibana.  
> 🔹 *Best Practice:* Parse logs into **structured JSON** early.

### ✅ 6. Output Routing with Tags

Tags make routing and filtering dynamic and scalable.  
> 🔹 *Best Practice:* Use tags and `match` blocks for flexibility.

### ✅ 7. Performance and Resource Efficiency

Fluentd processes **thousands of lines per second** per core with minimal memory use.  
> 🔹 *Best Practice:* Use multi-process/workers in high-throughput cases.

### ✅ 8. Built-In Monitoring

Expose Prometheus metrics for full observability into Fluentd performance.  
> 🔹 *Best Practice:* Monitor and alert on buffer size, retries, and errors.

### ✅ 9. Data Streams > Static Indices

Elasticsearch recommends Data Streams + ILM for all new deployments.  
> 🔹 *Best Practice:* Migrate to data streams like `logs-app`, `logs-system`.

---

## 🔄 Why Fluentd?

| Feature              | Python Shipper     | Fluentd (New)        |
|----------------------|--------------------|----------------------|
| Scalability          | ❌ One pod per config | ✅ Single deployment |
| Performance          | ⚠️ Limited I/O perf  | 🚀 High throughput   |
| Resilience           | ❌ Manual recovery   | ✅ Buffer & retry    |
| Maintenance          | ❌ Custom scripts    | ✅ Config-driven     |
| Elasticsearch Support| Basic (index only) | ✅ Native Data Stream |
| Community/Plugins    | Limited             | 🧩 Huge ecosystem     |

---

## 📊 Advantages of Fluentd

- **No custom Python code** → fewer maintenance concerns.
- **Faster throughput** → Fluentd handles thousands of lines/sec per core.
- **Unified deployment** → No need to spin up per-directory log shippers.
- **Dynamic configuration** → Easy to extend, filter, enrich, or reroute logs.
- **Native Elasticsearch support** → Better integration, retries, and compression.

---

## 📈 Why Data Streams over Indices?

- 🔄 **Automatic rollover & aging** with **Index Lifecycle Management (ILM)**.
- 🧩 **Standardized naming** and structure.
- 📉 **Optimized for time-series data** (e.g., logs, metrics).
- 🚀 Better performance and simpler queries in Kibana/Elastic UI.

---

## 💡 Additional Benefits (*added by ChatGPT*)

- 📥 **Input Plugins**: Fluentd can read from files, sockets, HTTP, Kafka, etc.
- ⚙️ **Output Flexibility**: Logs can be mirrored to Elastic, S3, or OpenSearch.
- 🧪 **Observability**: Native Prometheus metrics and error tracking.
- ☁️ **Cloud Native**: Easily integrated with OCP/Kubernetes workflows.

---

## 🛠️ Fluentd Configuration Example

Here is a minimal Fluentd configuration used in the new setup:

```conf
<source>
  @type tail
  path /mnt/nfs/logs/**/*.log
  pos_file /fluentd/pos/logs.pos
  tag logs.*
  <parse>
    @type json
  </parse>
</source>

<filter logs.**>
  @type record_transformer
  <record>
    source_file ${record["file"]}
  </record>
</filter>

<match logs.**>
  @type elasticsearch_data_stream
  host elasticsearch.logging.svc
  port 9200
  data_stream_name logs-app
  data_stream_type logs
  include_tag_key false
  flush_interval 5s
</match>
```

### 📌 About `pos_file`

Fluentd tracks read position in log files using the `pos_file`. This allows:

- Resuming on restart without reprocessing
- Tracking which files have been fully consumed

---

## 🧹 Log Cleanup Strategy

Previously, the **Python shipper** was responsible for deleting old log files from the NFS.  
In the new setup:

- A **cron job** reads the `pos_file` to determine which files have been fully consumed
- It then safely deletes only those files

This ensures that Fluentd has completely read a file before deletion.

---

## 🔍 Sanity Check: Log Count Verification

To ensure **no log loss** during the migration:

1. The **cron job** logs the number of lines per file before deletion.
2. An **Elasticsearch aggregation query** compares that count to the number of documents ingested for each source file in the data stream.

📊 As of now, **over 60,000 log files** have been processed — with **zero loss detected**.

---

## 🔚 Summary

This migration enhances our logging pipeline by making it:

- **More scalable** (1 pod → all logs),
- **More resilient** (buffering, retries),
- **More maintainable** (no more code updates),
- **More compliant with Elastic’s best practices** (Data Streams + ILM).

All routing, filtering, and output logic is now managed centrally via Fluentd configuration.
