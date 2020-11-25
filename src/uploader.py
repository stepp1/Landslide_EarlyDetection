import numpy as np
import fsspec
import gcsfs
from pathlib import Path

# import torch
from .ReMasFrame import ReMasFrame
from .api_gcp import GCSBucket


class Uploader():
    r"""
    Class to automate upload of data to GCP
    """
    def __init__(self, root_dir):
        self.gstorage = GCSBucket(token='default')
        self.root_dir = root_dir
        self.products = ReMasFrame.get_products()
        self.upload_path = None
        self.file_name = None

        self.event_date_str = None
        self.event_id = None
        self.event_geometry = None

        self.current_prod = None     # name of product in self.products
        self.current_cat = None      # name of category must be one of [weather, elevation, ...]
        self.current_scenes = None   # current scene collection
        self.current_ctx = None      # current geocontext of current scene
        self.current_stack = None    # current stack

    def set_current_prod(self, cat_str: str, prod_str: str):
        """
        Sets current product.
        """
        self.current_prod = prod_str
        self.current_cat = cat_str

    def set_current_event(self, event_date : str, event_id : str, event_geometry):
        """
        Sets current event.
        """
        self.event_date_str = event_date
        self.event_id = event_id
        self.event_geometry = event_geometry

    def create_upload_path(self):
        """
        Creates path dir for current event and prod
        """
        path = f"{self.root_dir}/{self.event_date_str}_{self.event_id}/"
        file_name = f"{self.current_prod}.npy"
        self.upload_path = path
        self.file_name = file_name
        return path, file_name
    
    def fill_value(self, masked_array, method='mean'):
        """
        Fills masked value with mean of each image in a 4d array

        e.g: 
        x is (bs, channels, w, h)
        for each image:
         >   for each channel:
                image.fill_value = image.mean()
                image.filled()
        """
        if method != 'mean':
            raise NotImplementedError

        for image in masked_array:
            for channel in image:
                channel.fill_value = channel.mean()
                channel.filled()

        return masked_array
        

    def upload_current_stack(self):
        """
        Uploads current stack to current upload_path.
        """
        Path(self.upload_path).mkdir(parents=True, exist_ok=True)
        np.save(f"{self.upload_path}/{self.file_name}", self.current_stack)

        self.gstorage.put(
            local_path=f"{self.upload_path}/{self.file_name}", 
            remote_path=f"{self.upload_path}"
            )
        Path(f"{self.upload_path}/{self.file_name}").unlink()

    def get_scenes(self, res, buffer_size=0.1):
        """
        Retrieves images from descarteslabs for the current prod
        """
        # Returns start and end date of a 10 day interval, last day is the date of event
        start_date, end_date = ReMasFrame.date_interval(self.event_date, delta_minus=10)
        
        scenes, ctx = ReMasFrame.search_scenes(
            self.event_geometry.buffer(buffer_size).envelope, 
            self.products[self.current_cat][self.current_prod], 
            start_date=start_date, 
            end_date=end_date
        )

        new_ctx = ctx.assign(resolution=res)

        self.current_scenes = scenes
        self.current_ctx = new_ctx

        return (scenes, new_ctx), (start_date, end_date)

    def create_stack(self):
        """
        Creates a stack of images from current Scene Collection
        """
        return self.current_scenes.stack(
            self.products[self.current_cat][self.current_prod]['bands'], 
            self.current_ctx
            )

    def sum_bands(self, idx_target_bands, update=True):
        """
        Sums given bands (as ndarray) and replaces them in the scene_stack.
        """
        # Retrieve bands
        to_replace_bands = self.current_stack[:, idx_target_bands, ...]
        
        # Update shape
        old_shape = list(to_replace_bands.shape)
        old_shape[1] = 1 # sum of bands equals to one
        new_shape = tuple(old_shape)

        # Sum and reshape bands
        summed_bands = np.sum(to_replace_bands, axis=1).reshape(new_shape)

        # Concatenate new summed band and delete old ones
        scene_stack = np.concatenate((self.current_stack, summed_bands), axis=1)
        new_scene_stack = np.delete(scene_stack, idx_target_bands, axis=1)

        if update:
            self.current_stack = new_scene_stack
        return new_scene_stack




