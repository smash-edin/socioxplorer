import org.gephi.graph.api.*;
import org.gephi.filters.api.Query;
import org.gephi.filters.api.FilterController;
import org.gephi.filters.plugin.graph.GiantComponentBuilder.GiantComponentFilter;
import org.gephi.preview.api.PreviewController;
import org.gephi.preview.api.PreviewModel;
import org.gephi.preview.api.PreviewProperty;
import org.gephi.io.exporter.api.ExportController;
import org.gephi.io.exporter.plugin.ExporterJson;
import org.gephi.io.exporter.plugin.ExporterGEXF;
import org.gephi.io.importer.api.Container;
import org.gephi.io.importer.api.EdgeDirectionDefault;
import org.gephi.io.importer.api.ImportController;
import org.gephi.io.processor.plugin.DefaultProcessor;
import org.gephi.layout.plugin.AutoLayout;
import org.gephi.layout.plugin.forceAtlas2.ForceAtlas2;
import org.gephi.project.api.ProjectController;
import org.gephi.project.api.Workspace;
import org.gephi.statistics.plugin.Modularity;
import org.openide.util.Lookup;
//import org.w3c.dom.Node;

import java.io.*;
import java.util.concurrent.TimeUnit;

//import javax.management.Query;

import java.util.Set;
import java.util.HashSet;
import java.util.HashMap;
import java.util.Random;
import java.util.Map;
import java.util.List;
import java.util.Collections;
import java.util.ArrayList;

import java.awt.Color;


public class GephiVis {

    public Random random = new Random(System.currentTimeMillis());

    public double calculateJaccard(Set<Node> set1, Set<Node> set2) {
        Set<Node> intersection = new HashSet<>(set1);
        intersection.retainAll(set2);

        Set<Node> union = new HashSet<>(set1);
        union.addAll(set2);

        return (double) intersection.size() / union.size();
    }

    public static double calculateOverlap(Set<Node> set1, Set<Node> set2) {
        if (set1.isEmpty() || set2.isEmpty()) return 0.0;

        Set<Node> intersection = new HashSet<>(set1);
        intersection.retainAll(set2);

        return (double) intersection.size() / Math.min(set1.size(), set2.size());
    }

    public static int findNextInteger(Set<Integer> set) {
        if (set.isEmpty()) return 0;
        int maxInteger = Collections.max(set);
        return maxInteger + 1;
    }

    // FOR TESTING
//    private Color[] generateColorPalette(int numColors) {
//        Color[] palette = new Color[numColors];
//        float saturation = 0.9f;
//        float brightness = 0.9f;
//
//        for (int i = 0; i < numColors; i++) {
//            float hue = (float) i / numColors; // Evenly distribute hues
//            palette[i] = Color.getHSBColor(hue, saturation, brightness);
//        }
//        return palette;
//    }

    // FOR TESTING
//    public void colorNodesByAttribute(GraphModel graphModel, Map<Integer, Color> classColorMap) {
//        Graph graph = graphModel.getGraph();
//        for (Node node : graph.getNodes()) {
//            Integer modClass = (Integer) node.getAttribute("previousModularityClass");
//            if (classColorMap.containsKey(modClass)) {
//                // Retrieve the color and apply it to the node
//                Color color = classColorMap.get(modClass);
//                node.setColor(color);
//            } else {
//                node.setColor(new Color(220,220,220));
//            }
//        }
//    }

    public void script(int duration, String sourceFile, String networkFilePath, String reProcessAll) throws FileNotFoundException {

        // Define outfile names
        String outFile = sourceFile.replace(".csv", "_GRAPH.json");
        String imgFile = sourceFile.replace(".csv", ".pdf");
        
        // Initialise project
        ProjectController pc = Lookup.getDefault().lookup(ProjectController.class);
        pc.newProject();
        Workspace workspace = pc.getCurrentWorkspace();

        //Get models and controllers for this new workspace - will be useful later
        GraphModel graphModel = Lookup.getDefault().lookup(GraphController.class).getGraphModel();
        ImportController importController = Lookup.getDefault().lookup(ImportController.class);
        ExportController ec = Lookup.getDefault().lookup(ExportController.class);

        // Import existing network if it exists
        Container containerNetwork;
        DirectedGraph graph = graphModel.getDirectedGraphVisible();
        System.out.println("Loading existing network if it exists...");
        File networkFile = new File(networkFilePath);

        Boolean firstTime = Boolean.TRUE;

        if (networkFile.exists()) {

            try {
                containerNetwork = importController.importFile(networkFile);
                containerNetwork.getLoader().setEdgeDefault(EdgeDirectionDefault.DIRECTED);   //Force DIRECTED
            } catch (Exception ex) {
                ex.printStackTrace();
                return;
            }

            //Append imported data to GraphAPI
            importController.process(containerNetwork, new DefaultProcessor(), workspace);

            //See if graph is well imported
            int nbNodes = graph.getNodeCount();
            int nbEdges = graph.getEdgeCount();
            System.out.println("\tNb nodes in existing network: " + nbNodes);
            System.out.println("\tNb edges in existing network: " + nbEdges);

            firstTime = Boolean.FALSE;

        } else {
            System.out.println("\t==> No network to load");
        }

        // Loading new data
        System.out.println("Loading new data...");
        Container containerNewData;
        try {
            File file = new File(getClass().getResource(sourceFile).toURI());
            containerNewData = importController.importFile(file);
            containerNewData.getLoader().setEdgeDefault(EdgeDirectionDefault.DIRECTED);   //Force DIRECTED
        } catch (Exception ex) {
            ex.printStackTrace();
            return;
        }

        //Append imported data to GraphAPI
        importController.process(containerNewData, new DefaultProcessor(), workspace);

        //See if graph is well imported
        int nbNodes = graph.getNodeCount();
        int nbEdges = graph.getEdgeCount();
        System.out.println("\tNb nodes new: " + nbNodes);
        System.out.println("\tNb edges new: " + nbEdges);

        // Preview
        PreviewModel previewModel = Lookup.getDefault().lookup(PreviewController.class).getModel();
        previewModel.getProperties().putValue(PreviewProperty.SHOW_EDGES, Boolean.FALSE);

        // Filter out nodes
        System.out.println("Filtering out nodes that are not in Giant Component");
        FilterController filterController = Lookup.getDefault().lookup(FilterController.class);
        GiantComponentFilter giantComponentFiler = new GiantComponentFilter();
        giantComponentFiler.init(graph);
        Query query = filterController.createQuery(giantComponentFiler);
        GraphView view = filterController.filter(query);
        graphModel.setVisibleView(view);


        graph = graphModel.getDirectedGraphVisible();
        nbNodes = graph.getNodeCount();
        nbEdges = graph.getEdgeCount();
        System.out.println("New nb nodes: " + nbNodes);
        System.out.println("New nb edges: " + nbEdges);

        //Layout
        //System.out.println("Running layout algorithm...");
        System.out.println(String.format("Running layout algorithm ... it is normal to have no feedback for %d seconds.", duration));
        
        AutoLayout autoLayout = new AutoLayout(duration, TimeUnit.MINUTES);
        autoLayout.setGraphModel(graphModel);
        ForceAtlas2 layout = new ForceAtlas2(null);
        if (nbNodes > 10000) {
            layout.setBarnesHutOptimize(Boolean.TRUE);
        }
        layout.setLinLogMode(Boolean.TRUE);
        AutoLayout.DynamicProperty adjustBySizeProperty = AutoLayout.createDynamicProperty("forceAtlas2.adjustSizes.name", Boolean.TRUE, 0.1f);
        autoLayout.addLayout(layout, 1f, new AutoLayout.DynamicProperty[]{adjustBySizeProperty});
        autoLayout.execute();

        //Run modularity algorithm - community detection
        System.out.println("Running modularity class...");
        Modularity modularity = new Modularity();
        modularity.execute(graphModel);
        Column modColumn = graphModel.getNodeTable().getColumn(Modularity.MODULARITY_CLASS);
        Map<Integer, Color> classColorMap = new HashMap<>();
        
        System.out.println(reProcessAll);
        System.out.println(reProcessAll.equals("true"));
        System.out.println(reProcessAll.equals("True"));
        if (firstTime || Boolean.parseBoolean(reProcessAll)) {
            System.out.println("First time or reprocess all");
            Map<Integer, Integer> frequencyMap = new HashMap<>();
            for (Node node : graph.getNodes()) {
                // Get the modularity class value
                Integer modularityClass = (Integer) node.getAttribute(modColumn);
                // Get size of communities
                if (modularityClass != null) {
                    frequencyMap.put(modularityClass, frequencyMap.getOrDefault(modularityClass, 0) + 1);
                }
            }

            // Sort modularity classes by frequency in descending order and rank them
            List<Map.Entry<Integer, Integer>> sortedByFrequency = new ArrayList<>(frequencyMap.entrySet());
            sortedByFrequency.sort((a, b) -> b.getValue().compareTo(a.getValue()));

            // Create a map to store ranks
            Map<Integer, Integer> rankMap = new HashMap<>();
            int rank = 1;
            for (Map.Entry<Integer, Integer> entry : sortedByFrequency) {
                rankMap.put(entry.getKey(), rank++);
            }

            // Add a new column to store modularity class
            Column labelColumn = graphModel.getNodeTable().addColumn("previousModularityClass", Integer.class);

            // Assign rank as label for each node
            for (Node node : graph.getNodes()) {
                Integer modularityClass = (Integer) node.getAttribute(modColumn);
                if (modularityClass != null && rankMap.containsKey(modularityClass)) {
                    node.setAttribute(labelColumn, rankMap.get(modularityClass));
                } else {
                    node.setAttribute(labelColumn, -1); // or handle undefined class appropriately
                }
            }

            // FOR TESTING: create a palette
//            Color[] colorPalette = generateColorPalette(40);
//            for (int i = 0; i < colorPalette.length; i++) {
//                Color color = colorPalette[i];
//                classColorMap.put(i, color);
//            }
//            try (ObjectOutputStream oos = new ObjectOutputStream(new FileOutputStream(palettePath))) {
//                oos.writeObject(classColorMap);
//            } catch (IOException e) {
//                e.printStackTrace();
//            }

        } else {
            // FOR TESTING: load palette
//            try (ObjectInputStream ois = new ObjectInputStream(new FileInputStream(palettePath))) {
//                classColorMap = (Map<Integer, Color>) ois.readObject();
//            } catch (Exception ex) {
//                ex.printStackTrace();
//                return;
//            }
            System.out.println("NOT NOT NOT First time or reprocess all NOT");
            Map<Integer, Set<Node>> modularityGroups = new HashMap<>();
            Map<Integer, Set<Node>> labelGroups = new HashMap<>();
            Set<Integer> allLabels = new HashSet<>();

            for (Node node : graph.getNodes()) {
                // Organize by modularity class
                Integer modClass = (Integer) node.getAttribute(modColumn);
                modularityGroups.computeIfAbsent(modClass, k -> new HashSet<>()).add(node);
                // Organize by label
                Integer label = (Integer) node.getAttribute("previousModularityClass");
                if (label != null) {
                    labelGroups.computeIfAbsent(label, k -> new HashSet<>()).add(node);
                    allLabels.add(label);
                }
            }

            Map<Integer, Integer> modClassToBestLabel = new HashMap<>();

            // Find label with highest Jaccard index or Overlap Coefficient for every modularity_class
            for (Map.Entry<Integer, Set<Node>> modEntry : modularityGroups.entrySet()) {
                Integer modClass = modEntry.getKey();
                Set<Node> modNodes = modEntry.getValue();

                Integer bestLabel = null;
                double bestMeasure = 0.0;

                for (Map.Entry<Integer, Set<Node>> labelEntry : labelGroups.entrySet()) {
                    Integer label = labelEntry.getKey();
                    Set<Node> labelNodes = labelEntry.getValue();

                    double measure;
                    String measureType = null;
                    if (modNodes.size() > labelNodes.size()) {
                        measure = calculateOverlap(modNodes, labelNodes);
                    } else {
                        measure = calculateJaccard(modNodes, labelNodes);
                    }

                    if (measure > bestMeasure) {
                        bestMeasure = measure;
                        bestLabel = label;
                    }
                }

                if (bestMeasure < 0.7 || bestLabel == null) {
                    Integer bestLabelNew = findNextInteger(allLabels);
                    allLabels.add(bestLabelNew);
                }
                modClassToBestLabel.put(modClass, bestLabel);
            }

            Column labelColumn = graphModel.getNodeTable().getColumn("previousModularityClass");
            for (Node node : graph.getNodes()) {
                Integer modClass = (Integer) node.getAttribute(modColumn);
                Integer bestLabel = modClassToBestLabel.get(modClass);
                node.setAttribute(labelColumn, bestLabel);
            }
        }

        // FOR TESTING: color nodes
//        colorNodesByAttribute(graphModel, classColorMap);

        //Export to JSON
        ExporterJson exporter = (ExporterJson) ec.getExporter("json");     //Get JSON exporter
        exporter.setWorkspace(workspace);
        try {
            ec.exportFile(new File(outFile), exporter);
        } catch (IOException ex) {
            ex.printStackTrace();
        }

        // Export image
        try {
            ec.exportFile(new File(imgFile));
        } catch (IOException ex) {
            ex.printStackTrace();
        }

        // Export network as GEXF file
        ExporterGEXF exporterGEXF = (ExporterGEXF) ec.getExporter("gexf");
        exporterGEXF.setWorkspace(workspace);

        try {
            ec.exportFile(new File(networkFilePath), exporterGEXF);
        } catch (IOException ex) {
            ex.printStackTrace();
        }

        System.out.println("DONE!");
    }
}