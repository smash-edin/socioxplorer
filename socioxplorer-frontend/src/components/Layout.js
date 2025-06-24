import React from "react";
import { Outlet, useNavigate } from "react-router-dom";
import {Button} from 'semantic-ui-react';


const Layout = ({logged}) => {
    let navigate = useNavigate();
    return (
    <main className="App">
        <Outlet />
        <section>
                    <header className="Input">
                        <div className={'mainContainer'}>
                            <div className = "PageTitle">
                                <h1>SocioXplorer Dashboard</h1>
                            </div>
                            <br/>
                           
                                <div className={'inputContainer'}>
                                    <Button className="SubmitButton" onClick={() => {navigate(logged? '/analysis':'/login')}}>{logged? 'Go to dashboard!':'Go to login page!!'}</Button>
                                </div>
                        </div>
                    </header>
                </section>
    </main>
    )
}
export default Layout