import React, {useState} from 'react'
import {AccordionTitle, AccordionContent, Accordion, Icon} from 'semantic-ui-react'

import nav_bar from '../images/nav_bar.png';
import input from '../images/input.png';
import date_selector from '../images/date_selector.png';
import save_report from '../images/save_report.png';
import timeline from '../images/timeline.png';
import new_report_popup from '../images/new_report_popup.png';
import sentiment from '../images/sentiment.png';
import language from '../images/language.png';
import map from '../images/map.png';
import map_sentiment_ratio from '../images/map_sentiment_ratio.png';
import top_content_tweets from '../images/top_content_tweets.png';
import top_content_users from '../images/top_content_users.png';
import top_content_urls from '../images/top_content_urls.png';
import top_content_menu from '../images/top_content_menu.png';
import wordcloud from '../images/wordcloud.png';
import wordcloud_topics from '../images/wordcloud_topics.png';
import wordcloud_communities from '../images/wordcloud_communities.png';
import topic_discovery from '../images/topic_discovery.png';
import topic_discovery_w_claim from '../images/topic_discovery_w_claim.png';
import renaming_topics from '../images/renaming_topics.png';
import renaming_communities from '../images/renaming_communities.png';

import topics_per_community from '../images/topics_per_community.png';

import social_network from '../images/social_network.png';
import communities_tweeting from '../images/communities_tweeting.png';
import communities_stats from '../images/communities_stats.png';
import load_report from '../images/load_report.png';
import get_users from '../images/get_users.png';
import add_user from '../images/add_user.png';
import reprocessing from '../images/reprocessing.png';

import community_alignment from '../images/community_alignment.png';

const Help = () => {

    const [preprocessing, setPreprocessing] = useState(false)
    const [navBar, setNavBar] = useState(false)
    const [analysis, setAnalysis] = useState(false)
    const [loadPage, setLoadPage] = useState(false)
    const [admin, setAdmin] = useState(false)

    const [inputA, setInput] = useState(false)
    const [timelineA, setTimeline] = useState(false)
    const [sentimentA, setSentiment] = useState(false)
    const [languageA, setLanguage] = useState(false)
    const [mapA, setMap] = useState(false)
    const [topContentA, setTopContent] = useState(false)
    const [wordcloudA, setWordcloud] = useState(false)
    const [topicModellingA, setTopicModelling] = useState(false)
    const [topicsPerCommunityA, setTopicsPerCommunity] = useState(false)
    const [socialNetworkA, setSocialNetwork] = useState(false)
    const [tweetingA, setTweeting] = useState(false)
    const [statsA, setStats] = useState(false)

    return (
        <div className="PageBody">
            <div className="HelpBody">
                <div className="PageTitle">
                    <h1>SocioXplorer Dashboard - User Guide</h1>
                </div>

                <Accordion>

                    <AccordionTitle
                        active={navBar}
                        onClick={(e, {value}) => {
                            setNavBar(!navBar)
                        }}
                        className="h2TitleContainer"
                    >
                        <h2><Icon name={(navBar ? "angle down" : 'angle right')}/>Navigation bar</h2>
                    </AccordionTitle>
                    <AccordionContent active={navBar}>
                        <p className="Paragraph">
                            The tabs in the navigation bar, at the top left corner of the page, allow the analyst to go
                            from one page to the
                            other. The "Logout" button allows them to log out of their personal session. Below, will
                            describe the
                            functionalities containing in the pages accessible from the navigation bar.
                        </p>
                        <div className="ImageContainer">
                            <img src={nav_bar} alt="NavBar" className="MediumImage"/>
                        </div>
                    </AccordionContent>


                    <AccordionTitle
                        active={analysis}
                        onClick={(e, {value}) => {
                            setAnalysis(!analysis)
                        }}
                        className="h2TitleContainer"
                    >
                        <h2><Icon name={(analysis ? "angle down" : 'angle right')}/>Analysis page</h2>
                    </AccordionTitle>
                    <AccordionContent active={analysis}>
                        <p className="Paragraph">
                            The Analysis page (accessible through the navigation bar at the top left corner of the
                            dashboard) allows
                            the analyst to explore and analyse their data. In what follows, we will describe each
                            feature contained
                            on this page.
                        </p>

                        <Accordion>
                            <AccordionTitle
                                active={inputA}
                                onClick={(e, {value}) => {
                                    setInput(!inputA)
                                }}
                                className="h3TitleContainer"
                            >
                                <h3 className="h3Title"><Icon name={(inputA ? "angle down" : 'angle right')}/>A. Input
                                    header</h3>
                            </AccordionTitle>
                            <AccordionContent active={inputA}>
                                <p className="Paragraph">
                                    The input header allows the analyst to specify the data in which they would like to
                                    discover
                                    narratives. A dataset must be selected. All other fields are optional filters: leave
                                    all of them
                                    empty to generate an analysis of the entire dataset, or specify some to narrow down
                                    your search.
                                </p>
                                <div className="ImageContainer">
                                    <img src={input} alt="Input" className="MediumImage"/>
                                </div>

                                <p className="Paragraph">
                                    <b>1. Dataset filter</b>: This filter allows you to choose the dataset for which you
                                    would like to generate
                                    a report, from all the datasets available.
                                </p>

                                <p className="Paragraph">
                                    <b>2. Keywords filter</b>: Leave the keywords field empty to see all tweets/YouTube
                                    comments, regardless of their content, or specify a keyword to only return those
                                    that contain that keyword. For example, searching for "Messi" will limit the
                                    results to tweets/comments that contain the word "Messi". The search is not
                                    case-sensitive, so searching messi or Messi will return the same results, but it is
                                    sensitive to spelling, including special characters, so searching Mbappé or Mbappe
                                    will return different results. Some special characters may not be supported, for
                                    example, it is not possible to search for exclamation marks.
                                </p>

                                <p className="Paragraph">
                                    You can also use more than one keyword and separate them with commas. If you do so,
                                    you will need to choose
                                    between "Any keyword" and "All keywords" to indicate how your keywords should be
                                    combined in the search. Selecting the option "Any keyword" (under the keyword field)
                                    will return all tweets/YouTube comments that contain any of the keywords: that is,
                                    they contain at least one of the keywords but not necessarily all of them. Selecting
                                    "All keywords", on the other hand, will only return tweets/YouTube comments that
                                    contain all of the keywords (although not necessarily in the same order as you
                                    enter them here). For example, searching "Messi, Ronaldo" and selecting "Any" will
                                    return tweets/comments that contain either of the two words. This allows you to
                                    compare how each of these two players is being mentioned. Selecting "All" will
                                    only return tweets/comments that contain both. This allows you to understand how
                                    they are mentioned together. Note that searching "Messi Ronaldo" will not return the
                                    same result at "Messi, Ronaldo": while in the latter "Messi" and "Ronaldo" are
                                    separate keywords, "Messi Ronaldo" would only return results that contain this
                                    whole phrase.
                                </p>

                                <p className="Paragraph">
                                    If "#" is used at the start of the keyword (e.g. "#myhashtag"), only tweets/YouTube
                                    comments that contain this hashtag will be returned. If "@" is used at the start of
                                    the keyword (e.g. "@journalist"), only tweets/comments by authors with that keyword
                                    in their user name or user description (if using Twitter data) will be returned. In
                                    other words, the latter essentially allows the analyst to filter the data based on
                                    users.
                                </p>

                                <p className="Paragraph">
                                    If you would only like to return results where two or more words appear together,
                                    you can wrap them in double inverted commas: for example, the query "Cristiano
                                    Ronaldo" will only return tweets/YouTube comments that contain "Cristiano" and
                                    "Ronaldo" in that order, with nothing in between.
                                </p>

                                <p className="Paragraph">
                                    <b>3. Languages filter</b>: By default, the report will show results for all
                                    languages ("All"). If a specific language is selected, however, only the
                                    tweets/YouTube comments in that language will be shown. Note that some languages
                                    contained in this list might not be present in the data. A tweet's/comment's
                                    language label was identified automatically by Twitter (X) and YouTube respectively.
                                    Each tweet/comment is assumed to be in one language primarily. Therefore a
                                    tweet/comment may not be returned by this filter if only part of that tweet/comment
                                    is in that language
                                </p>

                                <p className="Paragraph">
                                    <b>4. Sentiment filter</b>: By default, the report will show results for all
                                    sentiments ("All"). If a specific sentiment is selected however (i.e. "Positive",
                                    "Negative" or "Neutral"), only the tweets/YouTube comments with that sentiment will
                                    be shown. The sentiment of each tweet/comment was identified automatically using AI.
                                </p>

                                <p className="Paragraph">
                                    <b>5. Country filter</b>: Twitter datasets can be filtered by country. By default,
                                    the report will show results for all countries ("All"). The "Author's country" is
                                    inferred from the location authors declare as part of their profile. The "Tweet's
                                    country", on the other hand, corresponds to the location given when the author
                                    publishes a particular tweet. Note that selecting the option "All" will also return
                                    results without a declared location, which usually compose the majority of the data.
                                    Note that because YouTube comments do not include geolocation labels, trying to
                                    filter YouTube data by country will result in no results being returned.
                                </p>

                                <p className="Paragraph">
                                    <b>6. Dates filter</b>: Leave the date fields empty to get results for the entire
                                    time period covered by the chosen dataset. You can also specify only a start date or
                                    only an end date. Clicking on the "Last day", "Last week", "Last month" or "Last
                                    year" buttons will compute the date range automatically based on the current date.
                                    The user can also select the date directly on the pop-up date picker after clicking
                                    on the date field: the double arrow buttons (in red on Figure below) allow them to
                                    change the year while the single arrow buttons (in blue) allow them to change the
                                    month. If entering a date yourself instead of selecting it in the pop-up date
                                    picker, it must be in the "YYYY-MM-DD" format.
                                </p>
                                <div className="ImageContainer">
                                    <img src={date_selector} alt="DateSelector" className="SmallImage"/>
                                </div>

                                <p className="Paragraph">
                                    <b>7. "Show results" button</b>: Clicking the "Show results" button will generate
                                    the report for the selected input filters. The report will be shown on the same
                                    page, below the input header. The report can take from a few seconds to a few
                                    minutes to be generated, depending on the amount of data matching the filters.
                                </p>

                                <p className="Paragraph">
                                    <b>8. "Save report" button</b>: Clicking the "Save report" button allows the user to
                                    save all the filters they have applied to the data, to allow them to quickly access
                                    the same report again. Once the button is clicked, a pop-up will appear asking the
                                    user to specify the name they would like to give to this particular search and
                                    confirm (see Figure below). The report can then be loaded again from the "Load
                                    Report" page (see "Load Report page" section below).
                                </p>
                                <div className="ImageContainer">
                                    <img src={save_report} alt="SaveReport" className="MediumImage"/>
                                </div>
                            </AccordionContent>

                            <AccordionTitle
                                active={timelineA}
                                onClick={(e, {value}) => {
                                    setTimeline(!timelineA)
                                }}
                                className="h3TitleContainer"
                            >
                                <h3 className="h3Title"><Icon name={(timelineA ? "angle down" : 'angle right')}/>B.
                                    Timeline</h3>
                            </AccordionTitle>
                            <AccordionContent active={timelineA}>
                                <p className="Paragraph">
                                    The timeline component shows the volume of data per day matching the search filters
                                    (see 1 on Figure below). If more than one keyword was provided, a different line is
                                    plotted for each keyword as well as for all keywords together ("Any keyword"/"All
                                    keywords").
                                </p>
                                <div className="ImageContainer">
                                    <img src={timeline} alt="Timeline" className="MediumImage"/>
                                </div>

                                <p className="Paragraph">
                                    The volume for all the keywords is either labelled "Any keyword" or "All keywords"
                                    depending on the option selected for the keyword filter in the input header. Note
                                    that "Any keyword" corresponds to tweets/YouTube comments that contain either of the
                                    keyword but not necessarily all of them, so the volume shown should therefore
                                    be <b>greater</b> than that of any individual keyword. "All keywords", however,
                                    corresponds to tweets/comments that contain all keywords together: the volume should
                                    therefore be <b>smaller</b> than that of any individual keyword.
                                </p>

                                <p className="Paragraph">
                                    Click on a keyword in the legend (see 2) to hide/show its line, and double-click on
                                    it to make it
                                    the only visible line. You can also click on a specific datapoint in the
                                    visualisation (i.e. 1) to
                                    generate a new report (in a new tab) for the subset of the current data that
                                    corresponds to this
                                    specific day and keyword. If you do so, a pop up like the following will appear
                                    to let you know exactly the input values which will be used to generate the new
                                    report:
                                </p>

                                <div className="ImageContainer">
                                    <img src={new_report_popup} alt="NewReportPopup" className="MediumImage"/>
                                </div>

                                <p className="Paragraph">
                                    Finally, the four interactivity buttons (from left to right) at the top right corner
                                    of the
                                    visualisation (see 3) allow you to 1) save the plot as PNG file on your local
                                    machine, 2) to select
                                    an area of the plot to zoom in on it, 3) to pan over the plot and 4) to reset the
                                    axes.
                                </p>
                            </AccordionContent>

                            <AccordionTitle
                                active={sentimentA}
                                onClick={(e, {value}) => {
                                    setSentiment(!sentimentA)
                                }}
                                className="h3TitleContainer"
                            >
                                <h3 className="h3Title"><Icon name={(sentimentA ? "angle down" : 'angle right')}/>C.
                                    Sentiment graph</h3>
                            </AccordionTitle>
                            <AccordionContent active={sentimentA}>
                                <p className="Paragraph">
                                    The Sentiment component shows the break down of the data per sentiment (see 1 on
                                    Figure). Click on a
                                    sentiment in the legend (see 2) to hide/show it on the visualisation, and
                                    double-click on it to make
                                    it the only visible sentiment.
                                </p>

                                <div className="ImageContainer">
                                    <img src={sentiment} alt="Sentiment" className="MediumImage"/>
                                </div>

                                <p className="Paragraph">
                                    If more than one keyword was provided, you can use the "Keyword" filter (see 3) to
                                    display results for
                                    each keyword independently, as well as for all keywords together ("All keywords").
                                    The volume for all the
                                    keywords is either labelled "Any keyword" or "All keywords" depending on the option
                                    selected for the keyword
                                    filter in the input header.
                                </p>

                                <p className="Paragraph">
                                    If the "Method" option (see 4) is set to "Over time", the visualisation will show
                                    the break down of
                                    the data by sentiment over time. If "Method" is set to "Per language", the break
                                    down is shown per language.
                                </p>

                                <p className="Paragraph">
                                    You can use the "Percentage" toggle (see 5) to display the results as percentages
                                    per day instead of
                                    counts.
                                </p>

                                <p className="Paragraph">
                                    You can also click on a specific datapoint in the visualisation (i.e. 1) to generate
                                    a new report (in
                                    a new tab) for the subset of the current data that corresponds to this specific day
                                    (if "Method" is
                                    "Over time"), language (if "Method" is "Per language"), sentiment and keyword(s)
                                    (from the "Keyword"
                                    filter). If you do so, a pop up will then be shown to let you know exactly the input
                                    values which
                                    will be used to generate the new report.
                                </p>

                                <p className="Paragraph">
                                    The four interactivity buttons (from left to right) at the top right corner of the
                                    visualisation (see
                                    6) allow you to 1) save the plot as PNG file on your local machine, 2) to select an
                                    area of the plot
                                    to zoom in on it, 3) to pan over the plot and 4) to reset the axes .
                                </p>
                            </AccordionContent>

                            <AccordionTitle
                                active={languageA}
                                onClick={(e, {value}) => {
                                    setLanguage(!languageA)
                                }}
                                className="h3TitleContainer"
                            >
                                <h3 className="h3Title" style={{"margin-top": "30px"}}><Icon name={(languageA ? "angle down" : 'angle right')}/>D.
                                    Languages graph</h3>
                            </AccordionTitle>
                            <AccordionContent active={languageA}>
                                <p className="Paragraph">
                                    The Language component shows the volume of data per language (see 1 on Figure). Note
                                    that if the dataset
                                    only contains one language, a single bar will be shown in the graph (as below).
                                </p>

                                <div className="ImageContainer">
                                    <img src={language} alt="Language" className="MediumImage"/>
                                </div>

                                <p className="Paragraph">
                                    If the generated report is for specific keywords, these will appear under the
                                    "Keyword" filter (see 2).
                                    The "Community" filter (see 3) on the other hand will only appear if the Social
                                    Network Analysis visualisation
                                    has been generated (see "J. Social Network Analysis" below).
                                </p>

                                <p className="Paragraph">
                                    You can click on a specific bar to generate a new report (in a new tab) for the
                                    subset of the current data
                                    that corresponds to this specific language and keyword (from the "Keyword" filter).
                                    If you do so, a pop up
                                    will then be shown to let you know exactly the input values which will be used to
                                    generate the new report.
                                </p>

                                <p className="Paragraph">
                                    Finally, the four interactivity buttons at the top right corner of the visualisation
                                    (see 4) allow
                                    you to 1) save the plot as PNG file on your local machine, 2) to select an area of
                                    the plot to zoom in on it,
                                    3) to pan over the plot and 4) to reset the axes (from left to right).
                                </p>

                            </AccordionContent>

                            <AccordionTitle
                                active={mapA}
                                onClick={(e, {value}) => {
                                    setMap(!mapA)
                                }}
                                className="h3TitleContainer"
                            >
                                <h3 className="h3Title"><Icon name={(mapA ? "angle down" : 'angle right')}/>E. Map</h3>
                            </AccordionTitle>
                            <AccordionContent active={mapA}>

                                <p className="Paragraph">
                                    The Map component shows the break down of the data according to the geographical
                                    location of users
                                    or tweets (see 1). It is only features in reports for Twitter (X) data, and not in
                                    reports for
                                    YouTube data. This is because YouTube comments never have geo-tags.
                                </p>

                                <div className="ImageContainer">
                                    <img src={map} alt="Map" className="MediumImage"/>
                                </div>

                                <p className="Paragraph">
                                    <b>Keyword</b>: If more than one keyword was provided, you can use the "Keyword"
                                    filter (see 2) to display results for
                                    each keyword independently, as well as for all keywords together. The volume for all
                                    the keywords is
                                    either labelled "Any keyword" or "All keywords" depending on the option selected for
                                    the keyword
                                    filter in the input header.
                                </p>

                                <p className="Paragraph">
                                    <b>Filter</b>: Use the "Filter" menu (see 3) to filter the results shown by either
                                    sentiments, languages
                                    or communities. The option of filtering per communities is only available if the
                                    Social Network Analysis
                                    visualisation has been generated (see section "J. Social Network Analysis" below).
                                    If "Language" is selected, you can choose the language of interest with the
                                    "Language" filter
                                    (see 4). This same filter is renamed "Sentiment" filter if "Sentiment" is selected
                                    as the
                                    value for "Filter" instead. Similarly, the filter is renamed "Community" and
                                    displays the list of possible
                                    communities if "Community" is selected as the value for "Filter" instead. Finally,
                                    you can use the
                                    "Region" filter (see 5) to filter the data by world region (e.g. "Europe").
                                </p>

                                <p className="Paragraph">
                                    Note that if the option "Sentiment ratio" is selected under "Sentiment", a country
                                    will be
                                    shown as positive (i.e in green) if the data for this country contains more positive
                                    than negative tweets
                                    (see next Figure). Conversely, it will be shown as negative (i.e. in red) if the
                                    data contains more negative
                                    than positive tweets. The exact formula used to calculate the ratio is:
                                    (N(positive) - N(negative)) / (N(positive) + N(negative) + N(neutral))
                                    , where the "N(sentiment)" corresponds to the number of tweets with this sentiment
                                    (e.g.
                                    "N(positive)" is the number of positive tweets).
                                </p>

                                <div className="ImageContainer">
                                    <img src={map_sentiment_ratio} alt="MapSentimentRatio" className="MediumImage"/>
                                </div>

                                <p className="Paragraph">
                                    The "Method" menu (see 6) allows you to specify whether you want the data shown to
                                    correspond to
                                    either 1) the users' location ("Users") or the tweets' location ("Tweets"). This is
                                    because Twitter
                                    allows users to declare locations in two ways. Authors can declare a location for
                                    their account, in
                                    which case we assume all of their tweets share this location. Or authors can declare
                                    a location when
                                    posting a specific tweet. Note that declaring a location is optional so the majority
                                    of the data will
                                    usually not have a location and therefore not appear on this map.
                                </p>

                                <p className="Paragraph">
                                    You can click on a specific country to generate a new report (in a new tab) for the
                                    subset of the current data
                                    that corresponds to this specific country, keyword (from "Keyword" filter),
                                    sentiment (if "Filter" is set to
                                    "Sentiments") and language (if "Filter" is set to "Languages").
                                </p>

                                <p className="Paragraph">
                                    Finally, the 5 interactivity buttons at the top right corner of the visualisation
                                    (see 7) allow
                                    you to 1) save the plot as PNG file on your local machine, 2) to pan over the plot,
                                    3) to zoom in, 4) to zoom
                                    out and 5) to reset the axes (from left to right).
                                </p>
                            </AccordionContent>

                            <AccordionTitle
                                active={topContentA}
                                onClick={(e, {value}) => {
                                    setTopContent(!topContentA)
                                }}
                                className="h3TitleContainer"
                            >
                                <h3 className="h3Title"><Icon name={(topContentA ? "angle down" : 'angle right')}/>F.
                                    Top Content</h3>
                            </AccordionTitle>
                            <AccordionContent active={topContentA}>
                                <p className="Paragraph">
                                    The Top Content component shows the most popular content in the dataset as a table.
                                    For Twitter (X) data, the table contains the most retweeted tweets, the most
                                    retweeted users,
                                    the most frequent URLs, the most frequent media (i.e. images, videos) and the most
                                    frequent emojis in the data. For YouTube data on the other hand, it contains the
                                    most
                                    replied to comments, the most replied to users and the most frequent emojis. By
                                    default,
                                    results are shown in groups of 5. You can navigate to the
                                    next page of results by clicking on arrows at the bottom right of the table (see 1
                                    on Figure).
                                </p>

                                <div className="ImageContainer">
                                    <img src={top_content_tweets} alt="TopContentTweets" className="MediumImage"/>
                                </div>

                                <p className="Paragraph">
                                    If more than one keyword was provided, you can use the "Keyword" filter (see 2) to
                                    display results for
                                    each keyword independently, as well as for all keywords together. The volume for all
                                    the
                                    keywords is either labelled "Any keyword" or "All keywords" depending on the option
                                    selected for the
                                    keyword filter in the input header.
                                </p>

                                <p className="Paragraph">
                                    Use the "Sentiment" filter (see 3) to filter the results shown by sentiment. Note
                                    that the
                                    sentiment is obtained from the tweet/YouTube comment text only.
                                </p>

                                <p className="Paragraph">
                                    The "Tweets" (for Twitter datasets)/"Comments" (for YouTube datasets) tab (see 4)
                                    shows the most retweeted tweets/replied to comments in the current search (capped at
                                    30,000).
                                    Clicking on a tweet/comment ID (4a) will open the corresponding post on Twitter
                                    (X)/Youtube in a new tab (note that
                                    the screenshot shows an anonymised dataset where this will not work correctly). The
                                    number of
                                    retweets/replies (see 4b) corresponds to the retweets/replies for the given post in
                                    the whole dataset (not just the
                                    current search). For Twitter data, the location (see 4c) is the country declared as
                                    the location by the author when
                                    they posted the tweet.
                                </p>

                                <div className="ImageContainer">
                                    <img src={top_content_users} alt="TopContentUsers" className="MediumImage"/>
                                </div>

                                <p className="Paragraph">
                                    The "Users" tab (see 5 above) shows the most retweeted/replied to users who posted a
                                    tweet/YouTube comment contained in the
                                    current search (capped at 30,000). Clicking on a user screen name (see 5a) will open
                                    the corresponding
                                    user profile on Twitter (X) in a new tab (note that the screenshot shows an
                                    anonymised dataset where
                                    this will not work correctly). The number of retweets/replies (see 5b) corresponds
                                    to the retweets/replies
                                    for the user in the whole dataset (not just the current search). For Twitter data,
                                    the location (see 5c) is the location
                                    declared associated with the author's profile, not the location of their tweets.
                                    Note that, for Twitter data, users that have retweeted but not tweeted are not
                                    shown. Moreover, when filtering by
                                    sentiment, the users shown are those that authored at least one tweet/comment with
                                    the chosen sentiment in
                                    the current search. As such, if the same user authored several tweets/comments with
                                    different sentiments, they
                                    will appear under several sentiment values.
                                </p>

                                <div className="ImageContainer">
                                    <img src={top_content_urls} alt="TopContentURLs" className="MediumImage"/>
                                </div>

                                <p className="Paragraph">
                                    The URLs tab (see 6 above) shows the most retweeted/frequent URLs contained in the
                                    current search (capped at
                                    150). Clicking on a URL (see 6a) will open it in a new tab.
                                </p>

                                <p className="Paragraph">
                                    The Media tab (see 7) on the other hand shows the most retweeted/frequent media
                                    (i.e. images, videos)
                                    contained in the current search (capped at 150). Just like for URLs tab, clicking on
                                    a media URL will open it
                                    in a new tab.
                                </p>

                                <p className="Paragraph">
                                    Finally, the Emojis tab (see 8) shows the most retweeted/frequent emojis contained
                                    in the current
                                    search (capped at 150).
                                </p>

                                <div className="ImageContainer">
                                    <img src={top_content_menu} alt="TopContentMenu" className="SmallImage"/>
                                </div>


                                <p className="Paragraph">
                                    Across all tabs (e.g. "Tweets"/"Comments", "Users", "URLs"), when hovering over a
                                    column header, three dots
                                    appear on the right of the column name (see 9). Clicking on these three dots opens a
                                    menu which lets
                                    you sort the data by that column in ascending order (see 9a), sort in descending
                                    order (see 9b) or
                                    lets you filter the data (see 9c).
                                </p>
                            </AccordionContent>

                            <AccordionTitle
                                active={wordcloudA}
                                onClick={(e, {value}) => {
                                    setWordcloud(!wordcloudA)
                                }}
                                className="h3TitleContainer"
                            >
                                <h3 className="h3Title"><Icon name={(wordcloudA ? "angle down" : 'angle right')}/>G.
                                    Wordclouds</h3>
                            </AccordionTitle>
                            <AccordionContent active={wordcloudA}>
                                <p className="Paragraph">
                                    The Wordcloud component shows the most frequent words or emojis in the data in the
                                    form of a
                                    wordcloud (see 1 on Figure). Clicking on any word or emoji will generate a new
                                    report (in a new tab),
                                    where the clicked word/emoji will have been appended to the current keyword(s). Note
                                    that, if the
                                    "Any keyword" option was initially selected in the input for the current report, the
                                    new report will
                                    correspond to a superset of the current data: i.e. the current tweets/YouTube
                                    comments plus the tweets/comments including the
                                    new keyword. If on the other hand the "All keyword" option was selected, the new
                                    report will be a
                                    subset of the current data: i.e. only the current tweets/comments that also include
                                    the new keyword.
                                </p>

                                <div className="ImageContainer">
                                    <img src={wordcloud} alt="Wordcloud" className="MediumImage"/>
                                </div>

                                <p className="Paragraph">
                                    The "Field" menu (see 2) defines which field is used to generate the wordcloud.
                                    "Tweet"/"Comment" means the
                                    content of tweets/YouTube comments in the current search is used.
                                    "User descriptions" (only available for Twitter datasets) means the descriptions of
                                    users who have
                                    authored at least one tweet in the current search are used. "Hashtags" means the
                                    hashtags of the tweets/comments are
                                    used. If "Emojis" is selected, the emojis contained in the tweets/comments are used.
                                    Note that if either "Tweet"/"Comment" or
                                    "User descriptions" is selected under "Field", a toggle will appear (see 3) allowing
                                    you to filter out stop
                                    words from the wordcloud. Stop words are common words that serve a grammatical role
                                    but don't carry much
                                    meaning: e.g. "the", "for", "a", "to", "what", etc.
                                </p>

                                <p className="Paragraph">
                                    If more than one keyword was provided, you can use the "Keyword" filter (see 4) to
                                    display results for
                                    each keyword independently, as well as for all keywords together. The volume for all
                                    the
                                    keywords is either labelled "Any keyword" or "All keywords" depending on the option
                                    selected for the keyword
                                    filter in the input header.
                                </p>

                                <p className="Paragraph">
                                    The "Sentiment" filter (see 5) allows you to see the most prevalent terms for each
                                    sentiment.
                                    The options "Common terms in negative/positive/neutral" tweets/YouTube comments will
                                    display words that are very
                                    frequent for that sentiment, but not necessarily characteristic of it: e.g. if the
                                    word "football" is
                                    generally very frequent, it might appear in the wordcloud for positive
                                    tweets/comments but also negative and
                                    neutral tweets/comments. The option "Most negative/positive terms", on the other
                                    hand, will display words that
                                    are characteristic of this sentiment: i.e. frequent in tweets/comments with this
                                    sentiment but infrequent for
                                    other sentiments.
                                </p>

                                <div className="ImageContainer">
                                    <img src={wordcloud_topics} alt="WordcloudTopics" className="MediumImage"/>
                                </div>

                                <p className="Paragraph">
                                    If the Topic Discovery was generated with a number of topics greater than 0 (see the
                                    "Topic Discovery" section
                                    below for more information about this), the "Topics" option will also appear under
                                    the "Field" menu (see 6).
                                    This allows the analysts to see the most common terms in the text of tweets/YouTube
                                    comments that compose each
                                    topic. The "Topic" menu (see 7) then allows the analyst to choose the topic they
                                    want to see a
                                    wordcloud for. <b>Note</b>: This would only be visible <b>after</b> generating the Topic Discovery visualisation.
                                </p>

                                <div className="ImageContainer">
                                    <img src={wordcloud_communities} alt="WordcloudCommunities"
                                         className="MediumImage"/>
                                </div>

                                <p className="Paragraph">
                                    In the case of Twitter (X) data, if the Social Network Analysis was generated (see the "Social Network Analysis"
                                    section
                                    below for more information about this), the "Community user descriptions" option
                                    will also appear under the
                                    "Field" menu (see 8 above). This allows the analysts to see the most common terms in
                                    the user
                                    descriptions of users belonging to each community. The "Community" menu (see 9) then
                                    allows the
                                    analyst to choose the community they want to see a wordcloud for. <b>Note</b>: This would only be visible <b>after</b> generating the Social Network Analysis visualisation, and
                                    is only available for Twitter (X) data (not for YouTube data).
                                </p>
                            </AccordionContent>

                            <AccordionTitle
                                active={topicModellingA}
                                onClick={(e, {value}) => {
                                    setTopicModelling(!topicModellingA)
                                }}
                                className="h3TitleContainer"
                            >
                                <h3 className="h3Title"><Icon name={(topicModellingA ? "angle down" : 'angle right')}/>H.
                                    Topic Discovery</h3>
                            </AccordionTitle>
                            <AccordionContent active={topicModellingA}>
                                <p className="Paragraph">
                                    The Topic Discovery component allows the user to visualise the data from the current
                                    search in
                                    semantic space: i.e. tweets/YouTube comments that are semantically similar are
                                    located close to each
                                    other. Tweets/comments are
                                    represented as dots in the visualisation. Hovering over a dot will display the
                                    tweet/comment. Clicking on a
                                    datapoint will open the tweet/comment on Twitter (X)/YouTube in a new tab.
                                </p>

                                <div className="ImageContainer">
                                    <img src={topic_discovery} alt="TopicDiscovery" className="ImageLarge"/>
                                </div>

                                <p className="Paragraph">
                                    The content of this visualisation is not shown by default for performance reasons.
                                    Instead, the user must
                                    click on the "Generate" button (see 1 on Figure) to create the visualisation.
                                    Specifying a number of topics
                                    greater than zero under the "Nb topics" field (see 2) before generating will enable
                                    the clustering
                                    the tweets/YouTube comments into this given number of topics, visually signified
                                    with different
                                    colors in the graph
                                    (see 4). If the Social Network Analysis visualisation has been generated (see "J.
                                    Social Network Analysis"
                                    below) a toggle (see 3) will also be available allowing the Topic Discovery
                                    visualisation to only show posts by the
                                    main communities (i.e. the communities shown in the Social Network Analysis
                                    visualisation). Note that enabling the "Main communities only" toggle will not automatically
                                    display the "filtered" version of the visualisation (i.e. containing only
                                    posts from the main communities). Instead, you will need the "Generate" button again
                                    to generate this new visualisation. The number of
                                    tweets/comments shown in the visualisation is capped at 100,000. These are randomly
                                    sampled if the volume for the current search exceeds this threshold (see 5).
                                </p>

                                <div className="ImageContainer">
                                    <img src={topic_discovery_w_claim} alt="TopicDiscoveryWClaim"
                                         className="ImageLarge"/>
                                </div>

                                <p className="Paragraph">
                                    Specifying a claim in the "Claim" input field (see 6 above) will flag up the
                                    location of tweets/comments
                                    similar to the claim in the visualisation. This is shown as a large black dot (see
                                    7).
                                </p>

                                <p className="Paragraph">
                                    If more than one keyword was provided, you can use the "Keyword" filter (see 8) to
                                    display results for
                                    each keyword independently, as well as for all keywords together. The volume for all
                                    the
                                    keywords is either labelled "Any keyword" or "All keywords" depending on the option
                                    selected for the
                                    keyword filter in the input header. Moreover, the "Sentiment" filter (see 9 in
                                    Figure) allows
                                    you to filter the visualisation for each sentiment. Finally the "Community" filter
                                    (see 10) allows the user
                                    to focus on the posts from specific communities in the visualisation. This last
                                    filter will only appear
                                    if the Social Network Analysis visualisation has been generated (see "J. Social
                                    Network Analysis" below).
                                </p>

                                <p className="Paragraph">
                                    Clicking on the "Rename topics" button (see 11) will make a pop-up window appear
                                    (see
                                    below). You can use the fields in this window (see 12) to rename topics. Clicking
                                    on "Close" (see 13) will make the pop up disappear without applying the changes.
                                    If you were to re-open the pop-up, the fields previously filled will still contain
                                    the
                                    same text. Clicking on "Update topic names" (see 14) will apply the changes
                                    everywhere in the report. Topics that are not given a new name simply keep the
                                    same name. You can rename topics as often as you like.
                                </p>

                                <p className="Paragraph">
                                    Once you have generated the Topic Discovery, you can go to the
                                    Wordcloud component (see Wordcloud section above) to see a wordcloud for each topic
                                    by selecting "Topics" under the "Field" filter. The information shown in these
                                    wordclouds is useful when renaming the topics.
                                </p>

                                <p className="Paragraph">
                                    <b style={{color: "red"}}>Important</b>: The new topic names <b>will</b> be lost if
                                    you: 1) generate a new Topic Discovery visualisation (e.g. after
                                    changing the number of topics), 2) generate a new report altogether, 3) re-load the
                                    page, 4) log out of the dashboard. If you
                                    want to save the current version of the Topic Discovery visualisation with renamed
                                    topics, please use the "Save report" button at the very top of the report.
                                    You will then be able to re-load the report from the "Load Report" page.
                                </p>

                                <div className="ImageContainer">
                                    <img src={renaming_topics} alt="RenamingTopics" className="MediumImage"/>
                                </div>


                                {/*<p className="Paragraph">*/}
                                {/*  <b>Note 2</b>: To obtain the position of tweets in this semantic space, we first use the*/}
                                {/*  "all-mpnet-base-v2" transformer-based language model from the SBERT library (Reimers & Gurevych, 2019)*/}
                                {/*  to obtain a vector represention for each tweet (i.e. embeddings). We then use the UMAP algorithm to*/}
                                {/*  reduce these vector to 5 dimensions (for the clustering step) and then to 2 dimensions (to determine*/}
                                {/*  the exact position of each datapoint in the visualisation). These steps are performed once during the*/}
                                {/*  pre-processing of the data.*/}
                                {/*</p>*/}

                                <p className="Paragraph">
                                    <b>Note</b>: To obtain the position of tweets/YouTube comments in this semantic
                                    space, we used an
                                    AI model to represent each tweet/comment as a vector of numerical values, called an
                                    embedding. We then used a simple algorithm to transform this vector into a smaller
                                    vector containing only two values. These correspond to the y-axis and x-axis
                                    coordinates of each tweet/comment in the visualisation. The "similarity" of
                                    tweets/comments and
                                    whether they should be grouped into the same topic is decided simply based on these
                                    values.
                                </p>

                            </AccordionContent>

                            <AccordionTitle
                                active={topicsPerCommunityA}
                                onClick={(e, {value}) => {
                                    setTopicsPerCommunity(!topicsPerCommunityA)
                                }}
                                className="h3TitleContainer"
                            >
                                <h3 className="h3Title"><Icon
                                    name={(topicsPerCommunityA ? "angle down" : 'angle right')}/>I.
                                    Topics per community</h3>
                            </AccordionTitle>
                            <AccordionContent active={topicsPerCommunityA}>
                                <p className="Paragraph">
                                    The "Topic per community" component is only visible if the user has already
                                    generated both the "Topic Discovery" visualisation with a number of topics greater
                                    than 0 (see "H. Topic Discovery" above) and the "Social Network Analysis"
                                    visualisation (see "J. Social Network Analysis" below). This component allows the
                                    user to visualise the prevalence of different topics in the posts
                                    published by each of the main communities identified using the Social Network
                                    Analysis.
                                </p>

                                <div className="ImageContainer">
                                    <img src={topics_per_community} alt="TopicsPerCommunity" className="ImageLarge"/>
                                </div>

                                <p className="Paragraph">
                                    If more than one keyword was provided, you can use the "Keyword" filter (see 1) to
                                    display results for each keyword independently, as well as for all keywords together
                                    ("All keywords"). The volume for all the keywords is either labelled "Any keyword"
                                    or "All keywords" depending on the option selected for the keyword filter in the
                                    input header.
                                </p>

                                <p className="Paragraph">
                                    The "Sentiment" filter (see 2) allows you to see the distribution of topics per
                                    community for each sentiment independently.
                                </p>

                                <p className="Paragraph">
                                    You can use the "Percentage" toggle (see 3) to display the results as percentages
                                    per day instead of counts.
                                </p>

                            </AccordionContent>

                            <AccordionTitle
                                active={socialNetworkA}
                                onClick={(e, {value}) => {
                                    setSocialNetwork(!socialNetworkA)
                                }}
                                className="h3TitleContainer"
                            >
                                <h3 className="h3Title"><Icon name={(socialNetworkA ? "angle down" : 'angle right')}/>J.
                                    Social Network Analysis</h3>
                            </AccordionTitle>
                            <AccordionContent active={socialNetworkA}>
                                <p className="Paragraph">
                                    The Social Network Analysis components allows the user to visualise the "proximity"
                                    between accounts contained in the current search, as measured by the number
                                    of times they have interacted with each other in the dataset: i.e. accounts interact
                                    a lot are located closer to each other while those who don't are located further
                                    apart. Users are represented as dots in the visualisation. In the context of Twitter
                                    dataset, these interactions can either be retweets
                                    or replies whereas in the context of YouTube data these can only be replies. The
                                    visualisation also shows the community each account belongs to as inferred from
                                    these interactions in the overall dataset. Hovering over a dot will display the
                                    user's description (if available) as well as the community number. Clicking on a
                                    datapoint will open the user's profile on Twitter (X) in a new tab.
                                </p>

                                <div className="ImageContainer">
                                    <img src={social_network} alt="SocialNetwork" className="MediumImage"/>
                                </div>

                                <p className="Paragraph">
                                    Note that the community an account is labelled by does not depend on the current
                                    search query: e.g. community "1" in the context of a search about "Qatar" will
                                    also be community "1" in the context of a search about "Messi".
                                </p>

                                <p className="Paragraph">
                                    The Social Network Analysis visualisation is not shown by default for performance
                                    reasons. Instead, the user must first choose the type of interaction they want to
                                    generate the network for: i.e. retweet or replies for Twitter datasets, replies
                                    for YouTube datasets (see 1). The "Nb communities" field (see 2) on the other hand
                                    defines how many of the most active communities should be highlighted in the
                                    visualisation (10 by default). Once the relevant options
                                    are selected, click on the "Generate" button (see 3) to create the visualisation.
                                    Visually, different communities are signified with different
                                    colors in the graph (see 4). Users shown in grey are those that belong to
                                    communities that are not in the top N most active, where N is the number of
                                    communities defined in the "Nb communities" field.
                                </p>

                                <p className="Paragraph">
                                    If more than one keyword was provided, you can use the "Keyword" filter (see 5)
                                    to display results for
                                    each keyword independently, as well as for all keywords together. The volume for
                                    all the
                                    keywords is either labelled "Any keyword" or "All keywords" depending on the
                                    option selected for the
                                    keyword filter in the input header.
                                </p>

                                <p className="Paragraph">
                                    Clicking on the "Rename communities" button (see 6) will make a pop-up window
                                    appear (see below). You can use the fields in this window to rename communities
                                    (see 7). Clicking on "Close" (see 8) will make the pop up disappear without applying
                                    the changes. If you were to re-open the pop-up, the fields previously filled will
                                    still contain the same text. Clicking on "Update community names" (see 9) will
                                    apply the changes everywhere in the report. Communities that are not given a new
                                    name simply keep the same name. You can rename communities as often as you like.
                                    The "Reset community names" button allows you to disregard all renaming of
                                    communities and return to the original number label for each community.
                                    <b style={{color: "red"}}> Warning</b>: this cannot be undone.
                                </p>

                                <div className="ImageContainer">
                                    <img src={renaming_communities} alt="RenamingCommunities" className="MediumImage"/>
                                </div>

                                <p className="Paragraph">
                                    Once you have generated the Social Network Analysis, you can go to the Wordcloud
                                    component (see Wordcloud section above) to see a wordcloud from the user
                                    descriptions of users from each community by selecting "Community user
                                    descriptions" under the "Field" filter. You can also go to the Language
                                    component (see Languages graph section above) to see the languages spoken by each
                                    community, and to the Map component and select "Communities" under "Filter" to see
                                    the geolocation of members from different communities. The information
                                    shown in these different visualisation is useful when renaming the communities.
                                </p>

                                <p className="Paragraph">
                                    <b style={{color: "red"}}>Important considerations</b>:
                                </p>
                                <p className="Paragraph">
                                    <ul>
                                        <li>
                                            Community names that you have saved are visible only to yourself, not to
                                            other users.
                                        </li>
                                        <li>
                                            Communities will persist for new
                                            reports/queries. This can lead situations where the name of a community
                                            that was defined in the context of a specific search does not fit in the
                                            context of a different search. For instance: communities labelled in the
                                            context of a search focused on Messi might not make sense in the context
                                            of a search focused on Ronaldo. In general, we recommend that the user
                                            names communities while none of the filters are active (i.e. to provide the
                                            most general labels).
                                        </li>
                                        <li>
                                            The exact position of each user in the Social Network Analysis visualisation
                                            and the community each user is assigned to is re-processed each time data is
                                            added to the system (see "Pre-processing" section below). While we "align"
                                            communities across pre-processing timesteps, this means that communities
                                            can disappear. Moreover, community descriptions might become
                                            unrepresentative as communities morph. If you would like to save an exact
                                            snapshot of the current Social Network Analysis, we recommend saving the
                                            report using the "Save report" button at the top of the report. This can
                                            then be re-loaded from the "Load Report" page.
                                        </li>
                                    </ul>
                                </p>


                                {/*<p className="Paragraph">*/}
                                {/*  <b>Note 2</b>: The algorithm used to obtain the positioning of users based on their retweets is*/}
                                {/*  ForceAtlas2 by Jacomy et al. (2014) and the one used to infer their community is the Louvain*/}
                                {/*  algorithm by Blondel et al. (2008). These are used once during the pre-processing of the data.*/}
                                {/*</p>*/}

                                <p className="Paragraph">
                                    <b>Note</b>: The algorithm used to obtain the positioning of users based on
                                    their retweets/replies can be likened to a physics simulation, where nodes (i.e.
                                    users) repel each unless they are tied to each other by retweets/replies, in which
                                    case the "weight" of these ties (i.e. the number of retweets/replies between two
                                    users) is proportional to how much the nodes attract each other.
                                </p>
                            </AccordionContent>

                            <AccordionTitle
                                active={tweetingA}
                                onClick={(e, {value}) => {
                                    setTweeting(!tweetingA)
                                }}
                                className="h3TitleContainer"
                            >
                                <h3 className="h3Title"><Icon name={(tweetingA ? "angle down" : 'angle right')}/>K.
                                    Tweeting/Comments per community</h3>
                            </AccordionTitle>
                            <AccordionContent active={tweetingA}>
                                <p className="Paragraph">
                                    The "Tweeting/Comments per community" component shows the number of tweets posted
                                    over time
                                    by each of the
                                    communities highlighted in the Social Network Analysis visualisation (see 1 on
                                    Figure). Importantly, for Twitter data,
                                    this visualisation does <b>not</b> count retweets: this means that a given community
                                    might appear
                                    less active in this visualisation than in the previous "Social Network Analysis"
                                    visualistion. This
                                    component is only shown once the Social Network Analysis component has been
                                    generated (by clicking on
                                    the "Generate" button, see "Social Network Analysis" section above for more
                                    information).
                                </p>

                                <div className="ImageContainer">
                                    <img src={communities_tweeting} alt="CommunitiesTweeting" className="MediumImage"/>
                                </div>

                                <p className="Paragraph">
                                    Click on a community in the legend (see 2) to hide/show its line, and double-click
                                    on it to make it
                                    the only visible line.
                                </p>

                                <p className="Paragraph">
                                    If more than one keyword was provided, you can use the "Keyword" filter (see 3) to
                                    display results for
                                    each keyword independently, as well as for all keywords together. The volume for all
                                    the keywords is
                                    either labelled "Any keyword" or "All keywords" depending on the option selected for
                                    the keyword
                                    filter in the input header.
                                </p>

                                <p className="Paragraph">
                                    The four interactivity buttons at the top right corner of the visualisation (see 4)
                                    allow you to 1)
                                    save the plot as PNG file on your local machine, 2) to select an area of the plot to
                                    zoom in on it, 3) to pan
                                    over the plot and 4) to reset the axes (from left to right).
                                </p>
                            </AccordionContent>

                            <AccordionTitle
                                active={statsA}
                                onClick={(e, {value}) => {
                                    setStats(!statsA)
                                }}
                                className="h3TitleContainer"
                            >
                                <h3 className="h3Title"><Icon name={(statsA ? "angle down" : 'angle right')}/>L.
                                    Communities stats</h3>
                            </AccordionTitle>
                            <AccordionContent active={statsA}>
                                <p className="Paragraph">
                                    The "Communities stats" component shows statistics for each community. These include
                                    the number of accounts in the community for the current search, the average number
                                    of tweets/comments per account, the average number of retweets/replies per
                                    tweet/comment and the screen name of the 10 most retweeted/replied-to accounts in
                                    the community. Clicking on a user screen name (see 1 on Figure) will open the
                                    Twitter
                                    profile/YouTube channel on Twitter/X or YouTube in a new tab.
                                </p>

                                <div className="ImageContainer">
                                    <img src={communities_stats} alt="CommunitiesStats" className="MediumImage"/>
                                </div>

                                <p className="Paragraph">
                                    If more than one keyword was provided, you can use the "Keyword" filter (see 2) to
                                    display results for
                                    each keyword independently, as well as for all keywords together. The volume for all
                                    the keywords is
                                    either labelled "Any keyword" or "All keywords" depending on the option selected for
                                    the keyword
                                    filter in the input header.
                                </p>

                                <p className="Paragraph">
                                    One community might have a negative number (e.g. see 3). This community would then
                                    correspond to all the users that were not assigned a community. This would
                                    include users who have not retweeted/replied to other users (or retweeted/replied
                                    very rarely) and/or were never retweeted/replied to (or
                                    very little) in the whole dataset.
                                </p>

                                <p className="Paragraph">
                                    Clicking on a user screen name (see 2) will open the Twitter profile/YouTube on
                                    Twitter/X or YouTube in a new tab. Moreover, by default, results are shown in groups
                                    of 5. You can navigate to the next page of results by clicking on arrows at the
                                    bottom right of the table (see 4).
                                </p>
                            </AccordionContent>
                        </Accordion>
                    </AccordionContent>


                    <AccordionTitle
                        active={loadPage}
                        onClick={(e, {value}) => {
                            setLoadPage(!loadPage)
                        }}
                        className="h2TitleContainer"
                    >
                        <h2><Icon name={(loadPage ? "angle down" : 'angle right')}/>Load Report page</h2>
                    </AccordionTitle>
                    <AccordionContent active={loadPage}>
                        <p className="Paragraph">
                            The Load Report page, accessible via the navigation bar at the top left corner of the
                            dashboard, allows the user to view past searches that they have saved via the "Save report"
                            button (see "Analysis page" section above for more information) and load them again in a
                            new tab.
                        </p>

                        <div className="ImageContainer">
                            <img src={load_report} alt="LoadReport" className="MediumImage"/>
                        </div>

                        <p className="Paragraph">
                            When the user opens the Load Report page, they need to click on the "Get Reports" button
                            (see 1 on Figure) to load the table containing their saved past searches/reports. Each row
                            in this table corresponds to a search/report.
                        </p>

                        <p className="Paragraph">
                            The "Report Name" column (see 2) shows the name of the report, as defined by the analyst
                            when they
                            originally saved their search. When clicking on a report name, the report gets re-generated
                            in a new tab.
                            Depending on the amount of data needed to re-generate the report, the page can take between
                            a few seconds and
                            a few minutes to load.
                        </p>

                        <p className="Paragraph">
                            Each row also displays the values for the input filters originally used to create the report
                            (i.e. source
                            dataset, keywords, dates, sentiment) as well as the date when the report was saved (see 3).
                        </p>

                        <p className="Paragraph">
                            The user can select reports (see 4) and then click on the "Delete Selected Reports" button
                            (see 5) to delete
                            them.
                        </p>

                        <p className="Paragraph">
                            By default, saved reports are shown in groups of 5. You can navigate to the next page of
                            results by clicking on arrows at the bottom right of the table (see 6).
                        </p>

                        <p className="Paragraph">
                            Just as for the tables shown on the Analysis page, every column is sortable and filterable.
                            To sort or filter
                            the saved reports, hover over a column header. Three dots appear on the right of the column
                            name. Clicking on
                            these three dots opens a menu which lets you sort the data in ascending or descending order
                            and lets you
                            filter the data.
                        </p>

                        <p className="Paragraph">
                            <b>Important</b>: When loading a saved report, what is shown is an <b>exact snapshot</b> of
                            the report as it was displayed when it was saved. This means the Social Network Analysis
                            visualisation, community names or Topic Discovery visualisation might be quite different
                            from those shown if you were to generate a new report with the exact same filters. This is
                            due to the pre-processing steps that need to be re-run each time new data is added to the
                            system (see "Daily data pre-processing" section below). Moreover, the loaded report is
                            "static" meaning that you won't be able to change the Topic Discovery or Social Network
                            Analysis visualisations by changing the number of topics/communities/adding a claim.
                        </p>
                    </AccordionContent>

                    <AccordionTitle
                        active={admin}
                        onClick={(e, {value}) => {
                            setAdmin(!admin)
                        }}
                        className="h2TitleContainer"
                    >
                        <h2><Icon name={(admin ? "angle down" : 'angle right')}/>Admin page</h2>
                    </AccordionTitle>
                    <AccordionContent active={admin}>
                        <p className="Paragraph">
                            The Admin page, accessible via the navigation bar at the top left corner of the dashboard,
                            is only visible to and accessible by the administrator of the dashboard. This page allows
                            them to manage access to the tool by other users, as well as to manage the pre-processing
                            of the data in the back-end. Note that the Login/Logout system implemented for the
                            dashboard is intended as a way for users to keep their saved reports separate, and not as a
                            comprehensive layer of security. As such, please do not reuse a password that you have used
                            elsewhere.
                        </p>

                        <p className="Paragraph">
                            To view existing users, the administrator should first click on the "Get Current Users"
                            button (see 1 on Figure) under the "Current Users" tab to display a table with a list of
                            users. Each row in this table corresponds to a different user.
                        </p>

                        <div className="ImageContainer">
                            <img src={get_users} alt="GetUsers" className="MediumImage"/>
                        </div>

                        <p className="Paragraph">
                            The administrator can select users (see 2) and then click on the "Delete Selected User"
                            button (see 3) to delete them. By default, users are shown in groups of 5. You can navigate
                            to the next page of users by clicking on arrows at the bottom right of the table (see 4).
                        </p>

                        <p className="Paragraph">
                            To register a new user, the administrator needs to go to the "Add user" tab. They can then
                            simply provide a username in the "Username" field (see 5), an associated password in the
                            "Password" field (see 6) and click on the "Add User" button (see 7). Note
                            that the username can only contain letters and digits.
                        </p>

                        <div className="ImageContainer">
                            <img src={add_user} alt="AddUser" className="MediumImage"/>
                        </div>

                        <p className="Paragraph">
                            Finally, the "Processing Settings" page allows the admin user to explicitly request for the
                            pre-processing steps described in the "Daily data pre-processing" section below to be
                            applied to the whole dataset again, as if it were all new data. The "Dataset" filter (see 8)
                            allows the admin user to define the dataset for which the pre-processing needs to run again.
                            Checking the "Re-run pre-processing for all data" (see 9) will request for the Sentiment
                            Classification and Country Identification steps to be re-run (see "Daily data
                            pre-processing" below). Checking the "Re-run Topic Modelling Analysis" (see 10) will
                            request for the Topic Discovery related steps to be re-run. Finally, checking the "Re-run
                            Network Analysis" will request for the Social Network Analysis related to be re-run. Note
                            that Topic Discovery or Social Network Analysis visualisations might look completely
                            different after re-running the related pre-processing steps. Moreover, saved community
                            names will be lost when re-running the Social Network Analysis steps.
                        </p>

                        <div className="ImageContainer">
                            <img src={reprocessing} alt="ReProcessing" className="MediumImage"/>
                        </div>
                    </AccordionContent>

                    <AccordionTitle
                        active={preprocessing}
                        onClick={(e, {value}) => {
                            setPreprocessing(!preprocessing)
                        }}
                        className="h2TitleContainer"
                    >
                        <h2><Icon name={(preprocessing ? "angle down" : 'angle right')}/>Daily data pre-processing</h2>
                    </AccordionTitle>
                    <AccordionContent active={preprocessing}>
                        <p className="Paragraph">
                            Before being available in the SocioXplorer dashboard, new data needs to be pre-processed. The
                            pre-processing includes the following steps:
                        </p>

                        <p className="Paragraph">
                            <b>1. Sentiment classification</b>: Every new datapoint (i.e. YouTube comment or
                            tweet) is labelled with one of the following sentiment labels: "Positive",
                            "Negative", "Neutral", "Non-Text" (e.g. punctuation or emojis) or "Other Language"
                            (if it not written in a language supported by the sentiment classification model).
                            The sentiment classification model used is <a
                            href="https://huggingface.co/cardiffnlp/twitter-xlm-roberta-base-sentiment"
                            target="_blank">"twitter-xlm-roberta-base-sentiment"</a> from
                            CardiffNLP. The sentiment classification step for new data does not impact data already in
                            the system. Moreover, re-running this step for the whole dataset (i.e. by checking the
                            "Re-run pre-processing for all data" box on the "Processing Settings" Admin page) should
                            lead to very similar results.
                        </p>
                        <p className="Paragraph">
                            <b>2. Country identification</b>: In the context of Twitter data, user profiles can contain
                            geolocation information either in a dedicated "Location" field or the user's
                            self-decription.
                            These are not exact coordinates but rather free-form descriptions provided by the Twitter
                            users. Moreover, tweets are sometimes tagged with an exact location.
                            As a pre-processing step, we match these descriptions and coordinated to countries using a
                            dictionary method (e.g. the description "Paris, France" is mapped to the country "France").
                            location extraction step is performed for new data without impacting data already in the
                            system. Moreover, re-running this step for the whole dataset (i.e. by checking the
                            "Re-run pre-processing for all data" box on the "Processing Settings" Admin page) should
                            lead to very similar results.
                        </p>
                        <p className="Paragraph">
                            <b>3. Topic Discovery</b>: In order to be able to represent tweets/YouTube comments
                            in semantic space (see "Analysis > H. Topic Discovery" section above) we need to
                            run two pre-processing steps. The first is to turn the text of each new
                            tweet/comment into a 768-dimensional vector representation called an embedding.
                            To do this, we use the <a
                            href="https://huggingface.co/sentence-transformers/all-mpnet-base-v2" target="_blank">"all-mpnet-base-v2"
                            model </a>
                            from the <a href="https://sbert.net/index.html" target="_blank">SBERT library</a>. This
                            model can be applied to new data without impacting data already in the system.
                        </p>
                        <p className="Paragraph">
                            The second pre-processing step required is dimensionality
                            reduction: i.e. reducing the size of vectors from 768 to 5 dimensions, and then
                            to 2 dimensions. We do this because: 1) 768-dimensions embeddings would take a lot of space
                            in the Solr database are computationally and be inefficient to manipulate, whereas
                            5-dimensional ones take less space and are easier to manipulate while retaining much of the
                            information needed for clustering tweets/comments into topics, and 2) in the end
                            the visualisation shown to the analyst is in 2 dimensions. Normally, the dimensionality
                            reduction algorithm would consider the embeddings from the entirety of a dataset to
                            decide on the best way to reduce their dimensions without losing information.
                            However, this would be impossible to do with more than a few thousand datapoints.
                            Instead, we therefore use an approach called Parametric UMAP, which consists in
                            training a model on a subset of the data (~200K embeddings) and then applying it
                            to the rest of the dataset. This way, the dimensionality reduction model can also
                            be applied to new data without impacting data that is already in the system.
                        </p>
                        <p className="Paragraph">
                            However, it is important to note that as time passes and the dataset grows, the new
                            data might increasingly differ from the one the dimensionality reduction model was
                            trained on. This would lead to poorer results in the Topic Discovery visualisation.
                            We therefore give the option to the user with admin access to the SocioXplorer dashboard
                            to explicitly request for the model to be retrained on a new random training sample
                            that includes more recent datapoints (see "Admin page" section above). This would
                            then cause the 5-dimensional and 2-dimensional representations of all tweets/
                            comments to be updated.
                        </p>
                        <p className="Paragraph">
                            Note that re-running this step for the whole dataset (i.e. by
                            checking the "Re-run Topic Modelling Analysis" box on the "Processing Settings" Admin page)
                            might lead to visualisations that look completely different.
                        </p>
                        <p className="Paragraph">
                            <b>4. Social Network Analysis</b>: New tweets/YouTube comments might introduce new
                            relevant information for the Social Network Analysis. For instance, it might introduce new
                            users or new connections (replies or retweets) between users. For users that already appear
                            in the dataset, this new information would affect both their position in the Social Network
                            Analysis visualisation, and the community they are assigned to. In other words, as new data
                            is added into the system, <b>all</b> needs to be re-processed for the Social Network
                            Analysis.
                        </p>
                        <p className="Paragraph">
                            To provide consistency across pre-processing timesteps, we do the following two things:
                            instead of re-running the algorithm that determines users' position in the network from
                            scratch, we initialise the position of existing data from the last pre-processing timestep
                            to ensure their new position is as close to their previous ones as possible. Moreover, when
                            identifying the communities in the data, we align old communities with newer ones based on
                            their overlap and ensure that newer communities inherit their name from the old community
                            they match with (see "Community Alignment Algorithm" diagram below).
                        </p>

                        <div className="ImageContainer">
                            <img src={community_alignment} alt="CommunityAlignment" className="MediumImage"/>
                        </div>
                        <p className="Paragraph">
                            Note that re-running the Social Network Analysis pre-processing step for the whole dataset
                            (i.e. by checking the "Re-run Network Analysis" box on the "Processing Settings" Admin page)
                            might lead to visualisations that look completely different. Moreover, community
                            names saved by all users will be lost.
                        </p>
                    </AccordionContent>
                </Accordion>

            </div>
        </div>
    )
}
export default Help
