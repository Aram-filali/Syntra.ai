import { test as base, expect } from '@playwright/test';

/**
 * Fixture for creating a logged-in user
 */
export const test = base.extend({
  authenticatedPage: async ({ page }, use) => {
    // Navigate to landing page
    await page.goto('/');
    
    // Click on login link
    await page.click('a:has-text("Connexion")');
    
    // Wait for login form
    await page.waitForSelector('input[placeholder="Email"]', { timeout: 5000 }).catch(() => null);
    
    // Fill in credentials (test user)
    const email = 'test@example.com';
    const password = 'testpass123';
    
    await page.fill('input[placeholder="Email"]', email);
    await page.fill('input[type="password"]', password);
    
    // Submit login form
    await page.click('button:has-text("Connexion")');
    
    // Wait for dashboard to load
    await page.waitForURL('**/dashboard', { timeout: 10000 }).catch(() => null);
    
    // Use the authenticated page
    await use(page);
  },
});

export { expect };
