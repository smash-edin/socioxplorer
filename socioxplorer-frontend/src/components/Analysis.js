import React, {useState, useEffect} from "react"
import {InputHeader} from './Input';
import {VolumesGraph} from './VolumesGraph';
import {SentimentGraph} from "./SentimentGraph"
import {LanguagesGraph} from "./LanguagesGraph"
import {MapGraph} from './MapGraph';
import {WordcloudGraph} from './WordcloudGraph';
import {TopContent} from "./TopContent";
import {TopicModelling} from "./TopicModelling";
import {Button, Sticky} from "semantic-ui-react";
import 'semantic-ui-css/semantic.min.css'
import '../App.css';
import SNAGraph from './SNAGraph';
import {CommunitiesContent} from "./CommunitiesContent";
import {SNATrafficGraph} from "./SNATrafficGraph";
import TopicRenaming from "./TopicRenaming";
import { authFetch } from "../auth";
import { set } from "date-fns";
import { useLocation } from "react-router-dom";
import CommunityRenaming from "./CommunityRenaming";


const ANALYSIS_URL = '/analysis';
const LOGIN_PAGE = '/login';

let consumed = false;
const Analysis = ({logged}) => {
    const emptyData = {
        "show_report": false,
        "hits": 0,
        "datasetOrigin": "",
        "report": {}
    }

    useEffect(() => {
        const handleBackButton = () => {
            // Reload the page when the user presses the back button
            window.location.reload();
        };

        // Add event listener for the popstate event (back button)
        window.addEventListener('popstate', handleBackButton);

        // Clean up the event listener when the component unmounts
        return () => {
            window.removeEventListener('popstate', handleBackButton);
        };
    }, []);

    const [savingButton, setSavingButton] = useState(false);
    const [data, setData] = useState(emptyData)
    const [inputInfo, setInputInfo] = useState(null)
    const [loadingStatus, setLoadingStatus] = useState(false)
    const [topicWords, setTopicWords] = useState(null)
    const [communityWords, setCommunityWords] = useState(null)
    const [disableQueries, setDisableQueries] = useState(false)
    const [showSNAGraph, setShowSNAGraph] = useState(false)
    const [SNAcolors, setSNAcolors] = useState(null)
    const [sNATrafficGraphData, setSNATrafficGraphData] = useState(null);
    const [statesTable, setStatesTable] = useState(null);
    const [selectedKeywordsFiltersSNATrafficGraph, setSelectedKeywordsFiltersSNATrafficGraph] = useState(null);
    const [showSummary, setShowSummary] = useState(false)
    const [nbHits, setNbHits] = useState(null)
    const [keywordsList, setKeywordsList] = useState(null)
    const [savedReportDate, setSavedReportDate] = useState('')
    const [topicRenamingVisible, setTopicRenamingVisible] = useState(false)
    const [topicNames, setTopicNames] = useState(null)
    const [topicGraphs, setTopicGraphs] = useState(null);
    const [topicsPerCommunityGraph, setTopicsPerCommunityGraph] = useState(null)
    const [showTopicModelling, setShowTopicModelling] = useState(false)
    const [prevNbTopics, setPrevNbTopics] = useState(null);
    const [showAsPercentage, setShowAsPercentage] = useState(false)
    const [loadingTopicModelling, setLoadingTopicModelling] = useState(false)
    const [noTweetsForTheseFilters, setNoTweetsForTheseFilters] = useState(false)
    const [focusOnTopCommunities, setFocusOnTopCommunities] = useState(false)
    const [prevFocusOnTopCommunities, setPrevFocusOnTopCommunities] = useState(null);
    const [isSavedReport,setIsSavedReport] = useState(false);
    const [selectedNetworkInteraction, setSelectedNetworkInteraction] = useState(null);
    const [datasetOrigin, setDatasetOrigin] = useState(null);
    const [communityRenamingVisible, setCommunityRenamingVisible] = useState(false)
    const [communityNames, setCommunityNames] = useState(null)
    const [communityGraphs, setCommunityGraphs] = useState(null);
    const [selectedCommunityFilter, setSelectedCommunityFilter] = useState("All Communities");
    const [lastSNAQuery, setLastSNAQuery] = useState(null)
    const [currentSNAKeyword, setCurrentSNAKeyword] = useState(null)

    const [nbTopics, setNbTopics] = useState(10);
    const [claim, setClaim] = useState("");
    
    // Get URL location (from React Router)
    const location = useLocation();

    const [nbCommunities, setNbCommunities] = useState("10");

    useEffect(() => {
        const queryParameters = new URLSearchParams(location.search);
        const reportName = queryParameters.get("reportName");
        const parameters = queryParameters.get("report");
        // Only check parameters if they exist and haven't been consumed
        if (!consumed && parameters) {
            console.log("Client-side navigation detected with parameters.");
            const input_info = JSON.parse(decodeURIComponent(parameters));
            console.log(input_info)
            input_info.reportName = reportName;
            setInputInfo(input_info);
            setSelectedNetworkInteraction(input_info["selectedNetworkInteraction"] || (input_info["datasetOrigin"] === "Tweets" ? "Retweet" : 'Reply'))
            setLoadingStatus(true);
            setCommunityNames(null);
        }
    }, [location]); // Trigger on URL change (React Router)

    useEffect(() => {
        if (inputInfo !== null && !consumed) {
            setCommunityNames(null);
            console.log("Fetching data with inputInfo: ", inputInfo);
            if (inputInfo?.reportName !== null){
                fetchStoredData(inputInfo);
            }else{
                fetchData(inputInfo);
            }
            consumed = true; // Mark data as consumed after fetching
        }
    }, [inputInfo]);

    const fetchStoredData = async (inputInfo) => {
        consumed=true
        if (inputInfo) {
            console.log("input_info: " + inputInfo['reportName']);
            setLoadingStatus(true); // Initiate loading state
            try {
                const response = await authFetch('/api/search', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' }, // Corrected "header" to "headers"
                    body: JSON.stringify({ 'data': inputInfo })
                });
                const jsonData = await response.json();
                if (jsonData) {
                    console.log("Received data:", jsonData);
                    if (jsonData?.error !== undefined && jsonData?.error !== ''){
                        alert("Error1: " + jsonData['error']);
                    }
                    let data_resp = jsonData?.data;
                    console.log("Data response:", data_resp);
                    let keywords = data_resp.keywords;
                    if (keywords.length === 2) {
                        keywords = keywords.filter(key => key !== 'All');
                    }
                    setInputInfo({
                        ...inputInfo,
                        "keywords": keywords
                    });
                    setDatasetOrigin(data_resp?.datasetOrigin)
                    setSelectedNetworkInteraction(data_resp?.report?.selectedNetworkInteraction ||  (data_resp?.datasetOrigin === "Tweets" ? "Retweet" : 'Reply'))
                    setShowSNAGraph(data_resp?.report?.communityGraphs !== null);
                    setCommunityGraphs(data_resp?.report?.communityGraphs)
                    setSNAcolors(data_resp?.report?.sNAcolors)
                    setSNATrafficGraphData(data_resp?.report?.sNATrafficGraphData)
                    setStatesTable(data_resp?.report?.statesTable)
                    setCommunityNames(data_resp?.report?.communityNames)
                    setCommunityWords(data_resp?.report?.communityWords);
                    setSavedReportDate(data_resp?.reportDate || '');
                    setData(data_resp?.report?.mainReportData);
                    setKeywordsList(Object.keys(data_resp?.report?.mainReportData?.report));
                    setNbHits(data_resp?.hits ? data_resp?.hits : Object.fromEntries(Object.keys(data_resp.hits).map(key => [key, data_resp.hits[key].count])));
                    setTopicRenamingVisible(false)
                    setTopicGraphs(data_resp?.report?.topicGraphs)
                    setTopicsPerCommunityGraph(data_resp?.report?.topicsPerCommunityGraph)
                    setShowAsPercentage(false)
                    setTopicWords(data_resp?.report?.topicWords)
                    setTopicNames(data_resp?.report?.topicNames)
                    setNoTweetsForTheseFilters(false)
                    setShowTopicModelling(data_resp?.report?.topicGraphs !== null);
                    setPrevNbTopics(data_resp?.report?.inputInfo?.nbTopics)
                    setNbTopics(data_resp?.report?.inputInfo?.nbTopics)
                    setNbCommunities(data_resp?.report?.inputInfo?.nb_communities)
                    setPrevFocusOnTopCommunities(data_resp?.report?.prevFocusOnTopCommunities)
                    setLoadingTopicModelling(false);
                    setDisableQueries(false);
                    setFocusOnTopCommunities(data_resp?.report?.focusOnTopCommunities)
                    setIsSavedReport(true);
                    setSavingButton(false);
                    renderReport();
                }
            } catch (error) {
                if (error?.status === 401) {
                    window.open('/login');
                }else{
                    //alert("Error: " + error);
                    console.error('Error fetching data:', error);
                    //window.open('/login'); //window.open('/login', '_self'); //we make it open in a new page so no filter will be lost.
                }
            } finally {
                setLoadingStatus(false); // Reset loading state
            }
        }
    };

    const fetchData = async (inputInfo) => {
        consumed=true
        if (inputInfo) {
            console.log("input_info: " + inputInfo['reportName']);
            setLoadingStatus(true); // Initiate loading state
            try {
                const response = await authFetch('/api/search', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' }, // Corrected "header" to "headers"
                    body: JSON.stringify({ 'data': inputInfo })
                });
                const jsonData = await response.json();
                if (jsonData) {
                    console.log("Received data:", jsonData);
                    if (jsonData?.error !== undefined && jsonData?.error !== ''){
                        alert("Error: " + jsonData['error']);
                    }
                    let data_resp = jsonData?.data;
                    let keywords = data_resp.keywords;
                    if (keywords.length === 2) {
                        keywords = keywords.filter(key => key !== 'All');
                    }
                    setInputInfo({
                        ...inputInfo,
                        "keywords": keywords
                    });
                    setDatasetOrigin(data_resp?.datasetOrigin)
                    setSelectedNetworkInteraction(inputInfo["selectedNetworkInteraction"] || (data_resp?.datasetOrigin === "Tweets" ? "Retweet" : 'Reply'))
                    setTopicRenamingVisible(false)
                    setTopicNames(null)
                    setTopicGraphs(null)
                    setSavedReportDate('')
                    setPrevNbTopics(null)
                    setPrevFocusOnTopCommunities(null)
                    setTopicWords(null)
                    setNoTweetsForTheseFilters(false)
                    setShowSNAGraph(false);
                    setCommunityGraphs(null)
                    setSNAcolors(null)
                    setSNATrafficGraphData(null)
                    setStatesTable(null)
                    setCommunityNames(null)
                    setCommunityWords(null)
                    setData(data_resp);
                    setKeywordsList(Object.keys(data_resp.report));
                    setNbHits(Object.fromEntries(Object.keys(data_resp.report).map(key => [key, data_resp.report[key].count])));
                    setIsSavedReport(false);
                    setSavingButton(data_resp !== null);
                    renderReport();
                }
            } catch (error) {
                if (error?.status === 401) { 
                    window.open('/login');
                }else{
                    //alert("Error: " + error);
                    console.error('Error fetching data:', error);
                    //window.open('/login'); //window.open('/login', '_self'); //we make it open in a new page so no filter will be lost.
                }
            } finally {
                setLoadingStatus(false); // Reset loading state
            }
        }
    };


    const generateTopicModelling = async (community_names) => {

        let nbTopicsInt = 0
        if (nbTopics !== "") {
            nbTopicsInt = parseInt(nbTopics)
        }
        let info_for_api = {
            "keywords": inputInfo["keywords"],
            "date_start": inputInfo["date_start"],
            "date_end": inputInfo["date_end"],
            "limit": 100000,
            "dataSource": inputInfo["dataSource"],
            "datasetOrigin": datasetOrigin,
            "operator": inputInfo["operator"],
            "random_seed": inputInfo["random_seed"],
            "nb_topics": nbTopicsInt,
            "claim": claim,
            "language": inputInfo["language"],
            "sentiment": inputInfo["sentiment"],
            "interactionCommunity": selectedNetworkInteraction === "Retweet" ? "retweetCommunity" : "replyCommunity",
            "communities_list": community_names,
            "focusOnMainCommunities": focusOnTopCommunities,
            "location": inputInfo["location"],
            "location_type": inputInfo["location_type"]
        }

        setLoadingTopicModelling(true);
        setShowTopicModelling(false);

        console.log("GENERATING TOPIC MODELLING. Info being sent to backend is:", info_for_api)
        authFetch('/api/topic_modelling', {
            method: 'POST',
            headers: {'Content-Type': 'application/json', 'Accept-Encoding': 'gzip'},
            body: JSON.stringify({'data': info_for_api}),
            timeout: 30000,
        }).then(r => r.json()).then(response => {
            if (response && response.data && response.data.figures) {
                console.log("--> TOPIC MODELLING RESPONSE:", response)
                const figures = response.data.figures;
                setTopicGraphs(figures);
                setTopicsPerCommunityGraph(response.data.topics_per_community)
                setTopicWords(response.data.top_words);
                setTopicNames(response.data.topic_names);
                setPrevNbTopics(info_for_api["nb_topics"])
                setPrevFocusOnTopCommunities(info_for_api["focusOnMainCommunities"])
                setShowTopicModelling(true);
                setLoadingTopicModelling(false);
                setDisableQueries(false)
                // setDisableSNAGraphQueries(false)
            } else {
                console.error("--> TOPIC MODELLING: Invalid response data:", response);
                setTopicWords(null);
                setLoadingTopicModelling(false);
                setNoTweetsForTheseFilters(true);
                setDisableQueries(false)
                // setDisableSNAGraphQueries(false)
            }
        }).catch(error => {
            setDisableQueries(false)
            // setDisableSNAGraphQueries(false)
            console.error("API error:", error);
            if (error?.response?.status === 401) {
                window.open('/login');
            } else {
                alert("Something went wrong, please try again.");
            }
        });
    }



    const updateTopicModelling = async (community_names) => {

        let nbTopicsInt = 0
        if (nbTopics !== "") {
            nbTopicsInt = parseInt(nbTopics)
        }
        let info_for_api = {
            "communities_list": community_names,
            "topic_modelling_figures": topicGraphs,
            "interactionCommunity": selectedNetworkInteraction === "Retweet" ? "retweetCommunity" : "replyCommunity",
            "topic_mapping": topicNames
        }

        setLoadingTopicModelling(true);
        setShowTopicModelling(false);

        console.log("UPDATING TOPIC MODELLING. Info being sent to backend is:", info_for_api)
        authFetch('/api/update_topic_modelling_after_SNA', {
            method: 'POST',
            headers: {'Content-Type': 'application/json', 'Accept-Encoding': 'gzip'},
            body: JSON.stringify({'data': info_for_api}),
            timeout: 30000,
        }).then(r => r.json()).then(response => {
            if (response && response.data && response.data.figures) {
                console.log("--> TOPIC MODELLING UPDATE:", response)
                const figures = response.data.figures;
                setTopicGraphs(figures);
                setTopicsPerCommunityGraph(response.data.topics_per_community)
                setShowTopicModelling(true);
                setLoadingTopicModelling(false);
                setDisableQueries(false)
                // setDisableSNAGraphQueries(false)
            } else {
                console.error("--> TOPIC MODELLING: Invalid response data:", response);
                setLoadingTopicModelling(false);
                setNoTweetsForTheseFilters(true);
                setDisableQueries(false)
                // setDisableSNAGraphQueries(false)
            }
        }).catch(error => {
            setDisableQueries(false)
            // setDisableSNAGraphQueries(false)
            console.error("API error:", error);
            if (error?.response?.status === 401) {
                window.open('/login');
            } else {
                alert("Something went wrong, please try again.");
            }
        });
    }



    // Function to display or hide the summary of the current query when scrolling over the page
    const listenToScroll = () => {
        let heightToHideFrom = 600;
        const winScroll = document.body.scrollTop ||
            document.documentElement.scrollTop;

        setShowSummary(winScroll > heightToHideFrom);
    };

    // useEffect to add even listener to scroll upon first loading the page
    useEffect(() => {
        window.addEventListener("scroll", listenToScroll);
        return () =>
            window.removeEventListener("scroll", listenToScroll);
    }, [])


    // Render function for sticky summary (displayed at the top of the page when scrolling down on report)
    const renderSummary = () => {
        if (showSummary) {
            let keywordsSub = Array.isArray(inputInfo?.keywords) 
                ? inputInfo.keywords.filter(key => key !== 'All') 
                : [];
            let keywordsStr = keywordsSub.join(", ")
            return (
                <div className="SummaryContainer">
                    <div className="SummaryItem">
                        <p><b>Dataset</b>: {inputInfo["source_text"]}</p>
                    </div>
                    <div>
                        <p className="SummaryItem"><b>Keywords</b>: {keywordsStr}</p>
                    </div>
                    <div>
                        <p className="SummaryItem"><b>Start date</b>: {inputInfo["date_start"]}</p>
                    </div>
                    <div>
                        <p className="SummaryItem"><b>End date</b>: {inputInfo["date_end"]}</p>
                    </div>
                    <div>
                        <p className="SummaryItem"><b>Language</b>: {inputInfo["language"]}</p>
                    </div>
                    <div>
                        <p className="SummaryItem"><b>Sentiment</b>: {inputInfo["sentiment"]}</p>
                    </div>
                    <div>
                        <p className="SummaryItem"><b>Country</b>: {inputInfo["location"]}</p>
                    </div>
                </div>
            )
        } else {
            return (
                <div className="SummaryContainer"/>
            )
        }
    }

    // Function to render every component in the report
    const renderReport = () => {
        if (data?.show_report) {
            if (data?.hits > 0) {
                console.log("Analysis (renderReport) --> ", data)
                //{ nbHits && nbHits?.selectedKeywordsFilters !== '' ? <h2>{nbHits?.selectedKeywordsFilters} results found.</h2> : <h2></h2>}
                console.log("Analysis (renderReport) nbHits --> ", nbHits)
                console.log("Analysis (renderReport) nbHits --> ", nbHits['All'])
                return (
                    <div>
                        <Sticky className={showSummary ? 'StickySummary' : 'EmptySummaryContainer'}>
                            {renderSummary()}
                        </Sticky>
                        <div className="PageHeader">
                            { savedReportDate !== '' ? <h1>A saved report on {savedReportDate}</h1> : <h1>Analysis</h1>}
                            <h2>
                              {(data?.hits ?? nbHits?.['All']) ? `${data?.hits ?? nbHits?.['All']} results found.` : ''}
                            </h2>
                        </div>
                        <div className="PageBody">
                            <VolumesGraph data={data.report} keywords={keywordsList} inputInfo={inputInfo}/>
                            <SentimentGraph data={data.report} keywords={keywordsList} inputInfo={inputInfo}/>
                            <LanguagesGraph data={data} keywords={keywordsList} inputInfo={inputInfo}
                                            communities={communityNames}/>
                            <MapGraph data={data} keywords={keywordsList} inputInfo={inputInfo}
                                      datasetOrigin={data.datasetOrigin} communityNames={communityNames}/>
                            <TopContent data={data.report} keywords={keywordsList} inputInfo={inputInfo}
                                        datasetOrigin={data.datasetOrigin} communityNames={communityNames}/>
                            <WordcloudGraph
                                data={data.report}
                                keywords={keywordsList}
                                topics={topicWords}
                                inputInfo={inputInfo}
                                communityWords={communityWords}
                                communityNames={communityNames}
                                datasetOrigin={data.datasetOrigin}
                                topicNames={topicNames}
                            />
                            <TopicModelling
                                hits={nbHits}
                                input_info={inputInfo}
                                keywords={keywordsList}
                                topicWords={topicWords}
                                setTopicWords={setTopicWords}
                                setDisableGeneralQuery={setDisableQueries}
                                // setDisableSNAGraphQueries={setDisableSNAGraphQueries}
                                disableTopicModellingQueries={disableQueries}
                                setInput={setInputInfo}
                                setTopicRenamingVisible={setTopicRenamingVisible}
                                // setTopicNames={setTopicNames}
                                graphs={topicGraphs}
                                setGraphs={setTopicGraphs}
                                topicsPerCommunityGraph={topicsPerCommunityGraph}
                                communityNames={communityNames}
                                showTopicModelling={showTopicModelling}
                                setShowTopicModelling={setShowTopicModelling}
                                selectedNetworkInteraction={selectedNetworkInteraction}
                                selectedCommunityFilter={selectedCommunityFilter}
                                setSelectedCommunityFilter={setSelectedCommunityFilter}
                                nbTopics={nbTopics}
                                setNbTopics={setNbTopics}
                                claim={claim}
                                setClaim={setClaim}
                                generateTopicModelling={generateTopicModelling}
                                prevNbTopics={prevNbTopics}
                                loading={loadingTopicModelling}
                                setLoading={setLoadingTopicModelling}
                                noTweetsForTheseFilters={noTweetsForTheseFilters}
                                setNoTweetsForTheseFilters={setNoTweetsForTheseFilters}
                                focusOnTopCommunities={focusOnTopCommunities}
                                setFocusOnTopCommunities={setFocusOnTopCommunities}
                                prevFocusOnTopCommunities={prevFocusOnTopCommunities}
                                showAsPercentage={showAsPercentage}
                                setShowAsPercentage={setShowAsPercentage}
                                isSavedReport={isSavedReport}
                                datasetOrigin={datasetOrigin}
                                savedReportDate={savedReportDate}
                            />
                            <SNAGraph
                                input_info={inputInfo}
                                keywords={keywordsList}
                                setDisableGeneralQuery={setDisableQueries}
                                // setDisableTopicModellingQueries={setDisableTopicModellingQueries}
                                disableSNAGraphQueries={disableQueries}
                                dataSource={data.dataSource}
                                operator={data.operator}
                                source_text={data.source_text}
                                setCommunityWords={setCommunityWords}
                                showSNAGraph={showSNAGraph}
                                setShowSNAGraph={setShowSNAGraph}
                                data={data}
                                setData={setData}
                                topicGraphs={topicGraphs}
                                // setTopicGraphs={setTopicGraphs}
                                setCommunityRenamingVisible={setCommunityRenamingVisible}
                                setCommunityNames={setCommunityNames}
                                setCurrentSNAKeyword={setCurrentSNAKeyword}
                                setLastSNAQuery={setLastSNAQuery}
                                setSNAcolors={setSNAcolors}
                                setSNATrafficGraphData={setSNATrafficGraphData}
                                setStatesTable={setStatesTable}
                                communityGraphs={communityGraphs}
                                setCommunityGraphs={setCommunityGraphs}
                                datasetOrigin={data.datasetOrigin}
                                selectedNetworkInteraction={selectedNetworkInteraction}
                                setSelectedNetworkInteraction={setSelectedNetworkInteraction}
                                updateTopicModelling={updateTopicModelling}
                                nbCommunities={nbCommunities}
                                setNbCommunities={setNbCommunities}
                                savedReportDate={savedReportDate}
                            />
                            {showSNAGraph && (
                                <div>
                                    <SNATrafficGraph
                                        input_info={inputInfo}
                                        keywords={keywordsList}
                                        sNATrafficGraphData={sNATrafficGraphData}
                                        showSNAGraph={showSNAGraph}
                                        SNAcolors={SNAcolors}
                                        datasetOrigin={data.datasetOrigin}
                                        selectedKeywordsFilters= {selectedKeywordsFiltersSNATrafficGraph}
                                        setSelectedKeywordsFilters = {setSelectedKeywordsFiltersSNATrafficGraph}
                                    />
                                    <CommunitiesContent
                                        input_info={inputInfo}
                                        statesTable = {statesTable}
                                        keywords={keywordsList}
                                        showSNAGraph = {showSNAGraph}
                                        communityNames={communityNames}
                                        datasetOrigin={data.datasetOrigin}
                                        selectedKeywordsFiltersSNATrafficGraph= {selectedKeywordsFiltersSNATrafficGraph}
                                    />
                                </div>
                            )}
                        </div>
                    </div>
                )
            } else {
                return (
                    <div className="PageBody">
                        <div className="ErrorMessage">
                            <p>No {datasetOrigin === "Tweets" ? "tweets" : 'comments'} were found for these criteria.</p>
                        </div>
                    </div>
                )
            }
        }
    }
    return (
        <main className="App">
            {
                logged ? (
                    <>
                        <div className="App">
                            <InputHeader
                                inputInfo={inputInfo}
                                isSavedReport={isSavedReport}
                                disableGeneralQuery={disableQueries}
                                savingButton={savingButton}
                                setSavingButton={setSavingButton}
                                loadingStatus={loadingStatus}
                                setLoadingStatus={setLoadingStatus}
                                setShowTopicModelling={setShowTopicModelling}
                                setSelectedCommunityFilter={setSelectedCommunityFilter}
                                fetchData={fetchData}
                                selectedNetworkInteraction={selectedNetworkInteraction}
                                mainReportData={data}
                                communityGraphs={communityGraphs}
                                statesTable={statesTable}
                                sNATrafficGraphData={sNATrafficGraphData}
                                sNAcolors={SNAcolors}
                                communityWords={communityWords}
                                communityNames={communityNames}
                                topicGraphs={topicGraphs}
                                topicNames={topicNames}
                                topicWords={topicWords}
                                topicsPerCommunityGraph={topicsPerCommunityGraph}
                                nbCommunities={nbCommunities}
                                claim={claim}
                                nbHits={nbHits}
                                focusOnTopCommunities={focusOnTopCommunities}
                                prevFocusOnTopCommunities={prevFocusOnTopCommunities}
                            />
                            {renderReport()}
                            <TopicRenaming
                                isVisible={topicRenamingVisible}
                                setVisible={setTopicRenamingVisible}
                                topicNames={topicNames}
                                setTopicNames={setTopicNames}
                                graphs={topicGraphs}
                                setGraphs={setTopicGraphs}
                                topicsPerCommunityGraph={topicsPerCommunityGraph}
                                setTopicsPerCommunityGraph={setTopicsPerCommunityGraph}
                            />

                            <CommunityRenaming
                                isVisible={communityRenamingVisible}
                                setVisible={setCommunityRenamingVisible}
                                communityNames={communityNames}
                                setCommunityNames={setCommunityNames}
                                topicGraphs={topicGraphs}
                                setTopicGraphs={setTopicGraphs}
                                setCommunityGraphs={setCommunityGraphs}
                                lastSNAQuery={lastSNAQuery}
                                currentSNAKeyword={currentSNAKeyword}
                                setStatesTable={setStatesTable}
                                setSNATrafficGraphData={setSNATrafficGraphData}
                                setSNAcolors={setSNAcolors}
                                setCommunityWords={setCommunityWords}
                                data={data}
                                setData={setData}
                                updateTopicModelling={updateTopicModelling}
                                selectedNetworkInteraction={selectedNetworkInteraction}
                            />

                        </div>
                    </>
                ) : (
                    <>
                        <p>
                            {"Logged out!"}
                            <br></br>
                            <a href={{LOGIN_PAGE}}>{"Go to login...!"}</a>
                        </p>
                    </>
                )}


        </main>
    )

}
export default Analysis