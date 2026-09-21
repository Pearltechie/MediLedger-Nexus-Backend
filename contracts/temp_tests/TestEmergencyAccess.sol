// SPDX-License-Identifier: MIT
pragma solidity ^0.8.19;

import "../EmergencyAccess.sol";
import "forge-std/Test.sol";

/**
 * @title TestEmergencyAccess
 * @dev Comprehensive test suite for EmergencyAccess smart contract
 */
contract TestEmergencyAccess is Test {
    
    EmergencyAccess public emergencyAccess;
    address public owner;
    address public patient;
    address public emergencyProvider;
    address public hospital;
    address public unauthorizedUser;
    
    // Test data
    string[] public allergies;
    string[] public medications;
    string[] public conditions;
    
    event EmergencyProfileCreated(address indexed patient, uint256 timestamp);
    event EmergencyAccessRequested(address indexed patient, address indexed requester, string emergencyType, uint256 timestamp);
    event EmergencyAccessGranted(address indexed patient, address indexed requester, string emergencyType, uint256 expiresAt);
    
    function setUp() public {
        owner = address(this);
        patient = makeAddr("patient");
        emergencyProvider = makeAddr("emergencyProvider");
        hospital = makeAddr("hospital");
        unauthorizedUser = makeAddr("unauthorized");
        
        // Initialize test data
        allergies = new string[](2);
        allergies[0] = "penicillin";
        allergies[1] = "shellfish";
        
        medications = new string[](1);
        medications[0] = "aspirin";
        
        conditions = new string[](1);
        conditions[0] = "diabetes";
        
        // Deploy EmergencyAccess contract
        emergencyAccess = new EmergencyAccess();
    }
    
    function testEmergencyProfileCreation() public {
        // Create emergency profile
        vm.prank(patient);
        emergencyAccess.createEmergencyProfile(
            "O+",
            allergies,
            medications,
            conditions,
            "Emergency Contact: 555-1234",
            "Insurance: ABC123"
        );
        
        // Verify profile was created
        (
            string memory bloodType,
            string[] memory retrievedAllergies,
            string[] memory retrievedMedications,
            string[] memory retrievedConditions,
            string memory emergencyContact,
            string memory insuranceInfo,
            bool isActive,
            uint256 createdAt,
            uint256 lastUpdated
        ) = emergencyAccess.getEmergencyProfile(patient);
        
        assertEq(bloodType, "O+");
        assertEq(retrievedAllergies.length, 2);
        assertEq(retrievedAllergies[0], "penicillin");
        assertEq(retrievedAllergies[1], "shellfish");
        assertEq(retrievedMedications.length, 1);
        assertEq(retrievedMedications[0], "aspirin");
        assertEq(retrievedConditions.length, 1);
        assertEq(retrievedConditions[0], "diabetes");
        assertEq(emergencyContact, "Emergency Contact: 555-1234");
        assertEq(insuranceInfo, "Insurance: ABC123");
        assertTrue(isActive);
        assertTrue(createdAt > 0);
        assertTrue(lastUpdated > 0);
    }
    
    function testEmergencyProfileCreationAlreadyExists() public {
        // First create profile
        vm.prank(patient);
        emergencyAccess.createEmergencyProfile(
            "O+",
            allergies,
            medications,
            conditions,
            "Emergency Contact: 555-1234",
            "Insurance: ABC123"
        );
        
        // Try to create again
        vm.prank(patient);
        vm.expectRevert("Emergency profile already exists");
        emergencyAccess.createEmergencyProfile(
            "A+",
            allergies,
            medications,
            conditions,
            "Emergency Contact: 555-5678",
            "Insurance: DEF456"
        );
    }
    
    function testEmergencyProfileCreationEmptyBloodType() public {
        // Try to create profile with empty blood type
        vm.prank(patient);
        vm.expectRevert("Blood type cannot be empty");
        emergencyAccess.createEmergencyProfile(
            "",
            allergies,
            medications,
            conditions,
            "Emergency Contact: 555-1234",
            "Insurance: ABC123"
        );
    }
    
    function testEmergencyProfileCreationEmptyContact() public {
        // Try to create profile with empty emergency contact
        vm.prank(patient);
        vm.expectRevert("Emergency contact cannot be empty");
        emergencyAccess.createEmergencyProfile(
            "O+",
            allergies,
            medications,
            conditions,
            "",
            "Insurance: ABC123"
        );
    }
    
    function testUpdateEmergencyProfile() public {
        // First create profile
        vm.prank(patient);
        emergencyAccess.createEmergencyProfile(
            "O+",
            allergies,
            medications,
            conditions,
            "Emergency Contact: 555-1234",
            "Insurance: ABC123"
        );
        
        // Update profile
        string[] memory newAllergies = new string[](1);
        newAllergies[0] = "latex";
        
        vm.prank(patient);
        emergencyAccess.updateEmergencyProfile(
            "A+",
            newAllergies,
            medications,
            conditions,
            "Emergency Contact: 555-5678",
            "Insurance: DEF456"
        );
        
        // Verify profile was updated
        (
            string memory bloodType,
            string[] memory retrievedAllergies,
            string[] memory retrievedMedications,
            string[] memory retrievedConditions,
            string memory emergencyContact,
            string memory insuranceInfo,
            bool isActive,
            uint256 createdAt,
            uint256 lastUpdated
        ) = emergencyAccess.getEmergencyProfile(patient);
        
        assertEq(bloodType, "A+");
        assertEq(retrievedAllergies.length, 1);
        assertEq(retrievedAllergies[0], "latex");
        assertEq(emergencyContact, "Emergency Contact: 555-5678");
        assertEq(insuranceInfo, "Insurance: DEF456");
        assertTrue(isActive);
        assertTrue(lastUpdated > createdAt);
    }
    
    function testUpdateEmergencyProfileOnlyPatient() public {
        // First create profile
        vm.prank(patient);
        emergencyAccess.createEmergencyProfile(
            "O+",
            allergies,
            medications,
            conditions,
            "Emergency Contact: 555-1234",
            "Insurance: ABC123"
        );
        
        // Try to update as non-patient
        vm.prank(emergencyProvider);
        vm.expectRevert("No emergency profile found for this address");
        emergencyAccess.updateEmergencyProfile(
            "A+",
            allergies,
            medications,
            conditions,
            "Emergency Contact: 555-5678",
            "Insurance: DEF456"
        );
    }
    
    function testRequestEmergencyAccess() public {
        // First create profile and add authorized provider
        vm.prank(patient);
        emergencyAccess.createEmergencyProfile(
            "O+",
            allergies,
            medications,
            conditions,
            "Emergency Contact: 555-1234",
            "Insurance: ABC123"
        );
        
        emergencyAccess.addAuthorizedEmergencyProvider(emergencyProvider);
        
        // Request emergency access
        vm.prank(emergencyProvider);
        uint256 requestId = emergencyAccess.requestEmergencyAccess(
            patient,
            "cardiac_arrest",
            "Emergency Room A",
            5, // urgencyLevel
            "Dr. Smith - Emergency Medicine"
        );
        
        // Verify request was created
        assertEq(requestId, 1);
        assertEq(emergencyAccess.emergencyRequestCount(), 1);
        
        // Verify request details
        (
            address requestPatient,
            address requester,
            string memory emergencyType,
            string memory location,
            uint256 urgencyLevel,
            uint256 requestedAt,
            bool isApproved,
            uint256 expiresAt
        ) = emergencyAccess.getEmergencyRequest(requestId);
        
        assertEq(requestPatient, patient);
        assertEq(requester, emergencyProvider);
        assertEq(emergencyType, "cardiac_arrest");
        assertEq(location, "Emergency Room A");
        assertEq(urgencyLevel, 5);
        assertTrue(requestedAt > 0);
        assertTrue(isApproved); // Auto-approved for high urgency
        assertTrue(expiresAt > block.timestamp);
    }
    
    function testRequestEmergencyAccessUnauthorized() public {
        // First create profile
        vm.prank(patient);
        emergencyAccess.createEmergencyProfile(
            "O+",
            allergies,
            medications,
            conditions,
            "Emergency Contact: 555-1234",
            "Insurance: ABC123"
        );
        
        // Try to request access as unauthorized provider
        vm.prank(unauthorizedUser);
        vm.expectRevert("Not an authorized emergency provider");
        emergencyAccess.requestEmergencyAccess(
            patient,
            "cardiac_arrest",
            "Emergency Room A",
            5,
            "Dr. Smith - Emergency Medicine"
        );
    }
    
    function testRequestEmergencyAccessInvalidPatient() public {
        // Add authorized provider
        emergencyAccess.addAuthorizedEmergencyProvider(emergencyProvider);
        
        // Try to request access for non-existent profile
        vm.prank(emergencyProvider);
        vm.expectRevert("Emergency profile does not exist");
        emergencyAccess.requestEmergencyAccess(
            patient,
            "cardiac_arrest",
            "Emergency Room A",
            5,
            "Dr. Smith - Emergency Medicine"
        );
    }
    
    function testRequestEmergencyAccessEmptyEmergencyType() public {
        // First create profile and add authorized provider
        vm.prank(patient);
        emergencyAccess.createEmergencyProfile(
            "O+",
            allergies,
            medications,
            conditions,
            "Emergency Contact: 555-1234",
            "Insurance: ABC123"
        );
        
        emergencyAccess.addAuthorizedEmergencyProvider(emergencyProvider);
        
        // Try to request access with empty emergency type
        vm.prank(emergencyProvider);
        vm.expectRevert("Emergency type cannot be empty");
        emergencyAccess.requestEmergencyAccess(
            patient,
            "",
            "Emergency Room A",
            5,
            "Dr. Smith - Emergency Medicine"
        );
    }
    
    function testRequestEmergencyAccessInvalidUrgencyLevel() public {
        // First create profile and add authorized provider
        vm.prank(patient);
        emergencyAccess.createEmergencyProfile(
            "O+",
            allergies,
            medications,
            conditions,
            "Emergency Contact: 555-1234",
            "Insurance: ABC123"
        );
        
        emergencyAccess.addAuthorizedEmergencyProvider(emergencyProvider);
        
        // Try to request access with invalid urgency level
        vm.prank(emergencyProvider);
        vm.expectRevert("Urgency level must be between 1 and 5");
        emergencyAccess.requestEmergencyAccess(
            patient,
            "cardiac_arrest",
            "Emergency Room A",
            6, // Invalid urgency level
            "Dr. Smith - Emergency Medicine"
        );
    }
    
    function testGrantEmergencyAccess() public {
        // First create profile and add authorized provider
        vm.prank(patient);
        emergencyAccess.createEmergencyProfile(
            "O+",
            allergies,
            medications,
            conditions,
            "Emergency Contact: 555-1234",
            "Insurance: ABC123"
        );
        
        emergencyAccess.addAuthorizedEmergencyProvider(emergencyProvider);
        
        // Request emergency access (low urgency, not auto-approved)
        vm.prank(emergencyProvider);
        uint256 requestId = emergencyAccess.requestEmergencyAccess(
            patient,
            "minor_injury",
            "Emergency Room A",
            2, // Low urgency level
            "Dr. Smith - Emergency Medicine"
        );
        
        // Manually grant access
        vm.prank(patient);
        emergencyAccess.grantEmergencyAccess(requestId);
        
        // Verify access was granted
        (
            address requestPatient,
            address requester,
            string memory emergencyType,
            string memory location,
            uint256 urgencyLevel,
            uint256 requestedAt,
            bool isApproved,
            uint256 expiresAt
        ) = emergencyAccess.getEmergencyRequest(requestId);
        
        assertTrue(isApproved);
        assertTrue(expiresAt > block.timestamp);
    }
    
    function testGrantEmergencyAccessOnlyAuthorized() public {
        // First create profile and request access
        vm.prank(patient);
        emergencyAccess.createEmergencyProfile(
            "O+",
            allergies,
            medications,
            conditions,
            "Emergency Contact: 555-1234",
            "Insurance: ABC123"
        );
        
        emergencyAccess.addAuthorizedEmergencyProvider(emergencyProvider);
        
        vm.prank(emergencyProvider);
        uint256 requestId = emergencyAccess.requestEmergencyAccess(
            patient,
            "minor_injury",
            "Emergency Room A",
            2,
            "Dr. Smith - Emergency Medicine"
        );
        
        // Try to grant access as unauthorized user
        vm.prank(unauthorizedUser);
        vm.expectRevert("Not authorized to grant emergency access");
        emergencyAccess.grantEmergencyAccess(requestId);
    }
    
    function testRevokeEmergencyAccess() public {
        // First create profile, add provider, and grant access
        vm.prank(patient);
        emergencyAccess.createEmergencyProfile(
            "O+",
            allergies,
            medications,
            conditions,
            "Emergency Contact: 555-1234",
            "Insurance: ABC123"
        );
        
        emergencyAccess.addAuthorizedEmergencyProvider(emergencyProvider);
        
        vm.prank(emergencyProvider);
        uint256 requestId = emergencyAccess.requestEmergencyAccess(
            patient,
            "cardiac_arrest",
            "Emergency Room A",
            5,
            "Dr. Smith - Emergency Medicine"
        );
        
        // Revoke access
        vm.prank(patient);
        emergencyAccess.revokeEmergencyAccess(patient, emergencyProvider);
        
        // Verify access was revoked
        (bool hasAccess,,,) = emergencyAccess.checkEmergencyAccess(patient, emergencyProvider);
        assertFalse(hasAccess);
    }
    
    function testRevokeEmergencyAccessOnlyAuthorized() public {
        // First create profile and grant access
        vm.prank(patient);
        emergencyAccess.createEmergencyProfile(
            "O+",
            allergies,
            medications,
            conditions,
            "Emergency Contact: 555-1234",
            "Insurance: ABC123"
        );
        
        emergencyAccess.addAuthorizedEmergencyProvider(emergencyProvider);
        
        vm.prank(emergencyProvider);
        emergencyAccess.requestEmergencyAccess(
            patient,
            "cardiac_arrest",
            "Emergency Room A",
            5,
            "Dr. Smith - Emergency Medicine"
        );
        
        // Try to revoke access as unauthorized user
        vm.prank(unauthorizedUser);
        vm.expectRevert("Not authorized to revoke emergency access");
        emergencyAccess.revokeEmergencyAccess(patient, emergencyProvider);
    }
    
    function testCheckEmergencyAccess() public {
        // First create profile and grant access
        vm.prank(patient);
        emergencyAccess.createEmergencyProfile(
            "O+",
            allergies,
            medications,
            conditions,
            "Emergency Contact: 555-1234",
            "Insurance: ABC123"
        );
        
        emergencyAccess.addAuthorizedEmergencyProvider(emergencyProvider);
        
        vm.prank(emergencyProvider);
        emergencyAccess.requestEmergencyAccess(
            patient,
            "cardiac_arrest",
            "Emergency Room A",
            5,
            "Dr. Smith - Emergency Medicine"
        );
        
        // Check emergency access
        (bool hasAccess, string memory emergencyType, uint256 expiresAt, uint256 urgencyLevel) = 
            emergencyAccess.checkEmergencyAccess(patient, emergencyProvider);
        
        assertTrue(hasAccess);
        assertEq(emergencyType, "cardiac_arrest");
        assertTrue(expiresAt > block.timestamp);
        assertEq(urgencyLevel, 5);
    }
    
    function testCheckEmergencyAccessExpired() public {
        // First create profile and grant access
        vm.prank(patient);
        emergencyAccess.createEmergencyProfile(
            "O+",
            allergies,
            medications,
            conditions,
            "Emergency Contact: 555-1234",
            "Insurance: ABC123"
        );
        
        emergencyAccess.addAuthorizedEmergencyProvider(emergencyProvider);
        
        vm.prank(emergencyProvider);
        emergencyAccess.requestEmergencyAccess(
            patient,
            "cardiac_arrest",
            "Emergency Room A",
            1, // Low urgency, shorter access duration
            "Dr. Smith - Emergency Medicine"
        );
        
        // Fast forward time to expire access
        vm.warp(block.timestamp + 7 hours); // 6 hours + buffer
        
        // Check emergency access
        (bool hasAccess,,,) = emergencyAccess.checkEmergencyAccess(patient, emergencyProvider);
        assertFalse(hasAccess);
    }
    
    function testGetPatientEmergencyRequests() public {
        // First create profile and add provider
        vm.prank(patient);
        emergencyAccess.createEmergencyProfile(
            "O+",
            allergies,
            medications,
            conditions,
            "Emergency Contact: 555-1234",
            "Insurance: ABC123"
        );
        
        emergencyAccess.addAuthorizedEmergencyProvider(emergencyProvider);
        emergencyAccess.addAuthorizedHospital(hospital);
        
        // Create multiple emergency requests
        vm.prank(emergencyProvider);
        uint256 requestId1 = emergencyAccess.requestEmergencyAccess(
            patient,
            "cardiac_arrest",
            "Emergency Room A",
            5,
            "Dr. Smith - Emergency Medicine"
        );
        
        vm.prank(hospital);
        uint256 requestId2 = emergencyAccess.requestEmergencyAccess(
            patient,
            "stroke",
            "Emergency Room B",
            4,
            "Dr. Johnson - Neurology"
        );
        
        // Get patient emergency requests
        uint256[] memory patientRequests = emergencyAccess.getPatientEmergencyRequests(patient);
        
        assertEq(patientRequests.length, 2);
        assertEq(patientRequests[0], requestId1);
        assertEq(patientRequests[1], requestId2);
    }
    
    function testGetRequesterEmergencyRequests() public {
        // First create profile and add provider
        vm.prank(patient);
        emergencyAccess.createEmergencyProfile(
            "O+",
            allergies,
            medications,
            conditions,
            "Emergency Contact: 555-1234",
            "Insurance: ABC123"
        );
        
        emergencyAccess.addAuthorizedEmergencyProvider(emergencyProvider);
        
        // Create multiple emergency requests
        vm.prank(emergencyProvider);
        uint256 requestId1 = emergencyAccess.requestEmergencyAccess(
            patient,
            "cardiac_arrest",
            "Emergency Room A",
            5,
            "Dr. Smith - Emergency Medicine"
        );
        
        vm.prank(emergencyProvider);
        uint256 requestId2 = emergencyAccess.requestEmergencyAccess(
            patient,
            "stroke",
            "Emergency Room B",
            4,
            "Dr. Johnson - Neurology"
        );
        
        // Get requester emergency requests
        uint256[] memory requesterRequests = emergencyAccess.getRequesterEmergencyRequests(emergencyProvider);
        
        assertEq(requesterRequests.length, 2);
        assertEq(requesterRequests[0], requestId1);
        assertEq(requesterRequests[1], requestId2);
    }
    
    function testAddAuthorizedEmergencyProvider() public {
        // Add authorized emergency provider
        emergencyAccess.addAuthorizedEmergencyProvider(emergencyProvider);
        
        // Verify provider is authorized
        assertTrue(emergencyAccess.authorizedEmergencyProviders(emergencyProvider));
    }
    
    function testRemoveAuthorizedEmergencyProvider() public {
        // First add provider
        emergencyAccess.addAuthorizedEmergencyProvider(emergencyProvider);
        
        // Remove provider
        emergencyAccess.removeAuthorizedEmergencyProvider(emergencyProvider);
        
        // Verify provider is not authorized
        assertFalse(emergencyAccess.authorizedEmergencyProviders(emergencyProvider));
    }
    
    function testAddAuthorizedHospital() public {
        // Add authorized hospital
        emergencyAccess.addAuthorizedHospital(hospital);
        
        // Verify hospital is authorized
        assertTrue(emergencyAccess.authorizedHospitals(hospital));
    }
    
    function testRemoveAuthorizedHospital() public {
        // First add hospital
        emergencyAccess.addAuthorizedHospital(hospital);
        
        // Remove hospital
        emergencyAccess.removeAuthorizedHospital(hospital);
        
        // Verify hospital is not authorized
        assertFalse(emergencyAccess.authorizedHospitals(hospital));
    }
    
    function testDeactivateEmergencyProfile() public {
        // First create profile
        vm.prank(patient);
        emergencyAccess.createEmergencyProfile(
            "O+",
            allergies,
            medications,
            conditions,
            "Emergency Contact: 555-1234",
            "Insurance: ABC123"
        );
        
        // Deactivate profile
        vm.prank(patient);
        emergencyAccess.deactivateEmergencyProfile();
        
        // Verify profile is deactivated
        (,,,,,, bool isActive,,) = emergencyAccess.getEmergencyProfile(patient);
        assertFalse(isActive);
    }
    
    function testDeactivateEmergencyProfileOnlyPatient() public {
        // First create profile
        vm.prank(patient);
        emergencyAccess.createEmergencyProfile(
            "O+",
            allergies,
            medications,
            conditions,
            "Emergency Contact: 555-1234",
            "Insurance: ABC123"
        );
        
        // Try to deactivate as non-patient
        vm.prank(emergencyProvider);
        vm.expectRevert("No emergency profile found for this address");
        emergencyAccess.deactivateEmergencyProfile();
    }
    
    function testGetContractStats() public {
        // Create profile and request access
        vm.prank(patient);
        emergencyAccess.createEmergencyProfile(
            "O+",
            allergies,
            medications,
            conditions,
            "Emergency Contact: 555-1234",
            "Insurance: ABC123"
        );
        
        emergencyAccess.addAuthorizedEmergencyProvider(emergencyProvider);
        
        vm.prank(emergencyProvider);
        emergencyAccess.requestEmergencyAccess(
            patient,
            "cardiac_arrest",
            "Emergency Room A",
            5,
            "Dr. Smith - Emergency Medicine"
        );
        
        // Get contract stats
        (uint256 totalRequests, uint256 totalAccesses, uint256 activeProfiles) = 
            emergencyAccess.getContractStats();
        
        assertEq(totalRequests, 1);
        assertEq(totalAccesses, 1);
        assertEq(activeProfiles, 0); // Simplified implementation
    }
    
    function testHighUrgencyAutoApproval() public {
        // First create profile and add provider
        vm.prank(patient);
        emergencyAccess.createEmergencyProfile(
            "O+",
            allergies,
            medications,
            conditions,
            "Emergency Contact: 555-1234",
            "Insurance: ABC123"
        );
        
        emergencyAccess.addAuthorizedEmergencyProvider(emergencyProvider);
        
        // Request emergency access with high urgency (should auto-approve)
        vm.prank(emergencyProvider);
        uint256 requestId = emergencyAccess.requestEmergencyAccess(
            patient,
            "cardiac_arrest",
            "Emergency Room A",
            5, // High urgency
            "Dr. Smith - Emergency Medicine"
        );
        
        // Verify request was auto-approved
        (,,,,,, bool isApproved,) = emergencyAccess.getEmergencyRequest(requestId);
        assertTrue(isApproved);
        
        // Verify emergency access was granted
        (bool hasAccess,,,) = emergencyAccess.checkEmergencyAccess(patient, emergencyProvider);
        assertTrue(hasAccess);
    }
    
    function testLowUrgencyManualApproval() public {
        // First create profile and add provider
        vm.prank(patient);
        emergencyAccess.createEmergencyProfile(
            "O+",
            allergies,
            medications,
            conditions,
            "Emergency Contact: 555-1234",
            "Insurance: ABC123"
        );
        
        emergencyAccess.addAuthorizedEmergencyProvider(emergencyProvider);
        
        // Request emergency access with low urgency (should not auto-approve)
        vm.prank(emergencyProvider);
        uint256 requestId = emergencyAccess.requestEmergencyAccess(
            patient,
            "minor_injury",
            "Emergency Room A",
            2, // Low urgency
            "Dr. Smith - Emergency Medicine"
        );
        
        // Verify request was not auto-approved
        (,,,,,, bool isApproved,) = emergencyAccess.getEmergencyRequest(requestId);
        assertFalse(isApproved);
        
        // Manually approve
        vm.prank(patient);
        emergencyAccess.grantEmergencyAccess(requestId);
        
        // Verify request is now approved
        (,,,,,, isApproved,) = emergencyAccess.getEmergencyRequest(requestId);
        assertTrue(isApproved);
    }
}
