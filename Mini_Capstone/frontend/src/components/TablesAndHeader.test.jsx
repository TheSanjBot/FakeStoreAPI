import { render, screen } from "@testing-library/react";

import PageHeader from "./PageHeader";
import ShipmentTable from "./ShipmentTable";
import UserTable from "./UserTable";

describe("PageHeader", () => {
  test("renders the project title", () => {
    render(<PageHeader />);

    expect(screen.getByText("Logistics & Shipment Tracking System")).toBeInTheDocument();
  });
});

describe("ShipmentTable", () => {
  test("shows empty state", () => {
    render(<ShipmentTable shipments={[]} />);

    expect(screen.getByText("No shipments yet.")).toBeInTheDocument();
  });

  test("renders shipment rows", () => {
    render(
      <ShipmentTable
        shipments={[
          {
            id: "s1",
            tracking_number: "TRK1001",
            status: "created",
            current_location: null,
            assigned_agent: null
          }
        ]}
      />
    );

    expect(screen.getByText("TRK1001")).toBeInTheDocument();
    expect(screen.getByText("created")).toBeInTheDocument();
  });
});

describe("UserTable", () => {
  test("shows empty state", () => {
    render(<UserTable users={[]} />);

    expect(screen.getByText("No users yet.")).toBeInTheDocument();
  });

  test("renders user rows", () => {
    render(
      <UserTable
        users={[
          {
            id: "u1",
            name: "Admin User",
            email: "admin@example.com",
            role: "admin"
          }
        ]}
      />
    );

    expect(screen.getByText("Admin User")).toBeInTheDocument();
    expect(screen.getByText("admin@example.com")).toBeInTheDocument();
  });
});
