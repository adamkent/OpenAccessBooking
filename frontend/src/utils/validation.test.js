/**
 * Tests for validation utilities
 */

import {
  validateEmail,
  validateNHSNumber,
  validatePhoneNumber,
  validatePostcode,
  validatePassword
} from './validation';

describe('Email Validation', () => {
  test('validates correct email addresses', () => {
    expect(validateEmail('test@example.com')).toBe(true);
    expect(validateEmail('user.name@domain.co.uk')).toBe(true);
    expect(validateEmail('test+tag@gmail.com')).toBe(true);
  });

  test('rejects invalid email addresses', () => {
    expect(validateEmail('invalid')).toBe(false);
    expect(validateEmail('test@')).toBe(false);
    expect(validateEmail('@example.com')).toBe(false);
    expect(validateEmail('')).toBe(false);
  });
});

describe('NHS Number Validation', () => {
  test('validates correct NHS numbers', () => {
    expect(validateNHSNumber('9434765919')).toBe(true);
    expect(validateNHSNumber('943 476 5919')).toBe(true);
    expect(validateNHSNumber('401 023 2137')).toBe(true);
  });

  test('rejects invalid NHS numbers', () => {
    expect(validateNHSNumber('1234567890')).toBe(false);
    expect(validateNHSNumber('123456789')).toBe(false);
    expect(validateNHSNumber('')).toBe(false);
    expect(validateNHSNumber('abcdefghij')).toBe(false);
  });
});

describe('Phone Number Validation', () => {
  test('validates correct UK phone numbers', () => {
    expect(validatePhoneNumber('07123456789')).toBe(true);
    expect(validatePhoneNumber('07123 456789')).toBe(true);
    expect(validatePhoneNumber('+447123456789')).toBe(true);
    expect(validatePhoneNumber('020 7123 4567')).toBe(true);
  });

  test('rejects invalid phone numbers', () => {
    expect(validatePhoneNumber('123')).toBe(false);
    expect(validatePhoneNumber('')).toBe(false);
    expect(validatePhoneNumber('abcdefghijk')).toBe(false);
  });
});

describe('Postcode Validation', () => {
  test('validates correct UK postcodes', () => {
    expect(validatePostcode('SW1A 1AA')).toBe(true);
    expect(validatePostcode('M1 1AE')).toBe(true);
    expect(validatePostcode('B33 8TH')).toBe(true);
  });

  test('rejects invalid postcodes', () => {
    expect(validatePostcode('INVALID')).toBe(false);
    expect(validatePostcode('')).toBe(false);
    expect(validatePostcode('12345')).toBe(false);
  });
});

describe('Password Validation', () => {
  test('validates strong passwords', () => {
    expect(validatePassword('TestPass123!')).toBe(true);
    expect(validatePassword('Secure@Pass1')).toBe(true);
  });

  test('rejects weak passwords', () => {
    expect(validatePassword('short')).toBe(false);
    expect(validatePassword('nouppercase1!')).toBe(false);
    expect(validatePassword('NOLOWERCASE1!')).toBe(false);
    expect(validatePassword('NoNumbers!')).toBe(false);
    expect(validatePassword('')).toBe(false);
  });
});
