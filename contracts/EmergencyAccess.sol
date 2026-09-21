// SPDX-License-Identifier: MIT
pragma solidity ^0.8.19;

/**
 * @title EmergencyAccess
 * @dev Smart contract for managing emergency access to critical health data
 * @author MediLedger Nexus Team
 */
contract EmergencyAccess {
    
    // Events
    event EmergencyProfileCreated(address indexed patient, uint256 timestamp);
    event EmergencyAccessRequested(address indexed patient, address indexed requester, string emergencyType, uint256 timestamp);
    event EmergencyAccessGranted(address indexed patient, address indexed requester, string emergencyType, uint256 expiresAt);
    event EmergencyAccessRevoked(address indexed patient, address indexed requester);
    event EmergencyContactNotified(address indexed patient, address indexed contact, string message);
    event EmergencyProfileUpdated(address indexed patient, uint256 timestamp);
    
    // Structs
    struct EmergencyProfile {
        address patient;
        string bloodType;
        string[] allergies;
        string[] currentMedications;
        string[] medicalConditions;
        string emergencyContact;
        string insuranceInfo;
        bool isActive;
        uint256 createdAt;
        uint256 lastUpdated;
        mapping(address => EmergencyAccessRecord) emergencyAccesses;
    }
    
    struct EmergencyAccessRecord {
        address requester;
        string emergencyType;
        string location;
        uint256 urgencyLevel; // 1-5 scale
        uint256 requestedAt;
        uint256 expiresAt;
        bool isActive;
        string requesterCredentials;
    }
    
    struct EmergencyRequest {
        address patient;
        address requester;
        string emergencyType;
        string location;
        uint256 urgencyLevel;
        string requesterCredentials;
        uint256 requestedAt;
        bool isApproved;
        uint256 expiresAt;
    }
    
    // State variables
    address public owner;
    uint256 public emergencyRequestCount;
    uint256 public totalEmergencyAccesses;
    
    // Mappings
    mapping(address => EmergencyProfile) public emergencyProfiles;
    mapping(uint256 => EmergencyRequest) public emergencyRequests;
    mapping(address => bool) public authorizedEmergencyProviders;
    mapping(address => bool) public authorizedHospitals;
    mapping(address => uint256[]) public patientEmergencyRequests;
    mapping(address => uint256[]) public requesterEmergencyRequests;
    
    // Modifiers
    modifier onlyOwner() {
        require(msg.sender == owner, "Only contract owner can perform this action");
        _;
    }
    
    modifier onlyPatient() {
        require(emergencyProfiles[msg.sender].isActive, "No emergency profile found for this address");
        _;
    }
    
    modifier onlyAuthorizedProvider() {
        require(
            authorizedEmergencyProviders[msg.sender] || 
            authorizedHospitals[msg.sender] || 
            msg.sender == owner,
            "Not an authorized emergency provider"
        );
        _;
    }
    
    modifier profileExists(address patient) {
        require(emergencyProfiles[patient].isActive, "Emergency profile does not exist");
        _;
    }
    
    modifier requestExists(uint256 requestId) {
        require(requestId > 0 && requestId <= emergencyRequestCount, "Emergency request does not exist");
        _;
    }
    
    // Constructor
    constructor() {
        owner = msg.sender;
    }
    
    /**
     * @dev Create emergency profile for a patient
     * @param bloodType Patient's blood type
     * @param allergies Array of allergies
     * @param currentMedications Array of current medications
     * @param medicalConditions Array of medical conditions
     * @param emergencyContact Emergency contact information
     * @param insuranceInfo Insurance information
     */
    function createEmergencyProfile(
        string memory bloodType,
        string[] memory allergies,
        string[] memory currentMedications,
        string[] memory medicalConditions,
        string memory emergencyContact,
        string memory insuranceInfo
    ) external {
        require(!emergencyProfiles[msg.sender].isActive, "Emergency profile already exists");
        require(bytes(bloodType).length > 0, "Blood type cannot be empty");
        require(bytes(emergencyContact).length > 0, "Emergency contact cannot be empty");
        
        EmergencyProfile storage profile = emergencyProfiles[msg.sender];
        profile.patient = msg.sender;
        profile.bloodType = bloodType;
        profile.emergencyContact = emergencyContact;
        profile.insuranceInfo = insuranceInfo;
        profile.isActive = true;
        profile.createdAt = block.timestamp;
        profile.lastUpdated = block.timestamp;
        
        // Set arrays
        for (uint256 i = 0; i < allergies.length; i++) {
            profile.allergies.push(allergies[i]);
        }
        
        for (uint256 i = 0; i < currentMedications.length; i++) {
            profile.currentMedications.push(currentMedications[i]);
        }
        
        for (uint256 i = 0; i < medicalConditions.length; i++) {
            profile.medicalConditions.push(medicalConditions[i]);
        }
        
        emit EmergencyProfileCreated(msg.sender, block.timestamp);
    }
    
    /**
     * @dev Update emergency profile
     * @param bloodType Updated blood type
     * @param allergies Updated array of allergies
     * @param currentMedications Updated array of current medications
     * @param medicalConditions Updated array of medical conditions
     * @param emergencyContact Updated emergency contact
     * @param insuranceInfo Updated insurance information
     */
    function updateEmergencyProfile(
        string memory bloodType,
        string[] memory allergies,
        string[] memory currentMedications,
        string[] memory medicalConditions,
        string memory emergencyContact,
        string memory insuranceInfo
    ) external onlyPatient {
        require(bytes(bloodType).length > 0, "Blood type cannot be empty");
        require(bytes(emergencyContact).length > 0, "Emergency contact cannot be empty");
        
        EmergencyProfile storage profile = emergencyProfiles[msg.sender];
        
        // Update basic info
        profile.bloodType = bloodType;
        profile.emergencyContact = emergencyContact;
        profile.insuranceInfo = insuranceInfo;
        profile.lastUpdated = block.timestamp;
        
        // Clear and update arrays
        delete profile.allergies;
        for (uint256 i = 0; i < allergies.length; i++) {
            profile.allergies.push(allergies[i]);
        }
        
        delete profile.currentMedications;
        for (uint256 i = 0; i < currentMedications.length; i++) {
            profile.currentMedications.push(currentMedications[i]);
        }
        
        delete profile.medicalConditions;
        for (uint256 i = 0; i < medicalConditions.length; i++) {
            profile.medicalConditions.push(medicalConditions[i]);
        }
        
        emit EmergencyProfileUpdated(msg.sender, block.timestamp);
    }
    
    /**
     * @dev Request emergency access to patient data
     * @param patient Address of the patient
     * @param emergencyType Type of emergency
     * @param location Location of the emergency
     * @param urgencyLevel Urgency level (1-5)
     * @param requesterCredentials Credentials of the requester
     */
    function requestEmergencyAccess(
        address patient,
        string memory emergencyType,
        string memory location,
        uint256 urgencyLevel,
        string memory requesterCredentials
    ) external onlyAuthorizedProvider profileExists(patient) returns (uint256) {
        require(patient != address(0), "Invalid patient address");
        require(bytes(emergencyType).length > 0, "Emergency type cannot be empty");
        require(bytes(location).length > 0, "Location cannot be empty");
        require(urgencyLevel >= 1 && urgencyLevel <= 5, "Urgency level must be between 1 and 5");
        require(bytes(requesterCredentials).length > 0, "Requester credentials cannot be empty");
        
        emergencyRequestCount++;
        uint256 requestId = emergencyRequestCount;
        
        // Create emergency request
        EmergencyRequest storage request = emergencyRequests[requestId];
        request.patient = patient;
        request.requester = msg.sender;
        request.emergencyType = emergencyType;
        request.location = location;
        request.urgencyLevel = urgencyLevel;
        request.requesterCredentials = requesterCredentials;
        request.requestedAt = block.timestamp;
        request.isApproved = false;
        
        // Add to mappings
        patientEmergencyRequests[patient].push(requestId);
        requesterEmergencyRequests[msg.sender].push(requestId);
        
        emit EmergencyAccessRequested(patient, msg.sender, emergencyType, block.timestamp);
        
        // Auto-approve for high urgency levels (4-5) or authorized providers
        if (urgencyLevel >= 4 || authorizedEmergencyProviders[msg.sender]) {
            _grantEmergencyAccess(requestId);
        }
        
        return requestId;
    }
    
    /**
     * @dev Grant emergency access (internal function)
     * @param requestId ID of the emergency request
     */
    function _grantEmergencyAccess(uint256 requestId) internal {
        EmergencyRequest storage request = emergencyRequests[requestId];
        require(!request.isApproved, "Emergency access already granted");
        
        // Set expiration time based on urgency level (1-24 hours)
        uint256 accessDuration = request.urgencyLevel * 6 hours; // 6, 12, 18, 24, 30 hours
        uint256 expiresAt = block.timestamp + accessDuration;
        
        // Create emergency access
        EmergencyAccessRecord storage access = emergencyProfiles[request.patient].emergencyAccesses[request.requester];
        access.requester = request.requester;
        access.emergencyType = request.emergencyType;
        access.location = request.location;
        access.urgencyLevel = request.urgencyLevel;
        access.requestedAt = request.requestedAt;
        access.expiresAt = expiresAt;
        access.isActive = true;
        access.requesterCredentials = request.requesterCredentials;
        
        // Mark request as approved
        request.isApproved = true;
        request.expiresAt = expiresAt;
        
        totalEmergencyAccesses++;
        
        emit EmergencyAccessGranted(request.patient, request.requester, request.emergencyType, expiresAt);
        
        // Notify emergency contact if high urgency
        if (request.urgencyLevel >= 4) {
            _notifyEmergencyContact(request.patient, request.emergencyType, request.location);
        }
    }
    
    /**
     * @dev Manually grant emergency access (for patient or authorized provider)
     * @param requestId ID of the emergency request
     */
    function grantEmergencyAccess(uint256 requestId) external requestExists(requestId) {
        EmergencyRequest storage request = emergencyRequests[requestId];
        require(!request.isApproved, "Emergency access already granted");
        require(
            msg.sender == request.patient || 
            msg.sender == owner || 
            authorizedEmergencyProviders[msg.sender],
            "Not authorized to grant emergency access"
        );
        
        _grantEmergencyAccess(requestId);
    }
    
    /**
     * @dev Revoke emergency access
     * @param patient Address of the patient
     * @param requester Address of the requester to revoke access from
     */
    function revokeEmergencyAccess(address patient, address requester) external {
        require(
            msg.sender == patient || 
            msg.sender == owner || 
            authorizedEmergencyProviders[msg.sender],
            "Not authorized to revoke emergency access"
        );
        require(emergencyProfiles[patient].emergencyAccesses[requester].isActive, "No active emergency access found");
        
        emergencyProfiles[patient].emergencyAccesses[requester].isActive = false;
        
        emit EmergencyAccessRevoked(patient, requester);
    }
    
    /**
     * @dev Notify emergency contact (internal function)
     * @param patient Address of the patient
     * @param emergencyType Type of emergency
     * @param location Location of the emergency
     */
    function _notifyEmergencyContact(
        address patient,
        string memory emergencyType,
        string memory location
    ) internal {
        string memory contact = emergencyProfiles[patient].emergencyContact;
        string memory message = string(abi.encodePacked(
            "EMERGENCY ALERT: ",
            emergencyType,
            " at ",
            location,
            " - Patient: ",
            _addressToString(patient)
        ));
        
        // In a real implementation, this would trigger an actual notification
        // For now, we just emit an event
        emit EmergencyContactNotified(patient, address(0), message);
    }
    
    /**
     * @dev Get emergency profile data
     * @param patient Address of the patient
     * @return bloodType Patient's blood type
     * @return allergies Array of allergies
     * @return currentMedications Array of current medications
     * @return medicalConditions Array of medical conditions
     * @return emergencyContact Emergency contact information
     * @return insuranceInfo Insurance information
     * @return isActive Whether profile is active
     * @return createdAt When profile was created
     * @return lastUpdated When profile was last updated
     */
    function getEmergencyProfile(address patient) external view profileExists(patient) returns (
        string memory bloodType,
        string[] memory allergies,
        string[] memory currentMedications,
        string[] memory medicalConditions,
        string memory emergencyContact,
        string memory insuranceInfo,
        bool isActive,
        uint256 createdAt,
        uint256 lastUpdated
    ) {
        EmergencyProfile storage profile = emergencyProfiles[patient];
        return (
            profile.bloodType,
            profile.allergies,
            profile.currentMedications,
            profile.medicalConditions,
            profile.emergencyContact,
            profile.insuranceInfo,
            profile.isActive,
            profile.createdAt,
            profile.lastUpdated
        );
    }
    
    /**
     * @dev Check if requester has active emergency access
     * @param patient Address of the patient
     * @param requester Address of the requester
     * @return hasAccess Whether requester has active access
     * @return emergencyType Type of emergency
     * @return expiresAt When access expires
     * @return urgencyLevel Urgency level of the emergency
     */
    function checkEmergencyAccess(address patient, address requester) external view returns (
        bool hasAccess,
        string memory emergencyType,
        uint256 expiresAt,
        uint256 urgencyLevel
    ) {
        EmergencyAccessRecord storage access = emergencyProfiles[patient].emergencyAccesses[requester];
        return (
            access.isActive && access.expiresAt > block.timestamp,
            access.emergencyType,
            access.expiresAt,
            access.urgencyLevel
        );
    }
    
    /**
     * @dev Get emergency request details
     * @param requestId ID of the emergency request
     * @return patient Address of the patient
     * @return requester Address of the requester
     * @return emergencyType Type of emergency
     * @return location Location of the emergency
     * @return urgencyLevel Urgency level
     * @return requestedAt When request was made
     * @return isApproved Whether request is approved
     * @return expiresAt When access expires
     */
    function getEmergencyRequest(uint256 requestId) external view requestExists(requestId) returns (
        address patient,
        address requester,
        string memory emergencyType,
        string memory location,
        uint256 urgencyLevel,
        uint256 requestedAt,
        bool isApproved,
        uint256 expiresAt
    ) {
        EmergencyRequest storage request = emergencyRequests[requestId];
        return (
            request.patient,
            request.requester,
            request.emergencyType,
            request.location,
            request.urgencyLevel,
            request.requestedAt,
            request.isApproved,
            request.expiresAt
        );
    }
    
    /**
     * @dev Get patient's emergency requests
     * @param patient Address of the patient
     * @return requestIds Array of request IDs
     */
    function getPatientEmergencyRequests(address patient) external view returns (uint256[] memory requestIds) {
        return patientEmergencyRequests[patient];
    }
    
    /**
     * @dev Get requester's emergency requests
     * @param requester Address of the requester
     * @return requestIds Array of request IDs
     */
    function getRequesterEmergencyRequests(address requester) external view returns (uint256[] memory requestIds) {
        return requesterEmergencyRequests[requester];
    }
    
    /**
     * @dev Add authorized emergency provider
     * @param provider Address of the emergency provider
     */
    function addAuthorizedEmergencyProvider(address provider) external onlyOwner {
        require(provider != address(0), "Invalid provider address");
        authorizedEmergencyProviders[provider] = true;
    }
    
    /**
     * @dev Remove authorized emergency provider
     * @param provider Address of the emergency provider
     */
    function removeAuthorizedEmergencyProvider(address provider) external onlyOwner {
        require(provider != address(0), "Invalid provider address");
        authorizedEmergencyProviders[provider] = false;
    }
    
    /**
     * @dev Add authorized hospital
     * @param hospital Address of the hospital
     */
    function addAuthorizedHospital(address hospital) external onlyOwner {
        require(hospital != address(0), "Invalid hospital address");
        authorizedHospitals[hospital] = true;
    }
    
    /**
     * @dev Remove authorized hospital
     * @param hospital Address of the hospital
     */
    function removeAuthorizedHospital(address hospital) external onlyOwner {
        require(hospital != address(0), "Invalid hospital address");
        authorizedHospitals[hospital] = false;
    }
    
    /**
     * @dev Deactivate emergency profile
     */
    function deactivateEmergencyProfile() external onlyPatient {
        emergencyProfiles[msg.sender].isActive = false;
    }
    
    /**
     * @dev Get contract statistics
     * @return totalRequests Total emergency requests
     * @return totalAccesses Total emergency accesses granted
     * @return activeProfiles Number of active emergency profiles
     */
    function getContractStats() external view returns (
        uint256 totalRequests,
        uint256 totalAccesses,
        uint256 activeProfiles
    ) {
        // Note: This is a simplified implementation
        // In a real contract, you'd need to track active profiles separately
        return (emergencyRequestCount, totalEmergencyAccesses, 0);
    }
    
    /**
     * @dev Helper function to convert address to string
     * @param addr Address to convert
     * @return String representation of the address
     */
    function _addressToString(address addr) internal pure returns (string memory) {
        bytes32 value = bytes32(uint256(uint160(addr)));
        bytes memory alphabet = "0123456789abcdef";
        bytes memory str = new bytes(42);
        str[0] = '0';
        str[1] = 'x';
        for (uint256 i = 0; i < 20; i++) {
            str[2 + i * 2] = alphabet[uint8(value[i + 12] >> 4)];
            str[3 + i * 2] = alphabet[uint8(value[i + 12] & 0x0f)];
        }
        return string(str);
    }
}
