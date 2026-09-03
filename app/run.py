import os

from factory import create_app

app = create_app()

if __name__ == "__main__":
    debug = app.config.get("DEBUG", False)
    # use_reloader=False: the Werkzeug reloader drops connections mid-request
    # (browsers show "refused to connect") and double-runs seed on boot.
    # DEBUG stays on so students still see verbose error pages (A02 lab).
    app.run(
        host="0.0.0.0",
        port=int(os.environ.get("PORT", "8080")),
        debug=debug,
        use_reloader=False,
    )
