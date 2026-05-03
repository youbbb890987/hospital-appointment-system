import { useState } from "react";

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

  const handleLogin = async () => {
    try {
      const formData = new URLSearchParams();
      formData.append("username", email);
      formData.append("password", password);

      const res = await fetch("http://127.0.0.1:8000/auth/login", {
        method: "POST",
        headers: {
          "Content-Type": "application/x-www-form-urlencoded",
        },
        body: formData,
      });

      const data = await res.json();

      if (res.ok) {
        localStorage.setItem("token", data.access_token);

        const decoded = parseJwt(data.access_token);
        setUserRole(decoded.role);

        setPage("home");
      } else {
        alert(data.detail || "Login failed");
      }
    } catch {
      alert("Server error");
    }
  };

  const handleRegister = async () => {
    try {
      const res = await fetch("http://127.0.0.1:8000/auth/register", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          name,
          email,
          password,
          role,
        }),
      });

      const data = await res.json();

      if (res.ok) {
        alert("Registered successfully");
        setIsLogin(true);
      } else {
        alert(data.detail);
      }
    } catch {
      alert("Error");
    }
  };

  const handleLogout = () => {
    localStorage.removeItem("token");
    setUserRole(null);
    setPage("login");
  };

  const fetchDoctors = async () => {
    const res = await fetch("http://127.0.0.1:8000/doctors/");
    const data = await res.json();
    setDoctors(data);
    setPage("doctors");
  };

  const fetchAppointments = async () => {
    const token = localStorage.getItem("token");

    const url =
      userRole === "admin"
        ? "http://127.0.0.1:8000/appointments/"
        : "http://127.0.0.1:8000/appointments/my";

    const res = await fetch(url, {
      headers: {
        Authorization: `Bearer ${token}`,
      },
    });

    const data = await res.json();
    setAppointments(data);
    setPage("appointments");
  };

  const bookAppointment = async () => {
    const token = localStorage.getItem("token");

    const res = await fetch("http://127.0.0.1:8000/appointments/", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        Authorization: `Bearer ${token}`,
      },
      body: JSON.stringify({
        doctor_id: selectedDoctor,
        appointment_date: date,
      }),
    });

    const data = await res.json();

    if (res.ok) {
      alert("Booked");
      setPage("home");
    } else {
      alert(data.detail);
    }
  };

  const deleteAppointment = async (id) => {
    const token = localStorage.getItem("token");

    const url =
      userRole === "admin"
        ? `http://127.0.0.1:8000/appointments/admin/${id}`
        : `http://127.0.0.1:8000/appointments/${id}`;

    const res = await fetch(url, {
      method: "DELETE",
      headers: {
        Authorization: `Bearer ${token}`,
      },
    });

    if (res.ok) {
      fetchAppointments();
    } else {
      alert("Delete failed");
    }
  };

  const updateAppointment = async () => {
    const token = localStorage.getItem("token");

    const res = await fetch(
      `http://127.0.0.1:8000/appointments/${editingId}`,
      {
        method: "PUT",
        headers: {
          "Content-Type": "application/json",
          Authorization: `Bearer ${token}`,
        },
        body: JSON.stringify({
          doctor_id: selectedDoctor,
          appointment_date: newDate,
        }),
      }
    );

    if (res.ok) {
      setEditingId(null);
      fetchAppointments();
    } else {
      alert("Update failed");
    }
  };

  return (
    <div style={{ textAlign: "center", marginTop: "50px" }}>

      {page === "login" && (
        <>
          <h1>{isLogin ? "Login" : "Register"}</h1>

          {!isLogin && (
            <>
              <input
                placeholder="Name"
                onChange={(e) => setName(e.target.value)}
              />
              <br /><br />

              <select onChange={(e) => setRole(e.target.value)}>
                <option value="user">User</option>
                <option value="admin">Admin</option>
              </select>

              <br /><br />
            </>
          )}

          <input
            placeholder="Email"
            onChange={(e) => setEmail(e.target.value)}
          />
          <br /><br />

          <input
            type="password"
            placeholder="Password"
            onChange={(e) => setPassword(e.target.value)}
          />
          <br /><br />

          <button onClick={isLogin ? handleLogin : handleRegister}>
            {isLogin ? "Login" : "Register"}
          </button>

          <br /><br />

          <button onClick={() => setIsLogin(!isLogin)}>
            Switch
          </button>
        </>
      )}

      {page === "home" && (
        <>
          <h1>Home</h1>

          <button onClick={fetchDoctors}>Doctors</button>
          <br /><br />

          <button onClick={fetchAppointments}>Appointments</button>
          <br /><br />

          <button onClick={handleLogout}>Logout</button>
        </>
      )}

      {page === "doctors" && (
        <>
          <h2>Doctors</h2>

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
              <hr />
            </div>
          ))}

          <button onClick={() => setPage("home")}>Back</button>
        </>
      )}

      {page === "book" && (
        <>
          <h2>Book</h2>

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