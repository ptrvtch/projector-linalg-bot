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

st.title("Path Finding Algorithm")
st.info("""
Select the file example on the left, or select "Manual Input" and paste JSON to the window.
""")

# start page setup
graph = st.empty()

options = [
    "robot-test-1.json",
    "robot-test-4.json",
    "robot-test-25.json",
    "manual_input",
]

example = """{
	"start": [-8, 8],
	"finish": [-5, 6],
	"obstacles": [
	[[-10,6], [-4,10], [-6,7]],
	[[-10,0], [-7,6],[0,0]],
	[[-5,8], [0,8], [0,3]]
	]
}
"""

file_name = st.sidebar.selectbox("Select field", options=options)


if file_name != "manual_input":
    f = open(file_name)
    field = json.load(f)
else:
    input_area = st.sidebar.text_area("Manual Input", example, height=300)
    field = json.loads(input_area)

col1, col2 = st.beta_columns(2)

s = np.array(field["start"])
f = np.array(field["finish"])
o = field["obstacles"]

sides = get_sides_pairs(o)

path_points = []

# col1.write(plot_figure(s, f, o))

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

graph.write(plot_figure(s, f, o, np.array(path_points)))
