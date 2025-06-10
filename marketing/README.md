# 📦 Subscriber

A microservice responsible to act as a listener (persons) subscribed to promotions made by the marketing service within a distributed system. It communicates asynchronously with other services via **RabbitMQ** queues and/or topics.

---

## 🧠 Overview

- **Language/Framework:** [e.g., Node.js + NestJS, Python + FastAPI, etc.]
- **Message Broker:** RabbitMQ
- **Pattern:** [e.g., Publish/Subscribe, Work Queues, RPC]
- **Communication:** Asynchronous via queues and/or exchanges
- **Database:** [if applicable]

---

## 🚀 Features

- [x] [Feature 1]
- [x] [Feature 2]
- [x] [Optional Feature 3]

---

## 📬 Messaging Architecture

### Routing Keys Used

| Queue Name     | Purpose                    | Consumed By     |
| -------------- | -------------------------- | --------------- |
| `queue.name.1` | [Purpose of the queue]     | This service    |
| `queue.name.2` | [Purpose of another queue] | [Other service] |

### Exchanges Used

| Exchange Name   | Type                | Bound Queues   | Description               |
| --------------- | ------------------- | -------------- | ------------------------- |
| `exchange.name` | topic/fanout/direct | `queue.name.1` | [Purpose of the exchange] |

---

## 📥 Consumes

- Messages from:
  - `queue.name.1`: [brief explanation]
  - `queue.name.2`: [brief explanation]

## 📤 Publishes

- Messages to:
  - `queue.name.3`: [brief explanation]
  - `queue.name.4`: [brief explanation]

---

## ⚙️ Configuration

| Variable        | Description                   | Default            |
| --------------- | ----------------------------- | ------------------ |
| `RABBITMQ_URL`  | Connection string to RabbitMQ | `amqp://localhost` |
| `QUEUE_NAME`    | Queue used by this service    | `service.queue`    |
| `EXCHANGE_NAME` | Exchange used by this service | `service.exchange` |

---

## 🛠️ Running Locally

```bash
# Install dependencies
npm install

# Start the service
npm run start:dev
```
