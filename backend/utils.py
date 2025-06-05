def add_cors_headers(bp):
    @bp.after_request
    def after_request(response):
        header = response.headers
        header["Access-Control-Allow-Origin"] = "*"
        header["Access-Control-Allow-Headers"] = (
            "Origin, X-Requested-With, Content-Type, Accept"
        )
        return response

    return bp
