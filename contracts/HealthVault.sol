// SPDX-License-Identifier: MIT
pragma solidity ^0.8.19;

/**
 * @title HealthVault
 * @dev Smart contract for managing encrypted health records with zero-knowledge proofs
 * @author MediLedger Nexus Team
 */
contract HealthVault {
    
    // Events
    event VaultCreated(address indexed owner, string vaultName, uint256 timestamp);
    event RecordCreated(bytes32 indexed recordId, string recordType, uint256 timestamp);
    event AccessGranted(bytes32 indexed recordId, address indexed grantee, uint256 expiresAt);
    event AccessRevoked(bytes32 indexed recordId, address indexed grantee);
    event EmergencyAccessGranted(bytes32 indexed recordId, address indexed requester, string emergencyType);
    
    // Structs
    struct HealthRecord {
        bytes32 recordId;
        string recordType;
        string encryptedDataHash; // IPFS hash of encrypted data
        string dataIntegrityHash; // Hash for data integrity verification
        address owner;
        uint256 createdAt;
        bool isActive;
        mapping(address => AccessPermission) accessPermissions;
    }
    
    struct AccessPermission {
        bool hasAccess;
        uint256 grantedAt;
        uint256 expiresAt;
        string accessLevel; // "read", "write", "admin"
        bool isEmergency;
    }
    
    struct EmergencyProfile {
        string bloodType;
        string[] allergies;
        string[] currentMedications;
        string[] medicalConditions;
        string emergencyContact;
        bool isActive;
    }
    
    // State variables
    address public owner;
    string public vaultName;
    bool public encryptionEnabled;
    bool public zkProofsEnabled;
    string public privacyLevel;
    uint256 public recordCount;
    
    // Mappings
    mapping(bytes32 => HealthRecord) public healthRecords;
    mapping(address => bool) public authorizedProviders;
    mapping(address => EmergencyProfile) public emergencyProfiles;
    mapping(string => bool) public supportedRecordTypes;
    
    // Modifiers
    modifier onlyOwner() {
        require(msg.sender == owner, "Only vault owner can perform this action");
        _;
    }
    
    modifier onlyAuthorizedProvider() {
        require(authorizedProviders[msg.sender] || msg.sender == owner, "Not an authorized provider");
        _;
    }
    
    modifier recordExists(bytes32 recordId) {
        require(healthRecords[recordId].isActive, "Record does not exist or is inactive");
        _;
    }
    
    modifier hasAccess(bytes32 recordId, string memory requiredLevel) {
        require(
            healthRecords[recordId].accessPermissions[msg.sender].hasAccess &&
            healthRecords[recordId].accessPermissions[msg.sender].expiresAt > block.timestamp,
            "Access denied or expired"
        );
        _;
    }
    
    // Constructor
    constructor(
        string memory _vaultName,
        bool _encryptionEnabled,
        bool _zkProofsEnabled,
        string memory _privacyLevel
    ) {
        owner = msg.sender;
        vaultName = _vaultName;
        encryptionEnabled = _encryptionEnabled;
        zkProofsEnabled = _zkProofsEnabled;
        privacyLevel = _privacyLevel;
        
        // Initialize supported record types
        supportedRecordTypes["lab_results"] = true;
        supportedRecordTypes["imaging"] = true;
        supportedRecordTypes["prescriptions"] = true;
        supportedRecordTypes["genomics"] = true;
        supportedRecordTypes["vital_signs"] = true;
        supportedRecordTypes["allergies"] = true;
        supportedRecordTypes["immunizations"] = true;
        
        emit VaultCreated(owner, _vaultName, block.timestamp);
    }
    
    /**
     * @dev Create a new health record
     * @param recordType Type of health record
     * @param encryptedDataHash IPFS hash of encrypted data
     * @param dataIntegrityHash Hash for data integrity verification
     */
    function createRecord(
        string memory recordType,
        string memory encryptedDataHash,
        string memory dataIntegrityHash
    ) external onlyOwner returns (bytes32) {
        require(supportedRecordTypes[recordType], "Unsupported record type");
        require(bytes(encryptedDataHash).length > 0, "Encrypted data hash cannot be empty");
        require(bytes(dataIntegrityHash).length > 0, "Data integrity hash cannot be empty");
        
        bytes32 recordId = keccak256(abi.encodePacked(
            msg.sender,
            recordType,
            encryptedDataHash,
            block.timestamp,
            recordCount
        ));
        
        HealthRecord storage newRecord = healthRecords[recordId];
        newRecord.recordId = recordId;
        newRecord.recordType = recordType;
        newRecord.encryptedDataHash = encryptedDataHash;
        newRecord.dataIntegrityHash = dataIntegrityHash;
        newRecord.owner = msg.sender;
        newRecord.createdAt = block.timestamp;
        newRecord.isActive = true;
        
        // Owner gets admin access by default
        newRecord.accessPermissions[msg.sender] = AccessPermission({
            hasAccess: true,
            grantedAt: block.timestamp,
            expiresAt: type(uint256).max, // Never expires for owner
            accessLevel: "admin",
            isEmergency: false
        });
        
        recordCount++;
        
        emit RecordCreated(recordId, recordType, block.timestamp);
        return recordId;
    }
    
    /**
     * @dev Grant access to a health record
     * @param recordId ID of the record
     * @param grantee Address to grant access to
     * @param accessLevel Level of access ("read", "write", "admin")
     * @param durationHours Duration of access in hours
     */
    function grantAccess(
        bytes32 recordId,
        address grantee,
        string memory accessLevel,
        uint256 durationHours
    ) external onlyOwner recordExists(recordId) {
        require(grantee != address(0), "Invalid grantee address");
        require(
            keccak256(bytes(accessLevel)) == keccak256(bytes("read")) ||
            keccak256(bytes(accessLevel)) == keccak256(bytes("write")) ||
            keccak256(bytes(accessLevel)) == keccak256(bytes("admin")),
            "Invalid access level"
        );
        
        uint256 expiresAt = block.timestamp + (durationHours * 1 hours);
        
        healthRecords[recordId].accessPermissions[grantee] = AccessPermission({
            hasAccess: true,
            grantedAt: block.timestamp,
            expiresAt: expiresAt,
            accessLevel: accessLevel,
            isEmergency: false
        });
        
        emit AccessGranted(recordId, grantee, expiresAt);
    }
    
    /**
     * @dev Revoke access to a health record
     * @param recordId ID of the record
     * @param grantee Address to revoke access from
     */
    function revokeAccess(
        bytes32 recordId,
        address grantee
    ) external onlyOwner recordExists(recordId) {
        require(grantee != address(0), "Invalid grantee address");
        require(grantee != owner, "Cannot revoke owner access");
        
        delete healthRecords[recordId].accessPermissions[grantee];
        
        emit AccessRevoked(recordId, grantee);
    }
    
    /**
     * @dev Grant emergency access to a health record
     * @param recordId ID of the record
     * @param requester Address requesting emergency access
     * @param emergencyType Type of emergency
     */
    function grantEmergencyAccess(
        bytes32 recordId,
        address requester,
        string memory emergencyType
    ) external onlyAuthorizedProvider recordExists(recordId) {
        require(bytes(emergencyType).length > 0, "Emergency type cannot be empty");
        
        // Emergency access is temporary (24 hours)
        uint256 expiresAt = block.timestamp + 24 hours;
        
        healthRecords[recordId].accessPermissions[requester] = AccessPermission({
            hasAccess: true,
            grantedAt: block.timestamp,
            expiresAt: expiresAt,
            accessLevel: "read",
            isEmergency: true
        });
        
        emit EmergencyAccessGranted(recordId, requester, emergencyType);
    }
    
    /**
     * @dev Set emergency profile for the vault owner
     * @param bloodType Patient's blood type
     * @param allergies Array of allergies
     * @param currentMedications Array of current medications
     * @param medicalConditions Array of medical conditions
     * @param emergencyContact Emergency contact information
     */
    function setEmergencyProfile(
        string memory bloodType,
        string[] memory allergies,
        string[] memory currentMedications,
        string[] memory medicalConditions,
        string memory emergencyContact
    ) external onlyOwner {
        emergencyProfiles[owner] = EmergencyProfile({
            bloodType: bloodType,
            allergies: allergies,
            currentMedications: currentMedications,
            medicalConditions: medicalConditions,
            emergencyContact: emergencyContact,
            isActive: true
        });
    }
    
    /**
     * @dev Add authorized healthcare provider
     * @param provider Address of the healthcare provider
     */
    function addAuthorizedProvider(address provider) external onlyOwner {
        require(provider != address(0), "Invalid provider address");
        authorizedProviders[provider] = true;
    }
    
    /**
     * @dev Remove authorized healthcare provider
     * @param provider Address of the healthcare provider
     */
    function removeAuthorizedProvider(address provider) external onlyOwner {
        require(provider != address(0), "Invalid provider address");
        authorizedProviders[provider] = false;
    }
    
    /**
     * @dev Get record information
     * @param recordId ID of the record
     * @return recordType Type of the record
     * @return encryptedDataHash IPFS hash of encrypted data
     * @return dataIntegrityHash Data integrity hash
     * @return createdAt Creation timestamp
     * @return isActive Whether the record is active
     */
    function getRecordInfo(bytes32 recordId) external view recordExists(recordId) returns (
        string memory recordType,
        string memory encryptedDataHash,
        string memory dataIntegrityHash,
        uint256 createdAt,
        bool isActive
    ) {
        HealthRecord storage record = healthRecords[recordId];
        return (
            record.recordType,
            record.encryptedDataHash,
            record.dataIntegrityHash,
            record.createdAt,
            record.isActive
        );
    }
    
    /**
     * @dev Check if address has access to a record
     * @param recordId ID of the record
     * @param user Address to check access for
     * @return hasAccess_ Whether the user has access
     * @return accessLevel Level of access
     * @return expiresAt When access expires
     */
    function checkAccess(bytes32 recordId, address user) external view recordExists(recordId) returns (
        bool hasAccess_,
        string memory accessLevel,
        uint256 expiresAt
    ) {
        AccessPermission storage permission = healthRecords[recordId].accessPermissions[user];
        return (
            permission.hasAccess && permission.expiresAt > block.timestamp,
            permission.accessLevel,
            permission.expiresAt
        );
    }
    
    /**
     * @dev Get emergency profile
     * @param patient Address of the patient
     * @return bloodType Patient's blood type
     * @return allergies Array of allergies
     * @return currentMedications Array of current medications
     * @return medicalConditions Array of medical conditions
     * @return emergencyContact Emergency contact information
     * @return isActive Whether the profile is active
     */
    function getEmergencyProfile(address patient) external view returns (
        string memory bloodType,
        string[] memory allergies,
        string[] memory currentMedications,
        string[] memory medicalConditions,
        string memory emergencyContact,
        bool isActive
    ) {
        EmergencyProfile storage profile = emergencyProfiles[patient];
        return (
            profile.bloodType,
            profile.allergies,
            profile.currentMedications,
            profile.medicalConditions,
            profile.emergencyContact,
            profile.isActive
        );
    }
    
    /**
     * @dev Deactivate a health record
     * @param recordId ID of the record to deactivate
     */
    function deactivateRecord(bytes32 recordId) external onlyOwner recordExists(recordId) {
        healthRecords[recordId].isActive = false;
    }
    
    /**
     * @dev Update vault settings
     * @param _encryptionEnabled Whether encryption is enabled
     * @param _zkProofsEnabled Whether zero-knowledge proofs are enabled
     * @param _privacyLevel Privacy level setting
     */
    function updateVaultSettings(
        bool _encryptionEnabled,
        bool _zkProofsEnabled,
        string memory _privacyLevel
    ) external onlyOwner {
        encryptionEnabled = _encryptionEnabled;
        zkProofsEnabled = _zkProofsEnabled;
        privacyLevel = _privacyLevel;
    }
    
    /**
     * @dev Add supported record type
     * @param recordType Type of record to support
     */
    function addSupportedRecordType(string memory recordType) external onlyOwner {
        require(bytes(recordType).length > 0, "Record type cannot be empty");
        supportedRecordTypes[recordType] = true;
    }
    
    /**
     * @dev Remove supported record type
     * @param recordType Type of record to remove support for
     */
    function removeSupportedRecordType(string memory recordType) external onlyOwner {
        require(bytes(recordType).length > 0, "Record type cannot be empty");
        supportedRecordTypes[recordType] = false;
    }
}
