from django.contrib.admin.forms import AdminAuthenticationForm


class ScholarAdminAuthenticationForm(AdminAuthenticationForm):
    """Admin login: accept email or username in the username field."""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["username"].label = "Email or username"
