# Frontend Testing

## Running Tests

### Run All Tests
```bash
cd frontend
npm test
```

### Run Tests in Watch Mode
```bash
npm test -- --watch
```

### Run with Coverage
```bash
npm test -- --coverage
```

### Run Specific Test File
```bash
npm test -- validation.test.js
```

### Run Tests Once (CI Mode)
```bash
npm test -- --watchAll=false
```

## Test Structure

```
src/
├── components/
│   └── common/
│       └── Button.test.js
├── services/
│   └── api.test.js
├── utils/
│   └── validation.test.js
└── setupTests.js
```

## Writing New Tests

### Component Tests
```javascript
import { render, screen, fireEvent } from '@testing-library/react';
import MyComponent from './MyComponent';

test('renders component', () => {
  render(<MyComponent />);
  expect(screen.getByText('Hello')).toBeInTheDocument();
});
```

### API Tests
```javascript
import { myApiFunction } from './api';

test('calls API correctly', async () => {
  global.fetch = jest.fn(() =>
    Promise.resolve({
      ok: true,
      json: () => Promise.resolve({ data: 'test' })
    })
  );

  const result = await myApiFunction();
  expect(result.data).toBe('test');
});
```

### Utility Tests
```javascript
import { myUtilFunction } from './utils';

test('utility function works', () => {
  expect(myUtilFunction('input')).toBe('expected');
});
```

## Testing Libraries

- **Jest** - Test runner and assertion library
- **React Testing Library** - Component testing utilities
- **@testing-library/jest-dom** - Custom matchers for DOM

## Best Practices

1. **Test behaviour, not implementation**
2. **Use meaningful test descriptions**
3. **Keep tests simple and focused**
4. **Mock external dependencies**
5. **Test edge cases and error states**

## Coverage Goals

- **Statements**: > 80%
- **Branches**: > 75%
- **Functions**: > 80%
- **Lines**: > 80%

## CI Integration

Tests run automatically on:
- Pre-commit (when configured)
- Pull requests
- Main branch pushes

## Debugging Tests

### Run Single Test in Debug Mode
```bash
node --inspect-brk node_modules/.bin/jest --runInBand test_file.test.js
```

### View Test Output
```bash
npm test -- --verbose
```

### Update Snapshots
```bash
npm test -- -u
```
