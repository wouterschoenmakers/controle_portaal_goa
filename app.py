import streamlit as st
import geopandas as gpd
import pandas as pd
import numpy as np
import time
from utils import process_geometries

st.header("Welkom Bilal!👋")
st.subheader("Controleer hier de resultaten van de uploads")
st.markdown("In dit portaal wordt een vergelijking gemaakt of het upgeloade pakket terug te vinden is in gisib")

gisib_col, pakket_col = st.columns((1,1))
upload_gisib = gisib_col.file_uploader(label='Upload hier het Gisib file',
                                       accept_multiple_files=False,type="gpkg",key="load_gisib")
upload_pakket = pakket_col.file_uploader(label = "Upload hier het pakket",
                                      accept_multiple_files=False,type="gpkg",key="load_pakket")
gisib = None
pakket = None


relevant_cols = ["Guid","Type","Type gedetailleerd","Type extra gedetailleerd"]
@st.cache_data
def load_file(filepath : str):
    return gpd.read_file(filename=filepath, include_fields=relevant_cols,engine="fiona")

if st.button("Run"):
    if upload_gisib:
        gisib = load_file(filepath=upload_gisib)
        st.write(f"De gisib file heeft {gisib.shape[0]} rijen")

    if upload_pakket:

        pakket = load_file(filepath=upload_pakket)
        st.write(f"Het verwerkingspakket heeft {pakket.shape[0]} rijen")

guids_correct = False
geometry = False
types = False

relevant_cols_left = [col+"_left" for col in relevant_cols]
relevant_cols_right = [col +"_right" for col in relevant_cols]
results = {}
if isinstance(gisib,gpd.GeoDataFrame) and isinstance(pakket,gpd.GeoDataFrame):
    st.success("Beide bestanden zijn goed ingeladen! Lekker bezig Bilal 💯")

    result = process_geometries(left_df = gisib,
                                right_df = pakket,
                                how = "inner")
    guid_check = set(result.Guid_left).intersection(result.Guid_right)
    # st.write(f"Er zijn {len(guid_check)}, die overeenkomen")
    if len(guid_check) == len(pakket):
        guids_correct = True
        st.write("Guids ✅")
    check_result = result.loc[lambda df: ((df.overlap_percentage > 99.9) & (df.oppervlak_percentage > 99.9))]
    # st.write(f"Er zijn {check_result.shape[0]} vlakken die een overlap en oppervlak percentage > 99.9 hebben")
    results["Guid matches"] = len(guid_check)
    results["Geometry matches"] = check_result.shape[0]
    if len(check_result) == len(pakket):
        geometry = True
        st.write()
        st.write("Geometry ✅")
    types_check = (check_result.loc[:,relevant_cols_left].fillna(0).values == check_result.loc[:,relevant_cols_right].fillna(0).values).all(axis=1).sum()
    # st.write(f"Er zijn {types_check} matches op Guid, Type, Type gedetailleerd en Type extra gedetailleerd")
    results["Types matches"] = types_check
    if types_check == len(pakket):
        types = True
        st.write("Types ✅")
    results_table = pd.DataFrame(data=results,index=["Aantal matches"])
    st.write("Het aantal matches per check")
    st.table(results_table)
    st.table((results_table / len(pakket) * 100))
    if guids_correct:
        if geometry:
            if types:
                st.balloons()
                st.success("💯💯💯💯💯💯")


clear = st.button("Clear data cache")
if clear:
    st.cache_data.clear()

