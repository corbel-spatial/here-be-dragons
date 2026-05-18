import marimo

app = marimo.App(width="medium")


@app.cell
def _():
    import marimo as mo

    return (mo,)


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    # 🌍 Here Be Dragons 🐲
    """)
    return


@app.cell
def _():
    import geopandas as gpd

    gpd.show_versions()
    return (gpd,)


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    # Demo: Mapping Recent Earthquakes
    """)
    return


@app.cell
def _():
    # Install and import lonboard
    from lonboard import Map, ScatterplotLayer

    return Map, ScatterplotLayer


@app.cell
def _(gpd):
    # Get recent earthquake data from the USGS
    quake_gdf = gpd.read_file(
        "https://earthquake.usgs.gov/earthquakes/feed/v1.0/summary/1.0_month.geojson"
    )
    quake_gdf.crs = "EPSG:4326"
    quake_gdf
    return (quake_gdf,)


@app.cell
def _(Map, ScatterplotLayer, quake_gdf):
    # Map the data
    Map(
        layers=[
            ScatterplotLayer.from_geopandas(
                quake_gdf,
                get_radius=quake_gdf["mag"] * 50000,
                get_fill_color=[255, 140, 0, 200],
            )
        ]
    )
    return


if __name__ == "__main__":
    app.run()
