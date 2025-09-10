# Proxy server TADS

## Descrição

Este projeto implementa um **serviço proxy interno** para consumir a API externa [score.hsborges.dev](https://score.hsborges.dev/docs) respeitando **rate limit de 1 requisição/segundo**. Ele foi projetado para:

- Gerenciar requisições internas sem violar o limite externo.
- Minimizar penalidades.
- Expor métricas e observabilidade.
- Aplicar padrões de projeto para modularidade e manutenibilidade.

---

## Funcionalidades

- Endpoint `/proxy/score` para encaminhar requisições ao upstream.
- Endpoint `/health` para checagem de status.
- Endpoint `/metrics` (Prometheus) para métricas de filas, circuito e latência.
- Scheduler que garante **1 req/s ao upstream**.
- **Fila com prioridade e TTL** (FIFO ou customizável).
- **Circuit breaker** para lidar com falhas de upstream.
- **Cache** para respostas recentes.
- **Observers** para logs e métricas.
- **Decorators** para logging, retry e cache.

---

## Arquitetura e Padrões

- **Command:** encapsula requisições ao upstream.
- **Singleton:** garante instâncias únicas de filas e cache.
- **Decorator:** adiciona logging, retry e cache dinamicamente.
- **Iterator:** permite percorrer fila de requisições.
- **Observer:** notifica eventos de fila e estado do circuito.
- **Circuit Breaker e Scheduler**: controlam chamadas e falhas do upstream.

---

## Estrutura de Pastas

``` 
app/
├── main.py # Entrypoint FastAPI
├── services/
│ ├── queue.py
│ ├── circuit.py
│ └── scheduler.py
├── patterns/
│ ├── singleton.py
│ ├── observer.py
│ ├── iterator.py
│ ├── command.py
│ └── decorator.py
├── observers/
│ ├── log_observer.py
│ └── metrics_observer.py
├── config.py
├── requirements.txt
└── docker-compose.yml
```

## Como rodar 

### 1. Criar venv

```bash
python3 -m venv venv
source venv/bin/activate   # Linux/macOS
# venv\Scripts\activate    # Windows
```

### 2. Atualizar pip

```bash
pip install --upgrade pip
pip install -r requirements.txt
```

3. Rodar

```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

- Proxy: http://localhost:8000/proxy/score?q=test

- Health: http://localhost:8000/health

- Métricas Prometheus: http://localhost:8001/

## Configuração via variáveis de ambiente

| Variável                 | Padrão                            | Descrição                             |
|---------------------------|----------------------------------|---------------------------------------|
| `UPSTREAM_URL`            | `https://score.hsborges.dev/score` | URL da API externa                     |
| `RATE_LIMIT_INTERVAL`     | `1.0`                             | Intervalo entre chamadas ao upstream (s) |
| `QUEUE_MAX_SIZE`          | `200`                             | Tamanho máximo da fila                 |
| `REQUEST_TIMEOUT`         | `5.0`                             | Timeout para chamadas ao upstream (s) |
| `RETRY_COUNT`             | `2`                               | Número de tentativas em caso de falha |
| `CIRCUIT_ERROR_THRESHOLD` | `5`                               | Falhas para abrir circuito            |
| `CIRCUIT_OPEN_SECONDS`    | `30`                              | Tempo que o circuito fica aberto (s)  |
| `CACHE_TTL`               | `60`                              | Tempo de cache das respostas (s)      |


### Docker

```yaml
    version: "3.9"
    services:
    proxy:
    build: .
    ports:
        - "8000:8000"
        - "8001:8001"
    environment:
        UPSTREAM_URL: "https://score.hsborges.dev/score"
```

```bash
docker-compose up --build
```