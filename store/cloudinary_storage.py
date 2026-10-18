
import os

from cloudinary_storage.storage import MediaCloudinaryStorage as BaseMediaCloudinaryStorage
from cloudinary import CloudinaryResource


class MediaCloudinaryStorage(BaseMediaCloudinaryStorage):
    def _get_url(self, name):
        # Existing Cloudinary images use their filename as the Public ID.
        public_id = os.path.splitext(os.path.basename(name))[0]

        resource = CloudinaryResource(
            public_id,
            default_resource_type=self._get_resource_type(public_id),
        )
        return resource.url
