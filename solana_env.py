import os
import requests
SOLANA_RPC_URL = os.environ.get("SOLANA_RPC_URL", "https://api.devnet.solana.com")

class SolanaClient:
    MASTER_POOL_ADDRESS = "SolMasterPoolHub1111111111111111111111111"
    def __init__(self,live=False):
        self._live = live

    def create_wallet(self):
        pass 

    def generate_project_reference(self,projectId):
        unique_ref = f"REF-PROJECT-{projectId}"
        return {
            "master_pool": self.MASTER_POOL_ADDRESS,
            "project_reference": unique_ref
        }

    def toal_balance(self):
        balance = 0.0
        try:
            payload = {
                "jsonrpc": "2.0",
                "id": 1,
                "method": "getBalance",
                "params": [self.MASTER_POOL_ADDRESS]
            }
            response = requests.post(SOLANA_RPC_URL, json=payload, headers={"Content-Type": "application/json"}, timeout=5)
            result_json = response.json()
            if result_json and "result" in result_json and "value" in result_json["result"]:
                balance = result_json["result"]["value"] / 1_000_000_000
        except Exception as e:
            pass

        return balance

