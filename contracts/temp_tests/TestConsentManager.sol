// SPDX-License-Identifier: MIT
pragma solidity ^0.8.19;

import "../ConsentManager.sol";
import "forge-std/Test.sol";

/**
 * @title TestConsentManager
 * @dev Comprehensive test suite for ConsentManager smart contract
 */
contract TestConsentManager is Test {
    
    ConsentManager public consentManager;
    address public owner;
    address public patient;
    address public provider;
    address public researcher;
    address public unauthorizedUser;
    
    // Test data
    string[] public recordTypes;
    string constant PURPOSE = "Medical treatment";
    string constant PRIVACY_LEVEL = "high";
    
    event ConsentCreated(uint256 indexed consentId, address indexed patient, address indexed provider);
    event ConsentActivated(uint256 indexed consentId, uint256 activatedAt);
    event ConsentRevoked(uint256 indexed consentId, string reason);
    event CompensationPaid(uint256 indexed consentId, address indexed patient, uint256 amount);
    
    function setUp() public {
        owner = address(this);
        patient = makeAddr("patient");
        provider = makeAddr("provider");
        researcher = makeAddr("researcher");
        unauthorizedUser = makeAddr("unauthorized");
        
        // Initialize record types
        recordTypes = new string[](3);
        recordTypes[0] = "lab_results";
        recordTypes[1] = "imaging";
        recordTypes[2] = "prescriptions";
        
        // Deploy ConsentManager contract
        consentManager = new ConsentManager();
    }
    
    function testConsentCreation() public {
        // Create consent
        vm.prank(patient);
        uint256 consentId = consentManager.createConsent(
            provider,
            recordTypes,
            24, // durationHours
            1 ether, // compensationRate
            PURPOSE,
            PRIVACY_LEVEL,
            false // autoRenewal
        );
        
        // Verify consent was created
        assertEq(consentId, 1);
        assertEq(consentManager.consentCount(), 1);
        
        // Verify consent details
        (
            address consentPatient,
            address consentProvider,
            string[] memory consentRecordTypes,
            uint256 durationHours,
            uint256 compensationRate,
            string memory purpose,
            string memory privacyLevel,
            bool isActive,
            uint256 expiresAt
        ) = consentManager.getConsentDetails(consentId);
        
        assertEq(consentPatient, patient);
        assertEq(consentProvider, provider);
        assertEq(consentRecordTypes.length, 3);
        assertEq(consentRecordTypes[0], "lab_results");
        assertEq(consentRecordTypes[1], "imaging");
        assertEq(consentRecordTypes[2], "prescriptions");
        assertEq(durationHours, 24);
        assertEq(compensationRate, 1 ether);
        assertEq(purpose, PURPOSE);
        assertEq(privacyLevel, PRIVACY_LEVEL);
        assertFalse(isActive); // Not activated yet
        assertEq(expiresAt, 0); // Not set until activated
    }
    
    function testConsentCreationInvalidProvider() public {
        // Try to create consent with invalid provider
        vm.prank(patient);
        vm.expectRevert("Invalid provider address");
        consentManager.createConsent(
            address(0),
            recordTypes,
            24,
            1 ether,
            PURPOSE,
            PRIVACY_LEVEL,
            false
        );
    }
    
    function testConsentCreationEmptyRecordTypes() public {
        // Try to create consent with empty record types
        string[] memory emptyTypes = new string[](0);
        vm.prank(patient);
        vm.expectRevert("At least one record type must be specified");
        consentManager.createConsent(
            provider,
            emptyTypes,
            24,
            1 ether,
            PURPOSE,
            PRIVACY_LEVEL,
            false
        );
    }
    
    function testConsentCreationZeroDuration() public {
        // Try to create consent with zero duration
        vm.prank(patient);
        vm.expectRevert("Duration must be greater than 0");
        consentManager.createConsent(
            provider,
            recordTypes,
            0,
            1 ether,
            PURPOSE,
            PRIVACY_LEVEL,
            false
        );
    }
    
    function testConsentActivation() public {
        // First create consent
        vm.prank(patient);
        uint256 consentId = consentManager.createConsent(
            provider,
            recordTypes,
            24,
            1 ether,
            PURPOSE,
            PRIVACY_LEVEL,
            false
        );
        
        // Activate consent
        vm.prank(patient);
        consentManager.activateConsent(consentId);
        
        // Verify consent is activated
        (,,,,,,, bool isActive, uint256 expiresAt) = consentManager.getConsentDetails(consentId);
        assertTrue(isActive);
        assertTrue(expiresAt > block.timestamp);
    }
    
    function testConsentActivationOnlyPatient() public {
        // First create consent
        vm.prank(patient);
        uint256 consentId = consentManager.createConsent(
            provider,
            recordTypes,
            24,
            1 ether,
            PURPOSE,
            PRIVACY_LEVEL,
            false
        );
        
        // Try to activate as non-patient
        vm.prank(provider);
        vm.expectRevert("Only patient can perform this action");
        consentManager.activateConsent(consentId);
    }
    
    function testConsentActivationAlreadyActive() public {
        // First create and activate consent
        vm.prank(patient);
        uint256 consentId = consentManager.createConsent(
            provider,
            recordTypes,
            24,
            1 ether,
            PURPOSE,
            PRIVACY_LEVEL,
            false
        );
        
        vm.prank(patient);
        consentManager.activateConsent(consentId);
        
        // Try to activate again
        vm.prank(patient);
        vm.expectRevert("Consent is already active");
        consentManager.activateConsent(consentId);
    }
    
    function testConsentRevocation() public {
        // First create and activate consent
        vm.prank(patient);
        uint256 consentId = consentManager.createConsent(
            provider,
            recordTypes,
            24,
            1 ether,
            PURPOSE,
            PRIVACY_LEVEL,
            false
        );
        
        vm.prank(patient);
        consentManager.activateConsent(consentId);
        
        // Revoke consent
        vm.prank(patient);
        consentManager.revokeConsent(consentId, "Patient request");
        
        // Verify consent is revoked
        (,,,,,,, bool isActive,) = consentManager.getConsentDetails(consentId);
        assertFalse(isActive);
    }
    
    function testConsentRevocationOnlyPatient() public {
        // First create and activate consent
        vm.prank(patient);
        uint256 consentId = consentManager.createConsent(
            provider,
            recordTypes,
            24,
            1 ether,
            PURPOSE,
            PRIVACY_LEVEL,
            false
        );
        
        vm.prank(patient);
        consentManager.activateConsent(consentId);
        
        // Try to revoke as non-patient
        vm.prank(provider);
        vm.expectRevert("Only patient can perform this action");
        consentManager.revokeConsent(consentId, "Provider request");
    }
    
    function testConsentRevocationNotActive() public {
        // First create consent (don't activate)
        vm.prank(patient);
        uint256 consentId = consentManager.createConsent(
            provider,
            recordTypes,
            24,
            1 ether,
            PURPOSE,
            PRIVACY_LEVEL,
            false
        );
        
        // Try to revoke inactive consent
        vm.prank(patient);
        vm.expectRevert("Consent is not active");
        consentManager.revokeConsent(consentId, "Patient request");
    }
    
    function testGrantDataAccess() public {
        // First create and activate consent
        vm.prank(patient);
        uint256 consentId = consentManager.createConsent(
            provider,
            recordTypes,
            24,
            1 ether,
            PURPOSE,
            PRIVACY_LEVEL,
            false
        );
        
        vm.prank(patient);
        consentManager.activateConsent(consentId);
        
        // Grant data access
        vm.prank(provider);
        consentManager.grantDataAccess(consentId, researcher, "lab_results");
        
        // Verify data access was granted
        (bool hasAccess, bool isActive, uint256 expiresAt) = 
            consentManager.checkDataAccess(consentId, researcher, "lab_results");
        
        assertTrue(hasAccess);
        assertTrue(isActive);
        assertTrue(expiresAt > block.timestamp);
    }
    
    function testGrantDataAccessOnlyProvider() public {
        // First create and activate consent
        vm.prank(patient);
        uint256 consentId = consentManager.createConsent(
            provider,
            recordTypes,
            24,
            1 ether,
            PURPOSE,
            PRIVACY_LEVEL,
            false
        );
        
        vm.prank(patient);
        consentManager.activateConsent(consentId);
        
        // Try to grant access as non-provider
        vm.prank(researcher);
        vm.expectRevert("Only provider can perform this action");
        consentManager.grantDataAccess(consentId, researcher, "lab_results");
    }
    
    function testGrantDataAccessInvalidDataType() public {
        // First create and activate consent
        vm.prank(patient);
        uint256 consentId = consentManager.createConsent(
            provider,
            recordTypes,
            24,
            1 ether,
            PURPOSE,
            PRIVACY_LEVEL,
            false
        );
        
        vm.prank(patient);
        consentManager.activateConsent(consentId);
        
        // Try to grant access to invalid data type
        vm.prank(provider);
        vm.expectRevert("Data type not permitted in this consent");
        consentManager.grantDataAccess(consentId, researcher, "invalid_type");
    }
    
    function testRevokeDataAccess() public {
        // First create, activate consent, and grant access
        vm.prank(patient);
        uint256 consentId = consentManager.createConsent(
            provider,
            recordTypes,
            24,
            1 ether,
            PURPOSE,
            PRIVACY_LEVEL,
            false
        );
        
        vm.prank(patient);
        consentManager.activateConsent(consentId);
        
        vm.prank(provider);
        consentManager.grantDataAccess(consentId, researcher, "lab_results");
        
        // Revoke data access
        vm.prank(provider);
        consentManager.revokeDataAccess(consentId, researcher, "lab_results");
        
        // Verify data access was revoked
        (bool hasAccess,,) = consentManager.checkDataAccess(consentId, researcher, "lab_results");
        assertFalse(hasAccess);
    }
    
    function testPayCompensation() public {
        // First create and activate consent
        vm.prank(patient);
        uint256 consentId = consentManager.createConsent(
            provider,
            recordTypes,
            24,
            1 ether,
            PURPOSE,
            PRIVACY_LEVEL,
            false
        );
        
        vm.prank(patient);
        consentManager.activateConsent(consentId);
        
        // Pay compensation
        uint256 compensationAmount = 2 ether; // 2 hours * 1 ether per hour
        vm.prank(provider);
        consentManager.payCompensation{value: compensationAmount}(
            consentId,
            "lab_results",
            2 // accessDurationHours
        );
        
        // Verify compensation was paid
        uint256 patientEarnings = consentManager.getPatientEarnings(patient);
        assertEq(patientEarnings, compensationAmount);
    }
    
    function testPayCompensationInsufficientAmount() public {
        // First create and activate consent
        vm.prank(patient);
        uint256 consentId = consentManager.createConsent(
            provider,
            recordTypes,
            24,
            1 ether,
            PURPOSE,
            PRIVACY_LEVEL,
            false
        );
        
        vm.prank(patient);
        consentManager.activateConsent(consentId);
        
        // Try to pay insufficient compensation
        vm.prank(provider);
        vm.expectRevert("Insufficient compensation amount");
        consentManager.payCompensation{value: 0.5 ether}(
            consentId,
            "lab_results",
            2 // accessDurationHours
        );
    }
    
    function testPayCompensationOnlyProvider() public {
        // First create and activate consent
        vm.prank(patient);
        uint256 consentId = consentManager.createConsent(
            provider,
            recordTypes,
            24,
            1 ether,
            PURPOSE,
            PRIVACY_LEVEL,
            false
        );
        
        vm.prank(patient);
        consentManager.activateConsent(consentId);
        
        // Try to pay compensation as non-provider
        vm.prank(researcher);
        vm.expectRevert("Only provider can perform this action");
        consentManager.payCompensation{value: 1 ether}(
            consentId,
            "lab_results",
            1
        );
    }
    
    function testAutoRenewal() public {
        // Create consent with auto-renewal enabled
        vm.prank(patient);
        uint256 consentId = consentManager.createConsent(
            provider,
            recordTypes,
            1, // 1 hour duration
            1 ether,
            PURPOSE,
            PRIVACY_LEVEL,
            true // autoRenewal
        );
        
        vm.prank(patient);
        consentManager.activateConsent(consentId);
        
        // Fast forward time to expire consent
        vm.warp(block.timestamp + 2 hours);
        
        // Auto-renew consent
        consentManager.autoRenewConsent(consentId);
        
        // Verify consent is renewed
        (,,,,,,, bool isActive, uint256 expiresAt) = consentManager.getConsentDetails(consentId);
        assertTrue(isActive);
        assertTrue(expiresAt > block.timestamp);
    }
    
    function testAutoRenewalNotEnabled() public {
        // Create consent without auto-renewal
        vm.prank(patient);
        uint256 consentId = consentManager.createConsent(
            provider,
            recordTypes,
            1,
            1 ether,
            PURPOSE,
            PRIVACY_LEVEL,
            false // autoRenewal
        );
        
        vm.prank(patient);
        consentManager.activateConsent(consentId);
        
        // Fast forward time to expire consent
        vm.warp(block.timestamp + 2 hours);
        
        // Try to auto-renew
        vm.expectRevert("Auto-renewal is not enabled for this consent");
        consentManager.autoRenewConsent(consentId);
    }
    
    function testGetPatientConsents() public {
        // Create multiple consents
        vm.startPrank(patient);
        
        uint256 consentId1 = consentManager.createConsent(
            provider,
            recordTypes,
            24,
            1 ether,
            PURPOSE,
            PRIVACY_LEVEL,
            false
        );
        
        uint256 consentId2 = consentManager.createConsent(
            researcher,
            recordTypes,
            48,
            2 ether,
            "Research",
            PRIVACY_LEVEL,
            false
        );
        
        vm.stopPrank();
        
        // Get patient consents
        uint256[] memory patientConsents = consentManager.getPatientConsents(patient);
        
        assertEq(patientConsents.length, 2);
        assertEq(patientConsents[0], consentId1);
        assertEq(patientConsents[1], consentId2);
    }
    
    function testGetProviderConsents() public {
        // Create consent
        vm.prank(patient);
        uint256 consentId = consentManager.createConsent(
            provider,
            recordTypes,
            24,
            1 ether,
            PURPOSE,
            PRIVACY_LEVEL,
            false
        );
        
        // Get provider consents
        uint256[] memory providerConsents = consentManager.getProviderConsents(provider);
        
        assertEq(providerConsents.length, 1);
        assertEq(providerConsents[0], consentId);
    }
    
    function testAddAuthorizedProvider() public {
        // Add authorized provider
        consentManager.addAuthorizedProvider(provider);
        
        // Verify provider is authorized
        assertTrue(consentManager.authorizedProviders(provider));
    }
    
    function testRemoveAuthorizedProvider() public {
        // First add provider
        consentManager.addAuthorizedProvider(provider);
        
        // Remove provider
        consentManager.removeAuthorizedProvider(provider);
        
        // Verify provider is not authorized
        assertFalse(consentManager.authorizedProviders(provider));
    }
    
    function testGetContractStats() public {
        // Create and activate a consent
        vm.prank(patient);
        uint256 consentId = consentManager.createConsent(
            provider,
            recordTypes,
            24,
            1 ether,
            PURPOSE,
            PRIVACY_LEVEL,
            false
        );
        
        vm.prank(patient);
        consentManager.activateConsent(consentId);
        
        // Pay some compensation
        vm.prank(provider);
        consentManager.payCompensation{value: 1 ether}(
            consentId,
            "lab_results",
            1
        );
        
        // Get contract stats
        (uint256 totalConsents, uint256 totalCompensation, uint256 activeConsents) = 
            consentManager.getContractStats();
        
        assertEq(totalConsents, 1);
        assertEq(totalCompensation, 1 ether);
        assertEq(activeConsents, 1);
    }
    
    function testConsentExpiration() public {
        // Create and activate consent with short duration
        vm.prank(patient);
        uint256 consentId = consentManager.createConsent(
            provider,
            recordTypes,
            1, // 1 hour duration
            1 ether,
            PURPOSE,
            PRIVACY_LEVEL,
            false
        );
        
        vm.prank(patient);
        consentManager.activateConsent(consentId);
        
        // Verify consent is active
        (,,,,,,, bool isActive,) = consentManager.getConsentDetails(consentId);
        assertTrue(isActive);
        
        // Fast forward time to expire consent
        vm.warp(block.timestamp + 2 hours);
        
        // Verify consent is expired
        (,,,,,,, isActive,) = consentManager.getConsentDetails(consentId);
        assertFalse(isActive);
    }
    
    function testMultipleConsents() public {
        // Create multiple consents
        vm.startPrank(patient);
        
        uint256 consentId1 = consentManager.createConsent(
            provider,
            recordTypes,
            24,
            1 ether,
            PURPOSE,
            PRIVACY_LEVEL,
            false
        );
        
        uint256 consentId2 = consentManager.createConsent(
            researcher,
            recordTypes,
            48,
            2 ether,
            "Research",
            PRIVACY_LEVEL,
            false
        );
        
        vm.stopPrank();
        
        // Verify both consents were created
        assertEq(consentManager.consentCount(), 2);
        assertTrue(consentId1 != consentId2);
        
        // Activate both consents
        vm.prank(patient);
        consentManager.activateConsent(consentId1);
        
        vm.prank(patient);
        consentManager.activateConsent(consentId2);
        
        // Verify both are active
        (,,,,,,, bool isActive1,) = consentManager.getConsentDetails(consentId1);
        (,,,,,,, bool isActive2,) = consentManager.getConsentDetails(consentId2);
        assertTrue(isActive1);
        assertTrue(isActive2);
    }
}
