from re import S
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

s = field["start"]
f = field["finish"]
o = field["obstacles"]

sides = get_sides_pairs(o)

st.text(get_closest_intersection(s, f, sides))

st.write(plot_figure(s, f, o))


path_points = []
current_point = s
while current_point != f:
    path_points.append(current_point)

    nearest_intersection, line_points = get_closest_intersection(
        current_point, f, sides
    )

    break
# closest_intersection, side =
get_closest_intersection(
    current_point,
    f,
    sides,
)
# print(closest_intersection, side)
