import unittest
from agent.transport import BrowserBridgeServer

class TransportAddressTests(unittest.TestCase):
    def test_ephemeral_port_is_positive(self):
        bridge=BrowserBridgeServer(port=0)
        try:
            self.assertGreater(bridge.address[1],0)
        finally: bridge.close()

if __name__ == "__main__": unittest.main()
