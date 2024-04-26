import React, { useState, useEffect } from "react";
import NavBar from "./NavBar";
import httpClient from "../httpClient";
import Dashboard from "./Dashboard";

function LandingPage() {
  const [isLoggedIn, setIsLoggedIn] = useState(false);

  const [user, setUser] = useState({
    id: "",
    email: "",
  });

  useEffect(() => {
    const fetchData = async () => {
      try {
        const resp = await httpClient.get("//localhost:5000/@me");

        // Update user state correctly
        setUser({
          id: resp.data.id,
          email: resp.data.email,
        });
        setIsLoggedIn(true);
      } catch (error) {
        console.error("Error fetching user data:", error);
      }
    };

    fetchData();
  }, []);

  return (
    <div>
      <h1> Welcome </h1>
      {user.id !== "" && user.email !== "" ? (
        <>{(window.location.href = "/dashboard")}</>
      ) : (
        <div>
          <NavBar loggedIn={isLoggedIn} />
          <p>You are not logged in</p>
          <div className="button-span">
            <a href="/login">
              <button>Login</button>
            </a>
            <a href="/register">
              <button>Register</button>
            </a>
          </div>
        </div>
      )}

      <br />
    </div>
  );
}

export default LandingPage;
