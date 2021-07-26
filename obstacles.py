from re import S
import pandas as pd
import streamlit as st
import numpy as np
import plotly.graph_objects as go
import json
from utils import (
    check_polyline,
    get_closest_point,
    get_sides_pairs,
    get_closest_intersection,
    plot_figure,
    equal,
)

st.set_page_config(layout="wide")

st.title("Path Finding Algorithm")
st.sidebar.info(
    """
Select the file example on the left, or select "Manual Input" and paste JSON to the window.
"""
)

# start page setup
path_color = st.color_picker("Path Trace color", value="#FF0000")
graph = st.empty()
total_distance = st.empty()
path_coordinates = st.empty()

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

file_name = st.sidebar.selectbox("Select field", options=options, index=3)


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

finished_successfully = False

# col1.write(plot_figure(s, f, o))

current_point = s

with st.beta_expander("Click here to see step-by-step details:"):
    log = st.info(f"starting from point {current_point}")

    path_points.append(current_point)
    iteration = 0
    while not np.array_equal(current_point, f):
        iteration = iteration + 1
        st.markdown(iteration)
        if iteration == 100:
            st.warning(f"{iteration} iterations, aborting")
            break

        st.markdown(
            f"Looking for nearest intersection of point {current_point} and {f}"
        )
        nearest_intersection, line_points = get_closest_intersection(
            current_point, f, sides
        )
        if nearest_intersection is None:
            current_point = f
            st.info(
                f"\nNo obstacles between current and finish point, seting finish point as {current_point}"
            )
            path_points.append(current_point)
            finished_successfully = True
            break
        else:
            previous_point = current_point
            current_point = nearest_intersection
            st.markdown(f"\nMoving to nearest intersection: {current_point}")

            closest_obstacle_point = get_closest_point(line_points, f, s)
            if equal(current_point, closest_obstacle_point):
                st.info("current_point and closest_obstacle are equal!")
                continue
            a, b = get_closest_intersection(
                previous_point, closest_obstacle_point, sides
            )
            if a is not None:
                path_points.append(current_point)
            current_point = closest_obstacle_point
            st.markdown(
                f"\nMoving to the obstacle edge nearest to finish: {current_point}"
            )
            path_points.append(current_point)
if not finished_successfully:
    st.sidebar.warning(
        f"Algorithm not finished successfully! stopped after {iteration} iterations"
    )
st.sidebar.text("Path point coordinates below:")
path_coordinates.dataframe(path_points)
st.sidebar.markdown(
    json.dumps(pd.Series(path_points).to_json(orient="values"), indent=2)
)

total_len = 0
for i in range(1, len(path_points)):
    path_segment = np.array(path_points[i - 1] - path_points[i])
    length = np.linalg.norm(path_segment)
    total_len += length
total_distance.text(f"Total Distance is {total_len}")

if check_polyline(path_points, np.array(o)):
    st.info("No intersections found using function 'check_polilyne'")

graph.write(plot_figure(s, f, o, np.array(path_points), path_color=path_color))

st.markdown(
    """
### Algorithm of robot

0. Mark start point as the **[current step]** to the finish.
1. Check if segment from **[current step]** to the finish has any obstacles. 
  - 1.1. If it doesn't have obstacles, move **[current step]** to finish point and **go to [9]**
  - 1.2. If there are obstacles, go to **[3]**.
3. Move to the **[intersection]** between path segment and obstacle.
4. Measure distance to the finish for every of two dots that form a segment that intersects the path. 
5. Select the point that is closer to the finish point as an **[intermediate goal]**. 
6. Check if there is no obstacles between **[current step]** and **[intermediate goal]**. 
  - 6.1. If there is no intersection with obstacles, move to the  **[intermediate goal]** and make it **[current step]**
  - 6.2. If there is going to be an intersection, mark **[intersection]** as **[current step]**

7. Move to the **[intermediate goal]** and mark it as **[current step]**.
8. Go To 1.
9. Finish
"""
)
