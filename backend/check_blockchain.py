import requests
import json

MODULE_ADDRESS = "0x66ef268bf620b86702dca9ac4b2fbc53ca5c8db7fc7dd7a6eef80e7549e35dfd"

print("=" * 60)
print("BLOCKCHAIN VERIFICATION TOOL")
print("=" * 60)

# Get input from user
tx_hash = input("\nEnter transaction hash (tx_hash): ").strip()
file_hash = input("Enter file hash (file_hash): ").strip()

print("\n" + "=" * 60)
print("CHECKING BLOCKCHAIN STORAGE")
print("=" * 60)

# 1. Check transaction
print("\n1. Verifying Transaction...")
tx_url = f"https://fullnode.testnet.aptoslabs.com/v1/transactions/by_hash/{tx_hash}"
response = requests.get(tx_url)

if response.status_code == 200:
    tx = response.json()
    print(f"   ✅ Transaction Found!")
    print(f"   Success: {tx.get('success')}")
    print(f"   VM Status: {tx.get('vm_status')}")
    print(f"   Gas Used: {tx.get('gas_used')}")
    print(f"   Timestamp: {tx.get('timestamp')}")
    
    if 'payload' in tx:
        payload = tx['payload']
        print(f"\n   Function Called: {payload.get('function')}")
        print(f"   Arguments Sent:")
        args = payload.get('arguments', [])
        if len(args) >= 4:
            print(f"      - file_hash: {args[0]}")
            print(f"      - file_name: {args[1]}")
            print(f"      - file_size: {args[2]} bytes")
            print(f"      - content_type: {args[3]}")
else:
    print(f"   ❌ Transaction not found! Status: {response.status_code}")
    exit(1)
    
print("\n" + "=" * 60)
print("VERIFICATION COMPLETE")
print("=" * 60)