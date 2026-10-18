
import os

import cloudinary
from cloudinary import CloudinaryResource
from cloudinary_storage.storage import (
    MediaCloudinaryStorage as BaseMediaCloudinaryStorage,
)


class MediaCloudinaryStorage(BaseMediaCloudinaryStorage):
    """
    Cloudinary storage for product images.

    Existing images use their filename as the Public ID.
    Newly uploaded images are stored in the greatkart folder.
    """

    def _get_url(self, name):
        # Use the image filename without its extension.
        public_id = os.path.splitext(os.path.basename(name))[0]

        resource = CloudinaryResource(
            public_id,
            default_resource_type=self._get_resource_type(name),
        )
        return resource.url

    def _upload(self, name, content):
        # Keep the uploaded filename as the Cloudinary Public ID.
        filename = os.path.basename(name)
        public_id = os.path.splitext(filename)[0]

        response = cloudinary.uploader.upload(
            content,
            public_id=public_id,
            asset_folder="greatkart",
            resource_type=self._get_resource_type(name),
            overwrite=True,
            invalidate=True,
            tags=["greatkart"],
        )

        # Return the uploaded asset's Public ID and format.
        return f"{response['public_id']}.{response['format']}"
