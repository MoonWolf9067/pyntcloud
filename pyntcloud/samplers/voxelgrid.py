import numpy as np
import pandas as pd

from scipy.spatial.distance import cdist

from .base import Sampler


class VoxelgridSampler(Sampler):
    def __init__(self, *, pyntcloud, voxelgrid_id):
        super().__init__(pyntcloud=pyntcloud)
        self.voxelgrid_id = voxelgrid_id

    def extract_info(self):
        self.voxelgrid = self.pyntcloud.structures[self.voxelgrid_id]


class VoxelgridCentersSampler(VoxelgridSampler):
    """Returns the points that represent each occupied voxel's center."""
    def compute(self):
        return pd.DataFrame(
            self.voxelgrid.voxel_centers[np.unique(self.voxelgrid.voxel_n)],
            columns=["x", "y", "z"])


class VoxelgridCentroidsSampler(VoxelgridSampler):
    """Returns the centroid of each group of points inside each occupied voxel."""
    def compute(self):
        df = pd.DataFrame(self.pyntcloud.xyz, columns=["x", "y", "z"])
        df["voxel_n"] = self.voxelgrid.voxel_n
        return df.groupby("voxel_n").mean()


class VoxelgridNearestSampler(VoxelgridSampler):
    """Returns the N closests points to each occupied voxel's center."""

    def __init__(self, *, pyntcloud, voxelgrid_id, n=1):
        super().__init__(pyntcloud=pyntcloud, voxelgrid_id=voxelgrid_id)
        self.n = n

    def compute(self):
        df = pd.DataFrame(self.pyntcloud.xyz, columns=["x", "y", "z"])
        df["voxel_n"] = self.voxelgrid.voxel_n
        nearests = []
        for voxel_n, x in df.groupby("voxel_n", sort=False):
            xyz = x.loc[:, ["x", "y", "z"]].values
            center = self.voxelgrid.voxel_centers[voxel_n]
            voxel_nearest = cdist([center], xyz)[0].argsort()[:self.n]
            nearests.extend(x.index.values[voxel_nearest])
        return self.pyntcloud.points.iloc[nearests].reset_index(drop=True)
