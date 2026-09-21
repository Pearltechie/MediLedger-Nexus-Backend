// SPDX-License-Identifier: MIT
pragma solidity ^0.8.19;

/**
 * @title ConsentManager
 * @dev Smart contract for managing patient consent and data sharing agreements
 * @author MediLedger Nexus Team
 */
contract ConsentManager {
    
    // Events
    event ConsentCreated(uint256 indexed consentId, address indexed patient, address indexed provider);
    event ConsentActivated(uint256 indexed consentId, uint256 activatedAt);
    event ConsentRevoked(uint256 indexed consentId, string reason);
    event CompensationPaid(uint256 indexed consentId, address indexed patient, uint256 amount);
    event DataAccessGranted(uint256 indexed consentId, address indexed requester, string dataType);
    event DataAccessRevoked(uint256 indexed consentId, address indexed requester, string dataType);
    
    // Structs
    struct Consent {
        uint256 consentId;
        address patient;
        address provider;
        string[] recordTypes;
        uint256 durationHours;
        uint256 compensationRate; // HBAR per hour
        string purpose;
        string privacyLevel;
        bool autoRenewal;
        uint256 createdAt;
        uint256 activatedAt;
        uint256 expiresAt;
        bool isActive;
        bool isRevoked;
        string revocationReason;
        mapping(string => bool) dataTypePermissions;
        mapping(address => bool) authorizedAccessors;
    }
    
    struct DataAccess {
        uint256 consentId;
        address requester;
        string dataType;
        uint256 accessedAt;
        uint256 compensationEarned;
        bool isActive;
    }
    
    // State variables
    address public owner;
    uint256 public consentCount;
    uint256 public totalCompensationPaid;
    
    // Mappings
    mapping(uint256 => Consent) public consents;
    mapping(address => uint256[]) public patientConsents;
    mapping(address => uint256[]) public providerConsents;
    mapping(bytes32 => DataAccess) public dataAccesses;
    mapping(address => uint256) public patientEarnings;
    mapping(address => bool) public authorizedProviders;
    
    // Modifiers
    modifier onlyOwner() {
        require(msg.sender == owner, "Only contract owner can perform this action");
        _;
    }
    
    modifier onlyPatient(uint256 consentId) {
        require(consents[consentId].patient == msg.sender, "Only patient can perform this action");
        _;
    }
    
    modifier onlyProvider(uint256 consentId) {
        require(consents[consentId].provider == msg.sender, "Only provider can perform this action");
        _;
    }
    
    modifier consentExists(uint256 consentId) {
        require(consentId > 0 && consentId <= consentCount, "Consent does not exist");
        _;
    }
    
    modifier consentActive(uint256 consentId) {
        require(consents[consentId].isActive && !consents[consentId].isRevoked, "Consent is not active");
        _;
    }
    
    modifier consentNotExpired(uint256 consentId) {
        require(consents[consentId].expiresAt > block.timestamp, "Consent has expired");
        _;
    }
    
    // Constructor
    constructor() {
        owner = msg.sender;
    }
    
    /**
     * @dev Create a new consent agreement
     * @param provider Address of the healthcare provider
     * @param recordTypes Array of record types to be shared
     * @param durationHours Duration of consent in hours
     * @param compensationRate Compensation rate in HBAR per hour
     * @param purpose Purpose of data access
     * @param privacyLevel Privacy level required
     * @param autoRenewal Whether consent should auto-renew
     */
    function createConsent(
        address provider,
        string[] memory recordTypes,
        uint256 durationHours,
        uint256 compensationRate,
        string memory purpose,
        string memory privacyLevel,
        bool autoRenewal
    ) external returns (uint256) {
        require(provider != address(0), "Invalid provider address");
        require(recordTypes.length > 0, "At least one record type must be specified");
        require(durationHours > 0, "Duration must be greater than 0");
        require(bytes(purpose).length > 0, "Purpose cannot be empty");
        require(bytes(privacyLevel).length > 0, "Privacy level cannot be empty");
        
        consentCount++;
        uint256 consentId = consentCount;
        
        Consent storage newConsent = consents[consentId];
        newConsent.consentId = consentId;
        newConsent.patient = msg.sender;
        newConsent.provider = provider;
        newConsent.durationHours = durationHours;
        newConsent.compensationRate = compensationRate;
        newConsent.purpose = purpose;
        newConsent.privacyLevel = privacyLevel;
        newConsent.autoRenewal = autoRenewal;
        newConsent.createdAt = block.timestamp;
        newConsent.isActive = false;
        newConsent.isRevoked = false;
        
        // Set record types and permissions
        for (uint256 i = 0; i < recordTypes.length; i++) {
            newConsent.recordTypes.push(recordTypes[i]);
            newConsent.dataTypePermissions[recordTypes[i]] = true;
        }
        
        // Add to patient and provider mappings
        patientConsents[msg.sender].push(consentId);
        providerConsents[provider].push(consentId);
        
        emit ConsentCreated(consentId, msg.sender, provider);
        return consentId;
    }
    
    /**
     * @dev Activate a consent agreement
     * @param consentId ID of the consent to activate
     */
    function activateConsent(uint256 consentId) external onlyPatient(consentId) consentExists(consentId) {
        require(!consents[consentId].isActive, "Consent is already active");
        require(!consents[consentId].isRevoked, "Cannot activate revoked consent");
        
        consents[consentId].isActive = true;
        consents[consentId].activatedAt = block.timestamp;
        consents[consentId].expiresAt = block.timestamp + (consents[consentId].durationHours * 1 hours);
        
        emit ConsentActivated(consentId, block.timestamp);
    }
    
    /**
     * @dev Revoke a consent agreement
     * @param consentId ID of the consent to revoke
     * @param reason Reason for revocation
     */
    function revokeConsent(uint256 consentId, string memory reason) external onlyPatient(consentId) consentExists(consentId) {
        require(consents[consentId].isActive, "Consent is not active");
        require(!consents[consentId].isRevoked, "Consent is already revoked");
        require(bytes(reason).length > 0, "Revocation reason cannot be empty");
        
        consents[consentId].isRevoked = true;
        consents[consentId].isActive = false;
        consents[consentId].revocationReason = reason;
        
        emit ConsentRevoked(consentId, reason);
    }
    
    /**
     * @dev Grant data access to a specific requester
     * @param consentId ID of the consent
     * @param requester Address requesting data access
     * @param dataType Type of data to access
     */
    function grantDataAccess(
        uint256 consentId,
        address requester,
        string memory dataType
    ) external onlyProvider(consentId) consentExists(consentId) consentActive(consentId) consentNotExpired(consentId) {
        require(requester != address(0), "Invalid requester address");
        require(consents[consentId].dataTypePermissions[dataType], "Data type not permitted in this consent");
        
        consents[consentId].authorizedAccessors[requester] = true;
        
        bytes32 accessId = keccak256(abi.encodePacked(consentId, requester, dataType));
        dataAccesses[accessId] = DataAccess({
            consentId: consentId,
            requester: requester,
            dataType: dataType,
            accessedAt: block.timestamp,
            compensationEarned: 0,
            isActive: true
        });
        
        emit DataAccessGranted(consentId, requester, dataType);
    }
    
    /**
     * @dev Revoke data access from a specific requester
     * @param consentId ID of the consent
     * @param requester Address to revoke access from
     * @param dataType Type of data access to revoke
     */
    function revokeDataAccess(
        uint256 consentId,
        address requester,
        string memory dataType
    ) external onlyProvider(consentId) consentExists(consentId) {
        require(requester != address(0), "Invalid requester address");
        
        consents[consentId].authorizedAccessors[requester] = false;
        
        bytes32 accessId = keccak256(abi.encodePacked(consentId, requester, dataType));
        dataAccesses[accessId].isActive = false;
        
        emit DataAccessRevoked(consentId, requester, dataType);
    }
    
    /**
     * @dev Pay compensation to patient for data access
     * @param consentId ID of the consent
     * @param dataType Type of data accessed
     * @param accessDurationHours Duration of access in hours
     */
    function payCompensation(
        uint256 consentId,
        string memory dataType,
        uint256 accessDurationHours
    ) external payable onlyProvider(consentId) consentExists(consentId) consentActive(consentId) {
        require(msg.value > 0, "Compensation amount must be greater than 0");
        require(consents[consentId].dataTypePermissions[dataType], "Data type not permitted in this consent");
        
        uint256 expectedCompensation = consents[consentId].compensationRate * accessDurationHours;
        require(msg.value >= expectedCompensation, "Insufficient compensation amount");
        
        // Transfer compensation to patient
        address patient = consents[consentId].patient;
        payable(patient).transfer(msg.value);
        
        // Update tracking
        patientEarnings[patient] += msg.value;
        totalCompensationPaid += msg.value;
        
        // Update data access record
        bytes32 accessId = keccak256(abi.encodePacked(consentId, msg.sender, dataType));
        if (dataAccesses[accessId].isActive) {
            dataAccesses[accessId].compensationEarned += msg.value;
        }
        
        emit CompensationPaid(consentId, patient, msg.value);
    }
    
    /**
     * @dev Auto-renew consent if enabled
     * @param consentId ID of the consent to renew
     */
    function autoRenewConsent(uint256 consentId) external consentExists(consentId) {
        require(consents[consentId].autoRenewal, "Auto-renewal is not enabled for this consent");
        require(consents[consentId].isActive, "Consent is not active");
        require(consents[consentId].expiresAt <= block.timestamp, "Consent has not expired yet");
        
        consents[consentId].expiresAt = block.timestamp + (consents[consentId].durationHours * 1 hours);
        
        emit ConsentActivated(consentId, block.timestamp);
    }
    
    /**
     * @dev Get consent details
     * @param consentId ID of the consent
     * @return patient Address of the patient
     * @return provider Address of the provider
     * @return recordTypes Array of record types
     * @return durationHours Duration in hours
     * @return compensationRate Compensation rate
     * @return purpose Purpose of consent
     * @return privacyLevel Privacy level
     * @return isActive Whether consent is active
     * @return expiresAt Expiration timestamp
     */
    function getConsentDetails(uint256 consentId) external view consentExists(consentId) returns (
        address patient,
        address provider,
        string[] memory recordTypes,
        uint256 durationHours,
        uint256 compensationRate,
        string memory purpose,
        string memory privacyLevel,
        bool isActive,
        uint256 expiresAt
    ) {
        Consent storage consent = consents[consentId];
        return (
            consent.patient,
            consent.provider,
            consent.recordTypes,
            consent.durationHours,
            consent.compensationRate,
            consent.purpose,
            consent.privacyLevel,
            consent.isActive,
            consent.expiresAt
        );
    }
    
    /**
     * @dev Check if requester has access to specific data type
     * @param consentId ID of the consent
     * @param requester Address of the requester
     * @param dataType Type of data
     * @return hasAccess Whether requester has access
     * @return isActive Whether consent is active
     * @return expiresAt When consent expires
     */
    function checkDataAccess(
        uint256 consentId,
        address requester,
        string memory dataType
    ) external view consentExists(consentId) returns (
        bool hasAccess,
        bool isActive,
        uint256 expiresAt
    ) {
        Consent storage consent = consents[consentId];
        return (
            consent.authorizedAccessors[requester] && consent.dataTypePermissions[dataType],
            consent.isActive && !consent.isRevoked,
            consent.expiresAt
        );
    }
    
    /**
     * @dev Get patient's total earnings
     * @param patient Address of the patient
     * @return totalEarnings Total earnings in HBAR
     */
    function getPatientEarnings(address patient) external view returns (uint256 totalEarnings) {
        return patientEarnings[patient];
    }
    
    /**
     * @dev Get patient's consent IDs
     * @param patient Address of the patient
     * @return consentIds Array of consent IDs
     */
    function getPatientConsents(address patient) external view returns (uint256[] memory consentIds) {
        return patientConsents[patient];
    }
    
    /**
     * @dev Get provider's consent IDs
     * @param provider Address of the provider
     * @return consentIds Array of consent IDs
     */
    function getProviderConsents(address provider) external view returns (uint256[] memory consentIds) {
        return providerConsents[provider];
    }
    
    /**
     * @dev Add authorized healthcare provider
     * @param provider Address of the provider
     */
    function addAuthorizedProvider(address provider) external onlyOwner {
        require(provider != address(0), "Invalid provider address");
        authorizedProviders[provider] = true;
    }
    
    /**
     * @dev Remove authorized healthcare provider
     * @param provider Address of the provider
     */
    function removeAuthorizedProvider(address provider) external onlyOwner {
        require(provider != address(0), "Invalid provider address");
        authorizedProviders[provider] = false;
    }
    
    /**
     * @dev Get contract statistics
     * @return totalConsents Total number of consents created
     * @return totalCompensation Total compensation paid
     * @return activeConsents Number of active consents
     */
    function getContractStats() external view returns (
        uint256 totalConsents,
        uint256 totalCompensation,
        uint256 activeConsents
    ) {
        uint256 active = 0;
        for (uint256 i = 1; i <= consentCount; i++) {
            if (consents[i].isActive && !consents[i].isRevoked && consents[i].expiresAt > block.timestamp) {
                active++;
            }
        }
        
        return (consentCount, totalCompensationPaid, active);
    }
    
    /**
     * @dev Emergency function to pause all consents (only owner)
     */
    function emergencyPause() external onlyOwner {
        // This would pause all active consents in case of emergency
        // Implementation depends on specific requirements
    }
}
