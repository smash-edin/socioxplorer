// import { React } from "react";
import {DataGrid} from '@mui/x-data-grid';
import {Link} from "@material-ui/core";
import {useEffect, useState, Fragment} from "react";
import {Dropdown, Button, Popup, Icon} from "semantic-ui-react";


// TopContent component used to display most frequent tweets, users, emojis, media and hashtags
export const TopContent = ({data, keywords, inputInfo, datasetOrigin, communityNames}) => {

    // Content type
    const [selectedContentType, setSelectedContentType] = useState({
        "name": datasetOrigin,
        "value": "top_tweets"
    });
    const [allKeywordsLabel, setAllKeywordsLabel] = useState(inputInfo["operator"] === "AND" ? "All keywords" : "Any keyword")
    useEffect(() => {
        setAllKeywordsLabel(inputInfo["operator"] === "AND" ? "All keywords" : "Any keyword")
    }, [inputInfo]);

    // Dropdown menu options: keywords
    const dropKeywordsFilter = keywords.map((dictionaryKey) => {
        return {
            "key": dictionaryKey,
            "value": dictionaryKey,
            "text": dictionaryKey === "All" ? allKeywordsLabel : dictionaryKey[0].toUpperCase() + dictionaryKey.slice(1)
        }
    });
    const [selectedKeywordsFilter, setSelectedKeywordsFilter] = useState(null);


    // Dropdown menu options: sentiment
    const dropSentimentFilter = Object.keys(data[keywords[0]]["top_tweets"]).map((dictionaryKey) => {
        return {
            "key": dictionaryKey,
            "value": dictionaryKey,
            "text": dictionaryKey
        }
    });
    const [selectedSentiment, setSelectedSentiment] = useState(inputInfo["sentiment"] === "All" ? "All Sentiments" : inputInfo["sentiment"]);
    const [sentimentDisable, setSentimentDisable] = useState(false)

    // Function to render URLs in tweets and user descriptions as clickable hyperlinks
    const replaceTextWithURL = (params, field) => {
        const text = params.row[field];
        const urlRegex = /(https?:\/\/[^\s]+)/g;
        const parts = text.split(urlRegex);
        return (
            <p>
                {parts.map(part => {
                        return urlRegex.test(part) ? (
                            <a key={part} href={part} target="_blank">{
                                part
                            }</a>
                        ) : part
                    }
                )}
            </p>
        )
    }

    const addLineBreaks = (text, maxLength) => {
        const regex = new RegExp(`.{1,${maxLength}}`, 'g');
        return text.match(regex).map((part, index) => (
            <Fragment key={index}>
                {part}
                <br />
            </Fragment>
        ));
    }

    const addURLToText = (params, field, urlTemplate) => {
        let text = params.row['videoId'] !== undefined ? 'watch?v=' + params.row['videoId'] + '&lc=' + params.row[field] : params.row[field]

        if (params.row['videoId'] !== undefined) {
            return (
                <p>
                    <a key={text} href={urlTemplate.replace('@', text)} target="_blank"
                    > 
                        {addLineBreaks(params.row[field], 14)}
                    </a>
                </p>
            )
        } else {
            return (
                <p>
                    <a key={text}  href={urlTemplate.replace('@', text)} target="_blank" >
                        {params.row[field]}
                    </a>
                </p>
            )
        }
    }

    const mapCommunity = (params, field) => {
        if (communityNames !== undefined && communityNames !== null) {
            return communityNames[params.row[field]]
        } else {
            return params.row[field]
        }
    }


    // Function to format relevant data for the top content table object
    const formatData = (selectedContentType, keyword, sentiment) => {
        if (!data.hasOwnProperty(keyword)) {
            keyword = keywords[0]
        }

        let items = data[keyword][selectedContentType["value"]][sentiment]
        let rows = []
        let columns = []
        let heightType = null

        if (selectedContentType["value"] === "top_tweets") {
            // Formatted data object for top tweets
            rows = items

            columns = [
                {
                    field: 'id',
                    width: 150,
                    headerAlign: 'center',
                    align: 'center',
                    renderHeader: () => (
                        <strong>{datasetOrigin === "Comment" ? 'Comment ID' : 'Tweet ID'}</strong>),
                    renderCell: (params) => addURLToText(params, 'id', datasetOrigin === "Comment" ? "http://youtube.com/@" : "https://twitter.com/twitter/status/@")
                }, {
                    field: 'date',
                    width: 90,
                    align: "left",
                    headerAlign: 'center',
                    renderHeader: () => (<strong>Date</strong>),
                }, {
                    field: 'fullText',
                    width: 400,
                    align: "left",
                    headerAlign: 'center',
                    renderHeader: () => (<strong>{datasetOrigin}</strong>),
                    renderCell: (params) => replaceTextWithURL(params, 'fullText')
                }, datasetOrigin !== "Comment" && ({
                    field: 'retweetCount',
                    width: 75,
                    headerAlign: 'center',
                    align: 'center',
                    renderHeader: () => (
                        <strong>{datasetOrigin === "Comment" ? 'Comment' : 'Retweets'}</strong>),
                }), {
                    field: 'language',
                    width: 75,
                    headerAlign: 'center',
                    align: 'center',
                    renderHeader: () => (<strong>Language</strong>),
                }, datasetOrigin !== "Comment" && ({
                    field: 'location',
                    width: 100,
                    headerAlign: 'center',
                    align: 'center',
                    renderHeader: () => (<strong>Location</strong>),
                }), {
                    field: 'interactionCommunity',
                    width: 100,
                    headerAlign: 'center',
                    align: 'center',
                    renderHeader: () => (<strong>Community</strong>),
                    renderCell: (params) => mapCommunity(params, 'interactionCommunity')
                },
            ].filter(Boolean);
            heightType = "auto"
        } else if (selectedContentType["value"] === "top_users") {
            // Formatted data object for top users
            rows = Object.keys(items).map((dictionaryKey) => {
                const dictionaryData = items[dictionaryKey];
                return {
                    "id": dictionaryKey,
                    "userScreenName": dictionaryData["userScreenName"],
                    "user_description": dictionaryData["user_description"],
                    "retweetCount": dictionaryData["retweetCount"],
                    "userLocation": dictionaryData["userLocation"],
                    "nb_followers": dictionaryData["nb_followers"],
                    "community": dictionaryData["community"],
                };
            });
            columns = [
                {
                    field: 'userScreenName',
                    width: 150,
                    headerAlign: 'center',
                    align: 'center',
                    renderHeader: () => (<strong>User screen names</strong>),
                    renderCell: (params) => addURLToText(params, 'userScreenName', datasetOrigin === "Comment" ? "http://youtube.com/@" : "https://twitter.com/twitter/status/@")
                }, datasetOrigin !== "Comment" && ({
                    field: 'user_description',
                    width: 400,
                    headerAlign: 'center',
                    renderHeader: () => (<strong>User descriptions</strong>),
                    renderCell: (params) => replaceTextWithURL(params, 'user_description')
                }), datasetOrigin !== "Comment" && ({
                    field: 'retweetCount',
                    width: 100,
                    headerAlign: 'center',
                    align: "center",
                    renderHeader: () => (<strong>Retweets</strong>),
                }), datasetOrigin !== "Comment" && ({
                    field: 'userLocation',
                    width: 100,
                    headerAlign: 'center',
                    align: "center",
                    renderHeader: () => (<strong>Location</strong>),
                }), {
                    field: 'interactionCommunity',
                    width: 100,
                    headerAlign: 'center',
                    align: "center",
                    renderHeader: () => (<strong>Community</strong>),
                    renderCell: (params) => mapCommunity(params, 'interactionCommunity')
                }, datasetOrigin !== "Comment" && ({
                    field: 'nb_followers',
                    width: 100,
                    headerAlign: 'center',
                    align: "center",
                    renderHeader: () => (<strong>Followers</strong>),
                }),
            ].filter(Boolean);
            heightType = "auto"
        } else {
            // Formatted data object for URLs, media and emojis
            columns = [
                {
                    field: 'val',
                    width: 650,
                    renderHeader: () => (<strong>{selectedContentType["name"]}</strong>),
                }, {
                    field: 'count',
                    width: 150,
                    headerAlign: 'center',
                    align: 'center',
                    renderHeader: () => (<strong>{datasetOrigin === "Comment" ? "Counts" : "Retweets"}</strong>),
                },
            ];

            let val_field = "val"
            let count_field = "count"

            if (selectedContentType["value"] === "urls" || selectedContentType["value"] === "media") {
                // Get URLs data
                columns[0] = {
                    field: 'val',
                    width: 650,
                    renderHeader: () => (<strong>{selectedContentType["name"]}</strong>),
                    renderCell: (params) => (<Link href={params.row.val} target="_blank">{params.row.val}</Link>),
                }
            } else if (selectedContentType["value"] === "emojis") {
                // Get Emojis data
                val_field = "text"
                count_field = "value"
            }
            rows = Object.keys(items).map((dictionaryKey) => {
                const dictionaryData = items[dictionaryKey];
                return {
                    "id": dictionaryKey,
                    "val": dictionaryData[val_field],
                    "count": dictionaryData[count_field],
                };
            });

        }
        return {"rows": rows, "columns": columns, "heightType": heightType}
    };

    // Variable storing top content table config
    const [figureConfig, setFigureConfig] = useState(formatData(selectedContentType, selectedKeywordsFilter, selectedSentiment));

    // useEffect hook to update the selected keyword filter upon a change in the data  and keywords passed by the parent
    // component (i.e. TestPage)
    useEffect(() => {
        setSelectedKeywordsFilter(keywords.hasOwnProperty(selectedKeywordsFilter) || data.hasOwnProperty(selectedKeywordsFilter) ? selectedKeywordsFilter : keywords[0])
        setSentimentDisable(inputInfo["sentiment"] !== "All")
        setSelectedSentiment(inputInfo["sentiment"] === "All" ? "All Sentiments" : inputInfo["sentiment"])
    }, [data, keywords, inputInfo]);

    // useEffect hook to update the content to display in the table upon a change in the selected content type, keyword
    // and sentiment filters
    useEffect(() => {
        setFigureConfig(formatData(selectedContentType, selectedKeywordsFilter, selectedSentiment))
    }, [data, selectedContentType, selectedKeywordsFilter, selectedSentiment, communityNames]);

    // Render code for the SentimentGraph component
    return (
        <div className="Visualisation">
            <div className="MainTitleWithPopup">
                <h2 style={{marginRight: "5px"}}>Top Content</h2>
                <Popup
                    content="This component shows the most retweeted tweets, users, URLs, media and emojis, with associated information, in the current query. Every column in the table is sortable in either ascending or descending order, and filterable. Hover over the column name, click on the three dots and select the relevant option to do so. By default, results are shown in group of 5. You can navigate to the next page of results by clicking on arrows are the bottom right of the table."
                    trigger={<div className='InfoIcon'><Icon name='question circle' size="small"/></div>}
                />
            </div>
            <div className="DropDownGroup">
                <div className="DropDownMaps">
                    <div className="SubTitleWithPopup">
                        <h3 className="DropDownTitle">Keywords</h3>
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
                            options={dropKeywordsFilter}
                            text={dropKeywordsFilter.text}
                            floating
                            labeled={true}
                            className='source'
                            icon={null}
                            value={selectedKeywordsFilter}
                            onChange={(e, {value}) => setSelectedKeywordsFilter(value)}
                            closeOnChange={true}
                            name='tokensFiltersTypeDropdown'
                            id='tokensFiltersTypeDropdown'
                        ></Dropdown>
                    </div>
                </div>
                <div className="DropDownMaps">
                    <div className="SubTitleWithPopup">
                        <h3 className="DropDownTitle">{datasetOrigin}'
                            sentiment</h3>
                        <Popup
                            content="Use the Tweet's sentiment filter to filter the results shown by sentiment. Note that the sentiment is obtained from the tweet only and not from user descriptions. When filtering by sentiment and looking at users, the users shown are those that authored at least one tweet with the chosen sentiment in the current query. As such, if the same user authored several tweets with different sentiments, they will appear under several sentiment values. "
                            trigger={<div className='InfoIcon'><Icon name='question circle' size="small"/></div>}
                        />
                    </div>

                    <div className="DropDownMenu">
                        <Dropdown
                            disabled={sentimentDisable}
                            label='tokensFilter'
                            fluid
                            selection
                            options={dropSentimentFilter}
                            text={dropSentimentFilter.text}
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
            </div>
            <div className="TopContent">
                <Button.Group attached='top'>
                    <Button onClick={() => setSelectedContentType({"name": "Tweets", "value": "top_tweets"})}
                            active={selectedContentType["name"] === "Tweets"}>
                        <div className="ButtonWithPopup">
                            <span>{datasetOrigin}</span>
                            <Popup
                                content="This table shows the most retweeted tweets in the current query (capped at 30,000). Clicking on a tweet ID will open the corresponding tweet on Twitter (X) in a new tab. The number of retweet shown correspond to the retweets of the given tweet in the whole dataset. The location shown is the location declared when posting the tweet, not the location of the author."
                                trigger={<div className='InfoIcon'><Icon name='question circle' size="small"/></div>}
                            />
                        </div>
                    </Button>
                    <Button onClick={() => setSelectedContentType({"name": "Users", "value": "top_users"})}
                            active={selectedContentType["name"] === "Users"}>
                        <div className="ButtonWithPopup"><span>Users</span>
                            <Popup
                                content="This table shows the most retweeted users who posted a tweet contained in the current query (capped at 30,000). Clicking on a user screen name will open the corresponding user profile on Twitter (X) in a new tab. Users that have retweeted but not tweeted are not shown. Note that when filtering by sentiment, the users shown are those that authored at least one tweet with the chosen sentiment in the current query. As such, if the same user authored several tweets with different sentiments, they will appear under several sentiment values. "
                                trigger={<div className='InfoIcon'><Icon name='question circle' size="small"/></div>}
                            />
                        </div>
                    </Button>
                    {datasetOrigin !== "Comment" && (
                    <Button onClick={() => setSelectedContentType({"name": "URLs", "value": "urls"})}
                            active={selectedContentType["name"] === "URLs"}>
                        <div className="ButtonWithPopup"><span>URLs</span>
                            <Popup
                                content="This table shows the most retweeted URLs contained in the current query (capped at 150). Clicking on a URL will open it in a new tab."
                                trigger={<div className='InfoIcon'><Icon name='question circle' size="small"/></div>}
                            />
                        </div>
                    </Button>
                    )}
                    {datasetOrigin !== "Comment" && (
                    <Button onClick={() => setSelectedContentType({"name": "Media", "value": "media"})}
                            active={selectedContentType["name"] === "Media"}>
                        <div className="ButtonWithPopup"><span>Media</span>
                            <Popup
                                content="This table shows the most retweeted media (i.e. images, videos) contained in the current query (capped at 150). Clicking on a media URL will open it in a new tab. "
                                trigger={<div className='InfoIcon'><Icon name='question circle' size="small"/></div>}
                            />
                        </div>
                    </Button>
                    )}
                    <Button onClick={() => setSelectedContentType({"name": "Emojis", "value": "emojis"})}
                            active={selectedContentType["name"] === "Emojis"}>
                        <div className="ButtonWithPopup"><span>Emojis</span>
                            <Popup
                                content="This table shows the most retweeted emojis contained in the current query (capped at 150)."
                                trigger={<div className='InfoIcon'><Icon name='question circle' size="small"/></div>}
                            />
                        </div>
                    </Button>
                </Button.Group>
                <DataGrid
                    getRowHeight={() => figureConfig["heightType"]}
                    rows={figureConfig["rows"]}
                    columns={figureConfig["columns"]}
                    initialState={{
                        ...data.initialState,
                        pagination: {paginationModel: {pageSize: 5}},
                    }}
                    pageSizeOptions={[5, 10, 15]}
                    disableColumnSelector={true}
                />
            </div>
        </div>
    )
};