import React, { useState } from "react";
import ReactDOM from "react-dom/client";
import Router from "./Router.jsx";
import "./index.css";
import "bootstrap/dist/css/bootstrap.min.css";

ReactDOM.createRoot(document.getElementById("root")).render(
  <React.StrictMode>
    <Router />
  </React.StrictMode>
);
