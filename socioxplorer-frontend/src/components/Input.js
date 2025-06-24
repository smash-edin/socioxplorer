import React, { useState, useEffect } from 'react';
import {Dropdown, Button, Form, Input, Popup, Icon} from "semantic-ui-react";
import SemanticDatepicker from 'react-semantic-ui-datepickers';
import { csv } from 'd3'

import moment from "moment/moment";
import { parseISO } from 'date-fns';
import languageData from '../.data/languages.csv';
import countriesData from '../.data/countries_codes_english.csv';
import datasetData from '../.data/datasetOptions.csv';

import { authFetch } from '../auth';

const limit = 500;

// InputHeader component used to allow user to provide query parameters
export const InputHeader = ({inputInfo,
                              isSavedReport,
                              disableGeneralQuery,
                              savingButton,
                              setSavingButton,
                              loadingStatus,
                              setLoadingStatus,
                              setShowTopicModelling,
                              setSelectedCommunityFilter,
                              fetchData,
                              selectedNetworkInteraction,
                              mainReportData,
                              communityGraphs,
                              statesTable,
                              sNATrafficGraphData,
                              sNAcolors,
                              communityWords,
                              communityNames,
                              topicGraphs,
                              topicNames,
                              topicWords,
                              topicsPerCommunityGraph,
                              nbCommunities,
                              claim,
                              nbHits,
                              focusOnTopCommunities,
                              prevFocusOnTopCommunities,
                              }) => {

  // useState variable to store the choices of language
  const [languageOptions, setLanguageOptions] = useState([]);

  // useState variable to store the choices of country
  const [countryOptions, setCountryOptions] = useState([]);
  const [datasetOptions, setDatasetOptions] = useState([]);

  useEffect(() => {
    try {
      csv(languageData).then(response => {
        setLanguageOptions([{"language": "All"}].concat(response).concat([{"language": "Other"}]).map(row => {
          return {"key": row['language'], "text": row['language'], "value": row['language']}
        }));
      });
      csv(countriesData).then(response => {
        setCountryOptions([{"name": "All"}].concat(response).concat([{"name": "Other"}]).map(row => {
          return {"key": row['name'], "text": row['name'], "value": row['name']}
        }));
      });

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
      setDataSource(inputInfo === null ? datasetOptions!== null && datasetOptions.length > 0 ? datasetOptions[0].value: null : inputInfo["dataSource"]);
      setKeywords(inputInfo === null ? "" : inputInfo["keywords"]);
      setDateStart(inputInfo === null ? null: (String(parseISO(inputInfo["date_start"])) === "Invalid Date") ? null: parseISO(inputInfo["date_start"]));
      setDateEnd(inputInfo === null ? null: (String(parseISO(inputInfo["date_end"])) === "Invalid Date") ? null: parseISO(inputInfo["date_end"]));
      setDataSentiment(inputInfo === null ? "All" : inputInfo["sentiment"]);
      setDataLanguage(inputInfo === null ? "All" : inputInfo["language"]);
      setDataCountry(inputInfo === null ? "All" : inputInfo["location"]);
      setDataCountryType(inputInfo === null ? "author" : inputInfo["location_type"]);
    }
  }, [datasetOptions, inputInfo]);

  const sentimentOptions = [
    { key: 'All', text: 'All', value: 'All' },
    { key: 'Positive', text: 'Positive', value: 'Positive' },
    { key: 'Neutral', text: 'Neutral', value: 'Neutral' },
    { key: 'Negative', text: 'Negative', value: 'Negative' },
  ]

  // useState variable to store the choice of dataset (i.e. Solr core)
  const [dataSource, setDataSource] = useState(null);

  // useState variable to store the choice of sentiment
  const [dataSentiment, setDataSentiment] = useState(inputInfo === null ? "All" : inputInfo["sentiment"]);

  // useState variable to store the choice of language
  const [dataLanguage, setDataLanguage] = useState(inputInfo === null ? "All" : inputInfo["language"]);

  // useState variable to store the choice of country
  const [dataCountry, setDataCountry] = useState(inputInfo === null ? "All" : inputInfo["location"]);
  const [dataCountryType, setDataCountryType] = useState(inputInfo === null ? "author" : inputInfo["location_type"]);

  // Variables storing relevant information for keyword filters
  const [keywords, setKeywords] = useState(inputInfo === null ? "" : inputInfo["keywords"]);
  const [operator, setOperator] = useState(inputInfo === null ? "OR" : inputInfo["operator"]);

  // Variables storing relevant information for date range filters
  const [dateStart, setDateStart] = useState(inputInfo === null ? null: (String(parseISO(inputInfo["date_start"])) === "Invalid Date") ? null: parseISO(inputInfo["date_start"]));
  const [dateEnd, setDateEnd] = useState(inputInfo === null ? null: (String(parseISO(inputInfo["date_end"])) === "Invalid Date") ? null: parseISO(inputInfo["date_end"]));
  const [dateStartVal, setDateStartVal] = useState(true);
  const [dateEndVal, setDateEndVal] = useState(true);

  // Variables storing relevant information for quick fill buttons for date range filters
  const today =  moment().startOf('day').toDate();
  const yesterday = moment().subtract(1, 'days').startOf('day').toDate();
  const lastWeek = moment().subtract(7, 'days').startOf('day').toDate();
  const lastMonth = moment().subtract(1, 'months').startOf('day').toDate();
  const lastYear = moment().subtract(1, 'years').startOf('day').toDate();
  const [dateRangeType, setDateRangeType] = useState("custom");

  // Loading state, used while waiting for query response from Solr
  // const [loading, setLoading] = useState(false)

  // Function to generate random seed
  const random_seed = () => {
    return Math.floor(Math.random()
      * (9999));
  };

  
  const saveReport = async () => {
    let dataPackage = {
    'inputInfo': inputInfo,
    'mainReportData': mainReportData,
    'communityGraphs':communityGraphs,
    'statesTable': statesTable,
    'sNATrafficGraphData': sNATrafficGraphData,
    'sNAcolors': sNAcolors,
    'selectedNetworkInteraction': selectedNetworkInteraction,
    'communityWords': communityWords,
    'communityNames': communityNames,
    'topicGraphs': topicGraphs,
    'topicNames': topicNames,
    'topicWords': topicWords,
    'topicsPerCommunityGraph': topicsPerCommunityGraph,
    'nbCommunities': nbCommunities,
    'claim': claim,
    'count': nbHits,
    'focusOnTopCommunities': focusOnTopCommunities,
    'prevFocusOnTopCommunities': prevFocusOnTopCommunities
    }

    const report_name = prompt("Please enter a name for the report", "my_report")
    if (report_name !== "" && report_name !== null)
    {
      if (inputInfo.keywords.filter !== null && inputInfo.keywords.filter !== undefined) {
        try {
          const updatedKeywords = inputInfo.keywords.filter(keyword => keyword !== "All").join(',');
          const inputInfoTemp = {...inputInfo, keywords: updatedKeywords, 
            selectedNetworkInteraction: selectedNetworkInteraction, //TODO ADD COMMUNITY NAMES?
            savedReport: true
          };
          const reportInputEncoded = encodeURIComponent(JSON.stringify(
              inputInfoTemp));
          console.log("SAVING REPORT: reportInputEncoded:", reportInputEncoded);
          
          
          authFetch('/api/save_report', {
            method: 'POST',
            body: JSON.stringify({'data': {'token': reportInputEncoded, 'name': report_name, 'data': dataPackage}}),
            header: {'Content-Type': 'application/json'},
            timeout: 5000
          }).then((response) => {
            if (response.json.status === 200) {
              const user_msg = response?.data?.Message
              if (user_msg !== undefined && user_msg !== null && user_msg !== "") {
                alert(user_msg)
              }
            }
          }).catch((error) => {
            if (error.response && error.response.status !== 401) {
              console.error('--> SAVING REPORT: Error:', error);
            }
          });
        } catch (e) {
          console.error('--> SAVING REPORT: Error:', e);
        }
      }
    }
  }

  // Async function that posts the query to the API to get the necessary info to generate the report
  const submitFilters = async () => {
    setSavingButton(true)
    // Load random seed for query if it is saved, otherwise generate a new random seed
    const randomSeed = (inputInfo === null) ? random_seed() : (inputInfo["random_seed"] === null) ? random_seed() : inputInfo["random_seed"];
    // Convert dateStart to a string
    let dateStartStr = "" 
    if (dateStart !== null) {
      const yearStart = dateStart.getFullYear().toString();
      const monthStart = (dateStart.getMonth() + 1).toString().padStart(2, '0');
      const dayStart = dateStart.getDate().toString().padStart(2, '0');
      dateStartStr = yearStart + "-" + monthStart + "-" + dayStart
    }
    // Convert dateEnd to a string
    let dateEndStr = ""
    if (dateEnd !== null) {
      const yearEnd = dateEnd.getFullYear().toString();
      const monthEnd = (dateEnd.getMonth() + 1).toString().padStart(2, '0');
      const dayEnd = dateEnd.getDate().toString().padStart(2, '0');
      dateEndStr = yearEnd + "-" + monthEnd + "-" + dayEnd
    }

    const input_info = {
      "keywords": keywords,
      "date_start": dateStartStr,
      "date_end": dateEndStr,
      "limit": limit,
      "dataSource": dataSource,
      "source_text": datasetOptions.find(x => x.value === dataSource).text,
      "operator": operator,
      "random_seed": randomSeed,
      "language": dataLanguage,
      "sentiment": dataSentiment,
      "location": dataCountry,
      "location_type": dataCountryType
    }

    fetchData(input_info)
  }

  useEffect(() => {
    setSavingButton(!isSavedReport);
  }, [keywords, dataSource, operator, dateStart, dateEnd, dataSentiment, dataLanguage, dataCountry, dataCountryType]);
  // useEffect hook to update date range quick fill buttons and dateStart validity variable (to enable submitting)
  // upon a change in the value of dateStart
  useEffect(() => {
    if (dateStart === null) {
      setDateStartVal(true)
      setDateRangeType('custom')
    } else {
      const startDateObj = moment(dateStart, "YYYY-MM-DD", true)
      setDateStartVal(startDateObj.isValid())
      const dateStart_str = dateStart.toString()
      if (dateStart_str !== yesterday.toString() && dateStart_str !== lastWeek.toString() && dateStart_str !== lastMonth.toString()  && dateStart_str !== lastYear.toString()) {
        setDateRangeType('custom')
      }
    }
  }, [dateStart])

  // useEffect hook to update date range quick fill buttons and dateEnd validity variable (to enable submitting)
  // upon a change in the value of dateEnd
  useEffect(() => {
    if (dateEnd === null) {
      setDateEndVal(true)
      setDateRangeType('custom')
    } else {
      const endDateObj = moment(dateEnd, "YYYY-MM-DD", true)
      setDateEndVal(endDateObj.isValid())
      if (dateEnd.toString() !== today.toString()) {
        setDateRangeType('custom')
      }
    }
  }, [dateEnd])

  // Render code for the InputHeader component
  return(
    <header className="Input">
      <div className = "PageTitle">
        <h1>SocioXplorer Dashboard</h1>
      </div>

      <div className = "InputFields">
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

        <div className="TitleWithPopup">
          <h2 style={{marginRight: "5px"}}>Keywords </h2>
          <Popup
            content="Leave the keywords field empty to get unfiltered results. Use 'AND' between keywords to obtain data contain both keywords, and 'OR' to obtain data containing either keyword. The scope of the operator can be controlled using parentheses: e.g. '(keyword1 OR keyword2) AND keyword3'. If '#' is used at the start of the keyword (e.g. '#myhashtag'), the keyword filter will be applied to the data's hashtag field. If '@' is used at the start of the keyword (e.g. '@journalist'), the keyword filter will be applied to author's personal description and screen name (i.e. filtering by user)."
            trigger={<div className='InfoIcon'><Icon name='question circle' size="small"/></div>}
          />
        </div>
        <Input
          placeholder = "Enter keywords, separated by commas (optional)..."
          type="text"
          value={keywords}
          onChange={(e, { value }) => setKeywords(value)}
          className = "KeywordsInput"
        />

        <div className="OperatorButtonGroup">
          <Form.Radio
            label='Any keyword'
            value='OR'
            checked={operator === 'OR'}
            onChange={(e, { value }) => setOperator(value)}
            className="OperatorChoice"
          />
          <Form.Radio
            label='All keywords'
            value='AND'
            checked={operator === 'AND'}
            onChange={(e, { value }) => setOperator(value)}
            className="OperatorChoice"
          />
        </div>

        <div className='SelectionGroup'>
          <div className='SourceGroup'>
            <div className="SubTitleWithPopup">
              <h2 style={{marginRight: "5px"}}>Language </h2>
              <Popup
                content="By default, the report will show results for all languages. Note that the languages contained in this list might not be present in the data."
                trigger={<div className='InfoIcon'><Icon name='question circle' size="small"/></div>}
              />
            </div>
            <Form.Field>
              <Dropdown
                label='Language'
                fluid
                search
                selection
                options={languageOptions}
                text={languageOptions.text}
                floating
                labeled={true}
                icon={null}
                value={dataLanguage}
                onChange={(e, { value }) => setDataLanguage(value)}
                style={{width: '150px'}}
                name='sentiment'
                id='sentiment'
              ></Dropdown>
            </Form.Field>
          </div>

          <div className='SourceGroup'>
            <div className="SubTitleWithPopup">
              <h2 style={{marginRight: "5px"}}>Sentiment </h2>
              <Popup
                content="By default, the report will show results for all sentiments. "
                trigger={<div className='InfoIcon'><Icon name='question circle' size="small"/></div>}
              />
            </div>
            <Form.Field>
              <Dropdown
                label='Sentiment'
                fluid
                selection
                options={sentimentOptions}
                text={sentimentOptions.text}
                floating
                labeled={true}
                icon={null}
                value={dataSentiment}
                onChange={(e, { value }) => setDataSentiment(value)}
                style={{width: '150px'}}
                name='sentiment'
                id='sentiment'
              ></Dropdown>
            </Form.Field>
          </div>
        </div>

        <div className="TitleWithPopup">
          <h2 style={{marginRight: "5px"}}>Country </h2>
          <Popup
            content="By default, the report will show results for all countries. The author's country is inferred from the location authors declare as part of their profile. The tweet's country corresponds to the location given when the author publishes that tweet. Note that selecting the option 'All' will also return results without a declared location, which usually compose the majority of the data."
            trigger={<div className='InfoIcon'><Icon name='question circle' size="small"/></div>}
          />
        </div>
        <Form.Field>
          <Dropdown
            label='Language'
            fluid
            search
            selection
            options={countryOptions}
            text={countryOptions.text}
            floating
            labeled={true}
            icon={null}
            value={dataCountry}
            onChange={(e, { value }) => setDataCountry(value)}
            style={{width: '650px'}}
            name='country'
            id='country'
          ></Dropdown>
        </Form.Field>

        <div className="OperatorButtonGroup">
          <Form.Radio
            label="Author's country"
            value='author'
            checked={dataCountryType === 'author'}
            onChange={(e, { value }) => setDataCountryType(value)}
          />
          <Form.Radio
            label="Tweet's country"
            value='tweet'
            checked={dataCountryType === 'tweet'}
            onChange={(e, { value }) => setDataCountryType(value)}
          />
        </div>

        <div className="TitleWithPopup">
          <h2 style={{marginRight: "5px"}}>Dates </h2>
          <Popup
            content="Leave the date fields empty to get results for the entire time period. You can also specify  only a start date or an end date. Clicking on 'Last day', 'Last week', 'Last month' or 'Last year' will compute the date range automatically based on the current day."
            trigger={<div className='InfoIcon'><Icon name='question circle' size="small"/></div>}
          />
        </div>
        <div className="ButtonGroup">
          <Form.Radio
            label='Custom'
            value='custom'
            checked={dateRangeType === 'custom'}
            onChange={(e, { value }) => setDateRangeType(value)}
            style={{color: '#ffffff'}}
          />
          <Form.Radio
            label='Last day'
            value='lastday'
            checked={dateRangeType === 'lastday'}
            onChange={(e, { value }) => {
              setDateRangeType(value)
              setDateStart(yesterday)
              setDateEnd(today)
            }}
          />
          <Form.Radio
            label='Last week'
            value='lastweek'
            checked={dateRangeType === 'lastweek'}
            onChange={(e, { value }) => {
              setDateRangeType(value)
              setDateStart(lastWeek)
              setDateEnd(today)
            }}
          />
          <Form.Radio
            label='Last month'
            value='lastmonth'
            checked={dateRangeType === 'lastmonth'}
            onChange={(e, { value }) => {
              setDateRangeType(value)
              setDateStart(lastMonth)
              setDateEnd(today)
            }}
          />
          <Form.Radio
            label='Last year'
            value='lastyear'
            checked={dateRangeType === 'lastyear'}
            onChange={(e, { value }) => {
              setDateRangeType(value)
              setDateStart(lastYear)
              setDateEnd(today)
            }}
          />
        </div>
        <div className="DatePickerGroup">
          <p>From:</p>
          <SemanticDatepicker
            error={(dateStart !== null && !dateStartVal)}
            value={dateStart}
            onChange={(e, { value }) => {
              setDateStart(value)
            }}
            format="YYYY-MM-DD"
            className="DatePicker"
            placeholder='YYYY-MM-DD (optional)'
          />
          <p>To:</p>
          <SemanticDatepicker
            error={(dateEnd !== null && !dateEndVal)}
            value={dateEnd}
            onChange={(e, { value }) => {
              setDateEnd(value)
            }}
            format="YYYY-MM-DD"
            className="DatePicker"
            placeholder='YYYY-MM-DD (optional)'
          />
        </div>
        <div className="SubmitButton">
          <Button
            loading={loadingStatus}
            disabled={
              (!dateStartVal  || !dateEndVal || (dataSource === "") || disableGeneralQuery)
            }
            onClick = {() => {
              // setDisableTopicModellingQueries(true)
              // setDisableSNAGraphQueries(true)
              setLoadingStatus(true)
              setShowTopicModelling(false)
              setSelectedCommunityFilter('All Communities')
              submitFilters()
            }}
          >Show results</Button>

          {
            
            console.log("TTT !SAVING BUTTON:", !savingButton)
          }
          {
            console.log("TTT LOADING disableGeneralQuery:", !disableGeneralQuery  )
          }
          {
            console.log("TTT IS SAVED REPORT:", isSavedReport)
          }
          
          {(savingButton && !loadingStatus) && (
          <Button
            onClick = {saveReport}
            disabled= {(!savingButton || disableGeneralQuery)}
          >Save Report</Button>
              )}
        </div>
      </div>
    </header>
  );
}
