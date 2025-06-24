import React, {useState, useEffect} from 'react';
import {Button} from "semantic-ui-react";
import {DataGrid} from '@mui/x-data-grid';
import {useNavigate} from 'react-router-dom';
import { authFetch } from '../auth';

const LoadReport_URL = "/api/load_report"
const DeleteReport_URL = "/api/delete_report"


export const LoadReport = ({logged}) => {
    const navigate = useNavigate();
    const [response, setResponse] = useState([]);


    const [loading, setLoading] = useState(false)
    const [reportsTable, setReportsTable] = useState({});
    const [selectedRows, setSelectedRows] = useState([]);


    const handleSelectionChange = (selectionModel) => {
        // Assuming your DataGrid row ids are in the 'id' field
        console.log('selectionModel1:', selectionModel);

        if (selectionModel.length > 0) {
            setSelectedRows(selectionModel);
            console.log('selectedRowsData:', selectionModel);
        } else {
            setSelectedRows([]);
        }
    };

    const renderTextWithURLs = (params, dataField, labelField, url_) => {
        const label = params.row[labelField];
        const text = params.row[dataField];
        return (
            <>
                <a href={url_ + "/analysis?reportName=" + label + "&report=" + text} target="_blank">{label} </a>
            </>
        )
    }

    const getTermsFromToken = (params, dataField, labelField) => {
        const text = params.row[dataField];
        //const data = JSON.parse(atob(text))
        const data = JSON.parse(decodeURIComponent(text).toString())
        return (
            labelField === 'dates' ? (data['date_start'] !== null && data['date_start'] !== undefined ? data['date_start'].slice(0, 10) : "") + ' - ' + (data['date_end'] !== null && data['date_end'] !== undefined ? data['date_end'].slice(0, 10) : "") : labelField === 'keywords' ? data[labelField] : data[labelField]
        )
    }

    const deleteReport = async () => {
        authFetch(DeleteReport_URL,{
                method: 'POST',
                withCredentials: true, 
                body: JSON.stringify({"reports": selectedRows,}),
                timeout: 15000
            }
        ).then(() => {
            submitGetReports()
        }).catch(function (error) {
            console.log("responses didnt work");
            if (error.response) {
                if (error.response.status === 401) {
                    console.log("401 error, please login before continuing")
                    alert("401 error, please login before continuing")
                } else if (error.response.status === 409) {
                    console.log("User name already exists! Please choose another name.")
                    alert("User name already exists! Please choose another name.")
                } else {
                    console.log(error.response)
                }
            }
        });
        setLoading(false);
    }

    // Async function that posts the query to the API to get the necessary info to generate the report
    const submitGetReports = async () => {
        authFetch(LoadReport_URL, {
            method: 'POST',
            header: {'Content-Type': 'application/json'},
            timeout: 15000}).then(r=>r.json()).then((response) => {
            if (response) {
                const formatData = (response) => {
                    const currentUrl = window.location.origin
                    let heightType = "auto"
                    let rows = response
                    let columns = [
                        {
                            field: 'reportName',
                            width: 300,
                            align: "left",
                            headerAlign: 'center',
                            renderHeader: () => (<strong>Report Name</strong>),
                            renderCell: (params) => renderTextWithURLs(params, 'token', 'reportName', currentUrl)
                        },
                        {
                            field: 'username',
                            width: 100,
                            align: "left",
                            headerAlign: 'center',
                            renderHeader: () => (<strong>Created by</strong>),
                        },
                        {
                            field: 'creationTime',
                            width: 125,
                            align: "left",
                            headerAlign: 'center',
                            renderHeader: () => (<strong>Creation Time</strong>),
                        },
                        {
                            field: 'terms',
                            width: 125,
                            align: "left",
                            headerAlign: 'center',
                            renderHeader: () => (<strong>Keywords</strong>),
                            renderCell: (params) => getTermsFromToken(params, 'token', 'keywords')
                        },
                        {
                            field: 'dataSource',
                            width: 100,
                            align: "left",
                            headerAlign: 'center',
                            renderHeader: () => (<strong>Source</strong>),
                            renderCell: (params) => getTermsFromToken(params, 'token', 'source_text')
                        },
                        {
                            field: 'sentiment',
                            width: 75,
                            align: "left",
                            headerAlign: 'center',
                            renderHeader: () => (<strong>Sentiment</strong>),
                            renderCell: (params) => getTermsFromToken(params, 'token', 'sentiment')
                        },
                        {
                            field: 'dateRange',
                            width: 175,
                            align: "left",
                            headerAlign: 'center',
                            renderHeader: () => (<strong>Date Range</strong>),
                            renderCell: (params) => getTermsFromToken(params, 'token', 'dates')
                        }
                    ];
                    return {"rows": rows, "columns": columns, "heightType": heightType}
                };

                setReportsTable(formatData(response.data))
            } else {
                console.log("NO data_resp found!")
            }
        }).catch((err) => {
            console.log("responses didnt work")
            if (err.status === 401) {
                console.log("401 error, please login before continuing")
                alert("401 error, please login before continuing")
            } else if (err.status === 409) {
                console.log("User name already exists! Please choose another name.")
                alert("User name already exists! Please choose another name.")
            } else {
                console.log(err)
            }
        });
        setLoading(false);
    };

    return (
        <main className="App">
            {
                logged ? (
                    <>
                        {response?.data?.message}
                        <header className="Input">
                            <div className="PageTitle">
                                <h1>SocioXplorer Dashboard - Load Reports</h1>
                            </div>
                            <div className="InputFields">
                                <div className="SubmitButton">
                                    <Button
                                        onClick={() => {
                                            setLoading(true)
                                            submitGetReports()
                                        }}
                                        loading={loading}
                                    >Get Reports</Button>

                                </div>
                            </div>

                            {reportsTable["rows"] !== undefined && reportsTable["rows"] !== null && reportsTable["rows"].length > 0 &&
                                <div className='InputFields'>
                                    <div className="TopContent">
                                        <DataGrid
                                            getRowHeight={() => reportsTable["heightType"]}
                                            rows={reportsTable["rows"]}
                                            columns={reportsTable["columns"]}
                                            initialState={{
                                                ...reportsTable.initialState,
                                                pagination: {paginationModel: {pageSize: 5}},
                                            }}
                                            checkboxSelection
                                            onRowSelectionModelChange={handleSelectionChange}
                                            pageSizeOptions={[5, 10, 15]}
                                        />
                                        <div className="SubmitButton">
                                            <button onClick={deleteReport}>Delete Selected
                                                Reports{selectedRows.length > 1 && 's'} </button>
                                        </div>
                                    </div>
                                </div>
                            }

                        </header>
                    </>
                ) : (
                    <>
                        <p>
                            {"Not Authenticated"}
                        </p>
                    </>

                )
            }
        </main>

    );
}
export default LoadReport;
