import os

import numpy as np
from sklearn.linear_model import LinearRegression
from flask import jsonify, make_response
import umap
from sklearn.cluster import KMeans
from sklearn.feature_extraction.text import CountVectorizer

from sentence_transformers import SentenceTransformer
from umap.parametric_umap import load_ParametricUMAP

from matplotlib.pyplot import get_cmap
from matplotlib.colors import rgb2hex

from bokeh.plotting import figure, show
from bokeh.models import HoverTool, ColumnDataSource, CategoricalColorMapper, ColorBar, CustomJSHover, OpenURL, TapTool, CustomJS
from bokeh.embed import json_item
from bokeh.document import Document
import traceback
from os.path import abspath, join
import sys
try:
    source_dir = abspath(join('../../'))
    sys.path.append(source_dir)
except Exception as exp:
    print("Solr Class Not Found, please make sure the solr_class.py file exists in the root folder!")
    print("exiting...")
    sys.exit(-1)
from solr_class import *
from utils import get_request_components, create_logger, print_this
logger = create_logger(f"Topic Modelling Utils", file=f"topic_modelling_utils")
CURRENT_PATH = os.path.dirname(__file__)
MAX_VOL = 100000
import os
try:
    source_dir = os.path.abspath(os.path.join('../../'))
    sys.path.append(source_dir)
except Exception as exp:
    print("Solr Class Not Found, please make sure the solr_class.py file exists in the root folder!")
    print("exiting...")
    sys.exit(-1)
from configs import ApplicationConfig, ApplicationPaths
logger.info("Loading models...")

CLASSIFIER = SentenceTransformer(ApplicationPaths.EMBEDDINGS_MODEL_PATH)

cores = ApplicationConfig.SOLR_CORES
EMBEDDERS_5D = dict()
EMBEDDERS_2D = dict()

"""
for core_ in cores:
    try:
        EMBEDDERS_5D[core_] = load_ParametricUMAP(os.path.join(CURRENT_PATH, 'embedder', core_))
        EMBEDDERS_2D[core_] = load_ParametricUMAP(os.path.join(CURRENT_PATH, 'embedder_2D', core_))
    except Exception as e:
        print(f"Error loading core {core_}: {e}. Trying fallback cores.")
        fallback_loaded = False
        # Exclude the current `core_` from `cores`
        for temp_core in [c for c in cores if c != core_]:
            try:
                EMBEDDERS_5D[core_] = load_ParametricUMAP(os.path.join(CURRENT_PATH, 'embedder', temp_core))
                EMBEDDERS_2D[core_] = load_ParametricUMAP(os.path.join(CURRENT_PATH, 'embedder_2D', temp_core))
                fallback_loaded = True
                break  # Exit fallback loop once successful
            except Exception as fallback_error:
                print(f"Error loading fallback core {temp_core}: {fallback_error}")
        if not fallback_loaded:
            print(f"Failed to load any fallback core for {core_}")
"""

for core_ in cores:
    try:
        EMBEDDERS_5D[core_] = load_ParametricUMAP(os.path.join(CURRENT_PATH, 'embedder', core_))
        EMBEDDERS_2D[core_] = load_ParametricUMAP(os.path.join(CURRENT_PATH, 'embedder_2D', core_))
    except:
        continue

logger.info("Models loaded successfully!")

"""This utils file contains all the function used by the topic_modelling API endpoint. """

def get_color(topic, cmap, max_label):
    """Function that returns the HEX color code for a topic given that topic's number, a colormap and the total
       number of topics.

    Args:
        :topic: (int) Topic number.
        :cmap: (matplotlib.colors.LinearSegmentedColormap) Matplotlib colormap.
        :max_label: (int) Total number of labels.

    Returns:
        :str: HEX color code
    """
    if topic == -1:
        return '#BDBDBD'
    return rgb2hex(cmap(topic/max_label))

def get_plot(df, bokeh_cmap=None, datasetOrigin=None):
    """Function that generates the Bokeh scatter plot used for the Topic Discovery component from the data contained in
    a dataframe and a given colormap.

    Args:
        :df: (pandas.DataFrame) Dataframe containing at least the columns "display_text" (tweet text to show on hover), \
            "x" and "y" (coordinates of tweet in scatter plot), "color" and "size" (visual features).
        :bokeh_cmap: (bokeh.models.CategoricalColorMapper, optional) Bokeh colormap object used to color datapoints in \
            the scatter plot based on their topic. If this argument is different from None, the \
            dataframe in df needs to have the column "Topic". Defaults to None.

    Returns:
        :bokeh.plotting.figure: Bokeh figure containing scatter plot of Topic Discovery
    """
    
    #logger.info(f"COLUMNS IN TM DATA: {df.columns}")
    from bokeh.models import ColumnDataSource, CustomJS, HoverTool, ColorBar, TapTool
    from bokeh.plotting import figure
    import pandas as pd

    # Ensure 'datasource' is created properly with correct column names
    if 'replyCommunity' in df.columns:
        if "videoId" in df.columns:
            columns = ["id", "videoId", "display_text", "Topic", "x", "y", "color", "size"] + [c for c in df.columns if c in ["retweetCommunity", "replyCommunity"]]
            datasource = ColumnDataSource(df[columns])
        else:
            columns = ["id", "display_text", "Topic", "x", "y", "color", "size"] + [c for c in df.columns if c in ["retweetCommunity", "replyCommunity"]]
            datasource = ColumnDataSource(df[columns])
    else:
        datasource = ColumnDataSource(pd.DataFrame(columns=["id", "videoId", "display_text", "Topic", "x", "y", "color", "size", "retweetCommunity", "replyCommunity"]))

    # Define plot
    plot_figure = figure(
        width=600,
        height=600,
        tools=('pan', 'reset', 'tap', 'box_zoom', 'wheel_zoom')
    )

    # JavaScript hover custom formatter
    custom_hov = CustomJSHover(code="""
        special_vars.indices = special_vars.indices.slice(0,4)
        if (special_vars.indices.indexOf(special_vars.index) >= 0)
        {
            return " "
        }
        else
        {
            return " hidden "
        }
    """)

    # JavaScript click callback for opening URLs dynamically
    url_base = "http://youtube.com/watch?v=" if datasetOrigin == "Comment" else "https://twitter.com/twitter/status/"
    callbackClick = CustomJS(args={'source': datasource, 'url_base': url_base}, code="""
        const selected = source.selected.indices;
        if (selected.length) {
            const index = selected[0];
            const id = source.data.id[index];
            const videoId = source.data.videoId ? source.data.videoId[index] : '';
            
            let full_url = url_base;
            if (videoId) {
                full_url += `${videoId}&lc=${id}`;  // For YouTube
            } else {
                full_url += id;  // For Twitter
            }
            window.open(full_url);
        }
    """)

    # Attach callback to TapTool
    taptool = plot_figure.select(type=TapTool)
    taptool.callback = callbackClick

    # Add hover tooltips
    hover_tooltips = """
    <div @y{custom}>
        <div style="padding-top:5px">
            <span style='font-size: 14px; color: #224499'>Text:</span>
            <span style='font-size: 14px'>@display_text</span>
        </div>
        <div style="padding-bottom:5px">
            <span style='font-size: 14px; color: #224499'>Topic:</span>
            <span style='font-size: 14px'>@Topic</span>
        </div>
    </div>
    """
    plot_figure.add_tools(HoverTool(tooltips=hover_tooltips, formatters={'@y': custom_hov}))

    # Add optional color bar if color mapping is provided
    if bokeh_cmap is not None:
        cb = ColorBar(color_mapper=bokeh_cmap, location=(5, 6), title="Topic Name")
        plot_figure.add_layout(cb, 'right')

    # Draw circles on the plot
    plot_figure.circle(
        'x',
        'y',
        source=datasource,
        color="color",
        line_alpha=0.6,
        fill_alpha=0.6,
        size='size'
    )

    # Style plot
    plot_figure.grid.visible = False
    plot_figure.axis.visible = False

    # Return the final figure
    return plot_figure


def get_topics_per_communities_plot(df, communities_list, interactionCommunity, topics_list=None):
    """Function that generates the Bokeh bar chart used for the Topics per Community component

    Args:
        :df: (pandas.DataFrame) Dataframe containing at least the columns "topic", "color" and columns containing \
            community labels for each network ("replyCommunity", "retweetCommunity") and the topic colors.
        :communities_list: (dict) Mapping between community numbers (as stored in Solr) and community names (as \
            saved by user in the front-end).
        :interactionCommunity: (str) Network type for which the community names (from communities_list) are for. Must \
            be one of "retweet" or "reply" (if Twitter dataset) or simply "reply" (if YouTube dataset)
        :topics_list: (dict) Mapping between topic numbers (as automatically generated from the K-means clustering \
            algorithm) and the topic names saved by the user in the front-end.

    Returns:
        :dict[bokeh.plotting.figure]: Dictionary containing Bokeh bar plot for each keyword and sentiment for the \
            Topics per Community component.
    """
    def create_bar_chart(data, topics, topic_colors, value_label="Count"):
        p = figure(y_range=community_new_names, width=700, tools=('reset, box_zoom'))
        source = ColumnDataSource(data)
        renderers = p.hbar_stack(topics, y=interactionCommunity + '_STR', height=0.9, color=topic_colors, source=source)

        p.y_range.range_padding = 0.1
        p.ygrid.grid_line_color = None
        p.axis.minor_tick_line_color = None
        p.outline_line_color = None
        p.yaxis.axis_label = 'Community'

        # Create a categorical color mapper
        color_mapper = CategoricalColorMapper(factors=topics, palette=topic_colors)
        color_bar = ColorBar(color_mapper=color_mapper, location=(0, 0), title='Topics')
        p.add_layout(color_bar, 'right')

        hover = HoverTool()
        if value_label == "Count":
            hover.tooltips = [("Topic", "$name"), (value_label, "@$name")]
        if value_label == "Proportion":
            hover.tooltips = [("Topic", "$name"), (value_label, "@$name{0,0.000}")]
        p.add_tools(hover)

        return json.dumps(json_item(p))

    results = dict()

    colors = df.set_index('Topic')['color'].to_dict()

    #Drop rows with missing values in 'Topic' and community columns
    df = df.dropna(subset=['Topic', interactionCommunity])
    community_og_names = list(communities_list.keys())
    community_new_names = list(communities_list.values())
    df[interactionCommunity + "_STR"] = df[interactionCommunity].apply(lambda x: str(int(x)))
    df = df[df[interactionCommunity + "_STR"].isin(community_og_names)]
    df["Topic"] = df["Topic"].astype(str)
#     df["Topic_INT"] = df["Topic"].astype(int)

    df[interactionCommunity + "_STR"] = df[interactionCommunity + "_STR"].apply(lambda x: communities_list[x])
    data = df.groupby([interactionCommunity + '_STR', 'Topic']).size().unstack(fill_value=0)
    # data = data.reset_index()  # Reset index to make 'Topic' a column
    data.rename(columns={t: str(t) for t in data.columns}, inplace=True)

    if topics_list is None:
        topics_list = data.columns.tolist()  # Exclude 'retweetCommunity' from topics list
    print("TOPICS -->", topics_list)
    topics_list_str = [str(t) for t in topics_list if t in colors]
    topic_colors = [colors[t] for t in topics_list if t in colors]

    results["counts"] = create_bar_chart(data, topics_list_str, topic_colors)

    # Calculate proportions instead of counts
    data_proportions = data.div(data.sum(axis=1), axis=0)
    data_proportions = data_proportions.reset_index()
    data_proportions = data_proportions.replace([np.inf, -np.inf], 0)

    results["proportions"] = create_bar_chart(data_proportions, topics_list_str, topic_colors, value_label="Proportion")

    return results


def project_onto_line(x, y, slope, intercept):
    """Helper function that used to re-order topics based on their projection onto a best-fit line. This ensures
    that colors are arranged in a pretty way in the Topic Discovery visualisations.

    Args:
       :x: (float) x-coordinate of centroid of given topic
       :y: (float) y-coordinate of centroid of given topic
       :slope: (float) Slope of best-fit line of data
       :intercept: (float) y-intercept for best-fit line of data

    Returns:
       :float: Position of topic centroid along best-fit line
    """
    line_y = slope * x + intercept
    projection = ((x + (y - line_y) * slope) / (1 + slope**2), (slope * (x + (y - line_y) * slope) + intercept) / (1 + slope**2))
    return projection

def change_topic_order(df):
    """Helper function that used to re-order topics so that colors are arranged in a pretty way in the Topic Discovery
    visualisations.

    Args:
        :df: (pandas.DataFrame) dataframe containing data with topics labels

    Returns:
        :pandas.DataFrame: updated version of input dataframe where topics have been re-ordered.
    """
    # Step 1: Calculate centroids for each topic
    centroids = df.groupby('Topic')['embedding_2d'].apply(lambda group: np.mean(group.tolist(), axis=0)).reset_index()
    centroids[['x', 'y']] = pd.DataFrame(centroids['embedding_2d'].tolist(), index=centroids.index)

    # Step 2: Fit a best-fit line to the centroids
    X = centroids[['x', 'y']].values
    reg = LinearRegression().fit(X[:, 0].reshape(-1, 1), X[:, 1])

    # Get the slope and intercept of the best-fit line
    slope = reg.coef_[0]
    intercept = reg.intercept_

    # Step 3: Project the centroids onto the best-fit line
    # Calculate the projection of each point onto the best-fit line
    centroids['projection'] = centroids.apply(lambda row: project_onto_line(row['x'], row['y'], slope, intercept), axis=1)

    # Calculate the distance along the line (single dimension)
    centroids['1D_value'] = centroids['projection'].apply(lambda p: p[0] * slope + p[1])

    values_1D = sorted(list(set(centroids['1D_value'].to_list())))
    values_1D_mapping = {v:i for i,v in enumerate(values_1D)}

    # Keep the mapping between final value and the original topic name
    result = centroids[['Topic', '1D_value']]
    result_dict = result.set_index('Topic')['1D_value'].to_dict()

    df["Topic"] = df["Topic"].apply(lambda x: values_1D_mapping[result_dict[x]])
    return df


def add_claim_to_bokeh_plot(plot_json, new_row):
    """Helper function that used to re-order topics so that colors are arranged in a pretty way in the Topic Discovery
    visualisations.

    Args:
        :df: (pandas.DataFrame) dataframe containing data with topics labels

    Returns:
        :pandas.DataFrame: updated version of input dataframe where topics have been re-ordered.
    """
    # Re-ingest plot from JSON
    doc = Document.from_json(plot_json["doc"])
    plot=doc.roots[0]

    # Extract the data source and color mapper from the plot
    datasource = plot.select(dict(type=ColumnDataSource))[0]

    # Get the data from the datasource
    data = datasource.data

    # Create a mask to filter out data points where size == 12 (i.e. claims)
    mask = (data['size'] != 12)

    # Filter data
    new_data = {key: np.array(values)[mask] for key, values in data.items()}

    # Add new claim if specified
    if new_row != None:
        new_data = {key: np.append(new_data[key], new_row[key]) for key in new_row}
#         new_data["index"] = np.append(new_data["index"], max(new_data["index"]) + 1)

    # Update the datasource
    datasource.data = new_data

    return plot



def update_bokeh_plot(plot_json, topic_mapping):
    """Helper function that updates a Bokeh scatter plot for the Topic Discovery component after the user has \
    renamed topics.

    Args:
        :plot_json: (str) Stringified JSON of Bokeh scatter plot.
        :topic_mapping: (dict) Mapping between topic numbers (as automatically generated from the K-means clustering \
            algorithm) and the topic names saved by the user in the front-end.

    Returns:
        :str: Stringified JSON of new Bokeh scatter plot, where topic names have been updated
    """
    topic_mapping["No topic"] = "No topic"
    logger.info(f"topic_mapping: {topic_mapping}")
    logger.info(type(list(topic_mapping.keys())[0]))
    logger.info(type(list(topic_mapping.values())[0]))

    # Re-ingest plot from JSON
    plot_json = json.loads(plot_json) if type(plot_json) == str else plot_json
    doc = Document.from_json(plot_json["doc"])
    plot=doc.roots[0]

    # Extract the data source and color mapper from the plot
    datasource = plot.select(dict(type=ColumnDataSource))[0]
    color_mapper = plot.select(dict(type=CategoricalColorMapper))[0]

    # Update the data source with new topic values
    new_data = datasource.data.copy()
    new_data['Topic'] = [topic_mapping[str(old_topic)] if (old_topic is not None) else "No topic" for old_topic in new_data['Topic']]

    # Update the datasource
    datasource.data = new_data

    # Update the color mapper with new topic values
    new_factors = [str(topic_mapping[factor]) for factor in color_mapper.factors]
    color_mapper.factors = new_factors

    # Serialize the modified plot back to JSON
    updated_plot_json = json.dumps(json_item(plot))

    return updated_plot_json


def update_topics_per_communities_plot(plot_json, topic_mapping):
    """Helper function that updates a Bokeh bar chart for the Topics per Community component after the user has \
    renamed topics.

    Args:
        :plot_json: (str) Stringified JSON of Bokeh bar chart.
        :topic_mapping: (dict) Mapping between topic numbers (as automatically generated from the K-means clustering \
            algorithm) and the topic names saved by the user in the front-end.

    Returns:
        :str: Stringified JSON of new Bokeh bar chart, where topic names have been updated
    """
    topic_mapping["No topic"] = "No topic"

    # Re-ingest plot from JSON
    plot_json = json.loads(plot_json) if type(plot_json) == str else plot_json
    doc = Document.from_json(plot_json["doc"])
    plot=doc.roots[0]

    # Extract the data source and color mapper from the plot
    datasource = plot.select(dict(type=ColumnDataSource))[0]
    color_mapper = plot.select(dict(type=CategoricalColorMapper))[0]

    # Update the data source with new topic values
    new_data = datasource.data.copy()

    rel_columns = [c for c in new_data.keys() if not c in ["index", "retweetCommunity_STR", "replyCommunity_STR", "retweetCommunity", "replyCommunity"]]

    for c in rel_columns:
        new_data[str(topic_mapping[c])] = new_data.pop(c)

    # Update the datasource
    datasource.data = new_data

    for renderer in plot.renderers:
        renderer.name = str(topic_mapping[renderer.name])
        renderer.glyph.left.expr.fields = [str(topic_mapping[f]) for f in renderer.glyph.left.expr.fields]
        renderer.glyph.right.expr.fields = [str(topic_mapping[f]) for f in renderer.glyph.right.expr.fields]

    # Update the color mapper with new topic values
    new_factors = [str(topic_mapping[factor]) for factor in color_mapper.factors]
    color_mapper.factors = new_factors

    # Serialize the modified plot back to JSON
    updated_plot_json = json.dumps(json_item(plot))

    return updated_plot_json


def compute_positive_negative(top_words, keyword):
    """Function that calculates the "most negative terms" and "most positive terms" for the WordCloud component for
    each topic. This function modifies the input dictionary "top_words" in place.

    Args:
        :top_words: (dict) Dictionary containing the top words per topic for each keyword.
        :keyword: (str) Keyword for which to extract the data from top_words
    """
    positive_topics = set(top_words[keyword]['Positive'].keys()) if 'Positive' in top_words[keyword] and top_words[keyword]['Positive'] != None else set()
    negative_topics = set(top_words[keyword]['Negative'].keys()) if 'Negative' in top_words[keyword] and top_words[keyword]['Negative'] != None else set()

    top_words[keyword]['Positive_Negative'] = dict()
    top_words[keyword]['Negative_Positive'] = dict()
    for topic in positive_topics.intersection(negative_topics):
        logger.info(topic)
        df1 = pd.DataFrame.from_records(top_words[keyword]['Positive'][topic])
        df2 = pd.DataFrame.from_records(top_words[keyword]['Negative'][topic])

        try:
            merged_df = pd.merge(df1, df2, on='text', how='outer')
            merged_df.fillna('', inplace=True)

            merged_pos_df = merged_df[merged_df['value_y']==""].sort_values(by='value_x', ascending=False).head(150)[['text','value_x']]
            merged_neg_df = merged_df[merged_df['value_x']==""].sort_values(by='value_y', ascending=False).head(150)[['text','value_y']]
            top_words[keyword]['Positive_Negative'][topic] = [{key if key != 'value_x' else 'value': value for key, value in row.items()} for row in merged_pos_df.to_dict(orient='records')]
            top_words[keyword]['Negative_Positive'][topic] = [{key if key != 'value_y' else 'value': value for key, value in row.items()} for row in merged_neg_df.to_dict(orient='records')]
        except KeyError:
            top_words[keyword]['Positive_Negative'][topic] = []
            top_words[keyword]['Negative_Positive'][topic] = []

    for topic in positive_topics - negative_topics:
        merged_df = pd.DataFrame.from_records(top_words[keyword]['Positive'][topic])
        merged_df.fillna('', inplace=True)
        merged_pos_df = merged_df.sort_values(by='value', ascending=False).head(150)[['text','value']]
        top_words[keyword]['Positive_Negative'][topic] = [{key: value for key, value in row.items()} for row in merged_pos_df.to_dict(orient='records')]

    for topic in negative_topics - positive_topics:
        merged_df = pd.DataFrame.from_records(top_words[keyword]['Negative'][topic])
        merged_df.fillna('', inplace=True)
        merged_neg_df = merged_df.sort_values(by='value', ascending=False).head(150)[['text','value']]
        top_words[keyword]['Negative_Positive'][topic] = [{key: value for key, value in row.items()} for row in merged_neg_df.to_dict(orient='records')]

def process_text(text):
    """Function that removes URLs and Twitter handles from the text of a tweet.

    Args:
        :text: (str) Original tweet.

    Returns:
        :str: New tweet processed such that URLs and twitter handles are removed.
    """
    if isinstance(text, str):
        new = " ".join([t for t in text.split() if t[:4] != "http"])
        new = " ".join([t for t in new.split() if t[0] !="@"])
        new = re.sub("[a-f0-9]{16}", "", new)
    else:
        new = ""
    return new


def format_display_text(text, line_len=55):
    """Function that formats text from tweet so that it is split over several lines, each no longer than a given
    number of characters.

    Args:
        :text: (str) Original tweet.
        :line_len: (int, optional) The maximal length of the line in number of characters. Defaults to 55.

    Returns:
        :str: tweet split over several lines.
    """
    if isinstance(text, str):
        tokens = text.split()
        new_text = ""
        line_count = 0
        for t in tokens:
            if (line_count + len(t) + 1) > line_len:
                new_text += "<br>"
                line_count = 0
            new_text += t + " "
            line_count += len(t) + 1
    else:
        new_text = ""
    return new_text


def get_topic_data(req, interactionCommunity=None, communitiesList=None):
    """Function that retrieves from Solr the data that corresponds to the filters "dataSource" (name of Solr core),
    "keywords", "date_start", "date_end" and "operator".

    Args:
        :req: (dict) Query dictionary which must contain the fields "dataSource" (str), "keywords" (list[str]), \
            "date_start" (str), "date_end" (str) and "operator" (str, must be "OR" or "AND").

    Returns:
        :dict or tuple: If successful, returns a dictionary containing the relevant data for the topic \
            discovery module, faceted by sentiment. Otherwise, returns a tuple containing a dictionary with an error \
            message and an error code.
    """
    source, keywords_list, filters, operator, limit = get_request_components(req)
    if source==None:
        resp = {"Error": "No data source specified, or wrong one provided!"}
        return make_response(jsonify(resp)), 400

    print("THESE ARE THE FILTERS", filters)
    responses = dict()
    dataSource = SolrClass(filters=filters)
    query = dataSource.solr_query_builder(keywords_list, operator, limit, "TOPIC Utils")

    #for keyword in keywords_list:
    for keyword in query.keys():
        keywordsCommunitiesList = list(communitiesList[keyword].keys()) if communitiesList and keyword in communitiesList else None
        print("THESE ARE THE COMMUNITIES INSIDE TOPIC_MODELLING_UTILS", keywordsCommunitiesList)
        query_term = query[keyword]
#         response, hits = dataSource.optimised_json_query_handler_topics(solr_core=source, keyword=query_term, rows= limit, interactionCommunity=interactionCommunity, communitiesList=communitiesList)
        response, hits = dataSource.optimised_json_query_handler_topics(solr_core=source, keyword=query_term, rows=100000, interactionCommunity=interactionCommunity, communitiesList=keywordsCommunitiesList)

        if keyword == "" or keyword == None or keyword == "All":
            responses["All"] = response
        else:
            responses[keyword] = response

    return responses

def preprocess_data(df):
    """Function that creates the new columns "processed_text", "display_text", "x" and "y" in the dataframe containing
    the data used to generate the Topic Discovery scatterplot, and filters out duplicate tweets based on the field
    "process_text" (i.e. removes all duplicates when ignoring URLs and twitter handles).

    Args:
        :df: (pandas.DataFrame) Dataframe containing the tweets which will be used to generate the Topic Discovery \
            plot. It must contain the columns "fullText" (str, the tweet text) and "embedding_2d" (list, the two \
            dimensional embedding of the tweet).

    Returns:
        :pandas.DataFrame: The pre-processed dataframe containing the new fields "processed_text", "display_text", \
            "x" and "y".
    """
    logger.info(f"Check 1: {len(df)}")
    try:
        # Remove duplicate tweets (ignoring URLs and Twitter handles)
        df["processed_text"] = df["fullText"].apply(process_text)
        df["display_text"] = df["fullText"].apply(format_display_text)
#         df["interactionCommunity"] = df["replyCommunity"] if "replyCommunity" in df.columns else + df["retweetCommunity"] if "retweetCommunity" in df.columns else [None]*len(df)
        df = df.drop_duplicates(subset=["processed_text"])
        logger.info(f"Check 2: {len(df)}")
        # Sample 100K tweets if the total volume is greater than that
        if len(df) > MAX_VOL:
            df = df.sample(n=MAX_VOL)
        logger.info(f"Check 3: {len(df)}")
        # Create a separate "x" and "y" coordinate field from the 2 dimensional tweet embedding
        df = df.dropna(subset=['embedding_2d'])
        df['x'] = df["embedding_2d"].apply(lambda x: x[0])
        df['y'] = df["embedding_2d"].apply(lambda x: x[1])
        return df
    except Exception as exp:
        logger.warning(f"Exp: {exp}")
        traceback.print_exc()
        return pd.DataFrame()


def filter_topic_modelling_per_community(communitiesList, interactionCommunity, new_plot, datasource, df_rel):
    """Function that generates filtered versions of the Topic Discovery visualisation for each of the main \
    communities in the SNA.

    Args:
        :topic_modelling_figures: (dict) Dictionary containing existing Topic Discovery visualisation(s)
        :topic_mapping: (dict) Mapping between topic numbers (as automatically generated from the K-means clustering \
            algorithm) and topic names (as saved by the user in the front-end)
        :communities_list: (dict) Mapping between community numbers (as stored in Solr) and community names (as \
            saved by user in the front-end). If this field is different from None, for each community in \
            communities_list a filtered version of the Topic Discovery visualisation containing only posts from that \
            community is generated.
        :interactionCommunity: (str) Network type for which the community names (from communities_list) are for. Must \
            be one of "retweet" or "reply" (if Twitter dataset) or simply "reply" (if YouTube dataset)
        :new_plot: (str) copy of original Topic Discovery Bokeh plot to be filtered by each community.
        :datasource: (bokeh.models.ColumnDataSource) ColumnDataSource object extracted from the original Topic Discovery \
            visualisation
        :df_rel: (pandas.DataFrame) Dataframe containing data for Bokeh scatter plot, as extracted directly from \
            the original Topic Discovery Bokeh visualisation.

    Output:
        :dict[dict[bokeh.plotting.figure]] Bokeh figures per keyword (outter dict) and sentiment (inner dict), \
            including version filtered by community.
    """
    logger.info(f"--> Generating plot per community: {interactionCommunity}")
    results = {"All Communities": json.dumps(json_item(new_plot))}
    print(df_rel.columns)
    print(len(df_rel))
    print(df_rel[interactionCommunity].value_counts())
    if len(df_rel) == 0:
        for community in communitiesList:
            results[community] = None
        return results
    else:
        print(type(df_rel[interactionCommunity].iloc[0]))

    for community in communitiesList:
        community_int = int(community)
        print(community_int)
        if interactionCommunity in df_rel.columns:
            print("** PRINT 1 **")
            #df_com = df_rel[df_rel["interactionCommunity"].apply(lambda x: isinstance(x,list) and community_int in x)][["display_text", "Topic", "x", "y", "color", "size", "interactionCommunity"]]
            if "videoId" in df_rel.columns:
                print("** PRINT 2 **")
                columns = ["id", "videoId", "display_text", "Topic", "x", "y", "color", "size", interactionCommunity]
            else:
                print("** PRINT 3 **")
                columns = ["id", "display_text", "Topic", "x", "y", "color", "size", interactionCommunity]
            df_com = df_rel[df_rel[interactionCommunity].apply(lambda x: x == x)]
            df_com = df_com[df_com[interactionCommunity].apply(lambda x: str(int(x)) == str(community_int))][columns]
        else:
            print("** PRINT 4 **")
            df_com = []

        if len(df_com) == 0:
            print("** PRINT 5 **")
            results[community] = None
        else:
            print("** PRINT 6 **")
            datasource.data = df_com
            results[community] = json.dumps(json_item(new_plot))

    return results