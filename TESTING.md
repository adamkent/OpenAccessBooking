# Testing Guide

## Overview

Both backend and frontend have comprehensive test suites using industry-standard testing frameworks.

## Backend Testing (pytest)

### Quick Start
```bash
cd backend
pip install -r requirements.txt --break-system-packages
pytest
```

### Test Coverage
- ✅ Validators (NHS number, email, phone, postcode)
- ✅ Authentication (login, registration)
- ✅ Appointments (CRUD operations)
- ✅ Patients (CRUD operations)

### Run with Coverage
```bash
pytest --cov=src --cov-report=html
```

View coverage: `open backend/htmlcov/index.html`

## Frontend Testing (Jest + React Testing Library)

### Quick Start
```bash
cd frontend
npm test
```

### Test Coverage
- ✅ Validation utilities
- ✅ API service functions
- ✅ React components
- ✅ User interactions

### Run with Coverage
```bash
npm test -- --coverage --watchAll=false
```

## Test Structure

```
backend/tests/
├── conftest.py              # Shared fixtures
├── test_validators.py       # ~15 tests
├── test_auth.py            # ~8 tests
├── test_appointments.py    # ~6 tests
└── test_patients.py        # ~4 tests

frontend/src/
├── utils/validation.test.js     # ~20 tests
├── services/api.test.js         # ~8 tests
└── components/common/Button.test.js  # ~5 tests
```

## CI/CD Integration (Future)

### Pre-commit Hooks
```bash
# Install pre-commit
pip install pre-commit

# Setup hooks
pre-commit install

# Tests will run automatically before commits
```

### GitHub Actions (Example)
```yaml
name: Tests
on: [push, pull_request]
jobs:
  backend:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - run: cd backend && pip install -r requirements.txt
      - run: cd backend && pytest --cov
  
  frontend:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - run: cd frontend && npm install
      - run: cd frontend && npm test -- --coverage --watchAll=false
```

## Running All Tests

### Backend
```bash
cd backend && pytest -v
```

### Frontend
```bash
cd frontend && npm test -- --watchAll=false
```

### Both
```bash
# Backend
cd backend && pytest && cd ..

# Frontend
cd frontend && npm test -- --watchAll=false && cd ..
```

## Writing New Tests

### Backend (pytest)
```python
def test_my_function(mock_db):
    result = my_function()
    assert result == expected
```

### Frontend (Jest)
```javascript
test('my component renders', () => {
  render(<MyComponent />);
  expect(screen.getByText('Hello')).toBeInTheDocument();
});
```

## Best Practices

1. **Write tests first** (TDD when possible)
2. **Test behaviour, not implementation**
3. **Keep tests simple and focused**
4. **Mock external dependencies**
5. **Aim for >80% coverage**
6. **Run tests before committing**

## Debugging Failed Tests

### Backend
```bash
pytest -v --tb=long  # Verbose traceback
pytest -x            # Stop on first failure
pytest --pdb         # Drop into debugger on failure
```

### Frontend
```bash
npm test -- --verbose
npm test -- --no-coverage  # Faster
```

## Next Steps

- [ ] Add integration tests
- [ ] Add E2E tests (Playwright/Cypress)
- [ ] Setup pre-commit hooks
- [ ] Configure CI/CD pipeline
- [ ] Add performance tests
- [ ] Add security tests
