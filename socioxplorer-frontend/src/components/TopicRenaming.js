import React, {useEffect, useState} from "react";
import {Button} from "semantic-ui-react";
import {TextField} from "@mui/material";
import {DataGrid} from "@mui/x-data-grid";
import { authFetch } from "../auth";

// SNAGraph component used to display scatter plot of network interactions based on retweet interactions.
export const TopicRenaming = ({isVisible, setVisible, topicNames, setTopicNames, graphs, setGraphs,
                                  topicsPerCommunityGraph, setTopicsPerCommunityGraph}) => {

    const [rows, setRows] = useState([]);
    const [loading, setLoading] = useState(false)

    useEffect(() => {
        if (topicNames !== undefined && topicNames !== null) {
            let rowsData = Object.values(topicNames).map((value, index) => ({
                id: index,
                currentTopicName: value,
                newTopicName: ''
            }));
            setRows(rowsData);
        }
    }, [topicNames])


    const handleInputChange = (id, value) => {
        setRows(prevRows =>
            prevRows.map(row =>
                row.id === id ? { ...row, newTopicName: value } : row
            )
        );
    };

    const handleKeyDown = (event) => {
        if (event.key === ' ') {
            event.stopPropagation();
        }
    };

    const columns = [
        {
            field: 'currentTopicName',
            flex: 1,
            headerAlign: 'center',
            align: "center",
            renderHeader: () => (<strong>Current topic name</strong>),
        }, {
            field: 'newTopicName',
            flex: 1,
            headerAlign: 'center',
            align: "center",
            renderHeader: () => (<strong>New topic name</strong>),
            renderCell: (params) => (
                <TextField
                    value={params.row.newTopicName}
                    //onChange={(e) => handleInputChange(params.row.id, e.target.value)}
                    onChange={(e) => handleInputChange(params.row.id, e.target.value)}
                    fullWidth={true}
                    onKeyDown={handleKeyDown}
                    inputProps={{
                        maxLength: 15
                    }}
                />
            )
        }
    ];

    const updateTopicNames = async () => {

        let mapping = {};
        rows.forEach(row => {
            if (row.newTopicName.trim() === '') {
                mapping[row.currentTopicName] = row.currentTopicName;
            } else {
                mapping[row.currentTopicName] = row.newTopicName;
            }
        });

        const newTopicNames = Object.keys(topicNames).reduce((acc, key) => {
            const oldValue = topicNames[key];
            acc[key] = mapping[oldValue];
            return acc;
        }, {});

        let info_for_api = {
            "figures": graphs,
            "topic_names": mapping,
            "topics_per_communities": topicsPerCommunityGraph
        }

        console.log("--> RENAMING TOPICS: input:", info_for_api)

        authFetch('/api/update_topic_names', {
            method: 'POST',
            headers: {'Content-Type': 'application/json', 'Accept-Encoding': 'gzip'},
            body: JSON.stringify({'data': info_for_api}),
            timeout: 30000
        }).then(r => r.json()).then(response => {
            if (response && response.data) {
                    let data_resp = response.data
                    console.log("--> RENAMING TOPICS: response:", data_resp)
                    setGraphs(data_resp["new_figures"])
                    setTopicsPerCommunityGraph(data_resp["new_topics_per_communities"])
                    setTopicNames(newTopicNames)
                    setLoading(false)
            } else {
                console.log("responses didnt work")
                setLoading(false)
            }
        }).catch((error) => {
            if (error?.response?.status === 401) {
                window.open('/login')
            } else {
                alert("Something went wrong, please try again.")
            }
        });
    }

    return (isVisible) ? (
        <div className="Renaming">
            <div className="RenamingInner">
                <h3>Change topic names</h3>
                <p>If a topic field is left blank, it will automatically inherit the same name as before. Drafts of new
                    topic names will be saved if you click on "Close". However, you need to click on "Update topic
                    names"
                    to replace all topic names in the report.
                </p>
                <p>
                    <b style={{color: "red"}}>WARNING</b>: Generating a new Topic Discovery visualisation (e.g. with a different number of
                    topics) the new topic names <b>will</b> be lost. If you want to save the current version of the
                    Topic Discovery visualisation with renamed topics, we recommend using the "Save report" button
                    at the very top of the report. You will then be able to re-load the report from the "Load Report"
                    page.
                </p>
                <DataGrid
                    rowHeight={25}
                    rows={rows}
                    columns={columns}
                    sx={{
                        '& .MuiDataGrid-cell': {
                            padding: 0,
                        },
                    }}
                    initialState={{
                        pagination: {
                            paginationModel: {pageSize: 15, page: 0},
                        },
                    }}
                />
                <Button
                    onClick={() => setVisible(false)}
                    loading={loading}
                >Close</Button>
                <Button
                    onClick={() => {
                        setLoading(true)
                        updateTopicNames()
                    }}
                    loading={loading}
                >Update topic names</Button>
            </div>
        </div>
    ) : "";

};
export default TopicRenaming;