import unittest
from agent.transport import BrowserBridgeServer

class TransportUnknownResultTests(unittest.TestCase):
    def test_unknown_request_does_not_create_state(self):
        bridge=BrowserBridgeServer(port=0)
        try:
            bridge.complete("REQ_unknown",[])
            self.assertEqual(len(bridge._http.results),0)
        finally: bridge.close()

if __name__ == "__main__": unittest.main()
