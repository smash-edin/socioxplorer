import {Button, Checkbox, Dropdown, Icon, Popup} from "semantic-ui-react";
import React, {useEffect, useState} from "react";
import { authFetch } from "../auth";
import SentimentGraph from "./SentimentGraph";

// TopicModelling component used to display scatter plot of tweets based on 2D embeddings, to cluster tweets and to
// find location of tweets matching a given claim
export const TopicsPerCommunity = ({hits, input_info, keywords, showAsPercentage, setShowAsPercentage, topicsPerCommunityGraph, nbTopics}) => {

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
        setShowAsPercentage(false)
    }, [hits, input_info, keywords])

    // useEffect hook to remove existing TopicModelling scatter plot upon the generation of a new report
    useEffect(() => {
        var existingTopicsPerCom = document.getElementById('topic_per_community');
        if (existingTopicsPerCom) {
            existingTopicsPerCom.innerHTML = '';
        }
        setShowAsPercentage(false)
        if (!keywords.includes(selectedKeywordsFilters)) {
            setSelectedKeywordsFilters(keywords[0]);
        }
    }, [hits, keywords]);


    useEffect(() => {
        const timer = setTimeout(() => {
            const existingTopicsPerCom = document.getElementById('topic_per_community');
            if (existingTopicsPerCom) {
                existingTopicsPerCom.innerHTML = ''; // Clear previous content
            }
    
            if (topicsPerCommunityGraph != null) {
                const topicsPerComData = topicsPerCommunityGraph[selectedKeywordsFilters]?.[selectedSentiment];
                const parsedTopicsPerComData =
                    typeof topicsPerComData === 'string' ? JSON.parse(topicsPerComData) : topicsPerComData;
    
                if (parsedTopicsPerComData) {
                    try {
                        // Dynamically select data based on `showAsPercentage`
                        const embedData = JSON.parse(
                            showAsPercentage
                                ? parsedTopicsPerComData["proportions"]
                                : parsedTopicsPerComData["counts"]
                        );
    
                        // Embed the new plot
                        window.Bokeh.embed.embed_item(embedData, 'topic_per_community');
                    } catch (error) {
                        console.error('--> TOPICS PER COMMUNITY: Error embedding Bokeh item:', error);
                    }
                }
            }
        }, 400); // Delay execution to debounce state changes
    
        return () => {
            clearTimeout(timer); // Cleanup the timer
            const existingTopicsPerCom = document.getElementById('topic_per_community');
            if (existingTopicsPerCom) {
                existingTopicsPerCom.innerHTML = ''; // Ensure the element is cleared on dependency change
            }
        };
    }, [showAsPercentage, topicsPerCommunityGraph, selectedKeywordsFilters, selectedSentiment]);
    
    // useEffect hook to update the topic modelling scatter plot upon a change in the graph data or the keywords or
    // sentiment filters
    useEffect(() => {
        const timer = setTimeout(() => {
            const existingTopicsPerCom = document.getElementById('topic_per_community');
            if (existingTopicsPerCom) {
                existingTopicsPerCom.innerHTML = '';
            }
    
            if (topicsPerCommunityGraph) {
                const topicsPerComData = topicsPerCommunityGraph[selectedKeywordsFilters]?.[selectedSentiment];
                const parsedTopicsPerComData = typeof topicsPerComData === 'string' ? JSON.parse(topicsPerComData) : topicsPerComData;
    
                if (parsedTopicsPerComData) {
                    try {
                        const dataToEmbed = showAsPercentage
                            ? parsedTopicsPerComData["proportions"]
                            : parsedTopicsPerComData["counts"];
                        window.Bokeh.embed.embed_item(JSON.parse(dataToEmbed), 'topic_per_community');
                    } catch (error) {
                        console.error('--> TOPICS PER COMMUNITY: Error embedding Bokeh item:', error);
                    }
                }
            }
        }, 25); // Adjust the delay as needed
    
        return () => clearTimeout(timer); // Cleanup on dependency change
    }, [topicsPerCommunityGraph, selectedSentiment, selectedKeywordsFilters, showAsPercentage]);
    

    // Render code for the TopicModelling component
    if ( nbTopics !== ""){
    return (
        <div className="TopicModellingVisualisation">
            <div className="MainTitleWithPopup">
                <h2 style={{marginRight: "5px"}}>Topics per community</h2>
                <Popup
                    content="This component allows the user to visualise the prevalence of different topics in the posts published by each of the main communitoies identified using the Social Network Analysis."
                    trigger={<div className='InfoIcon'><Icon name='question circle' size="small"/></div>}
                />
            </div>
            <div className='DropDownGroup'>
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
                            content="Once the visualisation is generated, use the sentiment filter to filter the results shown by sentiment."
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
                <div className="SubTitleWithPopup">
                    <Checkbox
                        toggle={true}
                        label="Percentage"
                        value={showAsPercentage.toString()}
                        onChange={() => setShowAsPercentage(!showAsPercentage)}
                    ></Checkbox>
                    <Popup
                        content="Use the 'Percentage' toggle to display the results as percentages per day instead of counts. "
                        trigger={<div className='InfoIcon'><Icon name='question circle' size="small"/></div>}
                    />
                </div>
            </div>
            <div className='TopicModellingVis'>
                <div id="topic_per_community" className="bk-root"></div>
            </div>
        </div>
    );}
};
export default TopicsPerCommunity;