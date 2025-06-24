import Plot from "react-plotly.js";
import {Dropdown, Icon, Popup} from "semantic-ui-react";
import {useEffect, useState} from "react";

// MapGraph component used to display the geographic prevalence of data matching the given query
export const MapGraph = ({data, keywords, inputInfo, datasetOrigin, communityNames}) => {

    // Sentiment colormaps
    const sentimentColorScale = {
        'All': [[0, "rgb(235, 235, 235)"], [0.25, "rgb(155, 195, 50)"], [0.5, "rgb(94, 179, 39)"], [0.75, "rgb(67, 136, 33)"], [1, "rgb(33, 74, 12)"]],
        'Positive': [[0, "rgb(235, 235, 235)"], [0.5, "rgb(50, 150, 50)"], [1, "rgb(0, 125, 0)"]],
        'Neutral': [[0, "rgb(235, 235, 235)"], [0.5, "rgb(50, 50, 150)"], [1, "rgb(0, 0, 125)"]],
        'Negative': [[0, "rgb(235, 235, 235)"], [0.5, "rgb(150, 50, 50)"], [1, "rgb(125, 0, 0)"]],
        'Positive_Negative': [[0, "rgb(75, 0, 0)"], [0.25, "rgb(150, 50, 50)"], [0.50, "rgb(235, 235, 235)"], [0.75, "rgb(50, 150, 50)"], [1, "rgb(0, 75, 0)"]],
    }

    // Display to storing continent names mapping
    const continentsScopes = {
        'World': 'world', 'Europe': 'europe', 'Asia': 'asia', 'Africa': 'africa',
        'NorthAmerica': 'north america', 'SouthAmerica': 'south america'
    }

    const titleMapping = {
        "Sentiments": "Sentiment",
        "Languages": "Language",
        "Communities": "Community",
    }

    // Dropdown menu options: continent
    const dropContinent = [
        {key: 'World', text: 'World', value: 'World',},
        {key: 'Europe', text: 'Europe', value: 'Europe',},
        {key: 'Asia', text: 'Asia', value: 'Asia',},
        {key: 'Africa', text: 'Africa', value: 'Africa',},
        {key: 'NorthAmerica', text: 'North America', value: 'NorthAmerica',},
        {key: 'SouthAmerica', text: 'South America', value: 'SouthAmerica',}
    ]

    // Dropdown menu options: filter type
    // const dropSelectedFilterType = [
    //     {key: 'Sentiments', text: 'Sentiments', value: 'Sentiments',},
    //     {key: 'Languages', text: 'Languages', value: 'Languages',},
    //     {key: 'Communities', text: 'Communities', value: 'Communities',},
    // ]

    // Dropdown menu options: count units (users vs tweets)
    const dropSelectedCountType = [
        {key: 'Users', text: 'Users', value: 'Users',},
        {key: 'Tweets', text: 'Tweets', value: 'Tweets',}
    ]

    const sentimentDropValues = [{key: 'All Sentiments', text: 'All Sentiments', value: 'All Sentiments',},
        {key: 'Positive', text: 'Positive', value: 'Positive',},
        {key: 'Neutral', text: 'Neutral', value: 'Neutral',},
        {key: 'Negative', text: 'Negative', value: 'Negative',},
        {key: 'Sentiment ratio', text: 'Sentiment ratio', value: 'Positive_Negative',},
    ]

    // Dropdown menu options: sentiment
    const [dropSentimentFilter, setDropSentimentFilter] = useState(sentimentDropValues);

    const [allKeywordsLabel, setAllKeywordsLabel] = useState(inputInfo["operator"] === "AND" ? "All keywords" : "Any keyword")

    useEffect(() => {
        console.log("USE EFFECT 1")
        setAllKeywordsLabel(inputInfo["operator"] === "AND" ? "All keywords" : "Any keyword")
    }, [inputInfo]);

    // Dropdown menu options: keywords
    const dropKeywordsFilter = keywords.map((dictionaryKey) => {
        return {
            "key": dictionaryKey,
            "value": dictionaryKey,
            "text": dictionaryKey === "All" ? allKeywordsLabel : dictionaryKey[0].toUpperCase() + dictionaryKey.slice(1)
        }
    })

    // Variables storing filter values, figure data and layout options
    const [selectedKeywordFilter, setSelectedKeywordFilter] = useState(keywords[0]);
    const [selectedMapData, setSelectedMapData] = useState(data["report"][selectedKeywordFilter]);
    const [selectedCountType, setSelectedCountType] = useState(inputInfo === null ? "Users" : inputInfo["location_type"] === 'author' ? "Users" : "Tweets");
    const [selectedFilterType, setSelectedFilterType] = useState('Sentiments');
    const [selectedFilterValue, setSelectedFilterValue] = useState(inputInfo["sentiment"] === "All" ? "Positive_Negative" : inputInfo["sentiment"]);
    const [filterDisable, setFilterDisable] = useState(false)
    const [selectedContinent, setSelectedContinent] = useState('World');
    const [mapConfigs, setMapConfigs] = useState({});
    const [dropSelectedFilterType, setDropSelectedFilterType] = useState([
        {key: 'Sentiments', text: 'Sentiments', value: 'Sentiments',},
        {key: 'Languages', text: 'Languages', value: 'Languages',},
    ])

    useEffect(() => {
        if (communityNames !== undefined && communityNames !== null) {
            console.log("USE EFFECT 2 --> branch 1")
            setDropSelectedFilterType([
                {key: 'Sentiments', text: 'Sentiments', value: 'Sentiments',},
                {key: 'Languages', text: 'Languages', value: 'Languages',},
                {key: 'Communities', text: 'Communities', value: 'Communities',},
            ])
        } else {
            console.log("USE EFFECT 2 --> branch 2")
            setDropSelectedFilterType([
                {key: 'Sentiments', text: 'Sentiments', value: 'Sentiments',},
                {key: 'Languages', text: 'Languages', value: 'Languages',},
            ])
        }

    }, [communityNames]);

    const layout = {
        geo: {
            scope: continentsScopes[selectedContinent],
            projection: {
                type: 'robinson',
            }
        },
        modebar: {remove: ['lasso2d', 'select2d', "autoscale"]},
    };

    const tooltipContent = {
        "Languages": "Choose the language of interest here.",
        "Sentiments": "Choose the sentiment of interest here. If the option 'Sentiment ratio' is selected, a country will be shown as positive if the data for this country contains more positive than negative tweets. Inversely, it will be shown as negative if the data contains more negative than positive tweets. The exact formula used to calculate the ratio is: (N(pos) - N(neg)) / (N(pos) + N(neg) + N(neut)), where the function N(sentiment) corresponds to the number of datapoints with this given sentiment.",
        "Communities": "Choose the community of interest here.",
    }

    useEffect(() => {
        console.log("USE EFFECT 4")
        if (selectedKeywordFilter in data["report"]) {
            setSelectedMapData(data["report"][selectedKeywordFilter])
        } else {
            setSelectedKeywordFilter(keywords[0])
            setSelectedMapData(data["report"][keywords[0]])
        }
        setFilterDisable(false)

        let tmpFilteType = selectedCountType.toLowerCase() + '_locations_by_' + selectedFilterType.toLowerCase()
        const isValidFilter =
        selectedFilterValue &&
        data?.report[selectedKeywordFilter] &&
        Object.keys(data?.report[selectedKeywordFilter]).includes(tmpFilteType);
        
        const isValidSubFilter =
        isValidFilter &&
        Object.keys(data?.report[selectedKeywordFilter]?.[tmpFilteType]).includes(selectedFilterValue);
        
        setSelectedFilterType(isValidFilter ? selectedFilterType : "Sentiments");
        setSelectedFilterValue(isValidSubFilter ? selectedFilterValue : isValidFilter ? Object.keys(data?.report[selectedKeywordFilter]?.[tmpFilteType])[0]: "Positive_Negative");
        
    }, [data, keywords, selectedKeywordFilter]);

    useEffect(() => {
        

    }, [selectedKeywordFilter]);
    useEffect(() => {
        console.log("USE EFFECT 6")
        if (selectedFilterType === "Languages") {
            if (inputInfo["language"] === "All") {
                setFilterDisable(false)
                setSelectedFilterValue("All Languages")
            } else {
                setFilterDisable(true)
                setSelectedFilterValue(inputInfo["language"])
            }
        } else if (selectedFilterType === "Communities") {
            setFilterDisable(false)
            setSelectedFilterValue("All Communities")
        } else {
            if (inputInfo["sentiment"] === "All") {
                setFilterDisable(false)
                setSelectedFilterValue("Positive_Negative")
            } else {
                setFilterDisable(true)
                setSelectedFilterValue(inputInfo["sentiment"])
            }
        }
    }, [selectedFilterType])


    // useEffect hook to update the map visualisation information upon a change in the selected data
    useEffect(() => {
        console.log("USE EFFECT 5")
        let title = selectedCountType + ' Locations by ' + selectedFilterType
        console.log("THESE ARE THE FILTERS", selectedCountType, selectedFilterType, selectedFilterValue)
        let items = selectedMapData[selectedCountType.toLowerCase() + '_locations_by_' + selectedFilterType.toLowerCase()][selectedFilterValue]
        console.log("THESE ARE THE ITEMS", items)
        let items2 = selectedMapData[selectedCountType.toLowerCase() + '_locations_by_' + selectedFilterType.toLowerCase()][selectedFilterType === "Sentiments" ? "Positive_Negative" : (selectedFilterType === "Languages"? "All Languages" : "All Communities")]
        if (selectedFilterValue === "Positive_Negative") {
            const combinedCounts = {};
            items.map(item => {
                combinedCounts[item.val] = item.count;
            });
            items2.map(item => {
                combinedCounts[item.val] = [(combinedCounts[item.val] || 0), item.count];
            });
            items = Object.keys(combinedCounts).map(key => ({
                val: key,
                count: combinedCounts[key]
            }));
        }

        let key1 = "val"
        let key2 = "count"
        const dictionaryData = items;
        const x = dictionaryData.map(items => items[key1.toLowerCase()]);
        let y = (selectedFilterValue === "Positive_Negative") ? dictionaryData.map(items => items[key2.toLowerCase()][0].toPrecision(2) * 100) : dictionaryData.map(items => items[key2.toLowerCase()]);
        let z = (selectedFilterValue === "Positive_Negative") ? dictionaryData.map(items => `${(items[key2.toLowerCase()][0] * 100).toPrecision(3)}\% ${items[key2.toLowerCase()][0] === 0 ? "equal" : items[key2.toLowerCase()][0] > 0 ? "positive" : "negative"} out of : ${items[key2.toLowerCase()][1]}`) : dictionaryData.map(items => items[key2.toLowerCase()]);
        if (x.findIndex(obj => obj.toLowerCase() === 'not_available') >= 0) {
            y.splice(x.findIndex(obj => obj.toLowerCase() === 'not_available'), 1)
            z.splice(x.findIndex(obj => obj.toLowerCase() === 'not_available'), 1)
            x.splice(x.findIndex(obj => obj.toLowerCase() === 'not_available'), 1)
        }
        const zmin = Math.min(...y) < 0 ? -Math.max(Math.abs(...y)) : 0
        const zmax = Math.min(...y) < 0 ? Math.max(Math.abs(...y)) : Math.max(...y)

        const traces = [{
            x,
            y,
            type: 'choropleth',
            locationmode: 'country names',
            locations: x,
            showlegend: false,
            text: z.map((value, index) => `${x[index]}: ${value}`),
            z: y,
            zmax: zmax,
            zmin: zmin,
            name: selectedFilterValue,
            colorscale: selectedFilterValue in sentimentColorScale ? sentimentColorScale[selectedFilterValue] : sentimentColorScale['All'],
            color_continuous_scale: selectedFilterValue in sentimentColorScale ? sentimentColorScale[selectedFilterValue] : sentimentColorScale['All'],
            colorbar: {
                y: 0,
                yanchor: "bottom",
                title: {text: selectedFilterValue != "Positive_Negative" ? "Count" : "Ratio", side: "right"}
            },
            autocolorscale: false,
            hoverinfo: 'text'
        }];
        setMapConfigs({'data': traces, 'title': title})
    }, [selectedFilterValue, dropSentimentFilter]);

    // useEffect hook to update the selected map data to display upon a change in the filter type and count unit
    useEffect(() => {
        console.log("USE EFFECT 7")
        if (selectedFilterType === "Sentiments") {
            setDropSentimentFilter(sentimentDropValues)
        } else {
            let items = selectedMapData[selectedCountType.toLowerCase() + '_locations_by_' + selectedFilterType.toLowerCase()]
            console.log("*** These are the items ***", items)
            console.log("*** This is the mapping ***", communityNames)
            console.log("*** This is the selected keyword ***", selectedKeywordFilter)
            let list_of_items = []
            if (selectedFilterType === "Communities") {
                list_of_items = Object.keys(items).map((dictionaryKey) => {
                    console.log("From report...", dictionaryKey, typeof(dictionaryKey))
                    console.log("From mapping...", communityNames[selectedKeywordFilter][dictionaryKey])
                    return {
                        "key": dictionaryKey,
                        "value": dictionaryKey,
                        "text": dictionaryKey === "All Communities" ? "All Communities" : communityNames[selectedKeywordFilter][dictionaryKey]
                    }
                })
            } else {
                list_of_items = Object.keys(items).map((dictionaryKey) => {
                    return {
                        "key": dictionaryKey,
                        "value": dictionaryKey,
                        "text": dictionaryKey[0].toUpperCase() + dictionaryKey.slice(1)
                    }
                })
            }
            setDropSentimentFilter(list_of_items)
        }

    }, [selectedMapData, selectedFilterType, selectedCountType]);


    // Render code for the MapGraph component
    if (datasetOrigin === 'Tweets') {
        return (
            <div className="Visualisation">
                <div>
                    <div className="MainTitleWithPopup">
                        <h2 style={{marginRight: "5px"}}>{mapConfigs['title']}</h2>
                        <Popup
                            content="This component shows the break down of the data according to its geographical location. You can click on a specific country to generate a new report (in a new tab) for the subset of the current data that corresponds to this specific keyword, sentiment, language and country."
                            trigger={<div className='InfoIcon'><Icon name='question circle' size="small"/></div>}
                        />
                    </div>
                    <h3>Origin countries of tweets and users</h3>
                    <div className="DropDownGroup">
                        <div className="DropDownMaps">
                            <div className="SubTitleWithPopup">
                                <h3 className="DropDownTitle">Keyword</h3>
                                <Popup
                                    content="If more than 1 keyword was provided, you can use the 'Keyword' filter to display results for each keyword independently, as well as for all keywords together ('All keywords')."
                                    trigger={<div className='InfoIcon'><Icon name='question circle' size="small"/>
                                    </div>}
                                />
                            </div>
                            <div className='DropDownMenu'>
                                <Dropdown
                                    label='KeywordFilter'
                                    fluid
                                    selection
                                    options={dropKeywordsFilter}
                                    text={dropKeywordsFilter.text}
                                    floating
                                    labeled={true}
                                    icon={null}
                                    value={selectedKeywordFilter}
                                    onChange={(e, {value}) => setSelectedKeywordFilter(value)}
                                    closeOnChange={true}
                                    name='filtersTypeDropdown'
                                    id='filtersTypeDropdown'
                                ></Dropdown>
                            </div>
                        </div>

                        <div className="DropDownMaps">
                            <div className="SubTitleWithPopup">
                                <h3 className="DropDownTitle">Filter </h3>
                                <Popup
                                    content="Use the 'Filter' to filter the results shown by either sentiment or language."
                                    trigger={<div className='InfoIcon'><Icon name='question circle' size="small"/>
                                    </div>}
                                />
                            </div>
                            <div className='DropDownMenu'>
                                <Dropdown
                                    label='Filter'
                                    fluid
                                    selection
                                    options={dropSelectedFilterType}
                                    text={dropSelectedFilterType.text}
                                    floating
                                    labeled={true}
                                    icon={null}
                                    value={selectedFilterType}
                                    onChange={(e, {value}) => setSelectedFilterType(value)}
                                    closeOnChange={true}
                                    name='filtersTypeDropdown'
                                    id='filtersTypeDropdown'
                                ></Dropdown>
                            </div>
                        </div>

                        <div className="DropDownMaps">
                            <div className="SubTitleWithPopup">
                                <h3 className="DropDownTitle">{titleMapping[selectedFilterType]}</h3>
                                <Popup
                                    content={tooltipContent[selectedFilterType]}
                                    trigger={<div className='InfoIcon'><Icon name='question circle' size="small"/>
                                    </div>}
                                />
                            </div>

                            <div className='DropDownMenu'>
                                <Dropdown
                                    disabled={filterDisable}
                                    label='Filter Value'
                                    fluid
                                    selection
                                    options={dropSentimentFilter}
                                    text={dropSentimentFilter.text}
                                    floating
                                    labeled={true}
                                    icon={null}
                                    value={selectedFilterValue}
                                    onChange={(e, {value}) => setSelectedFilterValue(value)}
                                    closeOnChange={true}
                                    name='fliterTypeDropdown'
                                    id='fliterTypeDropdown'
                                ></Dropdown>
                            </div>
                        </div>
                    </div>
                    <div className="DropDownGroup">
                        <div className="DropDownMaps">
                            <div className="SubTitleWithPopup">
                                <h3 className="DropDownTitle">Region</h3>
                                <Popup
                                    content="Use the 'Region' filter to filter by world region."
                                    trigger={<div className='InfoIcon'><Icon name='question circle' size="small"/>
                                    </div>}
                                />
                            </div>

                            <div className='DropDownMenu'>
                                <Dropdown
                                    label='Map Type'
                                    fluid
                                    selection
                                    options={dropContinent}
                                    text={dropContinent.text}
                                    floating
                                    labeled={true}
                                    icon={null}
                                    value={selectedContinent}
                                    onChange={(e, {value}) => setSelectedContinent(value)}
                                    closeOnChange={true}
                                    name='mapTypeDropdown'
                                    id='mapTypeDropdown'
                                ></Dropdown>
                            </div>
                        </div>
                        <div className="DropDownMaps">
                            <div className="SubTitleWithPopup">
                                <h3 className="DropDownTitle">Method</h3>
                                <Popup
                                    content="Twitter allows users to declare locations in two ways. Authors can declare a location for their account, which is then inherited by all the tweets they post. Or authors can declare a location when posting a specific tweet. If 'Method' is set to 'Users' the location used is the former. If 'Method' is set to 'Tweets', the latter is used. Note that declaring a location is optional so the majority of the data will usually not have a location and therefore not appear on this map. "
                                    trigger={<div className='InfoIcon'><Icon name='question circle' size="small"/>
                                    </div>}
                                />
                            </div>

                            <div className='DropDownMenu'>
                                <Dropdown
                                    label='Locations Type'
                                    fluid
                                    selection
                                    options={dropSelectedCountType}
                                    text={selectedCountType}
                                    floating
                                    labeled={true}
                                    icon={null}
                                    value={selectedCountType}
                                    onChange={(e, {value}) => setSelectedCountType(value)}
                                    name='locationTypeDropdown'
                                    id='locationTypeDropdown'
                                ></Dropdown>
                            </div>
                        </div>
                    </div>
                </div>
                <div>
                    <Plot
                        data={mapConfigs['data']}
                        layout={layout}
                        onClick={function (event) {
                            const sentFilter = selectedFilterType === "Sentiments" ? (selectedFilterValue === "All Sentiments" ? "All" : (selectedFilterValue === "Positive_Negative" ? "All" : selectedFilterValue)) : inputInfo["sentiment"]
                            const langFilter = selectedFilterType === "Languages" ? (selectedFilterValue === "All Languages" ? "All" : selectedFilterValue) : inputInfo["language"]
                            const relKeyword = selectedKeywordFilter === "All" ? keywords.filter(function (key) {
                                return key !== 'All';
                            }).join(",") : selectedKeywordFilter
                            const page_path = window.location.pathname + "?report="
                            window.open(page_path + encodeURIComponent(
                                JSON.stringify(
                                    {
                                        "keywords": relKeyword,
                                        "dataSource": inputInfo["dataSource"],
                                        "source_text": inputInfo["source_text"],
                                        "operator": inputInfo["operator"],
                                        limit: 500,
                                        "date_start": inputInfo["date_start"],
                                        "date_end": inputInfo["date_end"],
                                        "sentiment": sentFilter,
                                        "language": langFilter,
                                        "location": event.points[0].location,
                                        "location_type": selectedCountType === "Users" ? "author" : "tweet",
                                    })),
                                "_blank");
                        }}
                    />
                </div>
            </div>
        );
    }
};