import streamlit as st
import numpy as np
import plotly.graph_objects as go
import json
from utils import get_sides_pairs, get_closest_intersection, plot_figure

st.set_page_config(layout="wide")

options = [
    "robot-test-1.json",
    "robot-test-4.json",
    "robot-test-25.json",
    "manual_input",
]
file_name = st.selectbox("Select field", options=options)

if file_name != "manual_input":
    f = open(file_name)
    field = json.load(f)

start = field["start"]
finish = field["finish"]
obstacles = field["obstacles"]

sides = get_sides_pairs(obstacles)

st.text(get_closest_intersection(start, finish, sides))

st.write(plot_figure(start, finish, obstacles))
