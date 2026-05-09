from __future__ import annotations

import os
from wsgiref.simple_server import make_server

from ngo_portal.database import ensure_storage
from ngo_portal.web import app


def main() -> None:
    ensure_storage()
    port = int(os.environ.get("PORT", "8010"))
    with make_server("127.0.0.1", port, app) as server:
        print(f"NGO Donation Portal running at http://127.0.0.1:{port}")
        print("Demo accounts:")
        print("  Admin: admin@ngo.local / Admin@1234")
        print("  Donor: donor@ngo.local / Donor@1234")
        try:
            server.serve_forever()
        except KeyboardInterrupt:
            print("Shutting down.")


if __name__ == "__main__":
    main()

