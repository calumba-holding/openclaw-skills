# mock-server-generator

Create mock HTTP servers for API testing and development. Generate fake data, define endpoints, and simulate responses without a real backend.

## Overview

A skill that helps developers create mock APIs quickly for testing frontend applications, prototyping, or decoupling microservices development.

## Features

- **Quick Server Creation**: Generate a mock server with a single command
- **Custom Endpoints**: Define custom routes, methods, and response bodies
- **Dynamic Responses**: Use templates to generate realistic fake data
- **Delay Simulation**: Add latency to simulate real network conditions
- **Error Simulation**: Easily simulate 4xx/5xx error responses
- **Data Persistence**: Store and retrieve mock data across requests
- **OpenAPI Import**: Generate mocks from OpenAPI/Swagger specifications

## Commands

### Start a Basic Mock Server

```
start mock server on port 3000
```

### Define Custom Endpoints

```
add GET /api/users returning [{"id": 1, "name": "John"}]
add POST /api/posts with delay 500ms
```

### Import from OpenAPI

```
generate mock from https://api.example.com/openapi.json
```

## Use Cases

- Frontend development without a backend
- API testing and test data generation
- Prototyping and demo environments
- CI/CD pipeline testing
- Microservice decoupling

## Requirements

- Node.js 18+
- Optional: Docker for containerized deployment
