import {Button, Checkbox, Dropdown, Icon, Input, Popup} from "semantic-ui-react";
import React, {useEffect, useState} from "react";
import { authFetch } from "../auth";
import TopicsPerCommunity from "./TopicsPerCommunity";

// TopicModelling component used to display scatter plot of tweets based on 2D embeddings, to cluster tweets and to
// find location of tweets matching a given claim
export const TopicModelling = ({
                                   hits,
                                   input_info,
                                   keywords,
                                   topicWords,
                                   setTopicWords,
                                   setDisableGeneralQuery,
                                   // setDisableSNAGraphQueries,
                                   disableTopicModellingQueries,
                                   setInput,
                                   setTopicRenamingVisible,
                                   // setTopicNames,
                                   graphs,
                                   setGraphs,
                                   topicsPerCommunityGraph,
                                   communityNames,
                                   showTopicModelling,
                                   setShowTopicModelling,
                                   selectedNetworkInteraction,
                                   selectedCommunityFilter,
                                   setSelectedCommunityFilter,
                                   nbTopics,
                                   setNbTopics,
                                   claim,
                                   setClaim,
                                   generateTopicModelling,
                                   prevNbTopics,
                                   loading,
                                   setLoading,
                                   noTweetsForTheseFilters,
                                   setNoTweetsForTheseFilters,
                                   focusOnTopCommunities,
                                   setFocusOnTopCommunities,
                                   prevFocusOnTopCommunities,
                                   showAsPercentage,
                                   setShowAsPercentage,
                                   isSavedReport,
                                   datasetOrigin,
                                   savedReportDate
                               }) => {

    const random_seed = (input_info === null || input_info === undefined) ? 42 : (input_info["random_seed"] === null) ? 42 : JSON.stringify(input_info['random_seed'])

    // Variables storing loading, disabling and error message states
    // const [loading, setLoading] = useState(false)
    // const [noTweetsForTheseFilters, setNoTweetsForTheseFilters] = useState(false)

    // Variables storing filters to apply to scatter plot
    const [selectedKeywordsFilters, setSelectedKeywordsFilters] = useState(keywords[0]);

    const [allKeywordsLabel, setAllKeywordsLabel] = useState(input_info["operator"] === "AND" ? "All keywords" : "Any keyword")

    // Dropdown menu options: keywords
    const dropKeywordsFilter = keywords.map((dictionaryKey) => {
        return {
            "key": dictionaryKey,
            "value": dictionaryKey,
            "text": dictionaryKey === "All" ? allKeywordsLabel : dictionaryKey[0].toUpperCase() + dictionaryKey.slice(1)
        }
    });

    const [dropSelectedSentiments, setDropSelectedSentiments] = useState([])
    const [sentimentDisable, setSentimentDisable] = useState(false)
    const [selectedSentiment, setSelectedSentiment] = useState('All Sentiments');

    const [showCommunityFilter, setShowCommunityFilter] = useState(false);
    const [dropCommunityFilter, setDropCommunityFilter] = useState(null);
    const [showTopicsPerCommunityGraph, setShowTopicsPerCommunityGraph] = useState(false);
    useEffect(() => {
        setAllKeywordsLabel(input_info["operator"] === "AND" ? "All keywords" : "Any keyword")
        if (input_info["sentiment"] === "All") {
            setDropSelectedSentiments([
                {key: 'All Sentiments', text: 'All Sentiments', value: 'All Sentiments',},
                {key: 'Positive', text: 'Positive', value: 'Positive',},
                {key: 'Neutral', text: 'Neutral', value: 'Neutral',},
                {key: 'Negative', text: 'Negative', value: 'Negative',},
            ])
        } else {
            setDropSelectedSentiments([
                {key: input_info["sentiment"], text: input_info["sentiment"], value: input_info["sentiment"]}
            ])
        }
        setSentimentDisable(input_info["sentiment"] !== "All")
        setSelectedSentiment(input_info["sentiment"] === 'All' ? 'All Sentiments' : input_info["sentiment"])
    }, [hits, input_info, keywords])

    // useEffect hook to remove existing TopicModelling scatter plot upon the generation of a new report
    useEffect(() => {
        var existingTopicMod = document.getElementById('topic_mod');
        if (existingTopicMod) {
            existingTopicMod.innerHTML = '';
        }
        console.log("CHANGING setFocusOnTopCommunities NB 2", focusOnTopCommunities)
        setShowTopicModelling(isSavedReport? showTopicModelling : false )
        setTopicWords(isSavedReport? topicWords : null)
        setNbTopics( isSavedReport? nbTopics : 
            input_info === null ? "10" : input_info['nbTopics'] === null || input_info['nbTopics'] === undefined ? "10" : input_info['nbTopics'])
        setClaim(isSavedReport? claim : 
            input_info === null ? "" : input_info['claim'] === null || input_info['claim'] === undefined ? "" : input_info['claim'])
        if (!keywords.includes(selectedKeywordsFilters)) {
            setSelectedKeywordsFilters(keywords[0]);
        }
    }, [hits, keywords]);

    useEffect(() => {
        setShowTopicsPerCommunityGraph(
            nbTopics > 0 && showTopicModelling
        )
    }, [nbTopics, showTopicModelling])

    useEffect(() => {
        const timer = setTimeout(() => {
            if (showTopicModelling) {
                const existingTopicMod = document.getElementById('topic_mod');
                if (existingTopicMod) {
                    existingTopicMod.innerHTML = ''; // Clear previous content
    
                    const plotData = graphs[selectedKeywordsFilters]?.[selectedSentiment]?.[selectedCommunityFilter];
                    const parsedPlotData = typeof plotData === 'string' ? JSON.parse(plotData) : plotData;
    
                    if (parsedPlotData) {
                        try {
                            window.Bokeh.embed.embed_item(parsedPlotData, 'topic_mod');
                            setNoTweetsForTheseFilters(false); // Data available, no issue
                        } catch (error) {
                            console.error('--> TOPIC MODELLING: Error embedding Bokeh item:', error);
                            setNoTweetsForTheseFilters(true); // Error occurred
                        }
                    } else {
                        console.log("--> TOPIC MODELLING: No graph data for keywords and sentiment:", selectedKeywordsFilters, selectedSentiment);
                        setNoTweetsForTheseFilters(true); // No data for current filters
                    }
                } else {
                    console.error('--> TOPIC MODELLING: #topic_mod element not found in DOM');
                }
            }
        }, 300); // Increase delay slightly to ensure DOM stability
    
        return () => clearTimeout(timer);
    }, [graphs, selectedSentiment, selectedKeywordsFilters, selectedCommunityFilter, showTopicModelling]);
    

    useEffect(() => {
        if (showTopicModelling  && graphs !== null) {
            setShowCommunityFilter(true);
        }else{
            setNoTweetsForTheseFilters(false);
        }
    }, [showTopicModelling])

    useEffect(() => {
        if (communityNames !== null) {
            let selectedKeywordsTemp = selectedKeywordsFilters in communityNames ? selectedKeywordsFilters : keywords[0]
            let communityNamesForKey = communityNames?.[selectedKeywordsTemp] || {};
            let communities = Object.keys(communityNamesForKey)
            .filter((dictionaryKey) => 
                !!graphs?.[selectedKeywordsTemp]?.[selectedSentiment]?.[dictionaryKey] 
            ).map((dictionaryKey) => {
                return {
                    "key": dictionaryKey,
                    "value": dictionaryKey,
                    "text": communityNamesForKey[dictionaryKey] || dictionaryKey
                }
            })
            communities.unshift({
                key: "All Communities",
                value: "All Communities",
                text: "All Communities"
            });

            setDropCommunityFilter(communities)
            setSelectedCommunityFilter("All Communities")
            setShowCommunityFilter(true)
        } else {
            setShowCommunityFilter(false)
            console.log("CHANGING setFocusOnTopCommunities NB 3", focusOnTopCommunities)
            setFocusOnTopCommunities(false)
        }
    }, [communityNames, selectedKeywordsFilters, graphs]);


    // Post query to API for TopicModelling visualisation
    const getVisualisation = async () => {
        let nbTopicsInt = 0
        if (nbTopics !== "") {
            nbTopicsInt = parseInt(nbTopics)
        }

        if (prevNbTopics !== nbTopicsInt || prevFocusOnTopCommunities !== focusOnTopCommunities || (nbTopicsInt === 0 && claim === "")) {
            generateTopicModelling(communityNames)
        } else {
            let info_for_api = {
                "figures": graphs,
                "claim": claim,
                "dataSource": input_info["dataSource"],
            }
            console.log("--> UPDATING TOPIC MODELLING: input", info_for_api)

            authFetch('/api/add_claim_topic_modelling', {
                method: 'POST',
                headers: {'Content-Type': 'application/json', 'Accept-Encoding': 'gzip'},
                body: JSON.stringify({'data': info_for_api}),
                timeout: 30000,

            }).then(response => {
                console.log("THIS IS THE RESPONSE")
                console.log(response)
                if (response.status === 401) {
                    window.open('/login')
                }
                response = response.json()
                if (response && response.data) {
                    let data_resp = response.data
                    console.log("--> UPDATING TOPIC MODELLING: response", data_resp)
                    setGraphs(data_resp["new_figures"])
                    setShowTopicModelling(true)
                    setLoading(false)
                    setDisableGeneralQuery(false)
                    // setDisableSNAGraphQueries(false)
                } else {
                    console.log("--> UPDATING TOPIC MODELLING: responses didnt work")
                    setLoading(false)
                    setDisableGeneralQuery(false)
                    // setDisableSNAGraphQueries(false)
                }
            }).catch((error) => {
                if (error?.response?.status === 401) {
                    window.open('/login')
                } else {
                    alert("--> UPDATING TOPIC MODELLING: Something went wrong, please try again.")
                }
            });
            setDisableGeneralQuery(false)
            // setDisableSNAGraphQueries(false)
        }


    }

    // Function to render message about volume matching query
    const renderVolumeMessage = () => {
        if (hits[selectedKeywordsFilters] !== undefined) {
            if (hits[selectedKeywordsFilters] > 100000) {
                return !noTweetsForTheseFilters?(
                    <div className="CappingWarningDisplay">
                        <p className="CappingWarning">
                            <b>{hits[selectedKeywordsFilters].toLocaleString()}</b> {datasetOrigin === "Tweets" ? "tweets" : "comments"} were found in total. To
                            enable the topic discovery to run in reasonable time, only <b>100K</b> randomly sampled 
                            {datasetOrigin === "Tweets" ? " tweets" : " comments"} will be used.
                        </p>
                    </div>
                ):<div></div>
            } else {
                return !noTweetsForTheseFilters?(
                    <div className="CappingWarningDisplay">
                        <p className="CappingWarning">
                            <b>{hits[selectedKeywordsFilters].toLocaleString()}</b> {datasetOrigin === "Tweets" ? " tweets" : " comments"} were found.
                        </p>
                    </div>
                ):<div></div>
            }
        }
    }

    // Function to display either the topic modelling Bokeh scatter plot, or an error message if the tweet volume for the
    // given filters is zero
    const renderTopicModVis = () => {
        if (noTweetsForTheseFilters) {
            return (
                <div className="CappingWarningDisplay">
                    <div className="ErrorMessage">
                        <p> There are no {datasetOrigin === "Tweets" ? "tweets" : 'comments'} for this {selectedKeywordsFilters ==='All' ? 'search' : 'keyword'}{selectedSentiment && selectedSentiment !== 'All Sentiments' ? ' and sentiments' :''}.</p>
                    </div>
                </div>
            )
        } else {
            return (
                <div className={showTopicModelling ? 'TopicModellingVis' : 'hidden'}>
                    <div id="topic_mod" className="bk-root"></div>
                </div>
            )
        }
    }

    const renderTopicsPerCommunity = () => {
        if (showTopicsPerCommunityGraph) {
            return (
                    <TopicsPerCommunity
                        hits={hits}
                        input_info={input_info}
                        keywords={keywords}
                        showAsPercentage={showAsPercentage}
                        setShowAsPercentage={setShowAsPercentage}
                        topicsPerCommunityGraph={topicsPerCommunityGraph}
                        nbTopics={nbTopics}
                    />
            )
        }
    }

    const renderCommunityFilter = () => {
        if (showCommunityFilter) {
            return (
                <div className="DropDownMaps">
                    <div className="SubTitleWithPopup">
                        <h3 className="DropDownTitle">Community</h3>
                        <Popup
                            content="This filter only appears once the Social Network Analysis below has been generated and allows filtering per community."
                            trigger={<div className='InfoIcon'><Icon name='question circle' size="small"/></div>}
                        />
                    </div>
                    <div className="DropDownMenu">
                        <Dropdown
                            label='Community'
                            fluid
                            selection
                            options={dropCommunityFilter}
                            text={dropCommunityFilter.text}
                            floating
                            labeled={true}
                            icon={null}
                            value={selectedCommunityFilter}
                            onChange={(e, {value}) => setSelectedCommunityFilter(value)}
                            closeOnChange={true}
                            name='filtersTypeDropdown'
                            id='filtersTypeDropdown'
                        ></Dropdown>
                    </div>
                </div>
            )
        }
    }

    // Render code for the TopicModelling component
    return (
        <div className="TopicModellingVisualisation">
            <div className="MainTitleWithPopup">
                <h2 style={{marginRight: "5px"}}>Topic Discovery</h2>
                <Popup
                    content="Clicking 'Generate' in this component will display the tweets in the current query in 'semantic space': i.e. tweets that are semantically similar are located close to each other. The number of results is capped at 100,000 (tweets are randomly sample if the volume exceeds this threshold). Once a visualisation is generated, hovering over a datapoint will display the tweet. Clicking on a datapoint will open the tweet on Twitter in a new tab."
                    trigger={<div className='InfoIcon'><Icon name='question circle' size="small"/></div>}
                />
            </div>
            <div className="ClusterGenerate">
                <div className="SubTitleWithPopup">
                    <h3 style={{marginRight: "5px"}}>Nb topics</h3>
                    <Popup
                        content="Specifying a number of topics greater than zero before generating will enable the clustering the tweets into this given number of topics, visually signified with different colors. You can then see a wordcloud of each topic using the 'Wordcloud' component above by selecting 'Topics' under the 'Field' filter. "
                        trigger={<div className='InfoIcon'><Icon name='question circle' size="small"/></div>}
                    />
                </div>
                <Input
                    placeholder="optional"
                    type="number"
                    min="0"
                    step="1"
                    // ref={nbTopicsRef}
                    value={nbTopics}

                    onChange={(e, {value}) => {
                        if (value === '' || isNaN(value)) {
                            setNbTopics(0);
                        }else{
                            setNbTopics(parseInt(value));
                        }
                        //setInput({ ...input_info, "nbTopics": value ===""? "":parseInt(value)})
                    }
                    }
                    className="NbTopicsInput"
                />

                <div className="SubTitleWithPopup">
                    <h3 style={{marginRight: "5px"}}>Claim</h3>
                    <Popup
                        content="Specifying a claim will flag up the location (shown as a large black dot) of tweets similar to the claim in the visualisation. "
                        trigger={<div className='InfoIcon'><Icon name='question circle' size="small"/></div>}
                    />
                </div>
                <Input
                    placeholder="optional"
                    type="text"
                    value={claim}
                    onChange={(e, {value}) => {
                        setClaim(value);
                        //setInput({ ...input_info, "claim": value})
                    }
                    }

                    className="ClaimInput"
                />

                <div className={showCommunityFilter ? "SubTitleWithPopup" : "hidden"}>
                    <Checkbox
                        toggle={true}
                        label="Main communities only"
                        //value={focusOnTopCommunities.toString()}
                        checked={focusOnTopCommunities}
                        onChange={() => setFocusOnTopCommunities(!focusOnTopCommunities)}
                    ></Checkbox>
                    <Popup
                        content="Use the 'Main communities only' to focus only on the top communities in the graph. Please re-generate the graphs after changing its state."
                        trigger={<div className='InfoIcon'><Icon name='question circle' size="small"/></div>}
                    />
                </div>

                <div className={savedReportDate !== ''? "hidden" : "ButtonNormal"}>
                    <Button
                        onClick={() => {
                            setDisableGeneralQuery(true)
                            // setDisableSNAGraphQueries(true)
                            setLoading(true)
                            setInput({...input_info, "claim": claim, "nbTopics": nbTopics})
                            getVisualisation()
                        }}
                        disabled={disableTopicModellingQueries}
                        loading={loading}
                        style={{marginLeft: 15}}
                    >Generate</Button>
                </div>

            </div>
            <div className={showTopicModelling ? 'DropDownGroup' : 'hidden'}>
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
                <div className="DropDownMaps">
                    <div className="SubTitleWithPopup">
                        <h3 style={{marginRight: "5px"}}>Sentiment</h3>
                        <Popup
                            content="Once the visualisation is generated, use the Tweet's sentiment filter to filter the results shown by sentiment."
                            trigger={<div className='InfoIcon'><Icon name='question circle' size="small"/></div>}
                        />
                    </div>
                    <div className="DropDownMenu">
                        <Dropdown
                            label='tokensFilter'
                            fluid
                            selection
                            disabled={sentimentDisable}
                            options={dropSelectedSentiments}
                            text={dropSelectedSentiments.text}
                            floating
                            labeled={true}
                            className='source'
                            icon={null}
                            value={selectedSentiment}
                            onChange={(e, {value}) => setSelectedSentiment(value)}
                            closeOnChange={true}
                            name='tokensFiltersTypeDropdown'
                            id='tokensFiltersTypeDropdown'
                        ></Dropdown>
                    </div>
                </div>
                {renderCommunityFilter()}
                <div className={savedReportDate !== ''? "hidden" : "ButtonNormal"}>
                    <Button
                        onClick={() => setTopicRenamingVisible(true)}
                        disabled={!showTopicModelling || loading || disableTopicModellingQueries}
                    >Rename topics</Button>
                </div>
            </div>
            {renderVolumeMessage()}
            {renderTopicModVis()}
            {renderTopicsPerCommunity()}
        </div>
    );
};