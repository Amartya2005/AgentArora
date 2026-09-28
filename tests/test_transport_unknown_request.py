import unittest
from agent.transport import BrowserBridgeServer

class TransportUnknownRequestTests(unittest.TestCase):
    def test_late_result_for_unknown_request_is_ignored(self):
        bridge=BrowserBridgeServer(port=0)
        try:
            bridge.complete("REQ_missing",[{"status":"SUCCESS"}])
            self.assertEqual(bridge._http.results,{})
        finally: bridge.close()

if __name__ == "__main__": unittest.main()
