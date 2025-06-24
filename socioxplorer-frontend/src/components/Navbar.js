import React, {useEffect, useState} from "react";
import { NavLink, useNavigate } from "react-router-dom";
import { logout } from "../auth";
const LOGOUT_URL = '/logout';


export const Navbar = ({logged}) => {
    const [userType, setUserType] = useState("");

    useEffect(() => {
        const user = JSON.parse(localStorage.getItem('REACT_TOKEN_AUTH_KEY'));
        setUserType(user?.userType);
    }, [logged]);

    const navLinkStyles = ({isActive}) => {
        return {
            fontWeight: isActive ? 'bold' : 'normal',
            textDecoration: isActive ? 'none' : 'underline',
            fontSize: 'x-large',
            margin: 10
        }
    }
    const navigate = useNavigate();
    const handleLogout = async () =>{
        try {
            const response = await fetch(LOGOUT_URL);
            if (!response.ok) throw new Error('Logout failed');
            logout();
            navigate("/")
        }catch (error) {
            console.error("Logout failed:", error);
        }
    }

    return(

        <nav className='primary-nav'>
        {logged ?  (
            <>
                <NavLink style={navLinkStyles} to='/analysis'>
                    Analysis
                </NavLink>

                <NavLink style={navLinkStyles} to='/help'>
                    Help
                </NavLink>

                {userType === 'admin' && (
                    <NavLink style={navLinkStyles} to='/admin'>
                        Admin
                    </NavLink>
                )}
                    <NavLink style={navLinkStyles} to='/load_report'>
                        Load Report
                    </NavLink>
                    <button onClick={handleLogout}>Logout</button>
            </>
            ) : (
                <NavLink style={navLinkStyles} state="Login"  to='/login'>
                    Login
                </NavLink>
            )
            }
        </nav>
    )
}