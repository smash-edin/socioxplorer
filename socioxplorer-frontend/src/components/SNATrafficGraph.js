import {Dropdown, Icon, Popup} from "semantic-ui-react";
import {useEffect, useState} from "react";
import Plot from "react-plotly.js";

export const SNATrafficGraph = ({input_info, keywords, sNATrafficGraphData, showSNAGraph, SNAcolors, datasetOrigin, 
  selectedKeywordsFilters, setSelectedKeywordsFilters}) => {

  const [] = useState(null);
  const [colors, setColors] = useState(null)
  const [temporGraphLayout, setTrafficGraphLayout] = useState(null)
  const [items, setItems] = useState(null)
  const [SNATrafficGraphConfig, setSNATrafficGraphConfig] = useState(null);
  const [allKeywordsLabel, setAllKeywordsLabel] = useState(input_info["operator"] === "AND" ? "All keywords" : "Any keyword")

  useEffect(() => {
    setAllKeywordsLabel(input_info["operator"] === "AND" ? "All keywords" : "Any keyword")
  },[input_info]);

  const dropKeywordsFilter = keywords.map((dictionaryKey) => {
    return {
      "key": dictionaryKey,
      "value": dictionaryKey,
      "text": dictionaryKey === "All" ? allKeywordsLabel : dictionaryKey[0].toUpperCase() + dictionaryKey.slice(1)
    }
  });

  useEffect(() => {
    if (sNATrafficGraphData !== null) {
      setItems(sNATrafficGraphData[selectedKeywordsFilters])
    } else {
      setItems(null)
    }
  }, [showSNAGraph, selectedKeywordsFilters, sNATrafficGraphData]);

  useEffect(() => {
    if (SNAcolors !== null) {
      setColors(SNAcolors[selectedKeywordsFilters])
    }
  }, [selectedKeywordsFilters, SNAcolors]);

  useEffect(() => {
    if (!(keywords.includes(selectedKeywordsFilters))) {
      setSelectedKeywordsFilters(keywords[0]);
    } else {
      setSelectedKeywordsFilters(selectedKeywordsFilters);
    }
  }, [showSNAGraph, keywords]);

  useEffect(() => {
    if (items !== null && items !== undefined) {
      const communitiesNames = Object.keys(items);
      let key1 = "Date";
      let key2 = "Count";
      communitiesNames.sort();
      const traces = communitiesNames.map((dictionaryKey) => {
        const dictionaryData = items[dictionaryKey];
        const x = dictionaryData.map(dictionaryData => dictionaryData[key1]);
        const y = dictionaryData.map(dictionaryData => dictionaryData[key2]);
        let color = colors[dictionaryKey]//TODO SNAcolors?
        let name = dictionaryKey === "All" ? allKeywordsLabel : dictionaryKey

        return {
          x,
          y,
          type: 'scatter',
          mode: 'lines+markers',
          showlegend: true,
          name: name,
          marker: {color: color},
        };

      });

      setSNATrafficGraphConfig({'data': traces, 'key1': key1, 'key2': key2})
      setTrafficGraphLayout({
        xaxis: {title: key1},
        yaxis: {title: key2},
        modebar: {remove: ['lasso2d', 'select2d', "autoscale"]},
        legend: {title: {text: "Communities"}
        }
      })
    } else {
      setSNATrafficGraphConfig(null)
      setTrafficGraphLayout(null)
    }
  }, [items]);

  let title = datasetOrigin === "Comment" ? "Comments per community" : "Tweeting per community"
  const renderSNATemporal = () => {
      if (SNATrafficGraphConfig === null || SNATrafficGraphConfig['data'].length === 0) {
        return (
            <div className="ErrorMessage">
              <p>No network interaction data for selected filters/query.</p>
            </div>
        )
      } else {
        return (

            <div>
              <div id="SNATrafficGraph" className={showSNAGraph ? 'SNATrafficGraph' : 'hidden'}>
                <Plot
                    data={SNATrafficGraphConfig['data']}
                    layout={temporGraphLayout}
                />
              </div>
            </div>
        )
      }
  }

  return (
      showSNAGraph && (
      <>
        <div className="Visualisation">
          <div className="MainTitleWithPopup">
            <h2 style={{marginRight: "5px"}}>{title}</h2>
            <Popup
              content="This component shows the volume over time of tweets/comments posted by each of the communities highlighted in the Social Network Analysis visualisation. Click on a community in the legend to hide/show its line, and double-click on it to make it the only visible line."
              trigger={<div className='InfoIcon'><Icon name='question circle' size="small"/></div>}
            />
          </div>
          <div className="DropDownGroup">
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
                    label='Metrics'
                    fluid
                    selection
                    options={dropKeywordsFilter}
                    text={dropKeywordsFilter.text}
                    floating
                    labeled={true}
                    icon={null}
                    value={selectedKeywordsFilters}
                    onChange={(e, {value}) => setSelectedKeywordsFilters(value)}
                    closeOnChange={true}
                    name='filtersTypeDropdown'
                    id='filtersTypeDropdown'
                ></Dropdown>
              </div>
            </div>
          </div>
          {renderSNATemporal()}
        </div>
      </>));
};
export default SNATrafficGraph;