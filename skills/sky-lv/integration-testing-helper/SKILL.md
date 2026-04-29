# integration-testing-helper

Comprehensive integration testing assistant for AI agents. Create, run, and manage integration tests across APIs, databases, and services.

## Overview

Helps agents perform end-to-end integration testing by orchestrating multiple services, setting up test data, and validating system behavior.

## Features

- **Test Scenario Design**: Create complex integration test scenarios
- **Service Orchestration**: Start/stop required services for tests
- **Data Setup**: Prepare test databases and fixtures
- **Assertion Library**: Built-in assertions for common patterns
- **Test Reports**: Generate detailed HTML/JSON test reports
- **CI Integration**: Easy integration with GitHub Actions, GitLab CI
- **Parallel Execution**: Run multiple test scenarios concurrently

## Commands

### Create Integration Test

```
create integration test for user registration flow
```

### Run Tests

```
run integration tests with coverage report
```

### Validate API Integration

```
test API integration between auth-service and user-service
```

## Use Cases

- API integration testing
- Database integration validation
- Microservice communication testing
- E2E workflow validation
- Regression testing

## Requirements

- Node.js 18+
- Docker (optional, for service containers)
