from django import forms


class RichTextWidget(forms.Textarea):
    class Media:
        css = {"all": ("css/richtext.css",)}
        js = ("js/richtext.js",)

    def __init__(self, attrs=None):
        attrs = attrs or {}
        css_classes = [attrs.get("class", "").strip(), "richtext-source"]
        merged_attrs = dict(attrs)
        merged_attrs.update({
            "data-richtext": "true",
            "data-richtext-profile": attrs.get("data-richtext-profile", "full"),
            "rows": attrs.get("rows", 10),
            "class": " ".join(filter(None, css_classes)),
        })
        super().__init__(attrs=merged_attrs)
