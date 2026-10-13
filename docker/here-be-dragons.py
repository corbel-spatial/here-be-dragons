import marimo

__generated_with = "0.25.1"
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
def _(gpd):
    # Get recent earthquake data from the USGS
    quakes = gpd.read_file(
        "https://earthquake.usgs.gov/earthquakes/feed/v1.0/summary/1.0_month.geojson"
    )

    # Sort by most recent
    quakes.sort_values("time", ascending=False, inplace=True)

    quakes  # "time" and "updated" are Unix time (milliseconds since 1970-01-01)
    return (quakes,)


@app.cell
def _(quakes):
    # Convert Unix time to dates
    import pandas as pd

    time = quakes["time"].copy()  # copy so we don't modify the time column
    dates = pd.to_datetime(time, unit="ms")
    quakes["date"] = dates  # create a new column named "date"

    # Show specific columns
    some_columns = ["mag", "place", "date", "geometry"]
    quakes[some_columns]
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## Visualization
    """)
    return


@app.cell
def _():
    from lonboard import Map, ScatterplotLayer  # https://developmentseed.org/lonboard

    return Map, ScatterplotLayer


@app.cell
def _(quakes):
    # Reproject to WGS 1984 for lonboard
    quakes.to_crs("EPSG:4326", inplace=True)
    return


@app.cell
def _(ScatterplotLayer, quakes):
    # Set up the layer
    import numpy as np

    quake_layer = ScatterplotLayer.from_geopandas(
        quakes,
        get_radius=np.exp(quakes["mag"])
        * 1000,  # exponential base reflects Richter scale magnitude
        get_fill_color=[255, 150, 0, 100],  # red, green, blue, alpha (0-255)
    )
    return np, quake_layer


@app.cell
def _(Map, quake_layer):
    # Map the data
    Map(layers=[quake_layer], view_state={"longitude": 0, "latitude": 20, "zoom": 1})
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## Symbolizing by Date: Normalize First
    """)
    return


@app.cell
def _(quakes):
    # Get the offset for our dataset range
    offset = min(quakes["time"])
    offset
    return (offset,)


@app.cell
def _(offset, quakes):
    # Calculate the maximum time value after offsetting
    max_time = max(quakes["time"]) - offset
    max_time
    return (max_time,)


@app.cell
def _(offset, quakes):
    # Calculate the time values
    time_series = quakes["time"] - offset

    (
        time_series[0],
        time_series[int(len(time_series) / 2)],
        time_series[len(time_series) - 1],
    )
    return (time_series,)


@app.cell
def _(max_time, time_series):
    # Normalize the time series
    time_normalized = time_series / max_time

    (
        time_normalized[0],
        time_normalized[int(len(time_series) / 2)],
        time_normalized[len(time_series) - 1],
    )
    return (time_normalized,)


@app.cell
def _(time_normalized):
    # Convert time to unsigned 8-bit integer (0-255) for RGB values
    reds = time_normalized * 255
    reds = reds.to_numpy(dtype="uint8")
    reds
    return (reds,)


@app.cell
def _(np, reds):
    # Generate the green and blue arrays
    array_length = len(reds)
    greens = np.full(shape=array_length, fill_value=0, dtype=np.uint8)
    blues = np.full(shape=array_length, fill_value=0, dtype=np.uint8)
    blues
    return blues, greens


@app.cell
def _(np, reds):
    # Generate the alpha array
    alphas = reds * 0.75
    alphas = np.astype(alphas, "uint8")
    alphas
    return (alphas,)


@app.cell
def _(alphas, blues, greens, np, reds):
    # Assemble the NumPy array of RGBA values
    colors = np.column_stack([reds, greens, blues, alphas])
    colors
    return (colors,)


@app.cell
def _(Map, ScatterplotLayer, colors, np, quakes):
    # Map it again
    quake_layer2 = ScatterplotLayer.from_geopandas(
        quakes,
        get_radius=np.exp(quakes["mag"]) * 1000,
        get_fill_color=colors,
    )

    Map(layers=[quake_layer2], view_state={"longitude": 0, "latitude": 20, "zoom": 1})
    return


if __name__ == "__main__":
    app.run()
