import { useState } from "react";
import API from "./api/api";

function App() {
  const [page, setPage] = useState("login");

  const [isLogin, setIsLogin] = useState(true);
  const [role, setRole] = useState("user");

  const [name, setName] = useState("");
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");

  const [userRole, setUserRole] = useState(null);

  const [doctors, setDoctors] = useState([]);
  const [appointments, setAppointments] = useState([]);
  const [patients, setPatients] = useState([]);

  const [selectedDoctor, setSelectedDoctor] = useState(null);
  const [date, setDate] = useState("");

  const [editingId, setEditingId] = useState(null);
  const [newDate, setNewDate] = useState("");

  const parseJwt = (token) => {
    try {
      return JSON.parse(atob(token.split(".")[1]));
    } catch {
      return null;
    }
  };

  // ================= AUTH =================
  const handleLogin = async () => {
    try {
      const formData = new URLSearchParams();
      formData.append("username", email);
      formData.append("password", password);

      const res = await API.post("/auth/login", formData, {
        headers: {
          "Content-Type": "application/x-www-form-urlencoded",
        },
      });

      localStorage.setItem("token", res.data.access_token);
      const decoded = parseJwt(res.data.access_token);
      setUserRole(decoded.role);

      setPage("home");
    } catch (err) {
      alert(err.response?.data?.detail || "Login failed");
    }
  };

  const handleRegister = async () => {
    try {
      await API.post("/auth/register", {
        name,
        email,
        password,
        role,
      });

      alert("Registered successfully");
      setIsLogin(true);
    } catch (err) {
      alert(err.response?.data?.detail || "Error");
    }
  };

  const handleLogout = () => {
    localStorage.removeItem("token");
    setUserRole(null);
    setPage("login");
  };

  // ================= DOCTORS =================
  const fetchDoctors = async () => {
    try {
      const res = await API.get("/doctors/");
      setDoctors(res.data);
      setPage("doctors");
    } catch {
      alert("Error loading doctors");
    }
  };

  const addDoctor = async () => {
    try {
      await API.post("/doctors/", { name });
      setName("");
      fetchDoctors();
    } catch {
      alert("Add doctor failed");
    }
  };

  const deleteDoctor = async (id) => {
    try {
      await API.delete(`/doctors/${id}`);
      fetchDoctors();
    } catch {
      alert("Delete doctor failed");
    }
  };

  // ================= PATIENTS =================
  const fetchPatients = async () => {
    try {
      const url =
        userRole === "admin" ? "/patients/" : "/profile";

      const res = await API.get(url);

      if (userRole === "admin") {
        setPatients(res.data);
      } else {
        setPatients([res.data]);
      }

      setPage("patients");
    } catch {
      alert("Error loading patients");
    }
  };

  const addPatient = async () => {
    try {
      await API.post("/patients/", { name, email });
      fetchPatients();
    } catch {
      alert("Add failed");
    }
  };

  const deletePatient = async (id) => {
    try {
      await API.delete(`/patients/${id}`);
      fetchPatients();
    } catch {
      alert("Delete failed");
    }
  };

  // ================= APPOINTMENTS =================
  const fetchAppointments = async () => {
    try {
      const url =
        userRole === "admin"
          ? "/appointments/"
          : "/appointments/my";

      const res = await API.get(url);
      setAppointments(res.data);
      setPage("appointments");
    } catch {
      alert("Error loading appointments");
    }
  };

  const bookAppointment = async () => {
    try {
      await API.post("/appointments/", {
        doctor_id: selectedDoctor,
        appointment_date: date,
      });

      alert("Booked");
      setPage("home");
    } catch (err) {
      alert(err.response?.data?.detail);
    }
  };

  const deleteAppointment = async (id) => {
    try {
      const url =
        userRole === "admin"
          ? `/appointments/admin/${id}`
          : `/appointments/${id}`;

      await API.delete(url);
      fetchAppointments();
    } catch {
      alert("Delete failed");
    }
  };

  const updateAppointment = async () => {
    try {
      await API.put(`/appointments/${editingId}`, {
        doctor_id: selectedDoctor,
        appointment_date: newDate,
      });

      setEditingId(null);
      fetchAppointments();
    } catch {
      alert("Update failed");
    }
  };

  // ================= UI =================
  return (
    <div style={{ textAlign: "center", marginTop: "50px" }}>
      
      {/* LOGIN */}
      {page === "login" && (
        <>
          <h1>{isLogin ? "Login" : "Register"}</h1>

          {!isLogin && (
            <>
              <input placeholder="Name" onChange={(e) => setName(e.target.value)} />
              <br /><br />

              <select onChange={(e) => setRole(e.target.value)}>
                <option value="user">User</option>
                <option value="admin">Admin</option>
              </select>
              <br /><br />
            </>
          )}

          <input placeholder="Email" onChange={(e) => setEmail(e.target.value)} />
          <br /><br />

          <input type="password" placeholder="Password" onChange={(e) => setPassword(e.target.value)} />
          <br /><br />

          <button onClick={isLogin ? handleLogin : handleRegister}>
            {isLogin ? "Login" : "Register"}
          </button>

          <br /><br />
          <button onClick={() => setIsLogin(!isLogin)}>Switch</button>
        </>
      )}

      {/* HOME */}
      {page === "home" && (
        <>
          <h1>Home</h1>

          <button onClick={fetchDoctors}>Doctors</button>
          <br /><br />

          <button onClick={fetchPatients}>Patients</button>
          <br /><br />

          <button onClick={fetchAppointments}>Appointments</button>
          <br /><br />

          <button onClick={handleLogout}>Logout</button>
        </>
      )}

      {/* DOCTORS */}
      {page === "doctors" && (
        <>
          <h2>Doctors</h2>

          {userRole === "admin" && (
            <>
              <input
                placeholder="Doctor name"
                onChange={(e) => setName(e.target.value)}
              />
              <br /><br />
              <button onClick={addDoctor}>Add Doctor</button>
              <hr />
            </>
          )}

          {doctors.map((doc) => (
            <div key={doc.id}>
              <p>{doc.name}</p>

              <button
                onClick={() => {
                  setSelectedDoctor(doc.id);
                  setPage("book");
                }}
              >
                Book
              </button>

              {userRole === "admin" && (
                <button onClick={() => deleteDoctor(doc.id)}>
                  Delete
                </button>
              )}

              <hr />
            </div>
          ))}

          <button onClick={() => setPage("home")}>Back</button>
        </>
      )}

      {/* BOOK */}
      {page === "book" && (
        <>
          <h2>Book</h2>

          <select onChange={(e) => setSelectedDoctor(e.target.value)}>
            <option>Select Doctor</option>
            {doctors.map((doc) => (
              <option key={doc.id} value={doc.id}>
                {doc.name}
              </option>
            ))}
          </select>

          <br /><br />

          <input
            placeholder="YYYY-MM-DD HH:MM"
            onChange={(e) => setDate(e.target.value)}
          />

          <br /><br />

          <button onClick={bookAppointment}>Confirm</button>

          <br /><br />
          <button onClick={() => setPage("doctors")}>Back</button>
        </>
      )}

      {/* APPOINTMENTS */}
      {page === "appointments" && (
        <>
          <h2>Appointments</h2>

          {appointments.map((a) => (
            <div key={a.id}>
              <p>Doctor: {a.doctor_id}</p>
              <p>Date: {a.appointment_date}</p>

              <button onClick={() => deleteAppointment(a.id)}>
                Delete
              </button>

              <button
                onClick={() => {
                  setEditingId(a.id);
                  setSelectedDoctor(a.doctor_id);
                }}
              >
                Edit
              </button>

              <hr />
            </div>
          ))}

          {editingId && (
            <>
              <input
                placeholder="New Date"
                onChange={(e) => setNewDate(e.target.value)}
              />
              <br /><br />
              <button onClick={updateAppointment}>Save</button>
            </>
          )}

          <br />
          <button onClick={() => setPage("home")}>Back</button>
        </>
      )}
    </div>
  );
}

export default App;