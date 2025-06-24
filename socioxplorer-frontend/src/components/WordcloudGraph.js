import {Dropdown, Checkbox, Icon, Popup} from "semantic-ui-react";
import {useEffect, useState} from "react";
import ReactWordcloud from "react-wordcloud";
import { set } from "date-fns";


// WordcloudGraph component used to display wordcloud of tweets, user descriptions, hashtags, emojis and topics (after
// using the topic modelling feature)
export const WordcloudGraph = ({data, keywords, topics, inputInfo, communityWords, communityNames, datasetOrigin, topicNames}) => {

    const prefixMapping = {
        "hashtags": "#",
        "processedDescTokens": "\@",
        "communities": "\@",
        'processedTokens': "",
        'emojis': "",
        'topics': "",
    }

    // Callback that enables the creation of a new report in a new page when clicking on one of the keywords
    const callbacks = {
        onWordClick: word => {
            const page_path = window.location.pathname + "?report="
            const relKeyword = selectedKeywords === "All" ? keywords.filter(function (key) {
                return key !== 'All';
            }).join(",") : selectedKeywords
            const relSentiment = sentimentSearchMapping[selectedSentiment]
            const generate_report = window.confirm("A new report will be generated with the following filters:" +
                "\n Keywords: " + relKeyword + "," + prefixMapping[selectedSourceField] + word.text +
                "\n Dataset: " + inputInfo["source_text"] +
                "\n Operator: " + inputInfo["operator"] +
                (inputInfo["date_start"] + " to " + inputInfo["date_end"] !== " to " ? "\t Dates :" + inputInfo["date_start"] + " to " + inputInfo["date_end"] : "") +
                "\n Sentiment: " + relSentiment +
                "\n Language: " + inputInfo["language"] +
                "\n Location of " + (inputInfo["location_type"] === 'author' ? 'users' : datasetOrigin) + ": " + inputInfo["location"] +
                "\n\n Do you want to continue?");
            if (generate_report !== false && generate_report !== null) {
                window.open(page_path + encodeURIComponent(
                    JSON.stringify({
                        "keywords": relKeyword + "," + prefixMapping[selectedSourceField] + word.text, //word.text,
                        "dataSource": inputInfo["dataSource"],
                        "source_text": inputInfo["source_text"],
                        "operator": inputInfo["operator"],
                        "limit": 1000,
                        "date_start": inputInfo["date_start"],
                        "date_end": inputInfo["date_end"],
                        "language": inputInfo["language"],
                        "sentiment": relSentiment,
                        "location": inputInfo["location"],
                        "location_type": inputInfo["location_type"],
                    })),
                    "_blank")
            }
            ;
        }
    }

    // Mapping between field value and display name of that field
    const mapValuesToNames = {
        'processedDescTokens': 'Description',
        'processedTokens': datasetOrigin === 'Comment' ? 'Comment' : 'Tweet',
        'hashtags': 'Hashtags',
        'emojis': 'Emojis',
        'topics': 'Topics',
        'communities': 'Communities'
    }

    const baseDropSourceFieldTweets = [
        {
            key: datasetOrigin === 'Comment' ? 'Comment' : 'Tweet',
            text: datasetOrigin === 'Comment' ? 'Comment' : 'Tweet',
            value: 'processedTokens',
        },
        {key: 'Hashtags', text: 'Hashtags', value: 'hashtags',},
        {key: 'User descriptions', text: 'User descriptions', value: 'processedDescTokens',},
        {key: 'Emojis', text: 'Emojis', value: 'emojis',}
    ]
    const baseDropSourceFieldReplies = [
        {
            key: datasetOrigin === 'Comment' ? 'Comment' : 'Tweet',
            text: datasetOrigin === 'Comment' ? 'Comment' : 'Tweet',
            value: 'processedTokens',
        },
        {key: 'Hashtags', text: 'Hashtags', value: 'hashtags',},
        {key: 'Emojis', text: 'Emojis', value: 'emojis',}
    ]

    // Dropdown menu options: source field
    const [dropSourceField, setDropSourceField] = useState(datasetOrigin === 'Tweets' ? baseDropSourceFieldTweets : baseDropSourceFieldReplies)

    // Dropdown menu options: topic (populated only if topic modelling was executed in TopicModelling component)
    const [dropTopic, setDropTopic] = useState(null)
    const [dropCommunities, setDropCommunities] = useState(null)

    const [allKeywordsLabel, setAllKeywordsLabel] = useState(inputInfo["operator"] === "AND" ? "All keywords" : "Any keyword")
    const [removeStopWords, setRemoveStopWords] = useState(false)

    useEffect(() => {
        setAllKeywordsLabel(inputInfo["operator"] === "AND" ? "All keywords" : "Any keyword")
    }, [inputInfo]);

    // Dropdown menu options: keyword
    const [dropKeywords, setDropKeywords] = useState(keywords.map((dictionaryKey) => {
        return {
            "key": dictionaryKey,
            "value": dictionaryKey,
            "text": dictionaryKey === "All" ? allKeywordsLabel : dictionaryKey[0].toUpperCase() + dictionaryKey.slice(1)
        }
    }));

    const sentimentSearchMapping = {
        "All Sentiments": "All",
        "Negative": 'Negative',
        "Positive": 'Positive',
        "Neutral": 'Neutral',
        "Positive_Negative": "Positive",
        "Negative_Positive": "Negative",
        "OtherLanguages": "Other Languages",
        "NonText": "None Text",
    }

    const sentimentMapping = {
        "All Sentiments": "All Sentiments",
        "Negative": 'Most common terms in negative ' + datasetOrigin.toLowerCase(),
        "Positive": 'Most common terms in positive ' + datasetOrigin.toLowerCase(),
        "Neutral": 'Most common terms in neutral ' + datasetOrigin.toLowerCase(),
        "Positive_Negative": "Most positive terms",
        "Negative_Positive": "Most negative terms",
        "OtherLanguages": "Other Languages",
        "NonText": "None Text",
    }

    const getSentimentLabels = (labels) => {
        return labels.map((dictionaryKey) => {
            return {
                "key": dictionaryKey,
                "value": dictionaryKey,
                "text": sentimentMapping[dictionaryKey],
            }
        });
    };

    // Dropdown menu options: sentiment
    const [dropSentiments, setDropSentiments] = useState(getSentimentLabels(Object.keys(data[keywords[0]]["processedTokens"])))

    const [selectedTopic, setSelectedTopic] = useState(null)
    const [selectedCommunity, setSelectedCommunity] = useState(null)
    const [selectedKeywords, setSelectedKeywords] = useState(null);

    // Variables storing filter values and visualisation data
    const [selectedSourceField, setSelectedSourceField] = useState(null);
    const [selectedSentiment, setSelectedSentiment] = useState(inputInfo["sentiment"] === "All" ? "All Sentiments" : inputInfo["sentiment"]);
    const [sentimentDisable, setSentimentDisable] = useState(false)
    const [wordcloudFigureConfig, setWordcloudFigureConfig] = useState({});

    // Display options for wordcloud graph
    let options = {
        enableTooltip: true,
        deterministic: true,
        fontFamily: "impact",
        fontSizes: [10, 100],
        fontStyle: "normal",
        fontWeight: "normal",
        padding: 5,
        rotations: 0,
        rotationAngles: [0, 0],
        scale: "linear",
        enableOptimizations: true,
        spiral: "rectangular",//"rectangular" // "archimedean"
        transitionDuration: 0
    };

    const size = [800, 400];

    useEffect(() => {
        setDropSourceField(datasetOrigin === 'Tweets' ? baseDropSourceFieldTweets : baseDropSourceFieldReplies)
    },[datasetOrigin])

    useEffect(() => {
        let sourceField = dropSourceField.find(option => option.value === selectedSourceField);
        setSelectedSourceField(sourceField ? sourceField.value : dropSourceField[0].value);

    }, [dropSourceField])

    // useEffect hook to update the options in the sentiment dropdown upon a change in the selected source field
    useEffect(() => {
        setDropSentiments(getSentimentLabels(Object.keys(data[keywords[0]]["processedTokens"])))
    }, [selectedSourceField])

    // useEffect hook to re-initialise filters upon a change in the data passed by the parent component (i.e. TestPage)
    useEffect(() => {
        let selectedSourceFieldTemp = selectedSourceField !== null && dropSourceField !== null ? dropSourceField.some(item => item.value === selectedSourceField) ? selectedSourceField : "processedTokens" : "processedTokens"
        setSelectedSourceField(selectedSourceFieldTemp)

        let selectedKeywordsTemp = selectedKeywords in data ? selectedKeywords : keywords[0]
        setSelectedKeywords(selectedKeywordsTemp)
        setSelectedTopic(null)

        let dropSentimentsTemp = ""
        try {
            dropSentimentsTemp = getSentimentLabels(Object.keys(data[keywords[0]][selectedSourceFieldTemp]))
        } catch (e) {
            selectedSourceFieldTemp = "processedTokens"
            dropSentimentsTemp = getSentimentLabels(Object.keys(data[keywords[0]][selectedSourceFieldTemp]))
        }
        let sentimentTemp = selectedSentiment !== null ? dropSentimentsTemp.some(item => item.value === selectedSentiment) ? selectedSentiment : inputInfo["sentiment"] === "All" ? "All Sentiments" : inputInfo["sentiment"] : inputInfo["sentiment"] === "All" ? "All Sentiments" : inputInfo["sentiment"]
        setSentimentDisable(inputInfo["sentiment"] !== "All")

        setSelectedSentiment(sentimentTemp)
        setDropSentiments(dropSentimentsTemp)

        let title = mapValuesToNames[selectedSourceFieldTemp] + " wordcloud"
        let key1 = "text"
        let key2 = "value"
        let sentiments = true
        let items = data[selectedKeywordsTemp][removeStopWords? selectedSourceFieldTemp === 'processedTokens' ? 'processedTokensStopped' : selectedSourceFieldTemp === 'processedDescTokens' ? 'processedDescTokensStopped' : selectedSourceFieldTemp: selectedSourceFieldTemp] 
        console.log("WORDCLOUD ITEMS", items)
        setWordcloudFigureConfig({
            'data': items[sentimentTemp].slice(0, 75),
            'title': title,
            'key1': key1,
            'key2': key2,
            'sentiments': sentiments
        })

    }, [data, keywords, removeStopWords, topics, communityWords, inputInfo])

    useEffect(() => {
        let localDropValues = datasetOrigin === 'Tweets' ? baseDropSourceFieldTweets : baseDropSourceFieldReplies
        if (topics != null && topics[selectedKeywords] !== undefined && topics[selectedKeywords][selectedSentiment] !== undefined) {
            localDropValues = localDropValues.concat([{key: 'Topics', text: 'Topics', value: 'topics'}])
            let firstKeyword = dropKeywords[0].value
            if (topics[firstKeyword][selectedSentiment] != null) {
                let topicValues = Object.keys(topics[firstKeyword][selectedSentiment]).map(
                    (dictionaryKey) => {
                        return {"key": dictionaryKey, "value": dictionaryKey, "text": topicNames[dictionaryKey]}
                    }
                )
                setDropTopic(topicValues)
                setSelectedTopic("0")
            } else {
                setDropTopic(null)
                setSelectedTopic(null)
            }
        }
        
        if ((communityNames?.[selectedKeywords] || communityNames?.[keywords[0] !== undefined])  && communityWords && dropKeywords?.[0]  !== undefined) {
            let firstKeyword = dropKeywords[0].value;
            if (communityNames?.[firstKeyword]) {
                // Add "Community user descriptions" if datasetOrigin is 'Tweets'
                if (datasetOrigin === 'Tweets') {
                    localDropValues = localDropValues.concat([{
                        key: "Community user descriptions",
                        text: "Community user descriptions",
                        value: 'communities'
                    }]);
                }

                // Determine selectedKeywordsTemp
                let selectedKeywordsTemp = selectedKeywords in communityWords ? selectedKeywords : keywords[0]
                // if the selected source is communities, we need to update the selectedKeywords to be a valid key
                if (selectedSourceField == 'communities'){
                    setSelectedKeywords(selectedKeywordsTemp);
                }

                // Prepare communitiesValues
                let communityNamesForKey = communityNames?.[selectedKeywordsTemp] || {};
                let communityWordsForKey = communityWords?.[selectedKeywordsTemp] || {};
                let communitiesValues = Object.keys(communityNamesForKey)
                    .filter((dictionaryKey) => 
                        communityWordsForKey[
                            communityNamesForKey[dictionaryKey] || dictionaryKey
                        ] !== undefined // Ensure non-empty communityWords
                    )
                    .map((dictionaryKey) => ({
                        key: dictionaryKey,
                        value: dictionaryKey,
                        text: communityNamesForKey[dictionaryKey] || dictionaryKey
                    }));

                // Update state
                setDropCommunities(communitiesValues);
                setSelectedCommunity(communitiesValues[0]?.value || null);
            } else {
                // Reset dropCommunities and selectedCommunity if no valid firstKeyword
                setDropCommunities(null);
                setSelectedCommunity(null);
            }
        }
        setDropSourceField(localDropValues)
    }, [topics, communityWords, topicNames, communityNames, selectedKeywords]);


    // useEffect hook to update wordcloud data to display upon a change in the selected filters or the data passed by the
    // parent component (i.e. TestPage)
    useEffect(() => {
        let title = mapValuesToNames[selectedSourceField] + " wordcloud"
        let key1 = "text"
        let key2 = "value"
        let sentiments = true
        let wordcloudData = null

        const formatKeyword = (dictionaryKey) => ({
            "key": dictionaryKey,
            "value": dictionaryKey,
            "text": dictionaryKey === "All" ? allKeywordsLabel : dictionaryKey[0].toUpperCase() + dictionaryKey.slice(1)
        });
        
        const dropKeywords_tmp = keywords
            .filter((dictionaryKey) => 
                selectedSourceField === "communities" 
                    ? Object.keys(communityWords || {}).includes(dictionaryKey) 
                    : true // Allow all keys if not filtering
            )
            .map(formatKeyword);
        //alert(Object.keys(dropKeywords_tmp))
        setDropKeywords(dropKeywords_tmp);

        if (selectedSourceField === "topics" && (topics !== null && topics !== undefined)) {
            if (topics[selectedKeywords] !== null && topics[selectedKeywords] !== undefined) {
                if (topics[selectedKeywords][selectedSentiment] !== null && topics[selectedKeywords][selectedSentiment] !== undefined) {
                    if (topics[selectedKeywords][selectedSentiment][selectedTopic] !== null && topics[selectedKeywords][selectedSentiment][selectedTopic] !== undefined) {
                        wordcloudData = topics[selectedKeywords][selectedSentiment][selectedTopic].slice(0, 75)
                    }
                }
            }
            setWordcloudFigureConfig({
                'data': wordcloudData,
                'title': title,
                'key1': key1,
                'key2': key2,
                'sentiments': sentiments
            })
        } else if (selectedSourceField === "communities") {
                
                
                console.log("WORDCLOUD ITEMS: 1 COMMUNITY NAMES", dropKeywords_tmp)

                if (communityWords?.[selectedKeywords] !== undefined) {
                    let value_ = communityWords[selectedKeywords][communityNames[selectedKeywords][selectedCommunity] || selectedCommunity]
                    if ( value_ !== null && value_ !== undefined && value_.length > 0) {
                        wordcloudData = value_.slice(0, 75)
                    }
                }else{
                    setSelectedKeywords(keywords[0])
                    let value_ = communityWords[keywords[0]][communityNames[keywords[0]][selectedCommunity] || selectedCommunity]
                    if ( value_ !== null && value_ !== undefined && value_.length > 0) {
                        wordcloudData = value_.slice(0, 75)
                    }
                }
            setWordcloudFigureConfig({
                'data': wordcloudData,
                'title': title,
                'key1': key1,
                'key2': key2,
                'sentiments': sentiments
            })
        } else if (selectedKeywords !== null) {
            let items = data[selectedKeywords][removeStopWords? selectedSourceField  === 'processedTokens' ? 'processedTokensStopped' : selectedSourceField === 'processedDescTokens' ? 'processedDescTokensStopped' : selectedSourceField: selectedSourceField]
            if (items === null || items === undefined) {
                let selectedFeature = removeStopWords === true? "processedTokensStopped" : "processedTokens"
                setSelectedSourceField(selectedFeature)
                items = data[selectedKeywords][selectedFeature]
            }

            setWordcloudFigureConfig({
                'data': items[selectedSentiment].slice(0, 75),
                'title': title,
                'key1': key1,
                'key2': key2,
                'sentiments': sentiments
            })
        }

    }, [selectedKeywords, selectedSentiment, removeStopWords, selectedSourceField, selectedTopic, selectedCommunity]);

    // Function to render the topic dropdown menu
    const renderTopicSelection = () => {
        if (selectedSourceField === "topics") {
            return (
                <div className="DropDownMaps">
                    <h3 className="DropDownTitle">Topic</h3>
                    <div className="DropDownMenu">
                        <Dropdown
                            label='TokensKeywordsFilter'
                            fluid
                            selection
                            options={dropTopic}
                            text={dropTopic.text}
                            floating
                            labeled={true}
                            className='source'
                            icon={null}
                            value={selectedTopic}
                            onChange={(e, {value}) => setSelectedTopic(value)}
                            closeOnChange={true}
                            name='tokensFiltersTypeDropdown'
                            id='tokensFiltersTypeDropdown'
                        ></Dropdown>
                    </div>
                </div>
            )
        }
    }

    const renderCommunitySelection = () => {
        if (selectedSourceField === "communities") {
            return (
                <div className="DropDownMaps">
                    <h3 className="DropDownTitle">Community</h3>
                    <div className="DropDownMenu">
                        <Dropdown
                            label='TokensKeywordsFilter'
                            fluid
                            selection
                            options={dropCommunities}
                            text={dropCommunities.text}
                            floating
                            labeled={true}
                            className='source'
                            icon={null}
                            value={selectedCommunity}
                            onChange={(e, {value}) => setSelectedCommunity(value)}
                            closeOnChange={true}
                            name='tokensFiltersTypeDropdown'
                            id='tokensFiltersTypeDropdown'
                        ></Dropdown>
                    </div>
                </div>
            )
        }
    }

    const renderSentimentSelection = () => {
        if (selectedSourceField !== "communities") {
            return (
                <div className="DropDownMaps">
                    <div className="SubTitleWithPopup">
                        <h3 className="DropDownTitle">{datasetOrigin}'
                            sentiment</h3>
                        <Popup
                            content="Choose the sentiment of interest here. The option 'Most common terms in negative/positive/neutral' sentences will display words that are very frequent for that sentiment, but not necessarily characteristic of it (e.g. if the word 'football' is generally very frequent, it might appear in the wordcloud of all sentiments). The option 'Most negative/positive terms', on the other hand, will display words that are characteristic of the sentiment: i.e. frequent in this sentiment but infrequent for other sentiments. "
                            trigger={<div className='InfoIcon'><Icon name='question circle' size="small"/></div>}
                        />
                    </div>
                    <div className="DropDownMenu">
                        <Dropdown
                            disabled={sentimentDisable}
                            label='tokensFilter'
                            fluid
                            selection
                            options={dropSentiments}
                            text={dropSentiments.text}
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
            )
        }
    }

    // Function to render the entire group of dropdown menus for filters
    const renderDropDowns = () => {
        return (
            <div className="DropDownGroup">
                <div className="DropDownMaps">
                    <div className="SubTitleWithPopup">
                        <h3 className="DropDownTitle">Field</h3>
                        <Popup
                            content="This menu defines which field is used to generate the wordcloud. 'Tweets' means the content of tweets in the current query is used. 'User descriptions' means the descriptions of users who have authored at least one tweet in the current query are used. 'Hashtags' means the hashtags of the tweets are used. If 'Emojis' is selected, the emojis contained in the tweets are used. If the Topic Discovery was generated with a number of topics greater than 0, the 'Topics' option will appear here: the text of tweets that compose each topic is then used. If the Social Network Analysis was generated, the 'Community user descriptions' option will appear here: the description of users that compose each community is then used. "
                            trigger={<div className='InfoIcon'><Icon name='question circle' size="small"/></div>}
                        />
                    </div>
                    <div>
                    <div className='DropDownMenu'>
                        <Dropdown
                            label='TokensKeywordsFilter'
                            fluid
                            selection
                            options={dropSourceField}
                            text={dropSourceField.text}
                            floating
                            labeled={true}
                            icon={null}
                            value={selectedSourceField}
                            onChange={(e, {value}) => setSelectedSourceField(value)}
                            closeOnChange={true}
                            name='tokensFiltersTypeDropdown'
                            id='tokensFiltersTypeDropdown'
                        ></Dropdown>
                    </div>
                    <br></br>
                    <div className="SubTitleWithPopup" hidden = {selectedSourceField!=='processedTokens' & selectedSourceField!=='processedDescTokens'}>
                        <Checkbox 
                            toggle={true}
                            label="Remove stopwords"
                            value={removeStopWords.toString()}
                            checked={removeStopWords}
                            onChange={() => setRemoveStopWords(!removeStopWords)}
                        ></Checkbox>
                        <Popup
                            content="Use the 'Remove stopwords' toggle to clean the wordcloud from the stopwords."
                            trigger={<div className='InfoIcon'><Icon name='question circle' size="small"/></div>}
                        />
                    </div>
                    </div>
                </div>
                <div className="DropDownMaps">
                    <div className="SubTitleWithPopup">
                        <h3 className="DropDownTitle">Keyword</h3>
                        <Popup
                            content="If more than 1 keyword was provided, you can use the 'Keyword' filter to display results for each keyword independently, as well as for all keywords together ('All keywords')."
                            trigger={<div className='InfoIcon'><Icon name='question circle' size="small"/></div>}
                        />
                    </div>
                    <div className="DropDownMenu">
                        <Dropdown
                            label='TokensKeywordsFilter'
                            fluid
                            selection
                            options={dropKeywords}
                            text={dropKeywords.text}
                            floating
                            labeled={true}
                            className='source'
                            icon={null}
                            value={selectedKeywords}
                            onChange={(e, {value}) => setSelectedKeywords(value)}
                            closeOnChange={true}
                            name='tokensFiltersTypeDropdown'
                            id='tokensFiltersTypeDropdown'
                        ></Dropdown>
                    </div>
                    
                </div>
                {renderSentimentSelection()}
                {renderTopicSelection()}
                {renderCommunitySelection()}
            </div>
            
        )
    }

    // Function to render the wordcloud visualisation
    const renderWordcloud = () => {
        if (wordcloudFigureConfig["data"] != null) {
            let maxValue = Math.max(...wordcloudFigureConfig["data"].map(item => item.value));
            let numItems = wordcloudFigureConfig["data"].filter(item => item.value === maxValue).length
            if (numItems > 10) {
                options = {
                    enableTooltip: true,
                    deterministic: true,
                    fontFamily: "impact",
                    fontSizes: [Math.round(100 / Math.log10(numItems)) < 10 ? Math.round(100 / Math.log10(numItems)) : 10, Math.round(100 / Math.log10(numItems))],
                    fontStyle: "normal",
                    fontWeight: "normal",
                    padding: 5,
                    rotations: 0,
                    rotationAngles: [0, 0],
                    scale: "linear",
                    enableOptimizations: true,
                    spiral: "rectangular",//"rectangular" // "archimedean"
                    transitionDuration: 0
                };
            }
            return (
                <div className="WordCloudContainer">
                    <ReactWordcloud
                        words={wordcloudFigureConfig['data']}
                        callbacks={selectedSourceField !== "emojis" ? callbacks : callbacks}
                        options={options}
                        size={size}
                    />
                </div>
            )
        } else {
            return (
                <div className="ErrorMessage">
                    <p>There are no documents for this keyword, {selectedSourceField === 'communities'? 'community' : 'sentiment'} and topic.</p>
                </div>
            )
        }
    }

    // Render code for WordcloudGraph component
    return (
        <>
            <div className="Visualisation">
                <div className="MainTitleWithPopup">
                    <h2 style={{marginRight: "5px"}}>{wordcloudFigureConfig['title']}</h2>
                    <Popup
                        content="This component shows the most frequent words in the data. You can click on any word or emoji to generate a new report (in a new tab) for the subset of the current data that also includes this word/emoji."
                        trigger={<div className='InfoIcon'><Icon name='question circle' size="small"/></div>}
                    />
                </div>
                {renderDropDowns()}
                {renderWordcloud()}
            </div>
        </>
    );
};