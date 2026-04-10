import { render, screen } from "@testing-library/react";

import App from "./App";

function jsonResponse(payload) {
  return {
    ok: true,
    text: async () => JSON.stringify(payload)
  };
}

describe("App", () => {
  beforeEach(() => {
    localStorage.clear();
    vi.restoreAllMocks();
  });

  afterEach(() => {
    vi.unstubAllGlobals();
  });

  test("renders login screen by default", () => {
    render(<App />);

    expect(screen.getByText("Access")).toBeInTheDocument();
    expect(screen.getAllByText("Login")).toHaveLength(2);
    expect(screen.getByRole("button", { name: "Register" })).toBeInTheDocument();
  });

  test("restores a customer session and renders customer dashboard", async () => {
    localStorage.setItem("mini_capstone_token", "token-123");
    localStorage.setItem(
      "mini_capstone_user",
      JSON.stringify({
        id: "u1",
        name: "Customer One",
        email: "customer@example.com",
        role: "customer"
      })
    );

    vi.stubGlobal(
      "fetch",
      vi
        .fn()
        .mockResolvedValueOnce(
          jsonResponse({
            id: "u1",
            name: "Customer One",
            email: "customer@example.com",
            role: "customer",
            is_active: true,
            created_at: "2024-01-01T12:00:00Z"
          })
        )
        .mockResolvedValueOnce(
          jsonResponse({
            shipments: [
              {
                id: "s1",
                tracking_number: "TRK1001",
                customer_id: "u1",
                source_address: "Chennai",
                destination_address: "Bangalore",
                status: "created",
                assigned_agent: null,
                current_location: null,
                created_at: "2024-01-01T12:00:00Z",
                updated_at: "2024-01-01T12:00:00Z"
              }
            ]
          })
        )
    );

    render(<App />);

    expect(await screen.findByText("Create Shipment")).toBeInTheDocument();
    expect(await screen.findByText("My Shipments")).toBeInTheDocument();
    expect(await screen.findByText("TRK1001")).toBeInTheDocument();
  });
});
