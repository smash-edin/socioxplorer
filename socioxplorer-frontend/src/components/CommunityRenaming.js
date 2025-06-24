import {Button} from "semantic-ui-react";
import {TextField} from "@mui/material";
import {DataGrid} from "@mui/x-data-grid";
import {useEffect, useState} from "react";
import {authFetch} from "../auth";
import { max, set } from "date-fns";

// SNAGraph component used to display scatter plot of network interactions based on retweet interactions.
export const CommunityRenaming = ({ isVisible, 
                                    setVisible, 
                                    communityNames, 
                                    setCommunityNames, 
                                    topicGraphs, 
                                    setTopicGraphs,
                                    setCommunityGraphs, 
                                    lastSNAQuery,
                                    currentSNAKeyword,
                                    setStatesTable, 
                                    setSNATrafficGraphData,
                                    setSNAcolors, 
                                    setCommunityWords, 
                                    data, 
                                    setData,
                                    updateTopicModelling,
                                    selectedNetworkInteraction
    }) => {
    const [rows, setRows] = useState([]);
    const [loading, setLoading] = useState(false)
    // Function to merge the dictionaries
    const mergeDictionaries = (report, communitiesMap) => {
        let updatedReport = report
        for (const key in communitiesMap) {
            updatedReport[key] = {
                ...updatedReport[key],
                ...communitiesMap[key],
            };
        }
        return updatedReport;
    };

    useEffect(() => {
        if (communityNames !== undefined && communityNames !== null) {
            let rowsData = communityNames[currentSNAKeyword]
            ? Object.entries(communityNames[currentSNAKeyword]).map(([key, value], index) => ({
                id: index,
                key: key,
                currentCommunityName: value,
                newCommunityName: ''
            })):[];
            setRows(rowsData);
        }
    }, [communityNames, currentSNAKeyword])


    const handleInputChange = (id, value) => {
        setRows(prevRows =>
            prevRows.map(row =>
                row.id === id ? { ...row, newCommunityName: value } : row
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
            field: 'currentCommunityName',
            flex: 1,
            headerAlign: 'center',
            align: "center",
            renderHeader: () => (<strong>Current community name</strong>),
        }, {
            field: 'newCommunityName',
            flex: 1,
            headerAlign: 'center',
            align: "center",
            renderHeader: () => (<strong>New community name</strong>),
            renderCell: (params) => (
                <TextField
                    value={params.row.newCommunityName}
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


    const updateCommunityNames = async (reset = false) => {
        let mapping = {};
        rows.forEach(row => {
            if (row.newCommunityName.trim() === '') {
                mapping[row.key] = row.currentCommunityName;
            } else {
                mapping[row.key] = row.newCommunityName;
            }
        });
        const generate_report = reset? window.confirm("Are you sure you want to reset all communities names?"): true;

        let info_for_api = {
            "keyword": lastSNAQuery["keyword"],
            "keywords": lastSNAQuery["keywords"],
            "date_start": lastSNAQuery["date_start"],
            "date_end": lastSNAQuery["date_end"],
            "limit": lastSNAQuery["limit"],
            "dataSource": lastSNAQuery["dataSource"],
            "operator": lastSNAQuery["operator"],
            "random_seed": lastSNAQuery["random_seed"],
            "language": lastSNAQuery["language"],
            "sentiment": lastSNAQuery["sentiment"],
            "location": lastSNAQuery["location"],
            "location_type": lastSNAQuery["location_type"],
            "nb_communities": lastSNAQuery["nb_communities"],
            "interaction": lastSNAQuery["interaction"],
            "topic_graphs": topicGraphs,
            "community_names": mapping,
            "datasetOrigin": lastSNAQuery["datasetOrigin"],
            "reset": reset
        }

        console.log("--> RENAMING COMMUNITIES: input:", info_for_api)
        if (generate_report){
            authFetch('/api/social_network_analysis', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({'data': info_for_api}),
                timeout: 30000
            }).then(r => r.json()).then(response => {
                console.log("--> RENAMING COMMUNITIES: response:")
                if (response && response.data) {
                    let data_resp = response.data
                    console.log("--> RENAMING COMMUNITIES: data_resp:", data_resp)
                    setCommunityGraphs(data_resp["sna_figure"])
                    setStatesTable(data_resp["network_stats"])
                    setSNATrafficGraphData(data_resp["communities_traffic"])
                    setSNAcolors(data_resp["communities_colors"])
                    setCommunityWords(data_resp["top_words"])
                    setCommunityNames(data_resp["community_names"])
                    //setTopicGraphs(data_resp["new_topic_graphs"])
                    let updatedReport = mergeDictionaries(data["report"], data_resp["communities_map"]);
                    setData((prevData) => ({
                        ...prevData,
                        report: updatedReport
                    }));
                    if (topicGraphs !== null && topicGraphs !== undefined) {
                        updateTopicModelling(data_resp["community_names"])
                    }
                    setLoading(false)
                } else {
                    console.log("--> RENAMING COMMUNITIES: responses didnt work")
                    setLoading(false)
                }
            }).catch((error) => {
                if (error?.response?.status === 401) {
                    window.open('/login')
                } else {
                    alert("--> RENAMING COMMUNITIES: Something went wrong, please try again.")
                }
            })
        }else{
            setLoading(false)
        }
    }

    return (isVisible) ? (
        <div className="Renaming">
            <div className="RenamingInner">
                <h3>Change community names for {lastSNAQuery["interaction"] && lastSNAQuery["interaction"] !== '' ? ' (' + lastSNAQuery["interaction"].charAt(0).toUpperCase() + lastSNAQuery["interaction"].slice(1) + ')' : ''}</h3>
                <p>If a community field is left blank, it will automatically inherit the same name as before. Drafts of new
                    community names will be saved if you click on "Close". However, you need to click on "Update community names"
                    to replace all community names in the report.
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
                            paginationModel: { pageSize: 15, page: 0 },
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
                        updateCommunityNames()}}
                    loading={loading}
                >Update community names</Button>
                <Button
                    onClick={() => {
                        setLoading(true)
                        updateCommunityNames(true)}}
                    loading={loading}
                >Reset community names</Button>
            </div>
        </div>
    ) : "";

};
export default CommunityRenaming;