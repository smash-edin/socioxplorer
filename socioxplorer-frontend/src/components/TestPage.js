import { useState, useEffect } from 'react';
import { InputHeader } from './Input';
import { VolumesGraph } from './VolumesGraph';
import { SentimentGraph } from "./SentimentGraph"
import { LanguagesGraph } from "./LanguagesGraph"
import { MapGraph } from './MapGraph';
import { WordcloudGraph } from './WordcloudGraph';
import { TopContent } from "./TopContent";
import { TopicModelling } from "./TopicModelling";
import { Sticky } from "semantic-ui-react";
import 'semantic-ui-css/semantic.min.css'

import '../App.css';
import SNATrafficGraph from './SNATrafficGraph';
import SNAGraph from './SNAGraph';
import { CommunitiesContent } from './CommunitiesContent';
import { authFetch } from '../auth';

const queryParameters = new URLSearchParams(window.location.search)
const parameters = queryParameters.get("report")
let response = null
let consumed = false
let data_set = null
let random_seed = null

// Generating report from info stored in URL
if (parameters !== null && response === null) {
  console.log("Inside TestPage with parameters")
  data_set = JSON.parse(atob(parameters))
  console.log(data_set)

  random_seed = data_set.random_seed
  response = authFetch('/api/search', {
    method: 'POST',
    header: {'Content-Type': 'application/json',
    },
    crossorigin: true,
    body: JSON.stringify(data_set)
  }).then(response => {
    var res = response;
    console.log("response --> : ", res) 
    return res;
  });
}

// TestPage component, which is the parent component containing and overseeing every input and report components and
// the links between them
const TestPage = () => {
  const emptyData = {
    "show_report": false,
    "hits": 0,
    "report": {}
  }

  // useState hooks storing variables to be passed between children components
  const [data, setData] = useState(emptyData)
  const [inputInfo, setInputInfo] = useState(data_set)
  const [topicWords, setTopicWords] = useState(null)
  const [disableGeneralQuery, setDisableGeneralQuery] = useState(false)
  const [disableTopicModellingQueries, setDisableTopicModellingQueries] = useState(false)
  const [disableSNAGraphQueries, setDisableSNAGraphQueries] = useState(false)
  const [showSNAGraph, setShowSNAGraph] = useState(false)
  const [statesTable, setStatesTable] = useState(null);
  const [sNATemporGraphData, setSNATemporGraphData] = useState(null);
  
  
  const [showSummary, setShowSummary] = useState(false)
  const [nbHits, setNbHits] = useState(null)
  const [keywordsList, setKeywordsList] = useState(null)

  // Setting useState variables to cached info if response is not null (i.e. generated from cache)
  if (response !== null && consumed === false) {
    if (response.ok) {
      response.json().then((data_resp => {
        //let keywords = Object.keys(data_resp.report)
        let keywords = data_resp.keywords
        if (keywords.length === 2) {
          keywords = keywords.filter(function (key) { return key !== 'All';});
        }
        data_set["keywords"] = keywords
        console.log("data_set --> : ", data_set)
        console.log("data_resp --> : ", data_resp)
        setData(data_resp);
        setInputInfo(data_set);
        setKeywordsList(keywords)
        setNbHits(Object.fromEntries(Object.keys(data_resp.report).map(key => [key, data_resp.report[key].count])));
        // setTopicWords(keywords.split(","));
        consumed = true;
        //window.history.pushState({}, document.title, "/test");
      }))}
  }

  // Function to display or hide the summary of the current query when scrolling over the page
  const listenToScroll = () => {
    let heightToHideFrom = 600;
    const winScroll = document.body.scrollTop ||
      document.documentElement.scrollTop;

    if (winScroll > heightToHideFrom) {
      setShowSummary(true);
    } else {
      setShowSummary(false);
    }
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
      console.log("THIS IS THE INPUT INFO", inputInfo)
      let keywordsSub = inputInfo["keywords"].filter(function (key) { return key !== 'All';})
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
    if (data.show_report) {
      if (data.hits > 0) {
        return (
          <div>
            <Sticky className={showSummary? 'StickySummary' : 'EmptySummaryContainer'}>
              {renderSummary()}
            </Sticky>
          <div className="PageBody">
            <VolumesGraph data={data.report} keywords={keywordsList} inputInfo={inputInfo}/>
            <SentimentGraph data={data.report} keywords={keywordsList} inputInfo={inputInfo}/>
            <LanguagesGraph data={data.report} keywords={keywordsList} inputInfo={inputInfo}/>
            <MapGraph data={data.report} keywords={keywordsList} inputInfo={inputInfo}/>
            <TopContent data={data.report} keywords={keywordsList} inputInfo={inputInfo}/>
            <WordcloudGraph data={data.report} keywords={keywordsList} topics={topicWords} inputInfo={inputInfo}/>
            <TopicModelling
              hits={nbHits}
              input_info={inputInfo}
              keywords={keywordsList}
              setTopicWords={setTopicWords}
              setDisableGeneralQuery={setDisableGeneralQuery}
              disableTopicModellingQueries={disableTopicModellingQueries}
            />
            <SNAGraph 
              input_info={inputInfo}
              keywords={keywordsList}
              setDisableGeneralQuery={setDisableGeneralQuery}
              disableSNAGraphQueries={disableSNAGraphQueries}
              dataSource={data.dataSource}
              operator={data.operator}
              source_text={data.source_text}
              showSNAGraph={showSNAGraph}
              setShowSNAGraph={setShowSNAGraph}
              setStatesTable={setStatesTable}
              setSNATemporGraphData={setSNATemporGraphData}
            />
            <SNATrafficGraph
              //data={data.report}
              sNATemporGraphData={sNATemporGraphData}
              keywords={keywordsList}
              showSNAGraph={showSNAGraph}
            />
            <CommunitiesContent
              statesTable = {statesTable}
              keywords={keywordsList}
              showSNAGraph = {showSNAGraph}
            />

            </div>
          </div>
        )
      } else {
        return (
          <div className="PageBody">
            <div className="ErrorMessage">
              <p>No {datasetOrigin === "Tweets" ? "tweets" : 'comments'} found for these criteria.</p>
            </div>
          </div>
        )
      }
    }
  }

  // Render code for the TestPage component
  return (
    <div className="App">
      <InputHeader
        inputInfo={inputInfo}
        setData={setData}
        setInput={setInputInfo}
        setNbHits={setNbHits}
        setKeywordsList={setKeywordsList}
        setDisableTopicModellingQueries={setDisableTopicModellingQueries}
        setDisableSNAGraphQueries={setDisableSNAGraphQueries}
        disableGeneralQuery={disableGeneralQuery}
      />
      {renderReport()}
    </div>
  );
}

export default TestPage;


