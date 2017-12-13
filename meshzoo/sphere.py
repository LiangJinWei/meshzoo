# -*- coding: utf-8 -*-
#
import numpy

from .helpers import create_edges, _refine


# pylint: disable=too-many-locals
def uv_sphere(num_points_per_circle=20, num_circles=10, radius=1.0):
    # Mesh parameters
    n_phi = num_points_per_circle
    n_theta = num_circles

    # Generate suitable ranges for parametrization
    phi_range = numpy.linspace(0.0, 2*numpy.pi, num=n_phi, endpoint=False)
    theta_range = numpy.linspace(
            -numpy.pi/2 + numpy.pi/(n_theta-1),
            numpy.pi/2 - numpy.pi/(n_theta-1),
            num=n_theta - 2
            )

    num_nodes = len(theta_range) * len(phi_range) + 2
    nodes = numpy.empty(num_nodes, dtype=numpy.dtype((float, 3)))
    # south pole
    south_pole_index = 0
    k = 0
    nodes[k] = numpy.array([0.0, 0.0, -1.0])
    k += 1
    # nodes in the circles of latitude (except poles)
    for theta in theta_range:
        for phi in phi_range:
            nodes[k] = numpy.array([
                numpy.cos(theta) * numpy.sin(phi),
                numpy.cos(theta) * numpy.cos(phi),
                numpy.sin(theta)
                ])
            k += 1
    # north pole
    north_pole_index = k
    nodes[k] = numpy.array([0.0, 0.0, 1.0])

    nodes *= radius

    # create the elements (cells)
    num_elems = 2 * (n_theta-2) * n_phi
    elems = numpy.empty(num_elems, dtype=numpy.dtype((int, 3)))
    k = 0

    # connections to south pole
    for i in range(n_phi - 1):
        elems[k] = numpy.array([south_pole_index, i+1, i+2])
        k += 1
    # close geometry
    elems[k] = numpy.array([south_pole_index, n_phi, 1])
    k += 1

    # non-pole elements
    for i in range(n_theta - 3):
        for j in range(n_phi - 1):
            elems[k] = numpy.array([
                i*n_phi + j+1,
                i*n_phi + j+2,
                (i+1)*n_phi + j+2
                ])
            k += 1
            elems[k] = numpy.array([
                i*n_phi + j+1,
                (i+1)*n_phi + j+2,
                (i+1)*n_phi + j + 1
                ])
            k += 1

    # close the geometry
    for i in range(n_theta - 3):
        elems[k] = numpy.array([(i+1)*n_phi, i*n_phi + 1, (i+1)*n_phi + 1])
        k += 1
        elems[k] = numpy.array([(i+1)*n_phi, (i+1)*n_phi + 1, (i+2)*n_phi])
        k += 1

    # connections to the north pole
    for i in range(n_phi - 1):
        elems[k] = numpy.array([
            i+1 + n_phi*(n_theta-3) + 1,
            i + n_phi*(n_theta-3) + 1,
            north_pole_index
            ])
        k += 1
    # close geometry
    elems[k] = numpy.array([
        0 + n_phi*(n_theta-3) + 1,
        n_phi-1 + n_phi*(n_theta-3) + 1,
        north_pole_index
        ])
    k += 1
    assert k == num_elems, 'Wrong element count.'

    return nodes, elems


def iso_sphere(ref_steps=4):
    # Start off with an isosahedron and refine.

    # Construction from
    # <http://blog.andreaskahler.com/2009/06/creating-icosphere-mesh-in-code.html>.
    # Create 12 vertices of a icosahedron.
    t = (1.0 + numpy.sqrt(5.0)) / 2.0
    nodes = numpy.array([
        [-1, +t, +0],
        [+1, +t, +0],
        [-1, -t, +0],
        [+1, -t, +0],
        #
        [+0, -1, +t],
        [+0, +1, +t],
        [+0, -1, -t],
        [+0, +1, -t],
        #
        [+t, +0, -1],
        [+t, +0, +1],
        [-t, +0, -1],
        [-t, +0, +1],
        ])

    cells_nodes = numpy.array([
        [0, 11, 5],
        [0, 5, 1],
        [0, 1, 7],
        [0, 7, 10],
        [0, 10, 11],
        [1, 5, 9],
        [5, 11, 4],
        [11, 10, 2],
        [10, 7, 6],
        [7, 1, 8],
        [3, 9, 4],
        [3, 4, 2],
        [3, 2, 6],
        [3, 6, 8],
        [3, 8, 9],
        [4, 9, 5],
        [2, 4, 11],
        [6, 2, 10],
        [8, 6, 7],
        [9, 8, 1],
        ])

    # Refine.
    edge_nodes, cells_edges = create_edges(cells_nodes)
    args = nodes, cells_nodes, edge_nodes, cells_edges
    for k in range(ref_steps):
        args = _refine(*args)

    # push all nodes to the sphere
    nodes = args[0]
    nodes = (nodes.T / numpy.sqrt(numpy.einsum('ij,ij->i', nodes, nodes)).T).T

    return nodes, args[1]
