# Backend Tests

## Running Tests

### Install Dependencies
```bash
cd backend
pip install -r requirements.txt --break-system-packages
```

### Run All Tests
```bash
pytest
```

### Run with Coverage
```bash
pytest --cov=src --cov-report=html
```

### Run Specific Test File
```bash
pytest tests/test_validators.py
```

### Run Specific Test Class
```bash
pytest tests/test_auth.py::TestLogin
```

### Run Specific Test
```bash
pytest tests/test_auth.py::TestLogin::test_login_success
```

### Run with Verbose Output
```bash
pytest -v
```

### Run and Stop on First Failure
```bash
pytest -x
```

## Test Structure

```
tests/
├── __init__.py
├── conftest.py              # Shared fixtures
├── test_validators.py       # Validation function tests
├── test_auth.py            # Authentication tests
├── test_appointments.py    # Appointment CRUD tests
└── test_patients.py        # Patient CRUD tests
```

## Writing New Tests

1. Create test file: `test_<module>.py`
2. Import module to test
3. Use fixtures from `conftest.py`
4. Follow naming convention: `test_<function_name>`

Example:
```python
def test_my_function(mock_db, sample_patient):
    result = my_function(sample_patient)
    assert result == expected_value
```

## Fixtures Available

- `mock_db` - Mocked database manager
- `sample_patient` - Sample patient data
- `sample_appointment` - Sample appointment data
- `lambda_event` - Lambda event builder

## Coverage Report

After running with `--cov`, open `htmlcov/index.html` in browser to view detailed coverage report.
