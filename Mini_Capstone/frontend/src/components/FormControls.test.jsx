import { fireEvent, render, screen } from "@testing-library/react";

import { FormInput, FormSelect } from "./FormControls";

describe("FormControls", () => {
  test("renders input and forwards changes", () => {
    const handleChange = vi.fn();

    render(<FormInput label="Email" value="" onChange={handleChange} />);
    fireEvent.change(screen.getByRole("textbox"), { target: { value: "alice@example.com" } });

    expect(handleChange).toHaveBeenCalledWith("alice@example.com");
  });

  test("renders select options and forwards changes", () => {
    const handleChange = vi.fn();

    render(
      <FormSelect
        label="Role"
        value="customer"
        options={[
          { value: "customer", label: "Customer" },
          { value: "agent", label: "Agent" }
        ]}
        onChange={handleChange}
      />
    );

    fireEvent.change(screen.getByRole("combobox"), { target: { value: "agent" } });

    expect(handleChange).toHaveBeenCalledWith("agent");
  });
});
