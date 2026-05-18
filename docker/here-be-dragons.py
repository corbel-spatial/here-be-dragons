import marimo

__generated_with = "0.23.6"
app = marimo.App(width="medium")


@app.cell
def _():
    import marimo as mo
    import geopandas as gpd

    return gpd, mo


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    # 🌍 Here Be Dragons 🐲
    """)
    return


@app.cell
def _(gpd):
    gpd.show_versions()
    return


if __name__ == "__main__":
    app.run()
