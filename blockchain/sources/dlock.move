module 0x66ef268bf620b86702dca9ac4b2fbc53ca5c8db7fc7dd7a6eef80e7549e35dfd::file_storage {
    use std::signer;
    use std::string::{Self, String};
    use aptos_framework::timestamp;
    use aptos_framework::event;
    use aptos_std::table::{Self, Table};
    use aptos_framework::account;

    // Error codes
    const E_NOT_INITIALIZED: u64 = 1;
    const E_ALREADY_INITIALIZED: u64 = 2;
    const E_NOT_OWNER: u64 = 3;
    const E_FILE_NOT_FOUND: u64 = 4;

    // File metadata structure
    struct FileMetadata has store, drop, copy {
        file_hash: String,
        file_name: String,
        file_size: u64,
        content_type: String,
        timestamp: u64,
        owner: address,
    }

    // Storage for user's files
    struct FileStorage has key {
        files: Table<String, FileMetadata>,
        file_count: u64,
    }

    // Events
    #[event]
    struct FileUploadedEvent has drop, store {
        file_hash: String,
        file_name: String,
        file_size: u64,
        content_type: String,
        timestamp: u64,
        owner: address,
    }

    #[event]
    struct FileVerifiedEvent has drop, store {
        file_hash: String,
        owner: address,
        timestamp: u64,
    }

    // Initialize storage
    public entry fun initialize(account: &signer) {
        let addr = signer::address_of(account);
        assert!(!exists<FileStorage>(addr), E_ALREADY_INITIALIZED);

        move_to(account, FileStorage {
            files: table::new(),
            file_count: 0,
        });
    }

    // Upload file
    public entry fun upload_file(
        account: &signer,
        file_hash: String,
        file_name: String,
        file_size: u64,
        content_type: String
    ) acquires FileStorage {
        let addr = signer::address_of(account);

        if (!exists<FileStorage>(addr)) {
            initialize(account);
        };

        let storage = borrow_global_mut<FileStorage>(addr);
        let now = timestamp::now_seconds();

        let metadata = FileMetadata {
            file_hash,
            file_name,
            file_size,
            content_type,
            timestamp: now,
            owner: addr,
        };

        table::add(&mut storage.files, file_hash, metadata);
        storage.file_count = storage.file_count + 1;

        event::emit(FileUploadedEvent {
            file_hash,
            file_name,
            file_size,
            content_type,
            timestamp: now,
            owner: addr,
        });
    }

    // Verify file
    #[view]
    public fun verify_file(owner: address, file_hash: String): bool acquires FileStorage {
        if (!exists<FileStorage>(owner)) return false;

        let storage = borrow_global<FileStorage>(owner);

        if (!table::contains(&storage.files, file_hash)) return false;

        event::emit(FileVerifiedEvent {
            file_hash,
            owner,
            timestamp: timestamp::now_seconds(),
        });

        true
    }

    // Get file metadata - returns 6 values
    #[view]
    public fun get_file_metadata(owner: address, file_hash: String): (String, String, u64, String, u64, address) acquires FileStorage {
        assert!(exists<FileStorage>(owner), E_NOT_INITIALIZED);
        let storage = borrow_global<FileStorage>(owner);
        assert!(table::contains(&storage.files, file_hash), E_FILE_NOT_FOUND);

        let metadata = table::borrow(&storage.files, file_hash);
        (
            metadata.file_hash,
            metadata.file_name,
            metadata.file_size,
            metadata.content_type,
            metadata.timestamp,
            metadata.owner
        )
    }

    #[view]
    public fun get_file_count(owner: address): u64 acquires FileStorage {
        if (!exists<FileStorage>(owner)) return 0;

        let storage = borrow_global<FileStorage>(owner);
        storage.file_count
    }

    // Update file metadata
    public entry fun update_file_metadata(
        account: &signer,
        file_hash: String,
        new_file_name: String,
        new_content_type: String
    ) acquires FileStorage {
        let addr = signer::address_of(account);

        assert!(exists<FileStorage>(addr), E_NOT_INITIALIZED);
        let storage = borrow_global_mut<FileStorage>(addr);

        assert!(table::contains(&storage.files, file_hash), E_FILE_NOT_FOUND);

        let metadata = table::borrow_mut(&mut storage.files, file_hash);
        assert!(metadata.owner == addr, E_NOT_OWNER);

        metadata.file_name = new_file_name;
        metadata.content_type = new_content_type;
    }

    #[view]
    public fun file_exists(owner: address, file_hash: String): bool acquires FileStorage {
        if (!exists<FileStorage>(owner)) return false;

        let storage = borrow_global<FileStorage>(owner);
        table::contains(&storage.files, file_hash)
    }
}