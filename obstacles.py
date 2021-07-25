from re import S
import streamlit as st
import numpy as np
import plotly.graph_objects as go
import json
from utils import (
    get_closest_point,
    get_sides_pairs,
    get_closest_intersection,
    plot_figure,
)

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

s = np.array(field["start"])
f = np.array(field["finish"])
o = field["obstacles"]

sides = get_sides_pairs(o)

intersection, line = get_closest_intersection(s, f, sides)

st.text((intersection, line))

st.text(get_closest_point(line, f))



path_points = []
current_point = s
while not np.array_equal(current_point, f):
    st.text(current_point)
    path_points.append(current_point)

    nearest_intersection, line_points = get_closest_intersection(
        current_point, f, sides
    )
    if nearest_intersection is None:
        current_point = f
        st.text(current_point)
        path_points.append(current_point)
        break
    else:
        current_point = nearest_intersection
        st.text(current_point)
        path_points.append(current_point)

        closest_obstacle_point = get_closest_point(line_points, f)
        current_point = closest_obstacle_point

st.write(path_points)

st.write(plot_figure(s, f, o, np.array(path_points)))

# closest_intersection, side =
get_closest_intersection(
    current_point,
    f,
    sides,
)
# print(closest_intersection, side)
