import Plot from "react-plotly.js";
import {Icon, Popup} from "semantic-ui-react";
import {useEffect, useState} from "react";


// VolumesGraph component used to display the prevalence of data matching query over time
export const VolumesGraph = ({data, keywords, inputInfo}) => {

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

  // Layout options
  let key1 = "Date"
  let key2 = "Count"

  const layout = {
    xaxis: {title: key1},
    yaxis: {title: key2},
    modebar: {remove: ['lasso2d', 'select2d', "autoscale"]},
  }

  const [allKeywordsLabel, setAllKeywordsLabel] = useState(inputInfo["operator"] === "AND" ? "All keywords" : "Any keyword")

  useEffect(() => {
    setAllKeywordsLabel(inputInfo["operator"] === "AND" ? "All keywords" : "Any keyword")
  },[inputInfo]);

  // Variable storing formatted data for volumes lines graph
  const traces = keywords.map((dictionaryKey) => {
      const dictionaryData = data[dictionaryKey]['traffic'];
      const x = dictionaryData.map(data => data[key1]);
      const y = dictionaryData.map(data => data[key2]);
      let color = getRandomColor(dictionaryKey);
      let name = dictionaryKey === "All"? allKeywordsLabel : dictionaryKey[0].toUpperCase() + dictionaryKey.slice(1);

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

  // Render code for the VolumesGraph component
  return (
    <div className="Visualisation">
      <div className="MainTitleWithPopup">
        <h2 style={{marginRight: "5px"}}>Timeline</h2>
        <Popup
          content="This component shows the volume of data per day matching the input query. If more than 1 keyword was provided, a different line is plotted for each keyword as well as for all keywords together ('All keywords'). Click on a keyword in the legend to hide/show its line, and double-click on it to make it the only visible line. You can also click on a specific datapoint to generate a new report (in a new tab) for the subset of the current data that corresponds to this specific day and keyword."
          trigger={<div className='InfoIcon'><Icon name='question circle' size="small"/></div>}
        />
      </div>
      <div>
        <Plot 
        data={traces}
        layout={layout}
        onClick={function(event){
            const page_path = window.location.pathname + "?report="
            const lineName = event.points[0].data.name
            const relKeywords = (lineName === "All keywords" || lineName === "Any keyword") ? inputInfo["keywords"].filter(function (key) { return key !== 'All'; }).join(",") : lineName.toLowerCase()
            const generate_report = window.confirm("A new report will be generated with the following filters:" +
                "\n Keywords:"+ relKeywords +
                "\n Dataset:"+ inputInfo["source_text"] +
                "\n Operator:"+ inputInfo["operator"] +
                "\n Date :" + event.points[0].x +
                "\n Sentiment:"+ inputInfo["sentiment"] +
                "\n Language:"+ inputInfo["location"] +
                "\n Location of "+ (inputInfo["location_type"] === 'author'? 'users':'tweets') + ": " + inputInfo["location"] +
                "\n\n Do you want to continue?");
            if (generate_report !== false && generate_report !== null) {
                window.open(page_path+encodeURIComponent(
                JSON.stringify(
                  {
                    "keywords": relKeywords,//keywords.filter(function (key) { return key !== 'All'; }).join(","),
                    "dataSource": inputInfo["dataSource"],
                    "operator": inputInfo["operator"],
                    "source_text": inputInfo["source_text"],
                    limit: 500,
                    "date_start": event.points[0].x,
                    "date_end": event.points[0].x,
                    "language": inputInfo["language"],
                    "sentiment": inputInfo["sentiment"],
                    "location": inputInfo["location"],
                    "location_type": inputInfo["location_type"],
                })),
                "_blank")};
          }
        }/>
      </div>
    </div>
  )
};