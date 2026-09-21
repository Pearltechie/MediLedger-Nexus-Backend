// SPDX-License-Identifier: MIT
pragma solidity ^0.8.19;

import "../HealthVault.sol";
import "forge-std/Test.sol";

/**
 * @title TestHealthVault
 * @dev Comprehensive test suite for HealthVault smart contract
 */
contract TestHealthVault is Test {
    
    HealthVault public healthVault;
    address public owner;
    address public patient;
    address public provider;
    address public unauthorizedUser;
    
    // Test data
    string constant VAULT_NAME = "Test Health Vault";
    string constant RECORD_TYPE = "lab_results";
    string constant ENCRYPTED_DATA_HASH = "QmTestHash123";
    string constant DATA_INTEGRITY_HASH = "0x1234567890abcdef";
    
    event VaultCreated(address indexed owner, string vaultName, uint256 timestamp);
    event RecordCreated(bytes32 indexed recordId, string recordType, uint256 timestamp);
    event AccessGranted(bytes32 indexed recordId, address indexed grantee, uint256 expiresAt);
    event AccessRevoked(bytes32 indexed recordId, address indexed grantee);
    
    function setUp() public {
        owner = address(this);
        patient = makeAddr("patient");
        provider = makeAddr("provider");
        unauthorizedUser = makeAddr("unauthorized");
        
        // Deploy HealthVault contract
        healthVault = new HealthVault(
            VAULT_NAME,
            true,  // encryptionEnabled
            true,  // zkProofsEnabled
            "high" // privacyLevel
        );
    }
    
    function testVaultCreation() public {
        // Test vault creation
        assertEq(healthVault.owner(), owner);
        assertEq(healthVault.vaultName(), VAULT_NAME);
        assertTrue(healthVault.encryptionEnabled());
        assertTrue(healthVault.zkProofsEnabled());
        assertEq(healthVault.privacyLevel(), "high");
        assertEq(healthVault.recordCount(), 0);
    }
    
    function testCreateRecord() public {
        // Test record creation
        vm.prank(owner);
        bytes32 recordId = healthVault.createRecord(
            RECORD_TYPE,
            ENCRYPTED_DATA_HASH,
            DATA_INTEGRITY_HASH
        );
        
        // Verify record was created
        assertTrue(recordId != bytes32(0));
        assertEq(healthVault.recordCount(), 1);
        
        // Verify record details
        (
            string memory recordType,
            string memory encryptedDataHash,
            string memory dataIntegrityHash,
            uint256 createdAt,
            bool isActive
        ) = healthVault.getRecordInfo(recordId);
        
        assertEq(recordType, RECORD_TYPE);
        assertEq(encryptedDataHash, ENCRYPTED_DATA_HASH);
        assertEq(dataIntegrityHash, DATA_INTEGRITY_HASH);
        assertTrue(createdAt > 0);
        assertTrue(isActive);
    }
    
    function testCreateRecordOnlyOwner() public {
        // Test that only owner can create records
        vm.prank(patient);
        vm.expectRevert("Only vault owner can perform this action");
        healthVault.createRecord(
            RECORD_TYPE,
            ENCRYPTED_DATA_HASH,
            DATA_INTEGRITY_HASH
        );
    }
    
    function testCreateRecordInvalidType() public {
        // Test creating record with invalid type
        vm.prank(owner);
        vm.expectRevert("Unsupported record type");
        healthVault.createRecord(
            "invalid_type",
            ENCRYPTED_DATA_HASH,
            DATA_INTEGRITY_HASH
        );
    }
    
    function testCreateRecordEmptyHash() public {
        // Test creating record with empty hash
        vm.prank(owner);
        vm.expectRevert("Encrypted data hash cannot be empty");
        healthVault.createRecord(
            RECORD_TYPE,
            "",
            DATA_INTEGRITY_HASH
        );
    }
    
    function testGrantAccess() public {
        // First create a record
        vm.prank(owner);
        bytes32 recordId = healthVault.createRecord(
            RECORD_TYPE,
            ENCRYPTED_DATA_HASH,
            DATA_INTEGRITY_HASH
        );
        
        // Grant access to provider
        vm.prank(owner);
        healthVault.grantAccess(recordId, provider, "read", 24);
        
        // Verify access was granted
        (bool hasAccess, string memory accessLevel, uint256 expiresAt) = 
            healthVault.checkAccess(recordId, provider);
        
        assertTrue(hasAccess);
        assertEq(accessLevel, "read");
        assertTrue(expiresAt > block.timestamp);
    }
    
    function testGrantAccessOnlyOwner() public {
        // First create a record
        vm.prank(owner);
        bytes32 recordId = healthVault.createRecord(
            RECORD_TYPE,
            ENCRYPTED_DATA_HASH,
            DATA_INTEGRITY_HASH
        );
        
        // Try to grant access as non-owner
        vm.prank(patient);
        vm.expectRevert("Only vault owner can perform this action");
        healthVault.grantAccess(recordId, provider, "read", 24);
    }
    
    function testGrantAccessInvalidLevel() public {
        // First create a record
        vm.prank(owner);
        bytes32 recordId = healthVault.createRecord(
            RECORD_TYPE,
            ENCRYPTED_DATA_HASH,
            DATA_INTEGRITY_HASH
        );
        
        // Try to grant access with invalid level
        vm.prank(owner);
        vm.expectRevert("Invalid access level");
        healthVault.grantAccess(recordId, provider, "invalid", 24);
    }
    
    function testRevokeAccess() public {
        // First create a record and grant access
        vm.prank(owner);
        bytes32 recordId = healthVault.createRecord(
            RECORD_TYPE,
            ENCRYPTED_DATA_HASH,
            DATA_INTEGRITY_HASH
        );
        
        vm.prank(owner);
        healthVault.grantAccess(recordId, provider, "read", 24);
        
        // Revoke access
        vm.prank(owner);
        healthVault.revokeAccess(recordId, provider);
        
        // Verify access was revoked
        (bool hasAccess,,) = healthVault.checkAccess(recordId, provider);
        assertFalse(hasAccess);
    }
    
    function testRevokeAccessOnlyOwner() public {
        // First create a record and grant access
        vm.prank(owner);
        bytes32 recordId = healthVault.createRecord(
            RECORD_TYPE,
            ENCRYPTED_DATA_HASH,
            DATA_INTEGRITY_HASH
        );
        
        vm.prank(owner);
        healthVault.grantAccess(recordId, provider, "read", 24);
        
        // Try to revoke access as non-owner
        vm.prank(patient);
        vm.expectRevert("Only vault owner can perform this action");
        healthVault.revokeAccess(recordId, provider);
    }
    
    function testEmergencyAccess() public {
        // First create a record
        vm.prank(owner);
        bytes32 recordId = healthVault.createRecord(
            RECORD_TYPE,
            ENCRYPTED_DATA_HASH,
            DATA_INTEGRITY_HASH
        );
        
        // Add provider as authorized
        vm.prank(owner);
        healthVault.addAuthorizedProvider(provider);
        
        // Grant emergency access
        vm.prank(provider);
        healthVault.grantEmergencyAccess(recordId, provider, "cardiac_arrest");
        
        // Verify emergency access was granted
        (bool hasAccess, string memory accessLevel,) = 
            healthVault.checkAccess(recordId, provider);
        
        assertTrue(hasAccess);
        assertEq(accessLevel, "read");
    }
    
    function testEmergencyAccessUnauthorized() public {
        // First create a record
        vm.prank(owner);
        bytes32 recordId = healthVault.createRecord(
            RECORD_TYPE,
            ENCRYPTED_DATA_HASH,
            DATA_INTEGRITY_HASH
        );
        
        // Try to grant emergency access as unauthorized provider
        vm.prank(provider);
        vm.expectRevert("Not an authorized provider");
        healthVault.grantEmergencyAccess(recordId, provider, "cardiac_arrest");
    }
    
    function testSetEmergencyProfile() public {
        string[] memory allergies = new string[](2);
        allergies[0] = "penicillin";
        allergies[1] = "shellfish";
        
        string[] memory medications = new string[](1);
        medications[0] = "aspirin";
        
        string[] memory conditions = new string[](1);
        conditions[0] = "diabetes";
        
        // Set emergency profile
        vm.prank(owner);
        healthVault.setEmergencyProfile(
            "O+",
            allergies,
            medications,
            conditions,
            "Emergency Contact: 555-1234"
        );
        
        // Verify emergency profile
        (
            string memory bloodType,
            string[] memory retrievedAllergies,
            string[] memory retrievedMedications,
            string[] memory retrievedConditions,
            string memory emergencyContact,
            bool isActive
        ) = healthVault.getEmergencyProfile(owner);
        
        assertEq(bloodType, "O+");
        assertEq(retrievedAllergies.length, 2);
        assertEq(retrievedAllergies[0], "penicillin");
        assertEq(retrievedAllergies[1], "shellfish");
        assertEq(retrievedMedications.length, 1);
        assertEq(retrievedMedications[0], "aspirin");
        assertEq(retrievedConditions.length, 1);
        assertEq(retrievedConditions[0], "diabetes");
        assertEq(emergencyContact, "Emergency Contact: 555-1234");
        assertTrue(isActive);
    }
    
    function testAddAuthorizedProvider() public {
        // Add authorized provider
        vm.prank(owner);
        healthVault.addAuthorizedProvider(provider);
        
        // Verify provider is authorized
        assertTrue(healthVault.authorizedProviders(provider));
    }
    
    function testRemoveAuthorizedProvider() public {
        // First add provider
        vm.prank(owner);
        healthVault.addAuthorizedProvider(provider);
        
        // Remove provider
        vm.prank(owner);
        healthVault.removeAuthorizedProvider(provider);
        
        // Verify provider is not authorized
        assertFalse(healthVault.authorizedProviders(provider));
    }
    
    function testDeactivateRecord() public {
        // First create a record
        vm.prank(owner);
        bytes32 recordId = healthVault.createRecord(
            RECORD_TYPE,
            ENCRYPTED_DATA_HASH,
            DATA_INTEGRITY_HASH
        );
        
        // Deactivate record
        vm.prank(owner);
        healthVault.deactivateRecord(recordId);
        
        // Verify record is deactivated
        (,,,, bool isActive) = healthVault.getRecordInfo(recordId);
        assertFalse(isActive);
    }
    
    function testUpdateVaultSettings() public {
        // Update vault settings
        vm.prank(owner);
        healthVault.updateVaultSettings(false, false, "medium");
        
        // Verify settings were updated
        assertFalse(healthVault.encryptionEnabled());
        assertFalse(healthVault.zkProofsEnabled());
        assertEq(healthVault.privacyLevel(), "medium");
    }
    
    function testAddSupportedRecordType() public {
        // Add new record type
        vm.prank(owner);
        healthVault.addSupportedRecordType("genomics");
        
        // Verify record type is supported
        assertTrue(healthVault.supportedRecordTypes("genomics"));
    }
    
    function testRemoveSupportedRecordType() public {
        // Remove existing record type
        vm.prank(owner);
        healthVault.removeSupportedRecordType("lab_results");
        
        // Verify record type is not supported
        assertFalse(healthVault.supportedRecordTypes("lab_results"));
    }
    
    function testAccessExpiration() public {
        // First create a record
        vm.prank(owner);
        bytes32 recordId = healthVault.createRecord(
            RECORD_TYPE,
            ENCRYPTED_DATA_HASH,
            DATA_INTEGRITY_HASH
        );
        
        // Grant access for 1 hour
        vm.prank(owner);
        healthVault.grantAccess(recordId, provider, "read", 1);
        
        // Verify access is granted
        (bool hasAccess,,) = healthVault.checkAccess(recordId, provider);
        assertTrue(hasAccess);
        
        // Fast forward time by 2 hours
        vm.warp(block.timestamp + 2 hours);
        
        // Verify access has expired
        (hasAccess,,) = healthVault.checkAccess(recordId, provider);
        assertFalse(hasAccess);
    }
    
    function testMultipleRecords() public {
        // Create multiple records
        vm.startPrank(owner);
        
        bytes32 recordId1 = healthVault.createRecord(
            "lab_results",
            "hash1",
            "integrity1"
        );
        
        bytes32 recordId2 = healthVault.createRecord(
            "imaging",
            "hash2",
            "integrity2"
        );
        
        vm.stopPrank();
        
        // Verify both records were created
        assertEq(healthVault.recordCount(), 2);
        assertTrue(recordId1 != recordId2);
        
        // Verify both records are active
        (,,,, bool isActive1) = healthVault.getRecordInfo(recordId1);
        (,,,, bool isActive2) = healthVault.getRecordInfo(recordId2);
        assertTrue(isActive1);
        assertTrue(isActive2);
    }
    
    function testOwnerAccessNeverExpires() public {
        // First create a record
        vm.prank(owner);
        bytes32 recordId = healthVault.createRecord(
            RECORD_TYPE,
            ENCRYPTED_DATA_HASH,
            DATA_INTEGRITY_HASH
        );
        
        // Verify owner has access
        (bool hasAccess, string memory accessLevel,) = 
            healthVault.checkAccess(recordId, owner);
        
        assertTrue(hasAccess);
        assertEq(accessLevel, "admin");
        
        // Fast forward time significantly
        vm.warp(block.timestamp + 365 days);
        
        // Verify owner still has access
        (hasAccess, accessLevel,) = healthVault.checkAccess(recordId, owner);
        assertTrue(hasAccess);
        assertEq(accessLevel, "admin");
    }
}
