import { expect, it } from "vitest";

it("blocks deployment when a test fails", () => {
  expect(true, "Intentional failure for isolated deployment-gate verification").toBe(false);
});
