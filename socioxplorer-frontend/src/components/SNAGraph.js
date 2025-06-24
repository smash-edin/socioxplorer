import {Button, Dropdown, Icon, Input, Popup} from "semantic-ui-react";
import React, {useEffect, useState} from "react";
import Plot from "react-plotly.js";
import { authFetch } from "../auth";

// SNAGraph component used to display scatter plot of network interactions based on retweet interactions.
export const SNAGraph = ({input_info, keywords, setDisableGeneralQuery,
                           // setDisableTopicModellingQueries,
                           disableSNAGraphQueries,
                           setCommunityWords, showSNAGraph, setShowSNAGraph, data, setData,
                           topicGraphs, setCurrentSNAKeyword,
                           // setTopicGraphs,
                           setCommunityRenamingVisible, setCommunityNames, setLastSNAQuery,
                           setSNAcolors, setSNATrafficGraphData, setStatesTable, communityGraphs, setCommunityGraphs,
                           datasetOrigin,selectedNetworkInteraction,setSelectedNetworkInteraction,
                           updateTopicModelling,nbCommunities, setNbCommunities, savedReportDate
                         }) => {

  
    // Variables storing loading, disabling and error message states
    const [loading, setLoading] = useState(false)
  
    // Variable to store scatter plots returned by API upon request
    // const [graphs, setGraphs] = useState(null);
    const [dropNetworkInteractionsFilter, setDropNetworkInteractionsFilter] = useState(datasetOrigin === "Twitter" ? [
        {key: 'Retweet', text: 'Retweet', value: 'Retweet'},
        {key: 'Reply', text: 'Reply', value: 'Reply'},] : [{key: 'Reply', text: 'Reply', value: 'Reply'},] );
    const [allKeywordsLabel, setAllKeywordsLabel] = useState(input_info["operator"] === "AND" ? "All keywords" : "Any keyword")

    useEffect(() => {
        setAllKeywordsLabel(input_info["operator"] === "AND" ? "All keywords" : "Any keyword")
    },[input_info]);

    // Dropdown menu options: keywords
    const dropKeywordsFilter = keywords.map((dictionaryKey) => {
        return {
            "key": dictionaryKey,
            "value": dictionaryKey,
            "text": dictionaryKey === "All"? allKeywordsLabel : dictionaryKey[0].toUpperCase()+dictionaryKey.slice(1)}
    });

    // Variables storing filters to apply to scatter plot
    const [selectedKeywordsFilters, setSelectedKeywordsFilters] = useState(keywords[0]);
    const [noNetworkForTheseFilters, setNoNetworkForTheseFilters] = useState(false)

    // useEffect hook to remove existing SNA scatter plot upon the generation of a new report
    useEffect(() => {
        console.log("inside THIS useEffect")
        console.log(input_info)
        if (!(keywords.includes(selectedKeywordsFilters))){
            setSelectedKeywordsFilters(keywords[0]);
        }else {
          setSelectedKeywordsFilters(selectedKeywordsFilters);
        }
        setDropNetworkInteractionsFilter(datasetOrigin === "Tweets" ? [
          {key: 'Retweet', text: 'Retweet', value: 'Retweet'},
          {key: 'Reply', text: 'Reply', value: 'Reply'},] : [{key: 'Reply', text: 'Reply', value: 'Reply'},]);
        var existingElement = document.getElementById('SNA');
        if (existingElement) {
          existingElement.innerHTML = '';
        }
    },[keywords, showSNAGraph, communityGraphs]);

    useEffect(() => {
        if (input_info?.claim === null) {
            setShowSNAGraph(false);
        }
        setNbCommunities(input_info?.nbCommunities ?? "10");
    }, [input_info]);
  
    // useEffect hook to update the SNA scatter plot upon a change in the graph data or the keywords or
    // sentiment filters
    useEffect(() => {
        const timer = setTimeout(() => {
            setCurrentSNAKeyword(selectedKeywordsFilters);
            console.log("USE EFFECT --> get community data");

            if (showSNAGraph) {
                console.log("Condition 1 met");

                if (communityGraphs != null) {
                    console.log("Condition 2 met");

                    const existingElement = document.getElementById('SNA');
                    if (existingElement) {
                        existingElement.innerHTML = ''; // Clear previous content
                    }

                    const plotData = communityGraphs[selectedKeywordsFilters];
                    console.log("--> communityGraphs", communityGraphs);

                    const parsedPlotData = typeof plotData === 'string' ? JSON.parse(plotData) : plotData;
                    console.log("--> parsedPlotData", parsedPlotData);

                    if (parsedPlotData) {
                        console.log("Condition 3 met");
                        try {
                            setNoNetworkForTheseFilters(false);
                            window.Bokeh.embed.embed_item(parsedPlotData, 'SNA');
                            console.log("Condition 4 met");
                        } catch (e) {
                            window.Bokeh.embed.embed_item(null, 'SNA');
                            setNoNetworkForTheseFilters(true); // Handle error gracefully
                        }
                    } else {
                        setNoNetworkForTheseFilters(true); // No data available
                    }
                }
            }
        }, 100); // Delay execution by 300ms

        // Cleanup previous timer to avoid overlapping calls
        return () => clearTimeout(timer);
    }, [communityGraphs, selectedKeywordsFilters, showSNAGraph]);


    useEffect(() => {
        if (!keywords.includes(selectedKeywordsFilters)){
            setSelectedKeywordsFilters(keywords[0]);
        }
    },[keywords]);


  // Function to merge the dictionaries
    const mergeDictionaries = (report, communitiesMap) => {
        let updatedReport = report
        for (const key in communitiesMap) {
            updatedReport[key] = {
                ...updatedReport[key],
                ...communitiesMap[key],
            };
        }
        console.log("NEW REPORT AFTER SNA", updatedReport)
        return updatedReport;
    };

  // Post query to API for Social Network Analysis (SNA) visualisation
    const getVisualisation = async () => {
        let nbCommunitiesInt = 0
        if (nbCommunities !== "") {
            nbCommunitiesInt = parseInt(nbCommunities)
        }

        let info_for_api = {
            "keyword": selectedKeywordsFilters,
            "keywords": input_info["keywords"].filter(keyword => keyword !== "All"),
            "date_start": input_info["date_start"],
            "date_end": input_info["date_end"],
            "limit": input_info["limit"],
            "dataSource": input_info["dataSource"],
            "operator": input_info["operator"],
            "random_seed": input_info["random_seed"],
            "language": input_info["language"],
            "sentiment": input_info["sentiment"],
            "location": input_info["location"],
            "location_type": input_info["location_type"],
            "nb_communities": nbCommunitiesInt,
            "interaction": selectedNetworkInteraction.toLowerCase(),
            "datasetOrigin": datasetOrigin,
            // "topic_graphs": topicGraphs,
        }
        console.log("INFO FOR API (SNA)", info_for_api)
        setLastSNAQuery(info_for_api)
        authFetch('/api/social_network_analysis', {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({'data': info_for_api}),
            timeout: 30000
        }).then(r => r.json()).then(response => {
            if (response && response.data) {
                let data_resp = response.data
                console.log("SNA RESPONSE", data_resp)
                setCommunityGraphs(data_resp["sna_figure"])
                setStatesTable(data_resp["network_stats"])
                setSNATrafficGraphData(data_resp["communities_traffic"])
                setSNAcolors(data_resp["communities_colors"])
                setCommunityWords(data_resp["top_words"])
                setCommunityNames(data_resp["community_names"])
                let updatedReport = mergeDictionaries(data["report"], data_resp["communities_map"]);
                setData((prevData) => ({
                    ...prevData,
                    report: updatedReport
                }));
                if (topicGraphs !== null) {
                    updateTopicModelling(data_resp["community_names"])
                }
                setShowSNAGraph(true);
                setLoading(false);
            } else {
                setLoading(false)
                setShowSNAGraph(false)
            }
        }).catch((error) => {
            if (error?.response?.status === 401) {
                window.open('/login')
            } else {
                alert("Something went wrong, please try again.")
                setLoading(false)
                setShowSNAGraph(false)
            }
        });
        setDisableGeneralQuery(false)
        // setDisableTopicModellingQueries(false)
    }


    const renderSNAVis = () => {
        if (noNetworkForTheseFilters) {
            return (
                <div className="ErrorMessage">
                    <p>No network interaction data for the selected keyword/filter.</p>
                </div>
            )
        } else {
            return (
                <div className={showSNAGraph ? 'SNAGraphVis' : 'hidden'}>
                    <div id="SNA" className="bk-root"></div>
                </div>
            )
        }
    }


    return (
        <div className="Visualisation">
            <div className="MainTitleWithPopup">
                <h2>Social Network Analysis ({selectedNetworkInteraction})</h2>
                <Popup
                    content="Clicking 'Generate' in this component will display authors for the current query such that users that retweet each other a lot are located close to each other. Once a visualisation is generated, hovering over a datapoint will display the user's screen name and description. Clicking on a datapoint will open the user profile on Twitter (X) in a new tab."
                    trigger={<div className='InfoIcon'><Icon name='question circle' size="small"/></div>}
                />
            </div>
            <div className="DropDownGroup">
                <div className="DropDownMaps">
                    <div className="SubTitleWithPopup">
                        <h3 style={{marginRight: "5px"}}>Network</h3>
                        <Popup
                            content="The network interaction for the social network analysis component. The network interaction is based on retweet and reply interactions between users. The visualisation will display authors for the current query such that users that retweet each other a lot are located close to each other. Once a visualisation is generated, hovering over a datapoint will display the user's screen name and description. Clicking on a datapoint will open the user profile on Twitter (X) in a new tab."
                            trigger={<div className='InfoIcon'><Icon name='question circle' size="small"/></div>}
                        />
                    </div>
                    <div className="DropDownMenu">
                        <Dropdown
                            label='NetworkFilter'
                            fluid
                            selection
                            options={dropNetworkInteractionsFilter}
                            text={dropNetworkInteractionsFilter.text}
                            floating
                            labeled={true}
                            className='source'
                            icon={null}
                            value={selectedNetworkInteraction}
                            onChange={(e, {value}) => setSelectedNetworkInteraction(value)}
                            closeOnChange={true}
                            name='networkFiltersTypeDropdown'
                            id='networkFiltersTypeDropdown'
                        ></Dropdown>
                    </div>
                </div>
                <div className="DropDownMaps">
                    <div className="SubTitleWithPopup">
                        <h3 style={{marginRight: "5px"}}>Nb communities</h3>
                        <Popup
                            content="The number of communities specified determines the number of communities highlighted in the visualisation. By default the number of communities is 10, which means only the top 10 biggest communities for the current query will be colored. Once the Social Network Analysis graph is generated, you can go to the Wordcloud component to see the wordcloud obtained from each community's user descriptions by selecting 'Community user descriptions' under the 'Field' filter. "
                            trigger={<div className='InfoIcon'><Icon name='question circle' size="small"/></div>}
                        />
                    </div>
                    <Input
                        placeholder="Nb communities (optional)..."
                        type="number"
                        min="1"
                        step="1"
                        // ref={nbTopicsRef}
                        value={nbCommunities}
                        onChange={(e, {value}) => {
                          setNbCommunities(value);
                        }}
                        className="NbCommunitiesInput"
                    />
                </div>
                <div>
                    <div className={savedReportDate !== ''? "hidden" : "ButtonNormal"}>
                        <Button
                            onClick={() => {
                                setDisableGeneralQuery(true)
                                // setDisableTopicModellingQueries(true)
                                setLoading(true)
                                getVisualisation()
                            }}
                            disabled={disableSNAGraphQueries}
                            loading={loading}
                            style={{marginRight: 50}}
                        >Generate</Button>
                    </div>
                </div>
            </div>
            <div className="DropDownGroup">
                <div className="DropDownMaps">
                    <div className="SubTitleWithPopup">
                        <h3 style={{marginRight: "5px"}}>Keywords</h3>
                        <Popup
                            content="Once the visualisation is generated, if more than 1 keyword was provided, you can use the 'Keyword' filter to display results for each keyword independently, as well as for all keywords together ('All keywords')."
                            trigger={<div className='InfoIcon'><Icon name='question circle' size="small"/></div>}
                        />
                    </div>
                    <div className="DropDownMenu">
                        <Dropdown
                            label='TokensKeywordsFilter'
                            fluid
                            selection
                            options={dropKeywordsFilter}
                            text={dropKeywordsFilter.text}
                            floating
                            labeled={true}
                            className='source'
                            icon={null}
                            value={selectedKeywordsFilters}
                            onChange={(e, {value}) => setSelectedKeywordsFilters(value)}
                            closeOnChange={true}
                            name='tokensFiltersTypeDropdown'
                            id='tokensFiltersTypeDropdown'
                        ></Dropdown>
                    </div>
                </div>
                <div>
                    <div className={savedReportDate !== ''? "hidden" : "ButtonNormal"}>
                        <Button
                            onClick={() => setCommunityRenamingVisible(true)}
                            disabled={!showSNAGraph || loading || disableSNAGraphQueries}
                        >Rename communities</Button>
                    </div>
                </div>
            </div>
            {renderSNAVis()}
        </div>
    );
};
export default SNAGraph;