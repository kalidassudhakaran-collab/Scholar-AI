from rest_framework import serializers

from .models import Feedback


class FeedbackSerializer(serializers.ModelSerializer):
    class Meta:
        model = Feedback
        fields = ("id", "feature", "likes", "drawbacks", "improvements", "created_at")
        read_only_fields = ("id", "created_at")

    def validate(self, attrs):
        likes = (attrs.get("likes") or "").strip()
        drawbacks = (attrs.get("drawbacks") or "").strip()
        improvements = (attrs.get("improvements") or "").strip()
        if not likes and not drawbacks and not improvements:
            raise serializers.ValidationError(
                "Share at least one of: what works, drawbacks, or improvements."
            )
        attrs["likes"] = likes
        attrs["drawbacks"] = drawbacks
        attrs["improvements"] = improvements
        return attrs
