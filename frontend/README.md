# NHS Appointment Booking System - Frontend

Modern React application enabling open-access healthcare booking across all NHS facilities. Provides dual portals for patients and healthcare staff with NHS-compliant design and accessibility standards.

## Features

### Patient Portal
- **User Registration & Authentication** - Secure account creation with NHS number validation
- **Appointment Booking** - Multi-step booking process with real-time availability
- **Appointment Management** - View, reschedule, and cancel appointments
- **Profile Management** - Update personal information and contact details
- **Dashboard** - Overview of upcoming appointments and practice information

### Staff Portal
- **Staff Dashboard** - Practice overview with key metrics and today's schedule
- **Appointment Management** - View, update, and manage all practice appointments
- **Patient Management** - Search and manage patient records
- **Practice Settings** - Configure practice information, hours, and services

### Design & Accessibility
- **NHS Design System** - Follows NHS Digital Service Manual guidelines
- **Responsive Design** - Works on desktop, tablet, and mobile devices
- **Accessibility** - WCAG 2.1 AA compliant with screen reader support
- **Progressive Web App** - Installable with offline capabilities

## Technology Stack

- **React 18** - Modern React with hooks and concurrent features
- **React Router** - Client-side routing with protected routes
- **React Query** - Server state management and caching
- **Tailwind CSS** - Utility-first CSS framework with NHS design tokens
- **Lucide React** - Beautiful, customisable icons
- **React Toastify** - Toast notifications for user feedback

## Project Structure

```
src/
├── components/           # Reusable UI components
│   ├── ErrorBoundary/   # Error handling components
│   ├── Layout/          # Layout components (headers, sidebars)
│   └── UI/              # Basic UI components (buttons, modals, spinners)
├── contexts/            # React contexts
│   └── AuthContext.js   # Authentication state management
├── pages/               # Page components
│   ├── auth/           # Authentication pages (login, register)
│   ├── patient/        # Patient portal pages
│   ├── public/         # Public pages (home)
│   └── staff/          # Staff portal pages
├── services/           # API services and utilities
│   └── api.js          # API client and endpoints
├── utils/              # Utility functions
│   ├── dateUtils.js    # Date formatting and manipulation
│   └── validation.js   # Form validation utilities
├── App.js              # Main app component with routing
├── index.css           # Global styles and NHS design system
└── index.js            # App entry point
```

## Getting Started

### Prerequisites

- Node.js 16+ and npm
- Backend API running (see backend documentation)

### Installation

1. **Install dependencies**
   ```bash
   npm install
   ```

2. **Configure environment**
   ```bash
   cp .env.example .env
   ```
   
   Update `.env` with your API configuration:
   ```
   REACT_APP_API_URL=http://localhost:3001
   REACT_APP_ENV=development
   ```

3. **Start development server**
   ```bash
   npm start
   ```
   
   The app will be available at `http://localhost:3000`

### Building for Production

```bash
npm run build
```

The built files will be in the `build/` directory, ready for deployment.

## Development

### Available Scripts

- `npm start` - Start development server
- `npm run build` - Build for production
- `npm test` - Run tests
- `npm run lint` - Run ESLint
- `npm run format` - Format code with Prettier

### Code Style

The project uses:
- **ESLint** - Code linting with React and accessibility rules
- **Prettier** - Code formatting
- **Husky** - Git hooks for pre-commit checks

### Component Guidelines

1. **Use functional components** with hooks
2. **Follow NHS design patterns** for consistency
3. **Implement proper error handling** with error boundaries
4. **Ensure accessibility** with proper ARIA labels and keyboard navigation
5. **Use TypeScript** for type safety (if migrating)

## API Integration

The frontend integrates with the serverless backend through:

- **Authentication API** - Login, register, token management
- **Appointments API** - CRUD operations for appointments
- **Patients API** - Patient record management
- **Practices API** - Practice information and settings

### Error Handling

- **Network errors** - Automatic retry with exponential backoff
- **Authentication errors** - Automatic token refresh and redirect to login
- **Validation errors** - Real-time form validation with user feedback
- **Server errors** - User-friendly error messages with support contact

## Security

### Authentication
- **JWT tokens** stored in localStorage with automatic expiry
- **Role-based access control** for patient vs staff features
- **Protected routes** with automatic redirects
- **Token refresh** handling for seamless user experience

### Data Protection
- **Input sanitization** to prevent XSS attacks
- **HTTPS enforcement** in production
- **Sensitive data handling** following NHS guidelines
- **Session management** with automatic logout

## Accessibility

The application follows WCAG 2.1 AA guidelines:

- **Keyboard navigation** - Full keyboard accessibility
- **Screen reader support** - Proper ARIA labels and roles
- **Colour contrast** - NHS-compliant colour ratios
- **Focus management** - Clear focus indicators
- **Alternative text** - Images and icons have descriptive alt text

## Performance

### Optimisation Techniques
- **Code splitting** - Lazy loading of routes and components
- **Image optimisation** - Responsive images with proper formats
- **Caching** - React Query for server state caching
- **Bundle analysis** - Regular bundle size monitoring
- **Performance monitoring** - Core Web Vitals tracking

### Loading States
- **Skeleton screens** for better perceived performance
- **Progressive loading** of content
- **Offline support** with service workers
- **Error recovery** with retry mechanisms

## Deployment

### Environment Configuration

Create environment-specific `.env` files:

```bash
# .env.production
REACT_APP_API_URL=https://api.nhs-appointments.uk
REACT_APP_ENV=production
REACT_APP_SENTRY_DSN=your-sentry-dsn
```

### Deployment Options

1. **Static Hosting** (Netlify, Vercel, S3)
   ```bash
   npm run build
   # Deploy build/ directory
   ```

2. **Docker Container**
   ```dockerfile
   FROM node:16-alpine
   COPY . /app
   WORKDIR /app
   RUN npm ci --only=production
   RUN npm run build
   EXPOSE 3000
   CMD ["npm", "start"]
   ```

3. **CI/CD Pipeline**
   - Automated testing on pull requests
   - Deployment on merge to main branch
   - Environment-specific deployments

## Testing

### Test Strategy
- **Unit tests** - Component logic and utilities
- **Integration tests** - API integration and user flows
- **E2E tests** - Critical user journeys
- **Accessibility tests** - Automated a11y testing

### Running Tests
```bash
# Unit tests
npm test

# E2E tests (if configured)
npm run test:e2e

# Coverage report
npm run test:coverage
```

## Browser Support

- **Modern browsers** - Chrome 90+, Firefox 88+, Safari 14+, Edge 90+
- **Mobile browsers** - iOS Safari 14+, Chrome Mobile 90+
- **Progressive enhancement** - Basic functionality on older browsers

## Deployment

### Production Build

```bash
npm run build
```

This creates an optimised production build in the `build/` directory.

### Deployment Options

**Netlify (Recommended):**
```bash
# Install Netlify CLI
npm install -g netlify-cli

# Deploy
netlify deploy --prod --dir=build
```

**Vercel:**
```bash
# Install Vercel CLI
npm install -g vercel

# Deploy
vercel --prod
```

**AWS S3 + CloudFront:**
```bash
# Build the app
npm run build

# Sync to S3 bucket
aws s3 sync build/ s3://your-bucket-name --delete

# Invalidate CloudFront cache
aws cloudfront create-invalidation --distribution-id YOUR_DIST_ID --paths "/*"
```

### Environment Variables for Production

Create a `.env.production` file:
```bash
REACT_APP_ENV=production
REACT_APP_API_URL=https://your-api-gateway-url.amazonaws.com/prod
REACT_APP_ENABLE_MOCK_DATA=false
REACT_APP_ENABLE_DEBUG=false
REACT_APP_LOG_LEVEL=error
```

### Post-Deployment Checklist

- ✅ Verify API endpoint is accessible
- ✅ Test authentication flow
- ✅ Check all routes work correctly
- ✅ Verify HTTPS is enabled
- ✅ Test on mobile devices
- ✅ Run accessibility audit
- ✅ Check performance metrics

## Contributing

1. **Fork the repository**
2. **Create a feature branch** (`git checkout -b feature/amazing-feature`)
3. **Follow coding standards** and write tests
4. **Commit changes** (`git commit -m 'Add amazing feature'`)
5. **Push to branch** (`git push origin feature/amazing-feature`)
6. **Open a Pull Request**

### Pull Request Guidelines
- Include description of changes
- Add tests for new features
- Ensure all tests pass
- Follow commit message conventions
- Update documentation if needed

## Support

For support and questions:
- **Technical issues** - Create GitHub issue
- **Security concerns** - Email security@nhs-appointments.uk
- **General questions** - Contact development team

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Acknowledgments

- **NHS Digital** - Design system and guidelines
- **React Team** - Amazing framework and ecosystem
- **Open source community** - Libraries and tools used in this project
