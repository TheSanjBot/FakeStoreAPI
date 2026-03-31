export function FormInput({ label, type = "text", value, onChange }) {
  return (
    <div className="form-row">
      <label>{label}</label>
      <input type={type} value={value} onChange={(event) => onChange(event.target.value)} />
    </div>
  );
}

export function FormSelect({ label, value, options, onChange }) {
  return (
    <div className="form-row">
      <label>{label}</label>
      <select value={value} onChange={(event) => onChange(event.target.value)}>
        {options.map((option) => (
          <option key={option.value || option.label} value={option.value}>
            {option.label}
          </option>
        ))}
      </select>
    </div>
  );
}
