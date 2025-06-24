import Plot from "react-plotly.js";
import {Dropdown, Checkbox, Popup, Icon} from "semantic-ui-react";
import {useEffect, useState} from "react";

// SentimentGraph component used to display the prevalence of different sentiments in data matching the given query
export const SentimentGraph = ({data, keywords, inputInfo}) => {

    // Function mapping sentiments to colours
    const getSentimentsColor = (index) => {
        const colors = {
            "Positive" : 'rgb(31, 119, 180)',
            "Neutral" : 'rgb(255, 160, 40)',
            "Negative" : 'rgb(214, 39, 40)',
            "Other" : 'rgb(148, 103, 189)',
            "NonText" : 'rgb(175, 175, 175)',
        };
        if (index in colors) {
            return colors[index];
        }else{
            return colors["Other"];
        }
    };

    // Function to obtain the mapping from an index to a color from specified colormap
    const getRandomColor = (index) => {
        const colors = [
            'rgb(31, 119, 180)',
            'rgb(255, 127, 14)',
            'rgb(44, 160, 44)',
            'rgb(214, 39, 40)',
            'rgb(148, 103, 189)',
        ];
        return colors[index % colors.length];
    };

    // Variable storing options to be displayed in a dropdown menu
    const dropSelectedSentimentMethodValues = [
        { key: 'Sentiments', text: 'Over time', value: 'Sentiments_Distributions', },
        { key: 'Sentiment/Language', text: 'Per language', value: 'Sentiment_per_Language', },
    ];

    const [allKeywordsLabel, setAllKeywordsLabel] = useState(inputInfo["operator"] === "AND" ? "All keywords" : "Any keyword")

    useEffect(() => {
        setAllKeywordsLabel(inputInfo["operator"] === "AND" ? "All keywords" : "Any keyword")
    },[inputInfo]);

    // Variable storing all the keywords to be displayed in a dropdown menu (used to filter language per keyword)
    const dropKeywordsFilter = Object.keys(data).map((dictionaryKey) => {
        return {
            "key": dictionaryKey,
            "value": dictionaryKey,
            "text": dictionaryKey === "All"? allKeywordsLabel : dictionaryKey[0].toUpperCase()+dictionaryKey.slice(1)}
    });

    // Mapping between display options (from dropdown) and graph title
    const titleMapping = {
        "Sentiments_Distributions": "Sentiment over time",
        "Sentiment_per_Language": "Sentiment per language",
    }

    // Variables storing filter values, figure data and layout options
    const [selectedKeywordFilter, setSelectedKeywordFilter] = useState(keywords[0]);
    const [selectedSentimentData, setSelectedSentimentData] = useState(data[selectedKeywordFilter]);
    const [selectedSentimentMethodValue, setSelectedSentimentMethodValue] = useState('Sentiments_Distributions');
    const [sentimentFigureConfig, setSentimentFigureConfig] = useState({});
    const [showAsPercentage, setShowAsPercentage] = useState(false)

    // Graph layout options
    const [layout, setLayout] = useState({
        //title: plot_title,
        xaxis: { title: 'Date' },
        yaxis: { title: 'Count' },
        barmode: 'stack',
        barnorm: "",
        modebar: {remove: ['lasso2d', 'select2d', "autoscale"]},
    })

    // useEffect hook to update the selected sentiment data to display upon a change in the keyword filter or in the data
    // passed by the parent component (i.e. TestPage)
    useEffect(() => {
        if (selectedKeywordFilter in data) {
            setSelectedSentimentData(data[selectedKeywordFilter])
        } else {
            setSelectedKeywordFilter(keywords[0])
            setSelectedSentimentData(data[keywords[0]])
        }
    },[data, keywords, selectedKeywordFilter]);

    /*
    function updateHoverTemplate(asPercentage) {
        if (asPercentage) {
            return "%{x}, %{y:.1f}%"
        } else {
            return "%{x}, %{y}"
        }
    }
     */
    // useEffect hook to update the sentiment plot information upon a change in the selected data or in the data passed
    // by the parent component (i.e. TestPage)
    useEffect(() => {
        let items = selectedSentimentData[selectedSentimentMethodValue]
        let title = titleMapping[selectedSentimentMethodValue]
        let key1 = "val"
        let key1_1 = selectedSentimentMethodValue === 'Sentiment_per_Language'? "Language":"Date"
        let key2 = "Count"
        let sentiments = selectedSentimentMethodValue !== 'languages_timelines'

        const sentimentNames = Object.keys(items)
        sentimentNames.sort()

        const traces = sentimentNames.map((dictionaryKey) => {
            const dictionaryData = items[dictionaryKey];
            const x = dictionaryData.map(items => items[key1.toLowerCase()]);
            const y = dictionaryData.map(items => items[key2.toLowerCase()]);

            let color = sentiments ? getSentimentsColor(dictionaryKey) : getRandomColor(dictionaryKey)
            return {
                x,
                y,
                type: 'bar',
                showlegend:true,
                name: dictionaryKey[0].toUpperCase()+dictionaryKey.slice(1),
                labels: {'language': "Language", key1: key1_1, 'count': "Count", 'english': 'English'},
                marker: {  color: color },
                hovertemplate: showAsPercentage? "%{x}, %{y:.1f}%":"%{x}, %{y}",//updateHoverTemplate(showAsPercentage),
                // hovertemplate: "%{x}, %{y:.1f}"
            };
        });

        setSentimentFigureConfig({'data': traces, 'title': title, 'key1': key1_1, 'key2': key2, 'sentiments': sentiments})
        setLayout(layout => ({
            ...layout,
            xaxis: { title: key1_1 },
            yaxis: { title: key2 },
        }))
    }, [data, showAsPercentage,selectedSentimentData, selectedSentimentMethodValue]);

    // useEffect hook to update sentiment plot upon a change in the selected display mode (percentage vs count)
    useEffect(() => {
        setLayout(layout => ({
            ...layout,
            barnorm: showAsPercentage? "percent":"",
            yaxis: { title: showAsPercentage ?'Percent':"Count" },
        }))
    }, [showAsPercentage])

    // Render code for the SentimentGraph component
    return (
        <div className="Visualisation">
            <div className="MainTitleWithPopup">
                <h2 style={{marginRight: "5px"}}>{sentimentFigureConfig['title']}</h2>
                <Popup
                    content="This component shows the break down of the data per sentiment. Click on a sentiment in the legend to hide/show it on the visualisation, and double-click on it to make it the only visible sentiment. You can also click on a specific datapoint to generate a new report (in a new tab) for the subset of the current data that corresponds to this specific day, sentiment and keyword."
                    trigger={<div className='InfoIcon'><Icon name='question circle' size="small"/></div>}
                />
            </div>
            <div  className="DropDownGroup">
                <div className="DropDownMaps">
                    <div className="SubTitleWithPopup">
                        <h3 className="DropDownTitle">Keyword</h3>
                        <Popup
                            content="If more than 1 keyword was provided, you can use the 'Keyword' filter to display results for each keyword independently, as well as for all keywords together ('All keywords'). "
                            trigger={<div className='InfoIcon'><Icon name='question circle' size="small"/></div>}
                        />
                    </div>
                    <div className="DropDownMenu">
                        <Dropdown
                            label='Keyword'
                            fluid
                            selection
                            options={dropKeywordsFilter}
                            text={dropKeywordsFilter.text}
                            floating
                            labeled={true}
                            icon={null}
                            value={selectedKeywordFilter}
                            onChange={(e, { value }) => setSelectedKeywordFilter(value)}
                            closeOnChange={true}
                            name='filtersTypeDropdown'
                            id='filtersTypeDropdown'
                        ></Dropdown>
                    </div>
                </div>
                <div className="DropDownMaps">

                    <div className="SubTitleWithPopup">
                        <h3 className="DropDownTitle">Method</h3>
                        <Popup
                            content="If 'Method' is set to 'Over time' the break down of the data by sentiment over time. If 'Method' is set to 'Per language', the break down is shown per language."
                            trigger={<div className='InfoIcon'><Icon name='question circle' size="small"/></div>}
                        />
                    </div>

                    <div className="DropDownMenu">
                        <Dropdown
                            label='Distribution Type'
                            fluid
                            selection
                            options={dropSelectedSentimentMethodValues}
                            text={dropSelectedSentimentMethodValues.text}
                            floating
                            labeled={true}
                            icon={null}
                            value={selectedSentimentMethodValue}
                            onChange={(e, { value }) => setSelectedSentimentMethodValue(value)}
                            name='distributionTypeDropdown'
                            id='distributionTypeDropdown'
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
            <div>
                <Plot
                    data={sentimentFigureConfig['data']}
                    layout={layout}
                    onClick={function(event) {
                        const relKeyword = selectedKeywordFilter === "All" ? keywords.filter(function (key) {
                            return key !== 'All';
                        }).join(",") : selectedKeywordFilter

                        const generate_report = window.confirm("A new report will be generated with the following filters:" +
                            "\n Keywords:"+ relKeyword +
                            "\n Dataset:"+ inputInfo["source_text"] +
                            "\n Operator:"+ inputInfo["operator"] +
                            "\n Date:"+ event.points[0].x +
                            "\n Sentiment:"+ event.points[0].fullData.name +
                            "\n Language:"+ inputInfo["language"] +
                            "\n Location of "+ (inputInfo["location_type"] === 'author'? 'users':'tweets') + ": " + inputInfo["location"] +
                            "\n\n Do you want to continue?");
                        if (generate_report !== false && generate_report !== null){

                            if (selectedSentimentMethodValue === "Sentiments_Distributions") {
                                const page_path = window.location.pathname + "?report="
                                window.open(page_path + encodeURIComponent(
                                    JSON.stringify(
                                        {
                                            "keywords": relKeyword,
                                            "dataSource": inputInfo["dataSource"],
                                            "source_text": inputInfo["source_text"],
                                            "operator": inputInfo["operator"],
                                            limit: 500,
                                            "date_start": event.points[0].x,
                                            "date_end": event.points[0].x,
                                            "sentiment": event.points[0].fullData.name,
                                            "language": inputInfo["language"],
                                            "location": inputInfo["location"],
                                            "location_type": inputInfo["location_type"],
                                        })),
                                    "_blank");
                            } else {
                                const page_path = window.location.pathname + "?report="
                                window.open(page_path + encodeURIComponent(
                                    JSON.stringify(
                                        {
                                            "keywords": keywords.filter(function (key) {
                                                return key !== 'All';
                                            }).join(","),
                                            "dataSource": inputInfo["dataSource"],
                                            "source_text": inputInfo["source_text"],
                                            "operator": inputInfo["operator"],
                                            limit: 1000,
                                            "date_start": inputInfo["date_start"],
                                            "date_end": inputInfo["date_end"],
                                            "sentiment": event.points[0].x,
                                            "language": inputInfo["language"],
                                            "location": inputInfo["location"],
                                            "location_type": inputInfo["location_type"],
                                        })),
                                    "_blank");
                            }
                        }
                    }}
                />
            </div>
        </div>
    );
};
export default SentimentGraph;