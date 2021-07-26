import numpy as np
from itertools import combinations
import plotly.graph_objects as go
import streamlit as st

# https://stackoverflow.com/a/9997374
# col1, col2, col3 = st.beta_col`umns(3)
def ccw(A, B, C):
    return (C[1] - A[1]) * (B[0] - A[0]) > (B[1] - A[1]) * (C[0] - A[0])


# Return true if line segments AB and CD intersect
def is_intersection(A, B, C, D):
    return ccw(A, C, D) != ccw(B, C, D) and ccw(A, B, C) != ccw(A, B, D)


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


def plot_figure(s, f, o, path_points=None):
    # s = np.array(field["start"])
    # f = np.array(field["finish"])
    # o = field["obstacles"]
    start = go.Scatter(x=[s[0]], y=[s[1]], name="Start")
    finish = go.Scatter(x=[f[0]], y=[f[1]], name="Finish")
    x, y = np.array([s, f]).T
    line = go.Scatter(x=x, y=y, name="Line")
    figures = [start, finish, line]
    if path_points is not None:
        path = go.Scatter(x=path_points.T[0], y=path_points.T[1], name="Path")
        figures.append(path)

    coords1 = [np.array(obj).T for obj in o]
    obstacles = [
        go.Scatter(x=c[0], y=c[1], fill="toself", showlegend=False) for c in coords1
    ]

    fig = go.Figure(
        obstacles + figures,
        layout=dict(
            width=800,
            height=800,
            # xaxis=dict(range=[-15, 15]),
            # yaxis=dict(range=[-10, 10]),
        ),
    )
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
