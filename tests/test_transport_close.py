import unittest
from agent.transport import BrowserBridgeServer

class TransportCloseTests(unittest.TestCase):
    def test_close_without_start_is_safe(self):
        bridge=BrowserBridgeServer(port=0)
        bridge.close()

if __name__ == "__main__": unittest.main()
