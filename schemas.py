TOOL_SCHEMAS = [
    {
        "name": "inspect_data",
        "description": "View a dataset overview: number of rows, column names, "
                       "and lists of all product and region names.count of missing values, date range, "
                       "Call this first when you are unsure which products, regions, or months are available.",
        "parameters": {"type": "object", "properties": {}, "required": []},
    },
    {
        "name": "group_stats",
        "description": "Groups data by a specific dimension and returns sorted results. Suitable for answering questions such as "
                       "Which product or region has the highest sales? or What are the sales figures for each region?",
        "parameters": {
            "type": "object",
            "properties": {
                "group_by": {"type": "string", "enum": ["products", "region", "month"],
                             "description": "group dimensions"},
                "agg": {"type": "string", "enum": ["sum", "mean", "count"],
                        "description": "Aggregation method, default sum"},
                "metric": {"type": "string", "enum": ["sales", "quantity"],
                           "description": "Statistical indicators, default sales"},
                "top_n": {"type": "integer", "description": "return the first N, default 10"},
                "filters": {"type": "object",
                            "description": "Optional filter criteria, like {\"month\": \"2025-12\", \"region\": \"East\"}"},
            },
            "required": ["group_by"],
        },
    },
    {
        "name": "time_trend",
        "description": "Returns a time-series of sales figures, available on a daily, weekly, or monthly basis. "
                       "Suitable for answering questions about trends or identifying the months with the highest or lowest sales.",
        "parameters": {
            "type": "object",
            "properties": {
                "freq": {"type": "string", "enum": ["day", "week", "month"],
                         "description": "Time granularity, default month"},
                "filters": {"type": "object",
                            "description": "Optional filter criteria, like {\"region\": \"East\"}"},
            },
            "required": [],
        },
    },
    {
        "name": "compare_periods",
        "description": "Compare sales figures between two months, broken down by product or region, "
                       "and return the change for each item as well as the contribution percentage of items showing a decline."
                       "Use this when answering questions like 'Why did sales drop/rise?' or "
                       "'Where did the change primarily originate?'—do not calculate the difference manually."
                       "Use the YYYY-MM format; the calculation is month_b minus month_a.",
        "parameters": {
            "type": "object",
            "properties": {
                "month_a": {"type": "string", "description": "reference month, like 2025-11"},
                "month_b": {"type": "string", "description": "comparison month, like 2025-12"},
                "group_by": {"type": "string", "enum": ["products", "region"],
                             "description": "split dimension, default region"},
            },
            "required": ["month_a", "month_b"],
        },
    },
    {
        "name": "plot",
        "description": "Generate the plot and save it as a PNG, then return the image path and the data plotted. "
                       "Line charts are suitable for showing trends over time, while bar charts are suitable for comparing categories.",
        "parameters": {
            "type": "object",
            "properties": {
                "kind": {"type": "string", "enum": ["line", "bar"]},
                "x": {"type": "string", "enum": ["products", "region", "month"]},
                "y": {"type": "string", "enum": ["sales", "quantity"]},
                "filters": {"type": "object", "description": "Filterable criteria"},
            },
            "required": ["kind", "x"],
        },
    },
]

# schemas：tool name -> Python function
from tools import inspect_data, group_stats, time_trend, compare_periods, plot

TOOL_FUNCS = {
    "inspect_data": inspect_data,
    "group_stats": group_stats,
    "time_trend": time_trend,
    "compare_periods": compare_periods,
    "plot": plot,
}