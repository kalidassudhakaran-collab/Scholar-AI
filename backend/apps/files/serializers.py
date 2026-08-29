from rest_framework import serializers

from .models import UploadedFile


class UploadedFileSerializer(serializers.ModelSerializer):
    url = serializers.SerializerMethodField()

    class Meta:
        model = UploadedFile
        fields = (
            "id",
            "original_name",
            "stored_name",
            "url",
            "file_type",
            "mime_type",
            "size_bytes",
            "extracted_text",
            "created_at",
        )
        read_only_fields = fields

    def get_url(self, obj):
        if obj.file:
            request = self.context.get("request")
            if request:
                return request.build_absolute_uri(obj.file.url)
            return obj.file.url
        return obj.storage_url
