// SPDX-License-Identifier: MIT
pragma solidity ^0.8.19;

/**
 * @title ResearchStudy
 * @dev Smart contract for managing research studies and participant consent
 * @author MediLedger Nexus Team
 */
contract ResearchStudy {
    
    // Events
    event StudyCreated(uint256 indexed studyId, address indexed principalInvestigator, string title);
    event ParticipantJoined(uint256 indexed studyId, address indexed participant, uint256 compensation);
    event ParticipantLeft(uint256 indexed studyId, address indexed participant);
    event DataContributed(uint256 indexed studyId, address indexed participant, string dataType, uint256 contributionValue);
    event CompensationPaid(uint256 indexed studyId, address indexed participant, uint256 amount);
    event StudyCompleted(uint256 indexed studyId, uint256 totalParticipants, uint256 totalCompensation);
    event StudyPaused(uint256 indexed studyId, string reason);
    event StudyResumed(uint256 indexed studyId);
    
    // Structs
    struct Study {
        uint256 studyId;
        address principalInvestigator;
        string institution;
        string title;
        string description;
        string[] dataTypes;
        uint256 compensationPerContribution; // HBAR per data contribution
        uint256 maxParticipants;
        uint256 durationWeeks;
        uint256 startDate;
        uint256 endDate;
        bool isActive;
        bool isPaused;
        bool isCompleted;
        uint256 participantCount;
        uint256 totalCompensationPaid;
        mapping(address => Participant) participants;
        mapping(string => uint256) dataTypeContributions;
    }
    
    struct Participant {
        address participant;
        uint256 joinedAt;
        uint256 totalContributions;
        uint256 totalCompensationEarned;
        bool isActive;
        mapping(string => uint256) dataTypeContributions;
        mapping(string => bool) dataTypeConsent;
    }
    
    struct DataContribution {
        uint256 studyId;
        address participant;
        string dataType;
        string anonymizedDataHash; // IPFS hash of anonymized data
        uint256 contributionValue;
        uint256 contributedAt;
        bool isValidated;
    }
    
    // State variables
    address public owner;
    uint256 public studyCount;
    uint256 public totalStudiesCompleted;
    
    // Mappings
    mapping(uint256 => Study) public studies;
    mapping(address => uint256[]) public participantStudies;
    mapping(address => uint256[]) public investigatorStudies;
    mapping(bytes32 => DataContribution) public dataContributions;
    mapping(address => bool) public authorizedInstitutions;
    mapping(address => uint256) public totalParticipantEarnings;
    
    // Modifiers
    modifier onlyOwner() {
        require(msg.sender == owner, "Only contract owner can perform this action");
        _;
    }
    
    modifier onlyInvestigator(uint256 studyId) {
        require(studies[studyId].principalInvestigator == msg.sender, "Only principal investigator can perform this action");
        _;
    }
    
    modifier studyExists(uint256 studyId) {
        require(studyId > 0 && studyId <= studyCount, "Study does not exist");
        _;
    }
    
    modifier studyActive(uint256 studyId) {
        require(studies[studyId].isActive && !studies[studyId].isPaused, "Study is not active");
        _;
    }
    
    modifier studyNotCompleted(uint256 studyId) {
        require(!studies[studyId].isCompleted, "Study is already completed");
        _;
    }
    
    modifier studyNotFull(uint256 studyId) {
        require(studies[studyId].participantCount < studies[studyId].maxParticipants, "Study is full");
        _;
    }
    
    modifier studyInProgress(uint256 studyId) {
        require(
            block.timestamp >= studies[studyId].startDate && 
            block.timestamp <= studies[studyId].endDate,
            "Study is not in progress"
        );
        _;
    }
    
    modifier isParticipant(uint256 studyId) {
        require(studies[studyId].participants[msg.sender].isActive, "Not a participant in this study");
        _;
    }
    
    // Constructor
    constructor() {
        owner = msg.sender;
    }
    
    /**
     * @dev Create a new research study
     * @param institution Institution conducting the study
     * @param title Title of the study
     * @param description Description of the study
     * @param dataTypes Array of data types to be collected
     * @param compensationPerContribution Compensation per data contribution in HBAR
     * @param maxParticipants Maximum number of participants
     * @param durationWeeks Duration of the study in weeks
     */
    function createStudy(
        string memory institution,
        string memory title,
        string memory description,
        string[] memory dataTypes,
        uint256 compensationPerContribution,
        uint256 maxParticipants,
        uint256 durationWeeks
    ) external returns (uint256) {
        require(bytes(institution).length > 0, "Institution cannot be empty");
        require(bytes(title).length > 0, "Title cannot be empty");
        require(bytes(description).length > 0, "Description cannot be empty");
        require(dataTypes.length > 0, "At least one data type must be specified");
        require(compensationPerContribution > 0, "Compensation must be greater than 0");
        require(maxParticipants > 0, "Max participants must be greater than 0");
        require(durationWeeks > 0, "Duration must be greater than 0");
        
        studyCount++;
        uint256 studyId = studyCount;
        
        Study storage newStudy = studies[studyId];
        newStudy.studyId = studyId;
        newStudy.principalInvestigator = msg.sender;
        newStudy.institution = institution;
        newStudy.title = title;
        newStudy.description = description;
        newStudy.compensationPerContribution = compensationPerContribution;
        newStudy.maxParticipants = maxParticipants;
        newStudy.durationWeeks = durationWeeks;
        newStudy.startDate = block.timestamp;
        newStudy.endDate = block.timestamp + (durationWeeks * 1 weeks);
        newStudy.isActive = true;
        newStudy.isPaused = false;
        newStudy.isCompleted = false;
        newStudy.participantCount = 0;
        newStudy.totalCompensationPaid = 0;
        
        // Set data types
        for (uint256 i = 0; i < dataTypes.length; i++) {
            newStudy.dataTypes.push(dataTypes[i]);
            newStudy.dataTypeContributions[dataTypes[i]] = 0;
        }
        
        // Add to investigator mapping
        investigatorStudies[msg.sender].push(studyId);
        
        emit StudyCreated(studyId, msg.sender, title);
        return studyId;
    }
    
    /**
     * @dev Join a research study
     * @param studyId ID of the study to join
     * @param dataTypeConsents Array of data types the participant consents to share
     */
    function joinStudy(
        uint256 studyId,
        string[] memory dataTypeConsents
    ) external studyExists(studyId) studyActive(studyId) studyNotCompleted(studyId) studyNotFull(studyId) {
        require(!studies[studyId].participants[msg.sender].isActive, "Already a participant in this study");
        require(dataTypeConsents.length > 0, "Must consent to at least one data type");
        
        // Validate data types
        for (uint256 i = 0; i < dataTypeConsents.length; i++) {
            bool isValidDataType = false;
            for (uint256 j = 0; j < studies[studyId].dataTypes.length; j++) {
                if (keccak256(bytes(dataTypeConsents[i])) == keccak256(bytes(studies[studyId].dataTypes[j]))) {
                    isValidDataType = true;
                    break;
                }
            }
            require(isValidDataType, "Invalid data type");
        }
        
        // Add participant
        Participant storage participant = studies[studyId].participants[msg.sender];
        participant.participant = msg.sender;
        participant.joinedAt = block.timestamp;
        participant.totalContributions = 0;
        participant.totalCompensationEarned = 0;
        participant.isActive = true;
        
        // Set data type consents
        for (uint256 i = 0; i < dataTypeConsents.length; i++) {
            participant.dataTypeConsent[dataTypeConsents[i]] = true;
            participant.dataTypeContributions[dataTypeConsents[i]] = 0;
        }
        
        studies[studyId].participantCount++;
        participantStudies[msg.sender].push(studyId);
        
        emit ParticipantJoined(studyId, msg.sender, studies[studyId].compensationPerContribution);
    }
    
    /**
     * @dev Leave a research study
     * @param studyId ID of the study to leave
     */
    function leaveStudy(uint256 studyId) external studyExists(studyId) isParticipant(studyId) {
        require(studies[studyId].isActive, "Study is not active");
        
        studies[studyId].participants[msg.sender].isActive = false;
        studies[studyId].participantCount--;
        
        emit ParticipantLeft(studyId, msg.sender);
    }
    
    /**
     * @dev Contribute data to a research study
     * @param studyId ID of the study
     * @param dataType Type of data being contributed
     * @param anonymizedDataHash IPFS hash of anonymized data
     * @param contributionValue Value/quality score of the contribution
     */
    function contributeData(
        uint256 studyId,
        string memory dataType,
        string memory anonymizedDataHash,
        uint256 contributionValue
    ) external studyExists(studyId) studyActive(studyId) studyInProgress(studyId) isParticipant(studyId) {
        require(bytes(dataType).length > 0, "Data type cannot be empty");
        require(bytes(anonymizedDataHash).length > 0, "Data hash cannot be empty");
        require(contributionValue > 0, "Contribution value must be greater than 0");
        require(studies[studyId].participants[msg.sender].dataTypeConsent[dataType], "No consent for this data type");
        
        // Create data contribution record
        bytes32 contributionId = keccak256(abi.encodePacked(studyId, msg.sender, dataType, block.timestamp));
        dataContributions[contributionId] = DataContribution({
            studyId: studyId,
            participant: msg.sender,
            dataType: dataType,
            anonymizedDataHash: anonymizedDataHash,
            contributionValue: contributionValue,
            contributedAt: block.timestamp,
            isValidated: false
        });
        
        // Update participant stats
        studies[studyId].participants[msg.sender].totalContributions++;
        studies[studyId].participants[msg.sender].dataTypeContributions[dataType]++;
        
        // Update study stats
        studies[studyId].dataTypeContributions[dataType]++;
        
        emit DataContributed(studyId, msg.sender, dataType, contributionValue);
    }
    
    /**
     * @dev Validate and pay compensation for data contribution
     * @param studyId ID of the study
     * @param participant Address of the participant
     * @param dataType Type of data contributed
     * @param contributionId ID of the contribution
     */
    function validateAndPayContribution(
        uint256 studyId,
        address participant,
        string memory dataType,
        bytes32 contributionId
    ) external payable onlyInvestigator(studyId) studyExists(studyId) {
        require(dataContributions[contributionId].participant == participant, "Invalid contribution");
        require(keccak256(bytes(dataContributions[contributionId].dataType)) == keccak256(bytes(dataType)), "Invalid data type");
        require(!dataContributions[contributionId].isValidated, "Contribution already validated");
        require(msg.value > 0, "Compensation amount must be greater than 0");
        
        // Validate contribution
        dataContributions[contributionId].isValidated = true;
        
        // Calculate compensation based on contribution value
        uint256 baseCompensation = studies[studyId].compensationPerContribution;
        uint256 contributionValue = dataContributions[contributionId].contributionValue;
        uint256 totalCompensation = baseCompensation * contributionValue;
        
        require(msg.value >= totalCompensation, "Insufficient compensation amount");
        
        // Pay compensation
        payable(participant).transfer(msg.value);
        
        // Update tracking
        studies[studyId].participants[participant].totalCompensationEarned += msg.value;
        studies[studyId].totalCompensationPaid += msg.value;
        totalParticipantEarnings[participant] += msg.value;
        
        emit CompensationPaid(studyId, participant, msg.value);
    }
    
    /**
     * @dev Complete a research study
     * @param studyId ID of the study to complete
     */
    function completeStudy(uint256 studyId) external onlyInvestigator(studyId) studyExists(studyId) studyNotCompleted(studyId) {
        require(block.timestamp >= studies[studyId].endDate, "Study has not reached its end date");
        
        studies[studyId].isCompleted = true;
        studies[studyId].isActive = false;
        totalStudiesCompleted++;
        
        emit StudyCompleted(studyId, studies[studyId].participantCount, studies[studyId].totalCompensationPaid);
    }
    
    /**
     * @dev Pause a research study
     * @param studyId ID of the study to pause
     * @param reason Reason for pausing
     */
    function pauseStudy(uint256 studyId, string memory reason) external onlyInvestigator(studyId) studyExists(studyId) {
        require(!studies[studyId].isPaused, "Study is already paused");
        require(!studies[studyId].isCompleted, "Cannot pause completed study");
        require(bytes(reason).length > 0, "Reason cannot be empty");
        
        studies[studyId].isPaused = true;
        studies[studyId].isActive = false;
        
        emit StudyPaused(studyId, reason);
    }
    
    /**
     * @dev Resume a paused research study
     * @param studyId ID of the study to resume
     */
    function resumeStudy(uint256 studyId) external onlyInvestigator(studyId) studyExists(studyId) {
        require(studies[studyId].isPaused, "Study is not paused");
        require(!studies[studyId].isCompleted, "Cannot resume completed study");
        
        studies[studyId].isPaused = false;
        studies[studyId].isActive = true;
        
        emit StudyResumed(studyId);
    }
    
    /**
     * @dev Get study details
     * @param studyId ID of the study
     * @return principalInvestigator Address of principal investigator
     * @return institution Institution name
     * @return title Study title
     * @return description Study description
     * @return dataTypes Array of data types
     * @return compensationPerContribution Compensation per contribution
     * @return maxParticipants Maximum participants
     * @return participantCount Current participant count
     * @return isActive Whether study is active
     * @return startDate Start date
     * @return endDate End date
     */
    function getStudyDetails(uint256 studyId) external view studyExists(studyId) returns (
        address principalInvestigator,
        string memory institution,
        string memory title,
        string memory description,
        string[] memory dataTypes,
        uint256 compensationPerContribution,
        uint256 maxParticipants,
        uint256 participantCount,
        bool isActive,
        uint256 startDate,
        uint256 endDate
    ) {
        Study storage study = studies[studyId];
        return (
            study.principalInvestigator,
            study.institution,
            study.title,
            study.description,
            study.dataTypes,
            study.compensationPerContribution,
            study.maxParticipants,
            study.participantCount,
            study.isActive,
            study.startDate,
            study.endDate
        );
    }
    
    /**
     * @dev Get participant details for a study
     * @param studyId ID of the study
     * @param participant Address of the participant
     * @return joinedAt When participant joined
     * @return totalContributions Total contributions made
     * @return totalCompensationEarned Total compensation earned
     * @return isActive Whether participant is active
     */
    function getParticipantDetails(uint256 studyId, address participant) external view studyExists(studyId) returns (
        uint256 joinedAt,
        uint256 totalContributions,
        uint256 totalCompensationEarned,
        bool isActive
    ) {
        Participant storage p = studies[studyId].participants[participant];
        return (
            p.joinedAt,
            p.totalContributions,
            p.totalCompensationEarned,
            p.isActive
        );
    }
    
    /**
     * @dev Get participant's studies
     * @param participant Address of the participant
     * @return studyIds Array of study IDs
     */
    function getParticipantStudies(address participant) external view returns (uint256[] memory studyIds) {
        return participantStudies[participant];
    }
    
    /**
     * @dev Get investigator's studies
     * @param investigator Address of the investigator
     * @return studyIds Array of study IDs
     */
    function getInvestigatorStudies(address investigator) external view returns (uint256[] memory studyIds) {
        return investigatorStudies[investigator];
    }
    
    /**
     * @dev Get contract statistics
     * @return totalStudies Total number of studies
     * @return completedStudies Number of completed studies
     * @return totalEarnings Total earnings across all participants
     */
    function getContractStats() external view returns (
        uint256 totalStudies,
        uint256 completedStudies,
        uint256 totalEarnings
    ) {
        uint256 earnings = 0;
        for (uint256 i = 1; i <= studyCount; i++) {
            earnings += studies[i].totalCompensationPaid;
        }
        
        return (studyCount, totalStudiesCompleted, earnings);
    }
    
    /**
     * @dev Add authorized institution
     * @param institution Address of the institution
     */
    function addAuthorizedInstitution(address institution) external onlyOwner {
        require(institution != address(0), "Invalid institution address");
        authorizedInstitutions[institution] = true;
    }
    
    /**
     * @dev Remove authorized institution
     * @param institution Address of the institution
     */
    function removeAuthorizedInstitution(address institution) external onlyOwner {
        require(institution != address(0), "Invalid institution address");
        authorizedInstitutions[institution] = false;
    }
}
