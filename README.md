# 📦 Service Name

A microservice responsible for _[brief description]_ within a distributed system. This service communicates asynchronously with other services using **RabbitMQ**.

---

## 🧠 Overview

- **Language/Framework:** _e.g., Node.js (NestJS), Python (FastAPI), etc._
- **Broker:** RabbitMQ
- **Communication Pattern:** _e.g., Pub/Sub, Work Queue, RPC_
- **Database:** _e.g., PostgreSQL, MongoDB (if applicable)_

---

## 🚀 Features

- ✅ Feature 1
- ✅ Feature 2
- ✅ Optional Feature 3

---

## 📬 Messaging Architecture

### Routing Keys

| Queue Name     | Purpose                           | Consumed By  |
| -------------- | --------------------------------- | ------------ |
| `queue.name.1` | Handles incoming tasks            | This service |
| `queue.name.2` | Processes events from XYZ service | This service |

### Exchanges

| Exchange Name   | Type  | Bound Queues   | Purpose                         |
| --------------- | ----- | -------------- | ------------------------------- |
| `exchange.name` | topic | `queue.name.1` | Routes messages for XYZ process |

---

## 📥 Consumes

- `queue.name.1`: Receives job requests for processing.
- `queue.name.2`: Listens for events from the XYZ service.

## 📤 Publishes

- `queue.name.3`: Sends results to downstream service.
- `queue.name.4`: Emits domain events for other services.

---

## ⚙️ Configuration

| Variable        | Description                | Default            |
| --------------- | -------------------------- | ------------------ |
| `RABBITMQ_URL`  | RabbitMQ connection string | `amqp://localhost` |
| `QUEUE_NAME`    | Name of the primary queue  | `service.queue`    |
| `EXCHANGE_NAME` | Name of the exchange       | `service.exchange` |

---

## 🛠️ Running Locally

```bash
# Install dependencies
npm install

# Start service
npm run start:dev
```

Ensure RabbitMQ is running. You can start it with Docker:

```bash
docker run -d \
  --hostname rabbit \
  --name rabbitmq \
  -p 5672:5672 -p 15672:15672 \
  rabbitmq:3-management
```

Access RabbitMQ UI at: [http://localhost:15672](http://localhost:15672)  
Default credentials: `guest` / `guest`

---

## 📈 Health & Metrics

- `GET /health` – Health check endpoint
- `GET /metrics` – Exposes Prometheus metrics _(if implemented)_

---

## 🧪 Testing

```bash
# Run tests
npm test
```

---

## 🔗 Related Services

- [auth-service](https://github.com/your-org/auth-service)
- [order-service](https://github.com/your-org/order-service)
- [notification-service](https://github.com/your-org/notification-service)

---

## 📝 License

This project is licensed under the [MIT License](./LICENSE).
