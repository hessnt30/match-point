import React, { useEffect, useState } from "react";
import httpClient from "../httpClient";
import NavBar from "./NavBar";

function Dashboard() {
  const [user, setUser] = useState({
    id: "",
    email: "",
  });

  const logoutUser = async () => {
    const resp = await httpClient.post("//localhost:5000/logout");
    window.location.href = "/";
  };

  useEffect(() => {
    const fetchData = async () => {
      try {
        const resp = await httpClient.get("//localhost:5000/@me");

        // Update user state correctly
        setUser({
          id: resp.data.id,
          email: resp.data.email,
        });
      } catch (error) {
        console.error("Error fetching user data:", error);
      }
    };

    fetchData();
  }, []);
  return (
    <>
      <NavBar loggedIn={true}></NavBar>
      <div>
        <h1>{user.email}'s dashboard</h1>
      </div>
    </>
  );
}

export default Dashboard;
