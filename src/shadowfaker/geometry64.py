"""Causal, local Riemannian-metric-inspired colouring of adjacent cells.

This is a discrete explanatory field, not a learned geodesic or a map of clicks.
The tangent comes from observed movement BEFORE time t and ally positions at t.
"""
import numpy as np


def local_metric(current: tuple[float,float], previous: tuple[float,float] | None,
                 ally_points: list[tuple[float,float]]) -> list[list[float]]:
    origin = np.asarray(current,dtype=float)
    inertia = origin - np.asarray(previous if previous is not None else current,dtype=float)
    attention = np.zeros(2)
    if ally_points:
        directions = [np.asarray(point,dtype=float)-origin for point in ally_points]
        nearby = sorted(directions,key=lambda v:np.linalg.norm(v))[:2]
        attention = np.mean(nearby,axis=0)
    tangent = .75*inertia + .25*attention
    length = np.linalg.norm(tangent)
    if length < 1e-6: tangent = np.array([1.0,0.0])
    else: tangent /= length
    normal = np.array([-tangent[1],tangent[0]])
    # Distances use cell coordinates. The tensor is symmetric positive definite:
    # 1/7^2 along observed momentum / nearby allies, 1/3.5^2 across it.
    g = np.outer(tangent,tangent)/49 + np.outer(normal,normal)/12.25
    return g.tolist()


def field64(current: tuple[float,float], metric: list[list[float]]) -> np.ndarray:
    yy,xx = np.mgrid[0:64,0:64]
    dx = xx+.5-float(current[0])*64
    dy = yy+.5-float(current[1])*64
    g = np.asarray(metric,dtype=float)
    if not np.allclose(g,g.T) or np.linalg.eigvalsh(g).min() <= 0:
        raise ValueError("The local metric must be symmetric positive definite")
    distance2 = g[0,0]*dx*dx + 2*g[0,1]*dx*dy + g[1,1]*dy*dy
    return np.exp(-.5*distance2).astype(np.float32)
