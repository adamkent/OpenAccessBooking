/**
 * Tests for API service
 */

import { login, register, getAppointments, createAppointment } from './api';

// Mock fetch
global.fetch = jest.fn();

describe('Authentication API', () => {
  beforeEach(() => {
    fetch.mockClear();
  });

  describe('login', () => {
    test('successful login returns user data and token', async () => {
      const mockResponse = {
        access_token: 'mock-token',
        user: { email: 'test@example.com', user_id: '123' }
      };

      fetch.mockResolvedValueOnce({
        ok: true,
        json: async () => mockResponse
      });

      const result = await login('test@example.com', 'password');

      expect(fetch).toHaveBeenCalledWith(
        expect.stringContaining('/auth/login'),
        expect.objectContaining({
          method: 'POST',
          body: JSON.stringify({ email: 'test@example.com', password: 'password' })
        })
      );
      expect(result).toEqual(mockResponse);
    });

    test('failed login throws error', async () => {
      fetch.mockResolvedValueOnce({
        ok: false,
        status: 401,
        json: async () => ({ error: 'Invalid credentials' })
      });

      await expect(login('test@example.com', 'wrong')).rejects.toThrow();
    });
  });

  describe('register', () => {
    test('successful registration returns user data', async () => {
      const mockResponse = {
        user_id: '123',
        email: 'newuser@example.com'
      };

      fetch.mockResolvedValueOnce({
        ok: true,
        json: async () => mockResponse
      });

      const userData = {
        email: 'newuser@example.com',
        password: 'TestPass123!',
        first_name: 'Test',
        last_name: 'User',
        nhs_number: '9434765919'
      };

      const result = await register(userData);

      expect(fetch).toHaveBeenCalledWith(
        expect.stringContaining('/auth/register'),
        expect.objectContaining({
          method: 'POST',
          body: JSON.stringify(userData)
        })
      );
      expect(result).toEqual(mockResponse);
    });
  });
});

describe('Appointments API', () => {
  beforeEach(() => {
    fetch.mockClear();
  });

  describe('getAppointments', () => {
    test('fetches appointments successfully', async () => {
      const mockAppointments = {
        appointments: [
          { appointment_id: '1', status: 'scheduled' },
          { appointment_id: '2', status: 'completed' }
        ]
      };

      fetch.mockResolvedValueOnce({
        ok: true,
        json: async () => mockAppointments
      });

      const result = await getAppointments('mock-token');

      expect(fetch).toHaveBeenCalledWith(
        expect.stringContaining('/appointments'),
        expect.objectContaining({
          headers: expect.objectContaining({
            'Authorization': 'Bearer mock-token'
          })
        })
      );
      expect(result).toEqual(mockAppointments);
    });
  });

  describe('createAppointment', () => {
    test('creates appointment successfully', async () => {
      const mockResponse = {
        appointment_id: '123',
        status: 'scheduled'
      };

      fetch.mockResolvedValueOnce({
        ok: true,
        json: async () => mockResponse
      });

      const appointmentData = {
        practice_id: 'practice-1',
        appointment_type: 'gp_consultation',
        appointment_date: '2024-12-01',
        appointment_time: '10:00',
        reason: 'Checkup'
      };

      const result = await createAppointment(appointmentData, 'mock-token');

      expect(fetch).toHaveBeenCalledWith(
        expect.stringContaining('/appointments'),
        expect.objectContaining({
          method: 'POST',
          body: JSON.stringify(appointmentData),
          headers: expect.objectContaining({
            'Authorization': 'Bearer mock-token'
          })
        })
      );
      expect(result).toEqual(mockResponse);
    });
  });
});
