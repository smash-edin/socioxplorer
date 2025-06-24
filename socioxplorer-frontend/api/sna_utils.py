import sys
from os.path import dirname, abspath, join
from flask import jsonify, make_response
from bokeh.plotting import figure
from bokeh.models import HoverTool, ColumnDataSource, ColorBar, CustomJSHover, OpenURL, TapTool, CustomJS
try:
    source_dir = abspath(join('../../'))
    sys.path.append(source_dir)
except Exception as exp:
    print("Solr Class Not Found, please make sure the solr_class.py file exists in the root folder!")
    print("exiting...")
    sys.exit(-1)
from solr_class import *
from utils import get_request_components, create_logger, print_this
logger = create_logger(f"SNA Modelling Utils", file=f"sna_utils")

CURRENT_PATH = dirname(__file__)

"""This utils file contains all the function used by the SNA API endpoint. """
    
def get_network_plot(df, bokeh_cmap, datasetOrigin="Tweet"):
    """ A function to generate the Bokeh visualisation for the social network analysis.

    Args:
        :df: (pandas.DataFrame) dataframe containing user data (username, description, community, x and y coordinates)
        :bokeh_cmap: (bokeh.models.CategoricalColorMapper) color map for communities
        :datasetOrigin: (str) Whether data is from Twitter ("Tweet") or YouTube ("Comment")

    Returns:
        bokeh.plotting.figure: A Bokeh visualisation of users in the retweet space
    """
    datasource = ColumnDataSource(df)
    plot_figure = figure(
        width=600,
        height=600,
        tools=('pan, wheel_zoom, reset', 'tap')
    )
    print_this(f"\n\n------------\nDATASET ORIGIN: {datasource}\n++++++++++++{df.columns}\n\n")

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

    url = "http://youtube.com/@@node" if datasetOrigin == "Comment" else "https://twitter.com/@node"
    callbackClick = CustomJS(args={'source': datasource, 'url':url}, code="""
            const selected = source.selected.indices;
            if (selected.length) {
                const index = selected[0];
                const id = source.data.node[index];
                const full_url = url.replace('@node', id)
                window.open(full_url);
            }
        """)

    taptool = plot_figure.select(type=TapTool)
    taptool.callback = callbackClick #OpenURL(url=url)

    plot_figure.add_tools(HoverTool(tooltips="""
    <div @y{custom}>
        <div style="padding-top:5px">
            <span style='font-size: 14px; color: #224499'>Username:</span>
            <span style='font-size: 14px'>@node</span>
        </div>
        <div>
            <span style='font-size: 14px; color: #224499'>Description:</span>
            <span style='font-size: 14px'>@desc</span>
        </div>
        <div style="padding-bottom:5px">
            <span style='font-size: 14px; color: #224499'>Community:</span>
            <span style='font-size: 14px'>@community</span>
        </div>
    </div>
    """, formatters={'@y':custom_hov}))

    cb = ColorBar(color_mapper = bokeh_cmap, location = (5,6), title = "Community Number")
    plot_figure.add_layout(cb, 'right')
    
    plot_figure.circle(
        'x',
        'y',
        color="color",
        source=datasource,
        line_alpha=0.6,
        fill_alpha=0.6,
    )
    plot_figure.grid.visible = False
    plot_figure.axis.visible = False
    return plot_figure


def get_sna_data(req, interaction='retweet'):
    """A function to get the data for the SNA by calling the corresponding function at SolrClass.

    Args:
        req (dict): request filters/parameters.
        interaction (str): network type (retweet, reply), defaults to 'retweet'.

    Returns:
        dict: A dict of dataframes for the network and nodes, and a dataframe for the network stats.
    """
    source, keywords_list, filters, operator, limit = get_request_components(req)

    if source==None:
        resp = {"Error": "No data source specified, or wrong one provided!"}
        return make_response(jsonify(resp)), 400

    dataSource = SolrClass(filters=filters)
    responses = dict()

    query = dataSource.solr_query_builder(keywords_list, operator, limit, "SNA Utils")

    for keyword in query.keys():
        query_term = query[keyword]
        logger.info(query_term)

        network_df, nodes_df = dataSource.get_network_of_users(solr_core=source, keyword=query_term, interaction=interaction)
        network_stats = dataSource.get_network_stats(solr_core=source, keyword=query_term, interaction=interaction, limit=limit)

        if keyword == None or keyword == "" or keyword == "All":
            responses["All"] = {'network_df': network_df, 'nodes_df': nodes_df, 'network_stats': network_stats}
        else:
            responses[keyword] = {'network_df': network_df, 'nodes_df': nodes_df, 'network_stats': network_stats}
    return responses


def get_communities_location_and_language(req, interaction, communities):
    """A function to get the location and language data for the specified communities by calling the corresponding function at SolrClass.

    Args:
        req (dict): request filters/parameters.
        interaction (str): network type (retweet, reply)

    Returns:
        dict: A dict of dataframes for the network and nodes, and a dataframe for the network stats.
    """
    source, keywords_list, filters, operator, limit = get_request_components(req)

    if source==None:
        resp = {"Error": "No data source specified, or wrong one provided!"}
        return make_response(jsonify(resp)), 400

    dataSource = SolrClass(filters=filters)
    responses = dict()

    query = dataSource.solr_query_builder(keywords_list, operator, limit, "SNA Utils")

    for keyword in query.keys():
        query_term = query[keyword]
        logger.info(query_term)
        logger.info(f"COMMUNITIES: {keyword}")
        print_this(f"COMMUNITIES: {keyword}")
        map_stats = dataSource.get_network_map_info(solr_core=source, keyword=query_term, interaction=interaction, communities=communities[keyword] if keyword in communities.keys() else [])

        if keyword == None or keyword == "" or keyword == "All":
            responses["All"] = map_stats
        else:
            responses[keyword] = map_stats

    return responses
    