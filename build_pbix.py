"""
build_pbix.py
Generates the Power BI Desktop file 'Sales_Performance_Dashboard.pbix'
with complete report layout, visual container metadata, theme, and data model references.
"""

import os
import json
import zipfile

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
POWERBI_DIR = os.path.join(BASE_DIR, "powerbi")
os.makedirs(POWERBI_DIR, exist_ok=True)

PBIX_OUTPUT = os.path.join(POWERBI_DIR, "Sales_Performance_Dashboard.pbix")
ROOT_PBIX_OUTPUT = os.path.join(BASE_DIR, "Sales_Performance_Dashboard.pbix")

# 1. Version file content
VERSION_CONTENT = "1.28\x00"

# 2. Settings file content
SETTINGS_CONTENT = json.dumps({
    "version": "2.0",
    "displaySettings": {
        "paneSettings": {
            "expandedPanes": ["fields", "visualizations"],
            "visiblePanes": ["fields", "visualizations", "filters"]
        }
    }
}, indent=2)

# 3. [Content_Types].xml
CONTENT_TYPES_XML = """<?xml version="1.0" encoding="utf-8"?>
<Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types">
  <Default Extension="json" ContentType="application/json" />
  <Default Extension="xml" ContentType="application/xml" />
  <Override PartName="/Version" ContentType="application/json" />
  <Override PartName="/Settings" ContentType="application/json" />
  <Override PartName="/Report/Layout" ContentType="application/json" />
  <Override PartName="/Metadata" ContentType="application/json" />
</Types>
"""

# 4. Report Theme JSON
THEME_JSON = {
    "name": "CorporateExecutiveNavy",
    "dataColors": ["#1E3A8A", "#3B82F6", "#10B981", "#F59E0B", "#8B5CF6", "#EC4899", "#14B8A6", "#64748B"],
    "background": "#F8FAFC",
    "foreground": "#0F172A",
    "tableAccent": "#1E3A8A",
    "visualStyles": {
        "*": {
            "*": {
                "background": [{"color": {"solid": {"color": "#FFFFFF"}}, "transparency": 0}],
                "border": [{"show": True, "color": {"solid": {"color": "#E2E8F0"}}, "radius": 6}]
            }
        }
    }
}

# 5. Report Layout JSON
LAYOUT_JSON = {
    "id": 0,
    "resourcePackages": [],
    "theme": json.dumps(THEME_JSON),
    "config": json.dumps({
        "version": "5.55",
        "themeCollection": {"baseTheme": {"name": "CY24SU02"}},
        "activeSectionIndex": 0,
        "defaultDrillFilterOtherVisuals": True
    }),
    "sections": [
        {
            "id": 0,
            "name": "ReportSection_SalesExecutive",
            "displayName": "Sales Executive Overview",
            "width": 1920,
            "height": 1080,
            "config": json.dumps({
                "objects": {
                    "background": [{"properties": {"color": {"solid": {"color": "#F8FAFC"}}, "transparency": 0}}]
                }
            }),
            "visualContainers": [
                # Visual 0: Header Banner
                {
                    "x": 20, "y": 15, "z": 0, "width": 1880, "height": 70,
                    "config": json.dumps({
                        "name": "HeaderBanner",
                        "singleVisual": {
                            "visualType": "textbox",
                            "objects": {
                                "general": [{
                                    "properties": {
                                        "paragraphs": [{
                                            "textRuns": [{
                                                "value": "RETAIL & E-COMMERCE SALES PERFORMANCE DASHBOARD",
                                                "textStyle": {"fontFamily": "Segoe UI", "fontSize": "20pt", "fontWeight": "bold", "color": "#0F172A"}
                                            }]
                                        }]
                                    }
                                }]
                            }
                        }
                    })
                },
                # Visual 1: Slicer - Region
                {
                    "x": 1280, "y": 20, "z": 1, "width": 280, "height": 60,
                    "config": json.dumps({
                        "name": "SlicerRegion",
                        "singleVisual": {
                            "visualType": "slicer",
                            "projections": {"Values": [{"queryRef": "DIM_LOCATION.Region"}]},
                            "objects": {"general": [{"properties": {"filter": {"filterType": "categorical"}}}]}
                        }
                    })
                },
                # Visual 2: Slicer - Category
                {
                    "x": 1580, "y": 20, "z": 2, "width": 320, "height": 60,
                    "config": json.dumps({
                        "name": "SlicerCategory",
                        "singleVisual": {
                            "visualType": "slicer",
                            "projections": {"Values": [{"queryRef": "DIM_PRODUCT.Category"}]}
                        }
                    })
                },
                # Visual 3: KPI Card - Total Revenue
                {
                    "x": 20, "y": 100, "z": 3, "width": 360, "height": 130,
                    "config": json.dumps({
                        "name": "KPITotalRevenue",
                        "singleVisual": {
                            "visualType": "card",
                            "projections": {"Fields": [{"queryRef": "FACT_SALES.Total_Sales"}]},
                            "objects": {
                                "labels": [{"properties": {"labelDisplayUnits": 0, "color": {"solid": {"color": "#1E3A8A"}}}}],
                                "categoryLabels": [{"properties": {"show": True, "color": {"solid": {"color": "#64748B"}}}}]
                            }
                        }
                    })
                },
                # Visual 4: KPI Card - Total Orders
                {
                    "x": 400, "y": 100, "z": 4, "width": 360, "height": 130,
                    "config": json.dumps({
                        "name": "KPITotalOrders",
                        "singleVisual": {
                            "visualType": "card",
                            "projections": {"Fields": [{"queryRef": "FACT_SALES.Total_Orders"}]},
                            "objects": {
                                "labels": [{"properties": {"color": {"solid": {"color": "#0284C7"}}}}],
                                "categoryLabels": [{"properties": {"show": True, "color": {"solid": {"color": "#64748B"}}}}]
                            }
                        }
                    })
                },
                # Visual 5: KPI Card - Units Sold
                {
                    "x": 780, "y": 100, "z": 5, "width": 360, "height": 130,
                    "config": json.dumps({
                        "name": "KPITotalUnits",
                        "singleVisual": {
                            "visualType": "card",
                            "projections": {"Fields": [{"queryRef": "FACT_SALES.Total_Units_Sold"}]},
                            "objects": {
                                "labels": [{"properties": {"color": {"solid": {"color": "#D97706"}}}}],
                                "categoryLabels": [{"properties": {"show": True, "color": {"solid": {"color": "#64748B"}}}}]
                            }
                        }
                    })
                },
                # Visual 6: KPI Card - Average Order Value (AOV)
                {
                    "x": 1160, "y": 100, "z": 6, "width": 360, "height": 130,
                    "config": json.dumps({
                        "name": "KPIAverageOrderValue",
                        "singleVisual": {
                            "visualType": "card",
                            "projections": {"Fields": [{"queryRef": "FACT_SALES.Average_Order_Value"}]},
                            "objects": {
                                "labels": [{"properties": {"color": {"solid": {"color": "#059669"}}}}],
                                "categoryLabels": [{"properties": {"show": True, "color": {"solid": {"color": "#64748B"}}}}]
                            }
                        }
                    })
                },
                # Visual 7: KPI Card - Active Customers
                {
                    "x": 1540, "y": 100, "z": 7, "width": 360, "height": 130,
                    "config": json.dumps({
                        "name": "KPITotalCustomers",
                        "singleVisual": {
                            "visualType": "card",
                            "projections": {"Fields": [{"queryRef": "FACT_SALES.Total_Customers"}]},
                            "objects": {
                                "labels": [{"properties": {"color": {"solid": {"color": "#7C3AED"}}}}],
                                "categoryLabels": [{"properties": {"show": True, "color": {"solid": {"color": "#64748B"}}}}]
                            }
                        }
                    })
                },
                # Visual 8: Monthly Sales & Orders Trend (Line Chart)
                {
                    "x": 20, "y": 250, "z": 8, "width": 1240, "height": 410,
                    "config": json.dumps({
                        "name": "MonthlySalesTrend",
                        "singleVisual": {
                            "visualType": "lineChart",
                            "projections": {
                                "Category": [{"queryRef": "DIM_DATE.Year_Month"}],
                                "Y": [{"queryRef": "FACT_SALES.Total_Sales"}],
                                "Y2": [{"queryRef": "FACT_SALES.Total_Orders"}]
                            },
                            "objects": {
                                "title": [{"properties": {"text": {"expr": {"literal": "Monthly Net Revenue ($K) and Order Volume Trend"}}}}]
                            }
                        }
                    })
                },
                # Visual 9: Category Revenue Share (Donut Chart)
                {
                    "x": 1280, "y": 250, "z": 9, "width": 620, "height": 410,
                    "config": json.dumps({
                        "name": "CategoryRevenueShare",
                        "singleVisual": {
                            "visualType": "pieChart",
                            "projections": {
                                "Category": [{"queryRef": "DIM_PRODUCT.Category"}],
                                "Y": [{"queryRef": "FACT_SALES.Total_Sales"}]
                            },
                            "objects": {
                                "title": [{"properties": {"text": {"expr": {"literal": "Revenue Contribution by Product Category"}}}}]
                            }
                        }
                    })
                },
                # Visual 10: Top 10 Products by Revenue (Bar Chart)
                {
                    "x": 20, "y": 680, "z": 10, "width": 1100, "height": 380,
                    "config": json.dumps({
                        "name": "Top10ProductsBar",
                        "singleVisual": {
                            "visualType": "barChart",
                            "projections": {
                                "Category": [{"queryRef": "DIM_PRODUCT.Product_Name"}],
                                "Y": [{"queryRef": "FACT_SALES.Total_Sales"}]
                            },
                            "objects": {
                                "title": [{"properties": {"text": {"expr": {"literal": "Top 10 Products by Total Net Sales"}}}}]
                            }
                        }
                    })
                },
                # Visual 11: Regional Market Performance (Clustered Column Chart)
                {
                    "x": 1140, "y": 680, "z": 11, "width": 760, "height": 380,
                    "config": json.dumps({
                        "name": "RegionalSalesBar",
                        "singleVisual": {
                            "visualType": "columnChart",
                            "projections": {
                                "Category": [{"queryRef": "DIM_LOCATION.Region"}],
                                "Series": [{"queryRef": "DIM_PRODUCT.Category"}],
                                "Y": [{"queryRef": "FACT_SALES.Total_Sales"}]
                            },
                            "objects": {
                                "title": [{"properties": {"text": {"expr": {"literal": "Regional Sales Performance by Category"}}}}]
                            }
                        }
                    })
                }
            ]
        }
    ]
}

# 6. Metadata JSON
METADATA_JSON = {
    "version": "1.0",
    "name": "Sales_Performance_Dashboard",
    "createdTimestamp": "2026-11-24T10:00:00Z",
    "modifiedTimestamp": "2026-11-24T11:00:00Z"
}

def create_pbix_file(output_path):
    """Package the components into a standard Power BI Desktop (.pbix) archive."""
    with zipfile.ZipFile(output_path, "w", compression=zipfile.ZIP_DEFLATED) as zf:
        zf.writestr("Version", VERSION_CONTENT)
        zf.writestr("[Content_Types].xml", CONTENT_TYPES_XML.strip())
        zf.writestr("Settings", SETTINGS_CONTENT)
        zf.writestr("Report/Layout", json.dumps(LAYOUT_JSON, indent=2))
        zf.writestr("Metadata", json.dumps(METADATA_JSON, indent=2))
        
    print(f"Generated Power BI Desktop file: {output_path} ({os.path.getsize(output_path)} bytes)")

if __name__ == "__main__":
    create_pbix_file(PBIX_OUTPUT)
    create_pbix_file(ROOT_PBIX_OUTPUT)
