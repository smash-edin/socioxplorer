import React, {useRef, useState, useEffect} from "react"
import {login, logout} from "../auth"
import {Button} from 'semantic-ui-react';
import {useLocation, useNavigate} from "react-router-dom";

const LOGIN_URL = '/api/login';

const Login = ({logged}) => {
    const navigate = useNavigate();
    const location = useLocation();
    const from_ = String(location.state?.from?.pathname).toLowerCase();
    const from = from_ === "/null" || from_ === "undefined" ? "/analysis" : from_;
    const userRef = useRef();
    const errRef = useRef();

    const [username, setUsername] = useState('')
    const [password, setPassword] = useState('')
    
    const [errMsg, setErrMsg] = useState('');

    useEffect(() => {
        setErrMsg('');
    }, [username, password]);

    const handleSubmit = (e) => {
        e.preventDefault();
        let opts = {
            'username': username,
            'password': password
          }
          fetch(LOGIN_URL, {
            method: 'post',
            header: {'Content-Type': 'application/json'},
            body: JSON.stringify(opts),
        }).then(r => r.json())
        .then(token => {
            if (token.accessToken){
            login(token)
            setUsername('');
            setPassword('');
            navigate(from, {replace: true});
            }
            else {
            console.log(token)
            setErrMsg('Please type in correct username/password')
            }
        }).catch((err) => {
            console.log(err);
            setErrMsg('No server response. Please check that the server is up and connected.');
        })
    };
    return (
        <>
            <br/>
            {!logged?.logged ? (
                <section>
                    <header className="Input">
                        <div className={'mainContainer'}>
                            <div className = "PageTitle">
                                <h1>SocioXplorer Dashboard</h1>
                            </div>
                            <div className={'titleContainer'}>
                                <h2>Login In</h2>
                                <br/>
                            </div>
                            <br/>
                            <form onSubmit={handleSubmit}>  
                                <div className={'inputContainer'}>
                                    <label htmlFor="username">Username:</label>
                                    <input
                                        type="text"
                                        id="username"
                                        ref={userRef}
                                        autoComplete="off"
                                        autoFocus={true}
                                        onChange={(e) => setUsername(e.target.value)}
                                        value={username}
                                        placeholder="Enter your username here"
                                        required/>
                                </div>
                                <div className={'inputContainer'}>
                                    <label htmlFor="password">Password</label>
                                    <input
                                        type="password"
                                        id="password"
                                        onChange={(e) => setPassword(e.target.value)}
                                        value={password}
                                        placeholder="Enter your password here"
                                        required/>
                                </div>
                                <br/>
                                <div className={'inputContainer'}>
                                    <Button className="SubmitButton">Sign In</Button>
                                </div>

                            </form>
                            <div className={'inputContainer'}>
                            <p ref={errRef}  className={errMsg ? "errorLabel" : "offscreen"} aria-live="assertive">{errMsg}</p>
                            </div>
                        </div>
                    </header>
                </section>
            ) : (
                <></>
            )
            }
        </>
    )
}
export default Login