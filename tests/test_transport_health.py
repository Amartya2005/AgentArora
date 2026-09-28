import unittest
from agent.transport import BrowserBridgeServer

class TransportHealthTests(unittest.TestCase):
    def test_address_is_exposed_after_ephemeral_bind(self):
        bridge=BrowserBridgeServer(port=0)
        try:
            host,port=bridge.address
            self.assertEqual(host,"127.0.0.1"); self.assertGreater(port,0)
        finally: bridge.close()
    def test_start_is_idempotent(self):
        bridge=BrowserBridgeServer(port=0)
        try:
            bridge.start(); bridge.start()
        finally: bridge.close()

if __name__ == "__main__": unittest.main()
