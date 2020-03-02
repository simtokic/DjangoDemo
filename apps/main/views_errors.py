from django.shortcuts import render_to_response


def handler404(exception, template_name="errors/404.html"):
    response = render_to_response("errors/404.html")
    response.status_code = 404
    return response


def handler500(exception, template_name="errors/500.html"):
    response = render_to_response("errors/500.html")
    response.status_code = 500
    return response
