import json
import threading
import unittest
from http.server import HTTPServer
from urllib.request import urlopen

from UI.server import RequestHandler


class TestMetaEndpointE2E(unittest.TestCase):
    def test_get_meta_endpoint(self):
        server = HTTPServer(("127.0.0.1", 0), RequestHandler)
        port = server.server_port
        thread = threading.Thread(target=server.serve_forever, daemon=True)
        thread.start()
        try:
            with urlopen(f"http://127.0.0.1:{port}/api/meta") as response:
                self.assertEqual(response.status, 200)
                body = json.loads(response.read().decode("utf-8"))
                self.assertIn("locations", body)
                self.assertIn("campaigns", body)
        finally:
            server.shutdown()
            server.server_close()
            thread.join(timeout=2)


if __name__ == "__main__":
    unittest.main()
