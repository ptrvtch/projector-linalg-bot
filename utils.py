import numpy as np
from itertools import combinations
import plotly.graph_objects as go
import streamlit as st


def check_polyline(polyline, obstacles):
    """this function returns True if the polyline does not intersect obstacles
    Otherwise it returns False
    You can use it to verify your algorithm
    """
    for obstacle in obstacles:
        for i in range(len(obstacle)):
            obstacle_segment = (obstacle[i - 1], obstacle[i])
            for j in range(1, len(polyline)):
                path_segment = (polyline[j - 1], polyline[j])
                if is_intersection(
                    obstacle_segment[0],
                    obstacle_segment[1],
                    path_segment[0],
                    path_segment[1],
                ):
                    st.warning(
                        f"segments intersect: {obstacle_segment}, {path_segment}"
                    )
                    return False
    return True


def is_intersection(A, B, C, D):
    ## let's find two line coming through the two points of each segment
    ## v = a * v1 + (1 - a) * v2
    ## u = b * u1 + (1 - b) * u2
    ## lines intersect at u = v, =>  a * v1 + (1 - a) * v2 = b * u1 + (1 - b) * u2
    ## or  (v1 - v2) * a + (u2 - u1) * b = u2 - v2
    ##
    ## if lines intersect within the given segments, a and b must be strictly between 0 and 1

    v1, v2 = np.array(A), np.array(B)
    u1, u2 = np.array(C), np.array(D)

    M = np.array([v1 - v2, u2 - u1]).T
    if np.linalg.matrix_rank(M) < 2:
        return False

    a, b = np.linalg.inv(M).dot(u2 - v2)

    return (0 < a < 1) and (0 < b < 1)


def get_sides_pairs(obstacles):
    o = obstacles
    coords1 = [np.array(obj) for obj in o]
    pairs = np.array([np.array(list(combinations(c, 2))) for c in coords1])
    flat_list = []
    for p in pairs:
        for pp in p:
            flat_list.append(np.array(pp).T)
    return np.array(flat_list)


def get_intersect(a1, a2, b1, b2):
    """
    Returns the point of intersection of the lines passing through a2,a1 and b2,b1.
    a1: [x, y] a point on the first line
    a2: [x, y] another point on the first line
    b1: [x, y] a point on the second line
    b2: [x, y] another point on the second line
    https://stackoverflow.com/a/42727584
    """
    s = np.vstack([a1, a2, b1, b2])  # s for stacked
    h = np.hstack((s, np.ones((4, 1))))  # h for homogeneous
    l1 = np.cross(h[0], h[1])  # get first line
    l2 = np.cross(h[2], h[3])  # get second line
    x, y, z = np.cross(l1, l2)  # point of intersection
    if z == 0:  # lines are parallel
        return (float("inf"), float("inf"))
    return np.array((x / z, y / z))


def get_closest_intersection(point, finish, sides):
    intersections = []
    min_length = np.inf
    lines = None
    next_intersection = None
    for s in sides:
        A, B, C, D = point, finish, s.T[0], s.T[1]
        intrs = is_intersection(A, B, C, D)
        if intrs:
            intersection = get_intersect(A, B, C, D)
            intersection_length = np.linalg.norm(intersection - point)
            if equal(A, C) or equal(A, D):
                continue
            if intersection_length < min_length:
                min_length = intersection_length
                lines = (C, D)
                next_intersection = intersection

            intersections.append(
                {
                    "intersection": intersection,
                    "distance": np.linalg.norm(intersection - point),
                    "sides": s,
                }
            )
    if next_intersection is None:
        return (None, None)
    return (next_intersection, lines)


def plot_figure(s, f, o, path_points=None, path_color=None):
    start = go.Scatter(x=[s[0]], y=[s[1]], name="Start")
    finish = go.Scatter(x=[f[0]], y=[f[1]], name="Finish")
    if not path_color:
        path_color = "orange"
    x, y = np.array([s, f]).T
    # line = go.Scatter(x=x, y=y, name="Line")
    figures = [start, finish]
    if path_points is not None:
        path = go.Scatter(
            x=path_points.T[0],
            y=path_points.T[1],
            name="Path",
            marker_color=path_color,
            line_width=3,
        )
        figures = [path] + figures

    coords1 = [np.array(obj).T for obj in o]
    obstacles = [
        go.Scatter(x=c[0], y=c[1], fill="toself", showlegend=False) for c in coords1
    ]

    fig = go.Figure(obstacles + figures)
    return fig


def get_closest_point(lines, finish, start):
    min_len = np.inf
    min_pt = None
    for i, line in enumerate(lines):
        if equal(line, start):
            st.info("close!")
            continue
        l = np.linalg.norm(finish - line)
        if l < min_len:
            min_len = l
            min_pt = line
    return min_pt


def equal(a, b, tol=1e-5):
    return np.linalg.norm(a - b) < tol
