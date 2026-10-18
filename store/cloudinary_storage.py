
import os
import uuid

import cloudinary
from cloudinary import CloudinaryResource
from cloudinary_storage.storage import (
    MediaCloudinaryStorage as BaseMediaCloudinaryStorage,
)
from django.utils.text import slugify


class MediaCloudinaryStorage(BaseMediaCloudinaryStorage):
    def _get_url(self, name):
        # Existing images use their filename as the Cloudinary Public ID.
        public_id = os.path.splitext(os.path.basename(name))[0]

        resource = CloudinaryResource(
            public_id,
            default_resource_type=self._get_resource_type(public_id),
        )
        return resource.url

    def _upload(self, name, content):
        # Save newly uploaded product images in Cloudinary's greatkart folder.
        original_name = os.path.splitext(os.path.basename(name))[0]
        base_name = slugify(original_name) or "product"
        public_id = f"{base_name}-{uuid.uuid4().hex[:8]}"

        response = cloudinary.uploader.upload(
            content,
            public_id=public_id,
            asset_folder="greatkart",
            resource_type=self._get_resource_type(name),
            overwrite=False,
            invalidate=True,
            tags=["greatkart"],
        )

        # Store the actual Cloudinary Public ID in the database field.
        return f"{response['public_id']}.{response['format']}"
