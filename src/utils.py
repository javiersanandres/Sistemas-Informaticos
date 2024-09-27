import os


def build_absolute_path(relative_filepath: str) -> str:
    """
    Build and absolute path for a given filepath.
    """

    absolute_path = os.path.abspath(os.path.join(os.path.dirname(os.path.realpath(__file__)), os.pardir))
    filepath = os.path.join(absolute_path, relative_filepath)

    return filepath


def build_bad_request_response(reason: str = "") -> str:
    """
    Builds an HTML response for a bad request.
    """
    response_html = "<!doctype html>\n" \
                    "<html lang=en>\n" \
                    "<title>400 Bad Request</title>\n" \
                    "<h1>Bad Request</h1>\n" \
                    "<p>The browser (or proxy) sent a request that this server could not understand.</p>"

    if reason:
        response_html += f"\n<p>{reason}<\p>"

    return response_html


def build_not_found_response() -> str:
    """
    Builds an HTML response for not found error.
    """
    response_html = "<!DOCTYPE html>\n" \
                    "<html lang=\"en\">\n" \
                    "<head>\n" \
                    "    <meta charset=\"UTF-8\">\n" \
                    "    <meta name=\"viewport\" content=\"width=device-width, initial-scale=1.0\">\n" \
                    "    <title>404 Not Found</title>\n" \
                    "</head>\n" \
                    "<body>\n" \
                    "    <h1>404 Not Found</h1>\n" \
                    "    <p>The requested resource could not be found on this server.</p>\n" \
                    "</body>\n" \
                    "</html>\n"

    return response_html


def build_unauthorized_response() -> str:
    """
    Builds an HTML response for unathorised error.
    """
    response_html = "<!DOCTYPE html>\n" \
                    "<html lang=\"en\">\n" \
                    "<head>\n" \
                    "    <meta charset=\"UTF-8\">\n" \
                    "    <meta name=\"viewport\" content=\"width=device-width, initial-scale=1.0\">\n" \
                    "    <title>401 Unauthorized</title>\n" \
                    "</head>\n" \
                    "<body>\n" \
                    "    <h1>401 Unauthorized</h1>\n" \
                    "    <p> You are not authorized to access this page. </p>\n" \
                    "</body>\n" \
                    "</html>\n"

    return response_html
