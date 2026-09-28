import unittest
from agent.transport import BrowserBridgeServer

class TransportTimeoutTests(unittest.TestCase):
    def test_submit_times_out_and_cleans_pending_request(self):
        bridge=BrowserBridgeServer(port=0)
        try:
            with self.assertRaises(TimeoutError): bridge.submit({"actions":[]},timeout=0.01)
            self.assertEqual(bridge._http.results,{})
        finally: bridge.close()

if __name__ == "__main__": unittest.main()
