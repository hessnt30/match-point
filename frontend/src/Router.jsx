import { BrowserRouter, Routes, Route, RouterProvider } from "react-router-dom";
import LandingPage from "./pages/LandingPage";
import NotFound from "./pages/NotFound";
import LoginPage from "./pages/LoginPage";
import RegisterPage from "./pages/RegisterPage";
import Dashboard from "./pages/Dashboard";

function Router() {
  return (
    <BrowserRouter>
      <Routes>
        <Route path="/" exact Component={LandingPage}></Route>
        <Route path="/login" exact Component={LoginPage}></Route>
        <Route path="/register" exact Component={RegisterPage}></Route>
        <Route path="/dashboard" exact Component={Dashboard}></Route>
        <Route path="*" Component={NotFound}></Route>
      </Routes>
    </BrowserRouter>
  );
}

export default Router;
