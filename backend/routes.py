# # from flask import Blueprint, request, jsonify, send_file
# # from aptos_sdk.account import Account
# # from aptos_sdk.async_client import RestClient
# # import asyncio

# # from aptos_sdk.transactions import (
# #     EntryFunction,
# #     TransactionArgument,
# #     TransactionPayload,
# # )
# # from aptos_sdk.bcs import Serializer
# # import hashlib
# # import os
# # from io import BytesIO

# # from encryption.encrypt import encrypt_file, decrypt_file

# # routes = Blueprint("routes", __name__)

# # # Aptos settings
# # NODE_URL = "https://fullnode.testnet.aptoslabs.com/v1"
# # MODULE_ADDRESS = "0x66ef268bf620b86702dca9ac4b2fbc53ca5c8db7fc7dd7a6eef80e7549e35dfd"

# # # Load Aptos account
# # private_key_hex = "506efb8cc8b48b412aaa19881851262d7e551965d14fa9fc11cb32f85184362a"
# # account = Account.load_key(private_key_hex)


# # async def submit_transaction_async(file_hash, filename, file_size, content_type):
# #     """Submit transaction to Aptos blockchain"""
# #     client = RestClient(NODE_URL)

# #     transaction_arguments = [
# #         TransactionArgument(str(file_hash), Serializer.str),
# #         TransactionArgument(str(filename), Serializer.str),
# #         TransactionArgument(int(file_size), Serializer.u64),
# #         TransactionArgument(str(content_type), Serializer.str),
# #     ]

# #     payload = EntryFunction.natural(
# #         f"{MODULE_ADDRESS}::file_storage",
# #         "upload_file",
# #         [],
# #         transaction_arguments,
# #     )

# #     signed_transaction = await client.create_bcs_signed_transaction(
# #         account, TransactionPayload(payload)
# #     )

# #     tx_hash = await client.submit_bcs_transaction(signed_transaction)

# #     # ✅ FIX: Properly handle transaction waiting
# #     try:
# #         tx = await client.wait_for_transaction(tx_hash)
# #         if tx is None:
# #             raise Exception(f"Transaction {tx_hash} returned None")  # ✅ Raise proper Exception
        
# #         if not tx.get("success", False):
# #             raise Exception(f"Transaction failed: {tx_hash}")  # ✅ Raise proper Exception
        
# #         return tx_hash
    
# #     except Exception as e:
# #         # If transaction fails, still return the hash so user can check manually
# #         print(f"Transaction warning: {e}")
# #         return tx_hash


# # @routes.route("/upload", methods=["POST"])
# # def upload_file():
# #     """Handle file upload, encryption, and blockchain storage"""
# #     try:
# #         # Validate file presence
# #         if "file" not in request.files:
# #             return jsonify({"error": "No file uploaded"}), 400

# #         file = request.files["file"]
# #         if file.filename == "":
# #             return jsonify({"error": "No file selected"}), 400

# #         # Read file data
# #         file_bytes = file.read()

# #         # 1. Encrypt file - returns encrypted data and decryption key
# #         encrypted_data, decryption_key = encrypt_file(file_bytes)

# #         # 2. Save encrypted file locally
# #         os.makedirs("storage", exist_ok=True)
# #         save_path = os.path.join("storage", file.filename + ".enc")
# #         with open(save_path, "wb") as f:
# #             f.write(encrypted_data)

# #         # 3. Compute hash of ORIGINAL file (not encrypted)
# #         file_hash = hashlib.sha256(file_bytes).hexdigest()

# #         # 4. Get file size
# #         file_size = int(len(file_bytes))

# #         # 5. Get content type
# #         raw_type = file.content_type or "application/octet-stream"
# #         content_type = raw_type.split(";")[0].strip()

# #         print(f"📤 Submitting to blockchain: {file.filename}")
# #         print(f"   Hash: {file_hash}")
# #         print(f"   Size: {file_size} bytes")
# #         print(f"   Type: {content_type}")

# #         # 6. Submit transaction to blockchain
# #         tx_hash = asyncio.run(
# #             submit_transaction_async(file_hash, file.filename, file_size, content_type)
# #         )

# #         print(f"✅ Transaction submitted: {tx_hash}")

# #         # 7. Return response with decryption key
# #         return jsonify({
# #             "message": "File uploaded successfully",
# #             "file_hash": file_hash,
# #             "file_name": file.filename,
# #             "file_size": file_size,
# #             "content_type": content_type,
# #             "saved_file": file.filename + ".enc",
# #             "tx_hash": tx_hash,
# #             "decryption_key": decryption_key,  # ⚠️ USER MUST SAVE THIS!
# #             "warning": "⚠️ SAVE YOUR DECRYPTION KEY! You cannot access this file without it."
# #         }), 200

# #     except Exception as e:
# #         print(f"❌ Upload error: {str(e)}")
# #         import traceback
# #         traceback.print_exc()
# #         return jsonify({"error": str(e)}), 500


# # @routes.route("/download/<file_hash>", methods=["POST"])
# # def download_file(file_hash):
# #     """Download and decrypt file"""
# #     try:
# #         data = request.get_json()
# #         decryption_key = data.get("decryption_key")
# #         filename = data.get("filename")
        
# #         if not decryption_key or not filename:
# #             return jsonify({"error": "decryption_key and filename required"}), 400

# #         # Find encrypted file
# #         encrypted_file_path = os.path.join("storage", filename + ".enc")
        
# #         if not os.path.exists(encrypted_file_path):
# #             return jsonify({"error": "File not found"}), 404

# #         print(f"📥 Downloading: {filename}")

# #         # Read encrypted file
# #         with open(encrypted_file_path, "rb") as f:
# #             encrypted_data = f.read()

# #         # Decrypt file
# #         try:
# #             decrypted_data = decrypt_file(encrypted_data, decryption_key)
# #         except Exception as e:
# #             print(f"❌ Decryption failed: {e}")
# #             return jsonify({"error": "Invalid decryption key"}), 401

# #         # Verify integrity
# #         computed_hash = hashlib.sha256(decrypted_data).hexdigest()
# #         if computed_hash != file_hash:
# #             print(f"❌ Hash mismatch! Expected: {file_hash}, Got: {computed_hash}")
# #             return jsonify({"error": "File integrity check failed!"}), 500

# #         print(f"✅ File decrypted and verified: {filename}")

# #         # Return decrypted file
# #         return send_file(
# #             BytesIO(decrypted_data),
# #             download_name=filename,
# #             as_attachment=True
# #         )

# #     except Exception as e:
# #         print(f"❌ Download error: {str(e)}")
# #         import traceback
# #         traceback.print_exc()
# #         return jsonify({"error": str(e)}), 500

# from flask import Blueprint, request, jsonify, send_file
# from aptos_sdk.account import Account
# from aptos_sdk.async_client import RestClient
# import asyncio

# from aptos_sdk.transactions import (
#     EntryFunction,
#     TransactionArgument,
#     TransactionPayload,
# )
# from aptos_sdk.bcs import Serializer
# import hashlib
# import os
# from io import BytesIO

# from encryption.encrypt import encrypt_file, decrypt_file

# routes = Blueprint("routes", __name__)

# # Aptos settings
# NODE_URL = "https://fullnode.testnet.aptoslabs.com/v1"
# MODULE_ADDRESS = "0x66ef268bf620b86702dca9ac4b2fbc53ca5c8db7fc7dd7a6eef80e7549e35dfd"

# # Load Aptos account
# private_key_hex = "506efb8cc8b48b412aaa19881851262d7e551965d14fa9fc11cb32f85184362a"
# account = Account.load_key(private_key_hex)


# async def submit_transaction_async(file_hash, filename, file_size, content_type):
#     """Submit transaction to Aptos blockchain"""
#     client = RestClient(NODE_URL)

#     transaction_arguments = [
#         TransactionArgument(str(file_hash), Serializer.str),
#         TransactionArgument(str(filename), Serializer.str),
#         TransactionArgument(int(file_size), Serializer.u64),
#         TransactionArgument(str(content_type), Serializer.str),
#     ]

#     payload = EntryFunction.natural(
#         f"{MODULE_ADDRESS}::file_storage",
#         "upload_file",
#         [],
#         transaction_arguments,
#     )

#     signed_transaction = await client.create_bcs_signed_transaction(
#         account, TransactionPayload(payload)
#     )

#     tx_hash = await client.submit_bcs_transaction(signed_transaction)

#     try:
#         tx = await client.wait_for_transaction(tx_hash)
#         if tx is None:
#             raise Exception(f"Transaction {tx_hash} returned None")
        
#         if not tx.get("success", False):
#             raise Exception(f"Transaction failed: {tx_hash}")
        
#         return tx_hash
    
#     except Exception as e:
#         print(f"Transaction warning: {e}")
#         return tx_hash


# @routes.route("/upload", methods=["POST"])
# def upload_file():
#     """Handle file upload, encryption, and blockchain storage"""
#     try:
#         if "file" not in request.files:
#             return jsonify({"error": "No file uploaded"}), 400

#         file = request.files["file"]
#         if file.filename == "":
#             return jsonify({"error": "No file selected"}), 400

#         print("\n" + "="*60)
#         print("📤 UPLOAD STARTING")
#         print("="*60)

#         # Read file data
#         file_bytes = file.read()
#         print(f"✅ File read: {file.filename}")
#         print(f"   Original size: {len(file_bytes)} bytes")

#         # IMPORTANT: Compute hash BEFORE encryption
#         file_hash = hashlib.sha256(file_bytes).hexdigest()
#         print(f"   Original file hash: {file_hash}")

#         # Encrypt file
#         encrypted_data, decryption_key = encrypt_file(file_bytes)
#         print(f"✅ File encrypted")
#         print(f"   Encrypted size: {len(encrypted_data)} bytes")
#         print(f"   Decryption key: {decryption_key}")

#         # Save encrypted file locally
#         os.makedirs("storage", exist_ok=True)
#         save_path = os.path.join("storage", file.filename + ".enc")
#         with open(save_path, "wb") as f:
#             f.write(encrypted_data)
#         print(f"✅ Encrypted file saved: {save_path}")

#         # Get file size and content type
#         file_size = int(len(file_bytes))
#         raw_type = file.content_type or "application/octet-stream"
#         content_type = raw_type.split(";")[0].strip()

#         # Submit to blockchain
#         print(f"📤 Submitting to blockchain...")
#         tx_hash = asyncio.run(
#             submit_transaction_async(file_hash, file.filename, file_size, content_type)
#         )
#         print(f"✅ Transaction: {tx_hash}")
#         print("="*60 + "\n")

#         return jsonify({
#             "message": "File uploaded successfully",
#             "file_hash": file_hash,
#             "file_name": file.filename,
#             "file_size": file_size,
#             "content_type": content_type,
#             "saved_file": file.filename + ".enc",
#             "tx_hash": tx_hash,
#             "decryption_key": decryption_key,
#             "warning": "⚠️ SAVE YOUR DECRYPTION KEY! You cannot access this file without it."
#         }), 200

#     except Exception as e:
#         print(f"❌ Upload error: {str(e)}")
#         import traceback
#         traceback.print_exc()
#         return jsonify({"error": str(e)}), 500


# @routes.route("/download/<file_hash>", methods=["POST"])
# def download_file(file_hash):
#     """Download and decrypt file with proper error handling"""
#     try:
#         data = request.get_json()
#         decryption_key = data.get("decryption_key")
#         filename = data.get("filename")
        
#         if not decryption_key or not filename:
#             return jsonify({"error": "decryption_key and filename required"}), 400

#         print("\n" + "="*60)
#         print("📥 DOWNLOAD STARTING")
#         print("="*60)
#         print(f"   Filename: {filename}")
#         print(f"   Expected hash: {file_hash}")
#         print(f"   Decryption key: {decryption_key[:16]}...{decryption_key[-16:]}")

#         # Find encrypted file
#         encrypted_file_path = os.path.join("storage", filename + ".enc")
        
#         if not os.path.exists(encrypted_file_path):
#             print(f"❌ File not found: {encrypted_file_path}")
#             return jsonify({"error": f"File not found: {filename}.enc"}), 404

#         print(f"✅ Found encrypted file: {encrypted_file_path}")

#         # Read encrypted file
#         with open(encrypted_file_path, "rb") as f:
#             encrypted_data = f.read()
#         print(f"✅ Read encrypted data: {len(encrypted_data)} bytes")

#         # Decrypt file
#         print(f"🔓 Attempting decryption...")
#         try:
#             decrypted_data = decrypt_file(encrypted_data, decryption_key)
#             print(f"✅ Decryption successful!")
#             print(f"   Decrypted size: {len(decrypted_data)} bytes")
#         except ValueError as e:
#             print(f"❌ Decryption failed: {e}")
#             return jsonify({"error": "Invalid decryption key"}), 401
#         except Exception as e:
#             print(f"❌ Decryption error: {e}")
#             return jsonify({"error": "Decryption failed. Invalid key or corrupted file."}), 401

#         # Verify integrity
#         computed_hash = hashlib.sha256(decrypted_data).hexdigest()
#         print(f"🔍 Hash verification:")
#         print(f"   Expected:  {file_hash}")
#         print(f"   Computed:  {computed_hash}")
#         print(f"   Match: {file_hash == computed_hash}")
        
#         if computed_hash != file_hash:
#             print(f"❌ HASH MISMATCH!")
#             print(f"   This means either:")
#             print(f"   1. Wrong file was uploaded with this hash")
#             print(f"   2. File was corrupted during storage")
#             print(f"   3. Frontend is passing wrong hash")
#             return jsonify({
#                 "error": f"File integrity check failed! Expected hash {file_hash[:16]}... but got {computed_hash[:16]}..."
#             }), 500

#         print(f"✅ Hash verified! File integrity confirmed!")
#         print("="*60 + "\n")

#         # Return decrypted file
#         return send_file(
#             BytesIO(decrypted_data),
#             download_name=filename,
#             as_attachment=True
#         )

#     except Exception as e:
#         print(f"❌ Download error: {str(e)}")
#         import traceback
#         traceback.print_exc()
#         return jsonify({"error": str(e)}), 500


from flask import Blueprint, request, jsonify, send_file
from aptos_sdk.account import Account
from aptos_sdk.async_client import RestClient
import asyncio
from aptos_sdk.transactions import (
    EntryFunction,
    TransactionArgument,
    TransactionPayload,
)
from aptos_sdk.bcs import Serializer
import hashlib
import os
from io import BytesIO
from cryptography.fernet import Fernet
import base64

from encryption.encrypt import encrypt_file, decrypt_file
from models import db, FileMetadata

routes = Blueprint("routes", __name__)

# Aptos settings
NODE_URL = "https://fullnode.testnet.aptoslabs.com/v1"
MODULE_ADDRESS = "0x66ef268bf620b86702dca9ac4b2fbc53ca5c8db7fc7dd7a6eef80e7549e35dfd"

# Load Aptos account
private_key_hex = "506efb8cc8b48b412aaa19881851262d7e551965d14fa9fc11cb32f85184362a"
account = Account.load_key(private_key_hex)

# Master key for encrypting decryption keys (store this securely in production!)
MASTER_KEY = Fernet.generate_key()
cipher_suite = Fernet(MASTER_KEY)


def encrypt_decryption_key(key: str) -> str:
    """Encrypt the file's decryption key before storing in DB"""
    return cipher_suite.encrypt(key.encode()).decode()


def decrypt_decryption_key(encrypted_key: str) -> str:
    """Decrypt the file's decryption key from DB"""
    return cipher_suite.decrypt(encrypted_key.encode()).decode()


async def submit_transaction_async(file_hash, filename, file_size, content_type):
    """Submit transaction to Aptos blockchain"""
    client = RestClient(NODE_URL)

    transaction_arguments = [
        TransactionArgument(str(file_hash), Serializer.str),
        TransactionArgument(str(filename), Serializer.str),
        TransactionArgument(int(file_size), Serializer.u64),
        TransactionArgument(str(content_type), Serializer.str),
    ]

    payload = EntryFunction.natural(
        f"{MODULE_ADDRESS}::file_storage",
        "upload_file",
        [],
        transaction_arguments,
    )

    signed_transaction = await client.create_bcs_signed_transaction(
        account, TransactionPayload(payload)
    )

    tx_hash = await client.submit_bcs_transaction(signed_transaction)

    try:
        tx = await client.wait_for_transaction(tx_hash)
        if tx is None:
            raise Exception(f"Transaction {tx_hash} returned None")
        
        if not tx.get("success", False):
            raise Exception(f"Transaction failed: {tx_hash}")
        
        return tx_hash
    
    except Exception as e:
        print(f"Transaction warning: {e}")
        return tx_hash


@routes.route("/upload", methods=["POST"])
def upload_file():
    """Handle file upload with database storage"""
    try:
        if "file" not in request.files:
            return jsonify({"error": "No file uploaded"}), 400

        file = request.files["file"]
        if file.filename == "":
            return jsonify({"error": "No file selected"}), 400

        # TODO: Get user_id from authentication (for now, use demo user)
        user_id = 1  # Replace with actual authenticated user ID

        print("\n" + "="*60)
        print("📤 UPLOAD WITH DATABASE")
        print("="*60)

        # Read file data
        file_bytes = file.read()
        print(f"✅ File read: {file.filename}")
        print(f"   Original size: {len(file_bytes)} bytes")

        # Compute hash of original file
        file_hash = hashlib.sha256(file_bytes).hexdigest()
        print(f"   Original file hash: {file_hash}")

        # Check if file already exists
        existing_file = FileMetadata.query.filter_by(file_hash=file_hash).first()
        if existing_file:
            print(f"⚠️  File already exists in database")
            return jsonify({"error": "File already exists"}), 409

        # Encrypt file
        encrypted_data, decryption_key = encrypt_file(file_bytes)
        print(f"✅ File encrypted")
        print(f"   Decryption key: {decryption_key[:16]}...{decryption_key[-16:]}")

        # Save encrypted file
        os.makedirs("storage", exist_ok=True)
        encrypted_filename = f"{file_hash}.enc"  # Use hash as filename for uniqueness
        save_path = os.path.join("storage", encrypted_filename)
        with open(save_path, "wb") as f:
            f.write(encrypted_data)
        print(f"✅ Encrypted file saved: {save_path}")

        # Get file info
        file_size = int(len(file_bytes))
        raw_type = file.content_type or "application/octet-stream"
        content_type = raw_type.split(";")[0].strip()

        # Submit to blockchain
        print(f"📤 Submitting to blockchain...")
        tx_hash = asyncio.run(
            submit_transaction_async(file_hash, file.filename, file_size, content_type)
        )
        print(f"✅ Transaction: {tx_hash}")

        # Encrypt the decryption key before storing
        encrypted_decryption_key = encrypt_decryption_key(decryption_key)

        # Save metadata to database
        file_metadata = FileMetadata(
            file_hash=file_hash,
            file_name=file.filename,
            file_size=file_size,
            content_type=content_type,
            encrypted_filename=encrypted_filename,
            decryption_key_encrypted=encrypted_decryption_key,
            tx_hash=tx_hash,
            user_id=user_id
        )
        
        db.session.add(file_metadata)
        db.session.commit()
        print(f"✅ Metadata saved to database (ID: {file_metadata.id})")
        print("="*60 + "\n")

        return jsonify({
            "message": "File uploaded successfully",
            "file_hash": file_hash,
            "file_name": file.filename,
            "file_size": file_size,
            "content_type": content_type,
            "saved_file": encrypted_filename,
            "tx_hash": tx_hash,
            "decryption_key": decryption_key,  # Return to user (they must save it!)
            "warning": "⚠️ SAVE YOUR DECRYPTION KEY! You cannot access this file without it."
        }), 200

    except Exception as e:
        db.session.rollback()
        print(f"❌ Upload error: {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({"error": str(e)}), 500


@routes.route("/files", methods=["GET"])
def list_files():
    """List all files for authenticated user"""
    try:
        # TODO: Get user_id from authentication
        user_id = 1  # Replace with actual authenticated user ID

        files = FileMetadata.query.filter_by(user_id=user_id).order_by(
            FileMetadata.upload_date.desc()
        ).all()

        return jsonify({
            "files": [{
                "id": f.id,
                "file_hash": f.file_hash,
                "file_name": f.file_name,
                "file_size": f.file_size,
                "content_type": f.content_type,
                "tx_hash": f.tx_hash,
                "upload_date": f.upload_date.isoformat(),
            } for f in files]
        }), 200

    except Exception as e:
        print(f"❌ Error listing files: {e}")
        return jsonify({"error": str(e)}), 500


@routes.route("/download/<file_hash>", methods=["POST"])
def download_file(file_hash):
    """Download and decrypt file using database lookup"""
    try:
        data = request.get_json()
        decryption_key = data.get("decryption_key")
        
        if not decryption_key:
            return jsonify({"error": "decryption_key required"}), 400

        print("\n" + "="*60)
        print("📥 DOWNLOAD WITH DATABASE")
        print("="*60)

        # Get file metadata from database
        file_metadata = FileMetadata.query.filter_by(file_hash=file_hash).first()
        
        if not file_metadata:
            print(f"❌ File not found in database: {file_hash}")
            return jsonify({"error": "File not found"}), 404

        print(f"✅ Found file in database:")
        print(f"   Name: {file_metadata.file_name}")
        print(f"   Hash: {file_hash}")

        # Find encrypted file
        encrypted_file_path = os.path.join("storage", file_metadata.encrypted_filename)
        
        if not os.path.exists(encrypted_file_path):
            print(f"❌ Encrypted file not found on disk: {encrypted_file_path}")
            return jsonify({"error": "Encrypted file not found"}), 404

        print(f"✅ Found encrypted file: {encrypted_file_path}")

        # Read encrypted file
        with open(encrypted_file_path, "rb") as f:
            encrypted_data = f.read()
        print(f"✅ Read encrypted data: {len(encrypted_data)} bytes")

        # Decrypt file
        print(f"🔓 Attempting decryption...")
        try:
            decrypted_data = decrypt_file(encrypted_data, decryption_key)
            print(f"✅ Decryption successful: {len(decrypted_data)} bytes")
        except ValueError as e:
            print(f"❌ Decryption failed: {e}")
            return jsonify({"error": "Invalid decryption key"}), 401
        except Exception as e:
            print(f"❌ Decryption error: {e}")
            return jsonify({"error": "Decryption failed"}), 401

        # Verify integrity
        computed_hash = hashlib.sha256(decrypted_data).hexdigest()
        print(f"🔍 Hash verification:")
        print(f"   Expected:  {file_hash}")
        print(f"   Computed:  {computed_hash}")
        
        if computed_hash != file_hash:
            print(f"❌ HASH MISMATCH!")
            return jsonify({"error": "File integrity check failed!"}), 500

        print(f"✅ Hash verified!")
        print("="*60 + "\n")

        # Return decrypted file
        return send_file(
            BytesIO(decrypted_data),
            download_name=file_metadata.file_name,
            as_attachment=True
        )

    except Exception as e:
        print(f"❌ Download error: {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({"error": str(e)}), 500

# ***
@routes.route("/debug/files", methods=["GET"])
def debug_all_files():
    """Debug endpoint to view all files in database"""
    try:
        files = FileMetadata.query.all()
        
        return jsonify({
            "total_files": len(files),
            "files": [{
                "id": f.id,
                "file_name": f.file_name,
                "file_hash": f.file_hash,
                "file_size": f.file_size,
                "content_type": f.content_type,
                "tx_hash": f.tx_hash,
                "upload_date": f.upload_date.isoformat(),
                "encrypted_filename": f.encrypted_filename,
                "user_id": f.user_id
            } for f in files]
        }), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@routes.route("/files/<int:file_id>", methods=["DELETE"])
def delete_file(file_id):
    """Delete a file"""
    try:
        # TODO: Get user_id from authentication
        user_id = 1

        file_metadata = FileMetadata.query.filter_by(
            id=file_id, 
            user_id=user_id
        ).first()
        
        if not file_metadata:
            return jsonify({"error": "File not found"}), 404

        # Delete encrypted file from disk
        encrypted_file_path = os.path.join("storage", file_metadata.encrypted_filename)
        if os.path.exists(encrypted_file_path):
            os.remove(encrypted_file_path)
            print(f"✅ Deleted file from disk: {encrypted_file_path}")

        # Delete from database
        db.session.delete(file_metadata)
        db.session.commit()
        print(f"✅ Deleted from database: {file_metadata.file_name}")

        return jsonify({"message": "File deleted successfully"}), 200

    except Exception as e:
        db.session.rollback()
        print(f"❌ Delete error: {e}")
        return jsonify({"error": str(e)}), 500

# visit http://localhost:5000/api/debug/files for seeing files stored in the database.

