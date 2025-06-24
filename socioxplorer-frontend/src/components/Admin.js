import React from 'react';
import {useState, useEffect} from 'react';
import {Dropdown, Form, Tab, Button, Input, Popup, Icon} from "semantic-ui-react";
import {DataGrid} from '@mui/x-data-grid';
import {useNavigate} from 'react-router-dom';
import {authFetch, useAuth, logout} from "../auth"

import { csv } from 'd3'
import datasetData from '../.data/datasetOptions.csv';

const ADMIN_ADDUSER_URL = "/api/register_user"
const ADMIN_GETUSERS_URL = "/api/get_users"
const ADMIN_DELUSER_URL = "/api/delete_user"
const ADMIN_REQUEST_PREPROCESSING = "/api/re_process_data"
const ADMIN_URL = '/admin';
const LOGIN_PAGE = '/login';



export const Admin = ({logged}) => {
    const userType = JSON.parse(localStorage?.getItem('REACT_TOKEN_AUTH_KEY'))?.userType
    const navigate = useNavigate();

    const [response, setResponse] = useState([]);
    const [loading, setLoading] = useState(false)
    const [ready, setReady] = useState(false)
    const [username, setUsername] = useState("")
    const [usernameError, setUsernameError] = useState("")
    const [password, setPassword] = useState("")
    const [passwordError, setPasswordError] = useState("")
    
    const [rePreProcessData, setRePreProcessData] = useState(false)
    const [reProcessTopics, setReProcessTopics] = useState(false)
    const [reProcessSNA, setReProcessSNA] = useState(false)
    const [rePreProcessDataError, setRePreProcessDataError] = useState("")
    const [showPassword, setShowPassword] = useState(false);

    const [usersTable, setUsersTable] = useState({});
    const [selectedRows, setSelectedRows] = useState([]);

    const [datasetOptions, setDatasetOptions] = useState([]);
    const [dataSource, setDataSource] = useState('');
    const [dataSourceText, setDataSourceText] = useState('');
    useEffect(() => {
    try {
      csv(datasetData).then(response => {
        setDatasetOptions(response.map(row => {
          return {"key": row['key'], "text": row['text'], "value": row['value']}}));
      });

    }catch (e) {
      console.log("ERROR::Input::" + e.toString())
    }
    }, []);
    useEffect(() => {
        if (datasetOptions!== null && datasetOptions.length > 0) {
            setDataSource(datasetOptions!== null && datasetOptions.length > 0 ? datasetOptions[0].value:'');
        }
      }, [datasetOptions]);

      useEffect(() => {
        if (datasetOptions!== null && datasetOptions.length > 0 && dataSource!== null && dataSource!== undefined) {
            setDataSourceText(datasetOptions ? datasetOptions?.find(x => x.value === dataSource).text: '')
        }else{
            setDataSourceText(datasetOptions!== null && datasetOptions.length > 0 ? datasetOptions[0].text:'');
        }
      }, [dataSource]);

      
    const togglePasswordVisibility = () => {
        setShowPassword(!showPassword);
    };

    const handleSelectionChange = (selectionModel) => {
        if (selectionModel.length > 0) {
            setSelectedRows(selectionModel);
        } else {
            setSelectedRows([]);
        }
    };

    const handleSelectAll = () => {
        const currentPageRows = usersTable.rows.slice(
            usersTable.pageSize * usersTable.page,
            usersTable.pageSize * (usersTable.page + 1)
        );
        const currentPageRowIds = currentPageRows.map(row => row.id);
        setSelectedRows(currentPageRowIds);
    };
    useEffect(() => {
        if (/[^0-9a-zA-Z_@\-$&]/.test(username)) {
            setUsernameError("Only characters, digits and these special chars (_@-$&) are allowed")
        } else {
            setUsernameError("")
        }
        if (/[^0-9a-zA-Z_@\-$&]/.test(password)) {
            setPasswordError("Only characters, digits and these special chars (_@-$&) are allowed")
        } else {
            setPasswordError("")
        }

        setReady((username.length >= 4 && password.length >= 6))
    }, [username, password]);

    const deleteUsers = async () => {
        authFetch(ADMIN_DELUSER_URL,{
            method: 'POST',
            //header: {'Content-Type': 'application/json'},
            body: JSON.stringify({"users": selectedRows}),}).then(() => {
            submitGetUsers()
        })
            .catch(function (error) {
                console.log("responses didnt work")
                if (error.response) {
                    if (error.response.status === 401) {
                        alert("401 error, please login before continuing")
                    } else if (error.response.status === 409) {
                        alert("User name already exists! Please choose another name.")
                    } else {
                        console.log(error.response)
                    }
                }
                setLoading(false)
            });
    }

    // Async function that posts the query to the API to get the necessary info to generate the report
    const submitAddUser = async () => {
        authFetch(ADMIN_ADDUSER_URL, {
            method: 'POST',
            header: {'Content-Type': 'application/json'},
            body: JSON.stringify({"username": username, "password": password})
            }).then((data_resp => {
            if (data_resp.hits > 0) {
                console.log("data_resp: " + data_resp)
            } else {
                console.log("NO data_resp found!")
            }
            submitGetUsers()
            if (data_resp.status === 200){
                alert("User " + username + " created.")
            } else if (data_resp.status === 409) {
                alert("User name already exists! Please choose another name.")
            }else{
                alert("Something went wrong!")
            }
            //setLoading(false)
        }))
            .catch(function (error) {
                console.log("responses didnt work")
                if (error.response) {
                    if (error.response.status === 401) {
                        alert("Not authorised to access, you will be redirected to the correct page!")
                        window.open('/login')
                    } else if (error.response.status === 409) {
                        alert("User name already exists! Please choose another name.")
                    } else {
                        console.log(error.response)
                    }
                }
                alert("Error occured while trying to create the user " + username)
                //setLoading(false)
            });
        setLoading(false)
        setUsername("")
        setPassword("")
    }

    const submitPreprocess = async () => {

        authFetch(ADMIN_REQUEST_PREPROCESSING, {
            method: 'POST',
            header: {'Content-Type': 'application/json'},
            body: JSON.stringify({
                "dataSource": dataSource,
                "dataSourceText": dataSourceText,
                "rePreProcessData": rePreProcessData,
                "reProcessTopics": reProcessTopics,
                "reProcessSNA": reProcessSNA,
            })
            }).then(response => response.json())
            .then(data_resp => {console.log("Response: ", data_resp?.result)
                setRePreProcessDataError(data_resp?.result)
            })
            .catch(function (error) {
                console.log("responses didnt work")
                if (error.response) {
                    if (error.response.status === 401) {
                        alert("Not authorised to access, you will be redirected to the correct page!")
                        window.open('/login')
                    } else {
                        setRePreProcessDataError(error?.response?.result)
                        console.log(error.response)
                    }
                }
                setRePreProcessDataError("Error occured while trying to submit preprocessing request.")
            });
        setRePreProcessData(false)
        setReProcessTopics(false)
        setReProcessSNA(false)
        setLoading(false)
    }

    const submitGetUsers = async () => {
        authFetch(ADMIN_GETUSERS_URL, {
            method: 'POST',
            header: {'Content-Type': 'application/json'},
        }).then(r => r.json())
        .then(response => {
            if (response?.users) {
                const formatData = () => {
                    let rows = response?.users
                    let heightType = "auto"
                    let columns = [
                        {
                            field: 'username',
                            width: 90,
                            align: "left",
                            headerAlign: 'center',
                            renderHeader: () => (<strong>Username</strong>),
                        },
                        {
                            field: 'roles',
                            width: 75,
                            headerAlign: 'center',
                            align: 'center',
                            renderHeader: () => (<strong>Roles</strong>),
                        },
                    ];

                    return {"rows": rows, "columns": columns, "heightType": heightType}
                };
                setUsersTable(formatData(response.data))
            }
            else {
                alert("No data!")
                console.log("NO data_resp found!")
            }
            setLoading(false)
        })
            .catch(function (error) {
                console.log("responses didnt work")
                if (error.response) {
                    if (error.response.status === 401) {
                        alert("Not authorised to access, you will be redirected to the correct page!")
                        window.open('/login')
                    } else {
                        console.log(error.response)
                    }
                }
                setLoading(false)

            });
    }

    const panes = [
    {
        menuItem: 'Current Users',
        render: () => (
        <Tab.Pane>
            <div className="InputFields">
                <div className="SubmitButton">
                    <Button
                        onClick={() => {
                            setLoading(true)
                            submitGetUsers()
                        }}
                        loading={loading}
                    >Get Current Users</Button>

                </div>
            </div>
            {usersTable.rows?.length > 0 &&(
            <div className='InputFields'>
                <div className="TopContent">
                    <DataGrid
                        getRowHeight={() => usersTable["heightType"]}
                        rows={usersTable["rows"]}
                        columns={usersTable["columns"]}
                        initialState={{
                            ...usersTable.initialState,
                            pagination: {paginationModel: {pageSize: 5}},
                        }}
                        checkboxSelection
                        onRowSelectionModelChange={handleSelectionChange}
                        onSelectionModelChange={handleSelectionChange}
                        pageSizeOptions={[5, 10, 15]}
                        selectionModel={selectedRows}
                    />
                </div>
                <div className="SubmitButton">
                    <Button onClick={deleteUsers}>Delete Selected
                        User{selectedRows.length > 1 && 's'} </Button>
                </div>
            </div>
            )}
        </Tab.Pane>
        ),
    },
    {
      menuItem: 'Add User',
      render: () => (
        <Tab.Pane>
            <div className="InputFields">
                {/*<h2>Add User</h2>*/}
                <div className="TitleWithPopup">
                    <h3>Username</h3><h3 style={{marginRight: "5px"}}></h3>
                    <Popup
                        content="The user name of the new user. Only letters and digits are allowed."
                        trigger={<div className='InfoIcon'><Icon name='question circle' size="small"/>
                        </div>}
                    />
                    <Input
                        placeholder="Username"
                        type="text"
                        value={username}
                        onChange={(e, {value}) => setUsername(value)}
                        className="usernameInput"
                    />
                    <div className='Error' style={{
                        marginLeft: "5px",
                        marginTop: "10px",
                        color: "red"
                    }}>{usernameError}</div>
                </div>

                <div className="TitleWithPopup">
                    <h3>Password</h3><h3 style={{marginRight: "5px"}}></h3>
                    <Popup
                        content="The password for the new user."
                        trigger={<div className='InfoIcon'><Icon name='question circle' size="small"/>
                        </div>}
                    />

                    <Input
                        type={showPassword ? 'text' : 'password'}
                        value={password}
                        onChange={(e, {value}) => setPassword(value)}
                        icon={
                            <Icon
                                name={showPassword ? 'eye slash outline' : 'eye'}
                                link
                                onClick={togglePasswordVisibility}
                            />
                        }
                        //iconPosition="left"
                        className="passwordInput"
                    />
                    <div className='Error' style={{
                        marginLeft: "5px",
                        marginTop: "10px",
                        color: "red"
                    }}>{passwordError}</div>
                </div>
            </div>
            <div className="SubmitButton">
                    <Button
                        onClick={() => {
                            setLoading(true)
                            submitAddUser()
                        }}
                        loading={loading}
                        disabled={!ready}
                    >Add User</Button>
                </div>
        </Tab.Pane>
      ),
    },
    {
        menuItem: 'Processing Settings',
        render: () => (
          <Tab.Pane>
              <div className="InputFields">
                <div className='SourceGroup'>
                <div className="SubTitleWithPopup">
                    <h2 style={{marginRight: "5px"}}>Dataset </h2>
                    <Popup
                    content="Choose the dataset you want to generate a report for."
                    trigger={<div className='InfoIcon'><Icon name='question circle' size="small"/></div>}
                    />
                </div>
                <Form.Field>
                    <Dropdown
                    label='Data Source'
                    fluid
                    selection
                    options={datasetOptions}
                    text={datasetOptions.text}
                    floating
                    labeled={true}
                    icon={null}
                    value={dataSource}
                    onChange={(e, { value }) => setDataSource(value)}
                    style={{width: '200px'}}
                    name='source'
                    id='source'
                    ></Dropdown>
                </Form.Field>
                </div>

                  {/*<h2>Prerocessing Settings</h2>*/}
                  <div className="TitleWithPopup">
                      <h3>Re-run preprocessing for all data of {dataSourceText} core?</h3><h3 style={{marginRight: "5px"}}></h3>
                      
                      <Popup
                          content="If you want to consider re-process all data, please tick this option. The pre-processing includes sentiment analysis and the location analysis. It is an expensive process, so please consider the available resources."
                          trigger={<div className='InfoIcon'><Icon name='question circle' size="small"/>
                          </div>}
                      />
                      <Input
                          type="checkbox"
                          checked={rePreProcessData}
                          onChange={(e) => setRePreProcessData(e.target.checked)}
                          className="rePreProcessData"
                      />
                      <div className='Error' style={{
                          marginLeft: "5px",
                          marginTop: "10px",
                          color: "red"
                      }}></div>
                </div>
                <div className="TitleWithPopup">
                      <h3>Re-run Topic Modelling Analysis for {dataSourceText} data?</h3><h3 style={{marginRight: "5px"}}></h3>
                      
                      <Popup
                          content="If you want to consider re-process topics modelling for all data, please tick this option. The pre-processing is limited to the topic modelling analysis. It is an expensive process, so please consider the available resources. It is recommended to be performed once every resonable time such as a month to include new topics."
                          trigger={<div className='InfoIcon'><Icon name='question circle' size="small"/>
                          </div>}
                      />
                      <Input
                          type="checkbox"
                          checked={reProcessTopics}
                          onChange={(e) => setReProcessTopics(e.target.checked)}
                          className="reProcessData"
                      />
                      <div className='Error' style={{
                          marginLeft: "5px",
                          marginTop: "10px",
                          color: "red"
                      }}></div>
                </div>
                <div className="TitleWithPopup">
                      <h3>Re-run Network Analysis for  {dataSourceText} data?</h3><h3 style={{marginRight: "5px"}}></h3>
                      
                      <Popup
                          content="If you want to consider re-process all data, please tick this option. The pre-processing is limited to the  social netowrk analysis. It is recommended to be performed once every resonable time."
                          trigger={<div className='InfoIcon'><Icon name='question circle' size="small"/>
                          </div>}
                      />
                      <Input
                          type="checkbox"
                          checked={reProcessSNA}
                          onChange={(e) => setReProcessSNA(e.target.checked)}
                          className="reProcessSNA"
                      />
                      <div className='Error' style={{
                          marginLeft: "5px",
                          marginTop: "10px",
                          color: "red"
                      }}></div>
                </div>
                <div className={'inputContainer'}>
                    <p className={rePreProcessDataError ? rePreProcessDataError.startsWith('Error') ? "errorLabel" : "messageLabel" : "offscreen"} aria-live="assertive">{rePreProcessDataError}</p>
                </div>
                  <div className="SubmitButton">
                      <Button
                          onClick={() => {
                              setLoading(true)
                              submitPreprocess()
                          }}
                          loading={loading}
                          disabled={false}
                      >Confirm</Button>
                  </div>
              </div>
          </Tab.Pane>
        ),
      },
    ];
    
    return (
        <main className="App">
            {
                logged && userType === 'admin' ? (
                    <>
                        {response?.data?.message}
                        <header className="Input">
                            <div className="PageTitle">
                                <h1>SocioXplorer Dashboard - Admin</h1>
                            </div>
                            <Tab panes={panes} className="AdminPanes"/>
                        </header>

                    </>
                ) : (
                    <p>
                        {"Not authenticated!"}
                    </p>
                )
            }
        </main>

    );
}
export default Admin;
