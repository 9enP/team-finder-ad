from urllib.parse import urlencode


def pagination_query_prefix(request):
    params = request.GET.copy()
    params.pop("page", None)
    encoded = urlencode(params)
    return f"{encoded}&" if encoded else ""
