function ShipmentTable({ shipments }) {
  if (!shipments.length) {
    return <p className="small-text">No shipments yet.</p>;
  }

  return (
    <div className="table-wrap">
      <table>
        <thead>
          <tr>
            <th>ID</th>
            <th>Tracking</th>
            <th>Status</th>
            <th>Current location</th>
            <th>Agent</th>
          </tr>
        </thead>
        <tbody>
          {shipments.map((shipment) => (
            <tr key={shipment.id}>
              <td>{shipment.id}</td>
              <td>{shipment.tracking_number}</td>
              <td>{shipment.status}</td>
              <td>{shipment.current_location || "-"}</td>
              <td>{shipment.assigned_agent || "-"}</td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}

export default ShipmentTable;
