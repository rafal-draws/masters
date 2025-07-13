# Masters Project

This repository contains two major components housed in `/back` and `/data`, each containerized for portability and ease of deployment.

---

## Table of Contents

- [Project Structure](#project-structure)
- [Containerization Overview](#containerization-overview)
  - [Back Service (Rust)](#back-service-rust)
  - [Data Service (Python/FastAPI)](#data-service-pythonfastapi)
- [How to Build and Run](#how-to-build-and-run)
- [Directory Details](#directory-details)
  - [back/](#back)
  - [data/](#data)
- [License](#license)

---

## Project Structure

```
masters/
├── back/
│   └── Dockerfile
├── data/
│   └── Dockerfile
```

---

## Containerization Overview

This repository is designed with containerization in mind, using Docker for both the backend (`/back`) and data processing/API layer (`/data`). Each service has its own `Dockerfile`, supporting isolated dependency management and deployment.

### Back Service (Rust)

- **Base Image:** `rust:1.87`
- **Build Steps:**
  - Sets working directory.
  - Copies all source files.
  - Installs `dos2unix` for script compatibility.
  - Converts and executes `libtorch_setup.sh` to install libtorch dependencies.
  - Sets environment variables for libtorch paths.
  - Installs `sqlx-cli` for database migration.
  - Runs database migrations.
  - Builds the project using `cargo`.
- **Entrypoint:** Runs the Rust backend binary.

**Dockerfile Summary:**
```dockerfile
FROM rust:1.87
WORKDIR /usr/src/myapp
COPY . .
RUN apt-get update && apt-get install -y dos2unix 
RUN dos2unix libtorch_setup.sh
RUN bash ./libtorch_setup.sh
ENV LIBTORCH=/home/util/libtorch/libtorch
ENV LIBTORCH_INCLUDE=/home/util/libtorch/libtorch
ENV LIBTORCH_LIB=/home/util/libtorch/libtorch
ENV LD_LIBRARY_PATH=/home/util/libtorch/libtorch/lib:$LD_LIBRARY_PATH
RUN cargo install sqlx-cli
RUN sqlx migrate run
RUN cargo build
CMD ["./target/debug/back"]
```

### Data Service (Python/FastAPI)

- **Base Image:** `python:3.12`
- **Build Steps:**
  - Sets working directory.
  - Installs Python dependencies from `requirements.txt`.
  - Copies all source files.
  - Installs `ffmpeg` for media processing.
- **Entrypoint:** Launches the FastAPI application on port 8888.

**Dockerfile Summary:**
```dockerfile
FROM python:3.12
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir  -r requirements.txt
COPY . .
RUN apt update
RUN  apt install -y ffmpeg
CMD ["fastapi", "run", "app.py", "--port", "8888"]
```

---

## How to Build and Run

### Prerequisites

- [Docker](https://docs.docker.com/get-docker/) installed

### Build and Run Each Service

#### Back (Rust)

```sh
cd back
docker build -t masters-back .
docker run --rm -p 8000:8000 masters-back
```

#### Data (Python/FastAPI)

```sh
cd data
docker build -t masters-data .
docker run --rm -p 8888:8888 masters-data
```

### (Optional) Compose

If you have a `docker-compose.yml`, you can orchestrate both services together. (Add details if available.)

---

## Directory Details

### back/

- **Purpose:** Rust-based backend service.
- **Containerization:** Uses `rust:1.87`, includes steps for setting up libtorch and database migrations.
- **Entrypoint:** Compiled Rust binary.

### data/

- **Purpose:** Python-based data processing/API service using FastAPI.
- **Containerization:** Uses `python:3.12`, installs dependencies, and includes `ffmpeg`.
- **Entrypoint:** Runs FastAPI app on port 8888.

---

## License

(Include license details here.)

---

_This README provides an overview of the project structure and containerization setup. For more details on service-specific endpoints, environment variables, or orchestration, refer to in-source documentation or additional files in each subdirectory._
