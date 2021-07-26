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
    equal,
)

st.set_page_config(layout="wide")

# start page setup


options = [
    "robot-test-1.json",
    "robot-test-4.json",
    "robot-test-25.json",
    "manual_input",
]
file_name = st.selectbox("Select field", options=options)


col1, col2 = st.beta_columns(2)

if file_name != "manual_input":
    f = open(file_name)
    field = json.load(f)

s = np.array(field["start"])
f = np.array(field["finish"])
o = field["obstacles"]

sides = get_sides_pairs(o)

path_points = []

col1.write(plot_figure(s, f, o))

current_point = s
log = st.info(f"starting from point {current_point}")

path_points.append(current_point)
iteration = 0
while not np.array_equal(current_point, f):
    iteration = iteration + 1
    st.markdown(iteration)
    if iteration == 10:
        st.warning(f"{iteration} iterations, aborting")
        break

    st.markdown(f"Looking for nearest intersection of point {current_point} and {f}")
    nearest_intersection, line_points = get_closest_intersection(
        current_point, f, sides
    )
    if nearest_intersection is None:
        current_point = f
        st.info(
            f"\nNo obstacles between current and finish point, seting finish point as {current_point}"
        )
        path_points.append(current_point)
        break
    else:
        previous_point = current_point
        current_point = nearest_intersection
        st.markdown(f"\nMoving to nearest intersection: {current_point}")

        closest_obstacle_point = get_closest_point(line_points, f, s)
        if equal(current_point, closest_obstacle_point):
            st.info("current_point and closest_obstacle are equal!")
            continue
        a, b = get_closest_intersection(previous_point, closest_obstacle_point, sides)
        if a is not None:
            path_points.append(current_point)
        current_point = closest_obstacle_point
        st.markdown(f"\nMoving to the obstacle edge nearest to finish: {current_point}")
        path_points.append(current_point)


st.dataframe(path_points)

col2.write(plot_figure(s, f, o, np.array(path_points)))
