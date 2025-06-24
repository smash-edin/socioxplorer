import './App.css';
import Layout from './components/Layout';
import Admin from './components/Admin';
import Login from './components/Login';
import Analysis from './components/Analysis';
import Help from './components/Help';
import Unauthorized from './components/Unauthorized';
import Missing from './components/Missing';
import {
  BrowserRouter as Router,
  Routes,
  Route,
  Navigate,
  Link,
  Outlet,
  useLocation,
} from "react-router-dom";

import { Navbar } from './components/Navbar';
import 'semantic-ui-css/semantic.min.css'
import LoadReport from "./components/LoadReport";
//import RequireAuth from './components/RequireAuth'
//import TestPage from "./components/TestPage"; <Route path="/test" element= { <TestPage /> } />
import {login, authFetch, useAuth, logout} from "./auth"

const PrivateRoute = ({ element: Component, ...rest }) => {
  const location = useLocation();
  const [logged]   = useAuth();
  return logged ? <Outlet /> : <Navigate to="/login"  state={{ from: location }} replace/>;
}

function App() {
  const [logged] = useAuth(false);
  return (
    <>
      <Navbar logged={logged}/>
      <Routes>
        <Route path="/" element= { <Layout logged={logged}/> } />
        <Route exact path="/load_report"element={<PrivateRoute/>}>
          <Route path="/load_report" element= {< LoadReport logged={logged}/>}/>
        </Route>
        <Route exact path="/analysis"element={<PrivateRoute/>}>
          <Route path="/analysis" element= { <Analysis logged={logged}/> } />
        </Route>
        <Route exact path="/admin"element={<PrivateRoute/>}>
          <Route path="/admin" element= {< Admin logged={logged}/> } />
        </Route>
        <Route exact path="/help"element={<PrivateRoute/>}>
          <Route path="/help" element= {< Help logged={logged}/> } />
        </Route>

        <Route exact path="/login" element={<Login logged={logged}/>}/>


        <Route path="unauthorized" element= {< Unauthorized /> } />
        <Route path="*" element= {< Missing /> } />
      </Routes>
    </>
  );
}

export default App;