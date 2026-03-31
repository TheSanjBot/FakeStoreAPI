import { useEffect, useState } from "react";
import { apiRequest } from "./api";
import { FormInput, FormSelect } from "./components/FormControls";
import PageHeader from "./components/PageHeader";
import ShipmentTable from "./components/ShipmentTable";
import UserTable from "./components/UserTable";

const loginDefaults = {
  email: "admin@logisticsapp.com",
  password: "Admin@123"
};

const registerDefaults = {
  name: "",
  email: "",
  password: "",
  role: "customer"
};

const shipmentDefaults = {
  source_address: "",
  destination_address: ""
};

const assignDefaults = {
  shipmentId: "",
  agentId: ""
};

const statusDefaults = {
  shipmentId: "",
  status: "in_transit",
  location: "",
  note: ""
};

function App() {
  const [authMode, setAuthMode] = useState("login");
  const [loginForm, setLoginForm] = useState(loginDefaults);
  const [registerForm, setRegisterForm] = useState(registerDefaults);
  const [shipmentForm, setShipmentForm] = useState(shipmentDefaults);
  const [assignForm, setAssignForm] = useState(assignDefaults);
  const [statusForm, setStatusForm] = useState(statusDefaults);
  const [trackingNumber, setTrackingNumber] = useState("");
  const [trackingResult, setTrackingResult] = useState(null);
  const [token, setToken] = useState(localStorage.getItem("mini_capstone_token") || "");
  const [currentUser, setCurrentUser] = useState(readStoredUser());
  const [shipments, setShipments] = useState([]);
  const [users, setUsers] = useState([]);
  const [agents, setAgents] = useState([]);
  const [reports, setReports] = useState(null);
  const [message, setMessage] = useState("");
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    if (!token) {
      return;
    }

    loadProfile();
  }, []);

  async function loadProfile() {
    try {
      const profile = await apiRequest("/auth/me", { token });
      setCurrentUser(profile);
      localStorage.setItem("mini_capstone_user", JSON.stringify(profile));
      await loadDashboardData(profile.role, token);
    } catch (error) {
      clearSession();
      setMessage(error.message);
    }
  }

  async function loadDashboardData(role, authToken = token) {
    if (!authToken || !role) {
      return;
    }

    try {
      if (role === "customer") {
        const shipmentResponse = await apiRequest("/shipments", { token: authToken });
        setShipments(shipmentResponse.shipments || []);
        setUsers([]);
        setAgents([]);
        setReports(null);
        return;
      }

      if (role === "agent") {
        const shipmentResponse = await apiRequest("/agent/shipments", { token: authToken });
        setShipments(shipmentResponse.shipments || []);
        setUsers([]);
        setAgents([]);
        setReports(null);
        return;
      }

      const [shipmentResponse, userResponse, agentResponse, reportResponse] = await Promise.all([
        apiRequest("/shipments", { token: authToken }),
        apiRequest("/admin/users", { token: authToken }),
        apiRequest("/users/agents", { token: authToken }),
        apiRequest("/admin/reports", { token: authToken })
      ]);

      setShipments(shipmentResponse.shipments || []);
      setUsers(userResponse.users || []);
      setAgents(agentResponse.users || []);
      setReports(reportResponse);
    } catch (error) {
      setMessage(error.message);
    }
  }

  async function handleLogin(event) {
    event.preventDefault();
    setLoading(true);
    setMessage("");

    try {
      const response = await apiRequest("/auth/login", {
        method: "POST",
        body: loginForm
      });

      setToken(response.access_token);
      setCurrentUser(response.user);
      localStorage.setItem("mini_capstone_token", response.access_token);
      localStorage.setItem("mini_capstone_user", JSON.stringify(response.user));
      setTrackingResult(null);
      setMessage("Login successful.");
      await loadDashboardData(response.user.role, response.access_token);
    } catch (error) {
      setMessage(error.message);
    } finally {
      setLoading(false);
    }
  }

  async function handleRegister(event) {
    event.preventDefault();
    setLoading(true);
    setMessage("");

    try {
      await apiRequest("/auth/register", {
        method: "POST",
        body: registerForm
      });

      setRegisterForm(registerDefaults);
      setAuthMode("login");
      setMessage("Registration successful. You can log in now.");
    } catch (error) {
      setMessage(error.message);
    } finally {
      setLoading(false);
    }
  }

  async function handleCreateShipment(event) {
    event.preventDefault();
    setLoading(true);
    setMessage("");

    try {
      await apiRequest("/shipments", {
        method: "POST",
        token,
        body: shipmentForm
      });

      setShipmentForm(shipmentDefaults);
      setMessage("Shipment created.");
      await loadDashboardData("customer");
    } catch (error) {
      setMessage(error.message);
    } finally {
      setLoading(false);
    }
  }

  async function handleAssignAgent(event) {
    event.preventDefault();
    setLoading(true);
    setMessage("");

    try {
      await apiRequest(`/shipments/${assignForm.shipmentId}/assign-agent`, {
        method: "PUT",
        token,
        body: { agent_id: assignForm.agentId }
      });

      setAssignForm(assignDefaults);
      setMessage("Agent assigned.");
      await loadDashboardData("admin");
    } catch (error) {
      setMessage(error.message);
    } finally {
      setLoading(false);
    }
  }

  async function handleUpdateStatus(event) {
    event.preventDefault();
    setLoading(true);
    setMessage("");

    try {
      await apiRequest(`/shipments/${statusForm.shipmentId}/status`, {
        method: "PUT",
        token,
        body: {
          status: statusForm.status,
          location: statusForm.location,
          note: statusForm.note
        }
      });

      setStatusForm(statusDefaults);
      setMessage("Shipment status updated.");
      await loadDashboardData("agent");
    } catch (error) {
      setMessage(error.message);
    } finally {
      setLoading(false);
    }
  }

  async function handleTrackShipment(event) {
    event.preventDefault();
    setLoading(true);
    setMessage("");

    try {
      const response = await apiRequest(`/shipments/${trackingNumber}`, {
        token
      });

      setTrackingResult(response);
    } catch (error) {
      setTrackingResult(null);
      setMessage(error.message);
    } finally {
      setLoading(false);
    }
  }

  function handleLogout() {
    clearSession();
    setMessage("Logged out.");
  }

  function clearSession() {
    setToken("");
    setCurrentUser(null);
    setShipments([]);
    setUsers([]);
    setAgents([]);
    setReports(null);
    setTrackingResult(null);
    localStorage.removeItem("mini_capstone_token");
    localStorage.removeItem("mini_capstone_user");
  }

  return (
    <div className="app-shell">
      <PageHeader />

      {message ? <div className="notice">{message}</div> : null}

      <div className="grid">
        <section className="panel">
          <h2>{currentUser ? "Session" : "Access"}</h2>

          {!currentUser ? (
            <>
              <div className="auth-toggle">
                <button
                  className={`pill ${authMode === "login" ? "active" : ""}`}
                  type="button"
                  onClick={() => setAuthMode("login")}
                >
                  Login
                </button>
                <button
                  className={`pill ${authMode === "register" ? "active" : ""}`}
                  type="button"
                  onClick={() => setAuthMode("register")}
                >
                  Register
                </button>
              </div>

              {authMode === "login" ? (
                <form onSubmit={handleLogin}>
                  <FormInput
                    label="Email"
                    value={loginForm.email}
                    onChange={(value) => setLoginForm({ ...loginForm, email: value })}
                  />
                  <FormInput
                    label="Password"
                    type="password"
                    value={loginForm.password}
                    onChange={(value) => setLoginForm({ ...loginForm, password: value })}
                  />
                  <div className="button-row">
                    <button className="button" disabled={loading} type="submit">
                      {loading ? "Please wait..." : "Login"}
                    </button>
                  </div>
                </form>
              ) : (
                <form onSubmit={handleRegister}>
                  <FormInput
                    label="Name"
                    value={registerForm.name}
                    onChange={(value) => setRegisterForm({ ...registerForm, name: value })}
                  />
                  <FormInput
                    label="Email"
                    value={registerForm.email}
                    onChange={(value) => setRegisterForm({ ...registerForm, email: value })}
                  />
                  <FormInput
                    label="Password"
                    type="password"
                    value={registerForm.password}
                    onChange={(value) => setRegisterForm({ ...registerForm, password: value })}
                  />
                  <FormSelect
                    label="Role"
                    value={registerForm.role}
                    options={[
                      { value: "customer", label: "Customer" },
                      { value: "agent", label: "Agent" }
                    ]}
                    onChange={(value) => setRegisterForm({ ...registerForm, role: value })}
                  />
                  <div className="button-row">
                    <button className="button" disabled={loading} type="submit">
                      {loading ? "Please wait..." : "Register"}
                    </button>
                  </div>
                </form>
              )}
            </>
          ) : (
            <>
              <p>
                <strong>Name:</strong> {currentUser.name}
                <br />
                <strong>Email:</strong> {currentUser.email}
                <br />
                <strong>Role:</strong> <span className="status-badge">{currentUser.role}</span>
              </p>
              <div className="button-row">
                <button className="button" type="button" onClick={() => loadDashboardData(currentUser.role)}>
                  Refresh data
                </button>
                <button className="button secondary" type="button" onClick={handleLogout}>
                  Logout
                </button>
              </div>
            </>
          )}
        </section>

        {currentUser ? (
          <section className="panel">
            <h2>Track Shipment</h2>
            <form onSubmit={handleTrackShipment}>
              <FormInput label="Tracking Number" value={trackingNumber} onChange={setTrackingNumber} />
              <div className="button-row">
                <button className="button" disabled={loading || !trackingNumber} type="submit">
                  Track
                </button>
              </div>
            </form>

            {trackingResult ? (
              <div>
                <p>
                  <strong>Shipment ID:</strong> {trackingResult.shipment_id}
                  <br />
                  <strong>Status:</strong> {trackingResult.current_status}
                  <br />
                  <strong>Current location:</strong> {trackingResult.current_location || "Not updated yet"}
                </p>
                <ol className="tracking-list">
                  {trackingResult.updates.map((item) => (
                    <li key={item.id}>
                      <strong>{item.status}</strong> at {item.location}
                      <br />
                      <span className="small-text">
                        {new Date(item.updated_at).toLocaleString()} {item.note ? `- ${item.note}` : ""}
                      </span>
                    </li>
                  ))}
                </ol>
              </div>
            ) : (
              <p className="small-text">Track any shipment you are allowed to view.</p>
            )}
          </section>
        ) : null}
      </div>

      {currentUser?.role === "customer" ? (
        <div className="grid" style={{ marginTop: 18 }}>
          <section className="panel">
            <h2>Create Shipment</h2>
            <form onSubmit={handleCreateShipment}>
              <FormInput
                label="Source address"
                value={shipmentForm.source_address}
                onChange={(value) => setShipmentForm({ ...shipmentForm, source_address: value })}
              />
              <FormInput
                label="Destination address"
                value={shipmentForm.destination_address}
                onChange={(value) => setShipmentForm({ ...shipmentForm, destination_address: value })}
              />
              <div className="button-row">
                <button className="button" disabled={loading} type="submit">
                  Create shipment
                </button>
              </div>
            </form>
          </section>

          <section className="panel">
            <h2>My Shipments</h2>
            <ShipmentTable shipments={shipments} />
          </section>
        </div>
      ) : null}

      {currentUser?.role === "agent" ? (
        <div className="grid" style={{ marginTop: 18 }}>
          <section className="panel">
            <h2>Update Status</h2>
            <form onSubmit={handleUpdateStatus}>
              <FormInput
                label="Shipment ID"
                value={statusForm.shipmentId}
                onChange={(value) => setStatusForm({ ...statusForm, shipmentId: value })}
              />
              <FormSelect
                label="Status"
                value={statusForm.status}
                options={[
                  { value: "in_transit", label: "in_transit" },
                  { value: "out_for_delivery", label: "out_for_delivery" },
                  { value: "delivered", label: "delivered" }
                ]}
                onChange={(value) => setStatusForm({ ...statusForm, status: value })}
              />
              <FormInput
                label="Location"
                value={statusForm.location}
                onChange={(value) => setStatusForm({ ...statusForm, location: value })}
              />
              <div className="form-row">
                <label htmlFor="note">Note</label>
                <textarea
                  id="note"
                  rows="4"
                  value={statusForm.note}
                  onChange={(event) => setStatusForm({ ...statusForm, note: event.target.value })}
                />
              </div>
              <div className="button-row">
                <button className="button" disabled={loading} type="submit">
                  Save update
                </button>
              </div>
            </form>
          </section>

          <section className="panel">
            <h2>Assigned Shipments</h2>
            <ShipmentTable shipments={shipments} />
          </section>
        </div>
      ) : null}

      {currentUser?.role === "admin" ? (
        <>
          <div className="grid" style={{ marginTop: 18 }}>
            <section className="panel">
              <h2>Reports</h2>
              {reports ? (
                <div>
                  <p>
                    <strong>Total users:</strong> {reports.total_users}
                    <br />
                    <strong>Total customers:</strong> {reports.total_customers}
                    <br />
                    <strong>Total agents:</strong> {reports.total_agents}
                    <br />
                    <strong>Total shipments:</strong> {reports.total_shipments}
                    <br />
                    <strong>Total hubs:</strong> {reports.total_hubs}
                  </p>
                  <ul className="tracking-list">
                    {Object.entries(reports.shipments_by_status).map(([status, count]) => (
                      <li key={status}>
                        {status}: {count}
                      </li>
                    ))}
                  </ul>
                </div>
              ) : (
                <p className="small-text">No report data loaded yet.</p>
              )}
            </section>

            <section className="panel">
              <h2>Assign Agent</h2>
              <form onSubmit={handleAssignAgent}>
                <FormInput
                  label="Shipment ID"
                  value={assignForm.shipmentId}
                  onChange={(value) => setAssignForm({ ...assignForm, shipmentId: value })}
                />
                <FormSelect
                  label="Agent"
                  value={assignForm.agentId}
                  options={[
                    { value: "", label: "Select an agent" },
                    ...agents.map((agent) => ({
                      value: agent.id,
                      label: `${agent.name} (${agent.email})`
                    }))
                  ]}
                  onChange={(value) => setAssignForm({ ...assignForm, agentId: value })}
                />
                <div className="button-row">
                  <button className="button" disabled={loading || !assignForm.agentId} type="submit">
                    Assign
                  </button>
                </div>
              </form>
            </section>
          </div>

          <div className="grid" style={{ marginTop: 18 }}>
            <section className="panel">
              <h2>All Users</h2>
              <UserTable users={users} />
            </section>

            <section className="panel">
              <h2>All Shipments</h2>
              <ShipmentTable shipments={shipments} />
            </section>
          </div>
        </>
      ) : null}
    </div>
  );
}

function readStoredUser() {
  const rawValue = localStorage.getItem("mini_capstone_user");
  if (!rawValue) {
    return null;
  }

  try {
    return JSON.parse(rawValue);
  } catch {
    return null;
  }
}

export default App;
