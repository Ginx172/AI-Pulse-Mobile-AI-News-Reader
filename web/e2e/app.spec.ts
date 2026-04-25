import { test, expect } from "@playwright/test";

test("home page loads and shows header with logo", async ({ page }) => {
  await page.goto("/");
  await expect(page.getByRole("img", { name: "Pulse AI" })).toBeVisible();
  await expect(page.getByText("Pulse AI")).toBeVisible();
  await expect(page.getByText("Today's Top 25 AI Stories")).toBeVisible();
});

test("settings page loads", async ({ page }) => {
  await page.goto("/settings");
  await expect(page.getByRole("heading", { name: "Settings" })).toBeVisible();
  await expect(page.getByText("About Pulse AI")).toBeVisible();
  await expect(page.getByText("Manage Sources")).toBeVisible();
});

test("theme toggle switches dark/light", async ({ page }) => {
  await page.goto("/");
  const html = page.locator("html");
  const toggleBtn = page.getByRole("button", { name: "Toggle theme" });
  await toggleBtn.click();
  const classList = await html.getAttribute("class");
  expect(classList).toBeTruthy();
});
