import java.io.File;
import java.io.FileWriter;
import java.io.IOException;
import java.util.ArrayList;
import java.util.HashMap;
import java.util.List;
import java.util.Map;

import com.sap.sl.sdk.authoring.businesslayer.*;
import com.sap.sl.sdk.authoring.datafoundation.*;
import com.sap.sl.sdk.authoring.local.LocalResourceService;
import com.sap.sl.sdk.framework.SlContext;

import org.json.JSONArray;
import org.json.JSONObject;

/**
 * BLXParser - Extracts metadata from BOBJ .blx files using SAP BusinessObjects SDK
 *
 * Usage: java BLXParser <path-to-blx-file> <output-json-path>
 *
 * This tool uses the SAP Semantic Layer SDK to:
 * 1. Load a .blx (Business Layer) file
 * 2. Extract dimensions, measures, tables, and joins
 * 3. Output the metadata as JSON
 */
public class BLXParser {

    public static void main(String[] args) {
        if (args.length < 2) {
            System.err.println("Usage: java BLXParser <blx-file-path> <output-json-path>");
            System.exit(1);
        }

        String blxPath = args[0];
        String outputPath = args[1];

        try {
            JSONObject result = parseBlx(blxPath);

            // Write JSON to file
            try (FileWriter file = new FileWriter(outputPath)) {
                file.write(result.toString(2));
                file.flush();
            }

            System.out.println("Successfully extracted metadata to: " + outputPath);

        } catch (Exception e) {
            System.err.println("Error parsing BLX file: " + e.getMessage());
            e.printStackTrace();
            System.exit(1);
        }
    }

    /**
     * Parse a .blx file and extract all metadata
     */
    public static JSONObject parseBlx(String blxPath) throws Exception {
        File blxFile = new File(blxPath);
        if (!blxFile.exists()) {
            throw new IOException("BLX file not found: " + blxPath);
        }

        JSONObject result = new JSONObject();
        result.put("source_file", blxPath);
        result.put("file_name", blxFile.getName());

        SlContext context = null;
        RelationalBusinessLayer businessLayer = null;
        MonoSourceDataFoundation dataFoundation = null;

        try {
            // Initialize SDK context
            context = SlContext.create();
            LocalResourceService service = context.getService(LocalResourceService.class);

            // Load the business layer
            businessLayer = (RelationalBusinessLayer) service.load(blxPath);

            // Extract business layer metadata
            result.put("universe_name", businessLayer.getName());
            result.put("description", businessLayer.getDescription() != null ? businessLayer.getDescription() : "");

            // Extract dimensions
            JSONArray dimensions = new JSONArray();
            extractDimensions(businessLayer.getRootFolder(), dimensions);
            result.put("dimensions", dimensions);
            result.put("dimension_count", dimensions.length());

            // Extract measures
            JSONArray measures = new JSONArray();
            extractMeasures(businessLayer.getRootFolder(), measures);
            result.put("measures", measures);
            result.put("measure_count", measures.length());

            // Extract filters
            JSONArray filters = new JSONArray();
            extractFilters(businessLayer.getRootFolder(), filters);
            result.put("filters", filters);
            result.put("filter_count", filters.length());

            // Load data foundation if available
            String dfxPath = businessLayer.getDataFoundationPath();
            if (dfxPath != null && !dfxPath.isEmpty()) {
                try {
                    dataFoundation = (MonoSourceDataFoundation) service.load(dfxPath);

                    // Extract tables
                    JSONArray tables = new JSONArray();
                    if (dataFoundation.getTables() != null) {
                        for (int i = 0; i < dataFoundation.getTables().size(); i++) {
                            Table table = dataFoundation.getTables().get(i);
                            JSONObject tableObj = new JSONObject();
                            tableObj.put("name", table.getName());
                            tableObj.put("alias", table.getAlias() != null ? table.getAlias() : table.getName());
                            tables.put(tableObj);
                        }
                    }
                    result.put("tables", tables);
                    result.put("table_count", tables.length());

                    // Extract joins
                    JSONArray joins = new JSONArray();
                    if (dataFoundation.getJoins() != null) {
                        for (int i = 0; i < dataFoundation.getJoins().size(); i++) {
                            Join join = dataFoundation.getJoins().get(i);
                            JSONObject joinObj = new JSONObject();
                            joinObj.put("name", join.getName());

                            // Get join expression
                            if (join.getExpression() != null) {
                                joinObj.put("expression", join.getExpression().toString());
                            }

                            joins.put(joinObj);
                        }
                    }
                    result.put("joins", joins);
                    result.put("join_count", joins.length());

                } catch (Exception e) {
                    System.err.println("Warning: Could not load data foundation: " + e.getMessage());
                }
            }

            // Release resources
            if (dataFoundation != null) {
                service.close(dataFoundation);
            }
            if (businessLayer != null) {
                service.close(businessLayer);
            }

        } finally {
            if (context != null) {
                context.close();
            }
        }

        return result;
    }

    /**
     * Recursively extract dimensions from business layer folders
     */
    private static void extractDimensions(BlItem container, JSONArray dimensions) {
        if (container instanceof Dimension) {
            Dimension dim = (Dimension) container;
            JSONObject dimObj = new JSONObject();
            dimObj.put("name", dim.getName());
            dimObj.put("description", dim.getDescription() != null ? dim.getDescription() : "");
            dimObj.put("type", "dimension");

            // Get data type
            if (dim.getDataType() != null) {
                dimObj.put("data_type", dim.getDataType().toString());
            }

            // Get expression/source
            if (dim.getSelect() != null && dim.getSelect().getExpression() != null) {
                String expr = dim.getSelect().getExpression().toString();
                dimObj.put("expression", expr);

                // Parse table.column from expression
                if (expr.contains(".")) {
                    String[] parts = expr.split("\\.", 2);
                    if (parts.length == 2) {
                        dimObj.put("table", parts[0].trim());
                        dimObj.put("column", parts[1].trim());
                    }
                }
            }

            dimensions.put(dimObj);
        }

        // Recurse into folders
        if (container instanceof BlContainer) {
            BlContainer folder = (BlContainer) container;
            List<BlItem> children = folder.getChildren();
            if (children != null) {
                for (BlItem child : children) {
                    extractDimensions(child, dimensions);
                }
            }
        }
    }

    /**
     * Recursively extract measures from business layer folders
     */
    private static void extractMeasures(BlItem container, JSONArray measures) {
        if (container instanceof Measure) {
            Measure meas = (Measure) container;
            JSONObject measObj = new JSONObject();
            measObj.put("name", meas.getName());
            measObj.put("description", meas.getDescription() != null ? meas.getDescription() : "");
            measObj.put("type", "measure");

            // Get data type
            if (meas.getDataType() != null) {
                measObj.put("data_type", meas.getDataType().toString());
            }

            // Get aggregation function
            if (meas.getAggregateFunction() != null) {
                measObj.put("aggregation", meas.getAggregateFunction().toString());
            }

            // Get expression/source
            if (meas.getSelect() != null && meas.getSelect().getExpression() != null) {
                String expr = meas.getSelect().getExpression().toString();
                measObj.put("expression", expr);

                // Parse table.column from expression
                if (expr.contains(".")) {
                    String[] parts = expr.split("\\.", 2);
                    if (parts.length == 2) {
                        measObj.put("table", parts[0].trim());
                        measObj.put("column", parts[1].trim());
                    }
                }
            }

            measures.put(measObj);
        }

        // Recurse into folders
        if (container instanceof BlContainer) {
            BlContainer folder = (BlContainer) container;
            List<BlItem> children = folder.getChildren();
            if (children != null) {
                for (BlItem child : children) {
                    extractMeasures(child, measures);
                }
            }
        }
    }

    /**
     * Recursively extract filters from business layer folders
     */
    private static void extractFilters(BlItem container, JSONArray filters) {
        if (container instanceof Filter) {
            Filter filter = (Filter) container;
            JSONObject filterObj = new JSONObject();
            filterObj.put("name", filter.getName());
            filterObj.put("description", filter.getDescription() != null ? filter.getDescription() : "");
            filterObj.put("type", "filter");

            // Get filter expression
            if (filter.getFilterExpression() != null) {
                filterObj.put("expression", filter.getFilterExpression().toString());
            }

            filters.put(filterObj);
        }

        // Recurse into folders
        if (container instanceof BlContainer) {
            BlContainer folder = (BlContainer) container;
            List<BlItem> children = folder.getChildren();
            if (children != null) {
                for (BlItem child : children) {
                    extractFilters(child, filters);
                }
            }
        }
    }
}
