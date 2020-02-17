import open3d as o3d
import numpy as np
from warnings import warn
from plyfile import PlyData
from phenotypy.pcd_tools import merge_pcd

def read_ply(file_path, unit='m'):
    """
    :param file_path:
    :param unit: 'm', 'cm', 'mm', 'km'
    :return:
    """
    pcd = o3d.io.read_point_cloud(file_path)
    if not pcd.has_colors():
        cloud_ply = PlyData.read(file_path)
        cloud_data = cloud_ply.elements[0].data
        ply_names = cloud_data.dtype.names

        if 'red' in ply_names:
            colors = np.vstack((cloud_data['red'] / 255, cloud_data['green'] / 255, cloud_data['blue'] / 255)).T
            pcd.colors = o3d.utility.Vector3dVector(colors)
        elif 'diffuse_red' in ply_names:
            colors = np.vstack((cloud_data['diffuse_red'] / 255, cloud_data['diffuse_green'] / 255,
                                cloud_data['diffuse_blue'] / 255)).T
            pcd.colors = o3d.utility.Vector3dVector(colors)
        else:
            print('Can not find color info in ', ply_names)

    if unit == 'm':
        divider = 1
    elif unit == 'dm':
        divider = 10
    elif unit == 'cm':
        divider = 100
    elif unit == 'mm':
        divider = 1000
    elif unit == 'km':
        divider = 0.001
    else:
        raise TypeError(f'Cannot use [{unit}] as unit, please only tape m, cm, mm, or km.')

    pcd.points = o3d.utility.Vector3dVector(np.asarray(pcd.points) / divider)  # cm to m
    pcd.estimate_normals()

    # check units
    pcd_xyz = np.asarray(pcd.points)
    len_xyz = pcd_xyz.max(axis=0) - pcd_xyz.min(axis=0)
    short = len_xyz.min()
    if short > 100:
        warn(f'The shortest axis is {round(short)} m, please check if the unit is wrong! (current use [{unit}])')

    return pcd

def read_plys(file_list, unit='m'):
    """
    read a bunch of ply (e.g. two ply), and merge them into one (without registration, just add x,y,z one by one)
    :param file_list: ['file1.ply', 'file2.ply']
    :return: o3d.geometry.pointclouds
    """
    pcd_list = []
    for file_path in file_list:
        pcd_list.append(read_ply(file_path, unit=unit))

    return merge_pcd(pcd_list)

def write_ply(file_path):
    pass