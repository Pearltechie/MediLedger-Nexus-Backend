// SPDX-License-Identifier: MIT
pragma solidity ^0.8.19;

import "../ResearchStudy.sol";
import "forge-std/Test.sol";

/**
 * @title TestResearchStudy
 * @dev Comprehensive test suite for ResearchStudy smart contract
 */
contract TestResearchStudy is Test {
    
    ResearchStudy public researchStudy;
    address public owner;
    address public investigator;
    address public participant1;
    address public participant2;
    address public unauthorizedUser;
    
    // Test data
    string constant INSTITUTION = "Test Medical Center";
    string constant STUDY_TITLE = "Diabetes Research Study";
    string constant STUDY_DESCRIPTION = "A comprehensive study on diabetes management";
    string[] public dataTypes;
    
    event StudyCreated(uint256 indexed studyId, address indexed principalInvestigator, string title);
    event ParticipantJoined(uint256 indexed studyId, address indexed participant, uint256 compensation);
    event ParticipantLeft(uint256 indexed studyId, address indexed participant);
    event DataContributed(uint256 indexed studyId, address indexed participant, string dataType, uint256 contributionValue);
    event StudyCompleted(uint256 indexed studyId, uint256 totalParticipants, uint256 totalCompensation);
    
    function setUp() public {
        owner = address(this);
        investigator = makeAddr("investigator");
        participant1 = makeAddr("participant1");
        participant2 = makeAddr("participant2");
        unauthorizedUser = makeAddr("unauthorized");
        
        // Initialize data types
        dataTypes = new string[](3);
        dataTypes[0] = "lab_results";
        dataTypes[1] = "vital_signs";
        dataTypes[2] = "medications";
        
        // Deploy ResearchStudy contract
        researchStudy = new ResearchStudy();
    }
    
    function testStudyCreation() public {
        // Create study
        vm.prank(investigator);
        uint256 studyId = researchStudy.createStudy(
            INSTITUTION,
            STUDY_TITLE,
            STUDY_DESCRIPTION,
            dataTypes,
            1 ether, // compensationPerContribution
            100, // maxParticipants
            12 // durationWeeks
        );
        
        // Verify study was created
        assertEq(studyId, 1);
        assertEq(researchStudy.studyCount(), 1);
        
        // Verify study details
        (
            address principalInvestigator,
            string memory institution,
            string memory title,
            string memory description,
            string[] memory studyDataTypes,
            uint256 compensationPerContribution,
            uint256 maxParticipants,
            uint256 participantCount,
            bool isActive,
            uint256 startDate,
            uint256 endDate
        ) = researchStudy.getStudyDetails(studyId);
        
        assertEq(principalInvestigator, investigator);
        assertEq(institution, INSTITUTION);
        assertEq(title, STUDY_TITLE);
        assertEq(description, STUDY_DESCRIPTION);
        assertEq(studyDataTypes.length, 3);
        assertEq(studyDataTypes[0], "lab_results");
        assertEq(studyDataTypes[1], "vital_signs");
        assertEq(studyDataTypes[2], "medications");
        assertEq(compensationPerContribution, 1 ether);
        assertEq(maxParticipants, 100);
        assertEq(participantCount, 0);
        assertTrue(isActive);
        assertTrue(startDate > 0);
        assertTrue(endDate > startDate);
    }
    
    function testStudyCreationInvalidInstitution() public {
        // Try to create study with empty institution
        vm.prank(investigator);
        vm.expectRevert("Institution cannot be empty");
        researchStudy.createStudy(
            "",
            STUDY_TITLE,
            STUDY_DESCRIPTION,
            dataTypes,
            1 ether,
            100,
            12
        );
    }
    
    function testStudyCreationInvalidTitle() public {
        // Try to create study with empty title
        vm.prank(investigator);
        vm.expectRevert("Title cannot be empty");
        researchStudy.createStudy(
            INSTITUTION,
            "",
            STUDY_DESCRIPTION,
            dataTypes,
            1 ether,
            100,
            12
        );
    }
    
    function testStudyCreationEmptyDataTypes() public {
        // Try to create study with empty data types
        string[] memory emptyTypes = new string[](0);
        vm.prank(investigator);
        vm.expectRevert("At least one data type must be specified");
        researchStudy.createStudy(
            INSTITUTION,
            STUDY_TITLE,
            STUDY_DESCRIPTION,
            emptyTypes,
            1 ether,
            100,
            12
        );
    }
    
    function testStudyCreationZeroCompensation() public {
        // Try to create study with zero compensation
        vm.prank(investigator);
        vm.expectRevert("Compensation must be greater than 0");
        researchStudy.createStudy(
            INSTITUTION,
            STUDY_TITLE,
            STUDY_DESCRIPTION,
            dataTypes,
            0,
            100,
            12
        );
    }
    
    function testStudyCreationZeroMaxParticipants() public {
        // Try to create study with zero max participants
        vm.prank(investigator);
        vm.expectRevert("Max participants must be greater than 0");
        researchStudy.createStudy(
            INSTITUTION,
            STUDY_TITLE,
            STUDY_DESCRIPTION,
            dataTypes,
            1 ether,
            0,
            12
        );
    }
    
    function testStudyCreationZeroDuration() public {
        // Try to create study with zero duration
        vm.prank(investigator);
        vm.expectRevert("Duration must be greater than 0");
        researchStudy.createStudy(
            INSTITUTION,
            STUDY_TITLE,
            STUDY_DESCRIPTION,
            dataTypes,
            1 ether,
            100,
            0
        );
    }
    
    function testJoinStudy() public {
        // First create study
        vm.prank(investigator);
        uint256 studyId = researchStudy.createStudy(
            INSTITUTION,
            STUDY_TITLE,
            STUDY_DESCRIPTION,
            dataTypes,
            1 ether,
            100,
            12
        );
        
        // Join study
        vm.prank(participant1);
        researchStudy.joinStudy(studyId, dataTypes);
        
        // Verify participant joined
        (,,,,,,, uint256 participantCount,,,) = researchStudy.getStudyDetails(studyId);
        assertEq(participantCount, 1);
        
        // Verify participant details
        (uint256 joinedAt, uint256 totalContributions, uint256 totalCompensationEarned, bool isActive) = 
            researchStudy.getParticipantDetails(studyId, participant1);
        
        assertTrue(joinedAt > 0);
        assertEq(totalContributions, 0);
        assertEq(totalCompensationEarned, 0);
        assertTrue(isActive);
    }
    
    function testJoinStudyInvalidDataTypes() public {
        // First create study
        vm.prank(investigator);
        uint256 studyId = researchStudy.createStudy(
            INSTITUTION,
            STUDY_TITLE,
            STUDY_DESCRIPTION,
            dataTypes,
            1 ether,
            100,
            12
        );
        
        // Try to join with invalid data types
        string[] memory invalidTypes = new string[](1);
        invalidTypes[0] = "invalid_type";
        
        vm.prank(participant1);
        vm.expectRevert("Invalid data type");
        researchStudy.joinStudy(studyId, invalidTypes);
    }
    
    function testJoinStudyAlreadyParticipant() public {
        // First create study and join
        vm.prank(investigator);
        uint256 studyId = researchStudy.createStudy(
            INSTITUTION,
            STUDY_TITLE,
            STUDY_DESCRIPTION,
            dataTypes,
            1 ether,
            100,
            12
        );
        
        vm.prank(participant1);
        researchStudy.joinStudy(studyId, dataTypes);
        
        // Try to join again
        vm.prank(participant1);
        vm.expectRevert("Already a participant in this study");
        researchStudy.joinStudy(studyId, dataTypes);
    }
    
    function testJoinStudyFull() public {
        // Create study with max 1 participant
        vm.prank(investigator);
        uint256 studyId = researchStudy.createStudy(
            INSTITUTION,
            STUDY_TITLE,
            STUDY_DESCRIPTION,
            dataTypes,
            1 ether,
            1, // maxParticipants
            12
        );
        
        // First participant joins
        vm.prank(participant1);
        researchStudy.joinStudy(studyId, dataTypes);
        
        // Second participant tries to join
        vm.prank(participant2);
        vm.expectRevert("Study is full");
        researchStudy.joinStudy(studyId, dataTypes);
    }
    
    function testLeaveStudy() public {
        // First create study and join
        vm.prank(investigator);
        uint256 studyId = researchStudy.createStudy(
            INSTITUTION,
            STUDY_TITLE,
            STUDY_DESCRIPTION,
            dataTypes,
            1 ether,
            100,
            12
        );
        
        vm.prank(participant1);
        researchStudy.joinStudy(studyId, dataTypes);
        
        // Leave study
        vm.prank(participant1);
        researchStudy.leaveStudy(studyId);
        
        // Verify participant left
        (,,,,,,, uint256 participantCount,,,) = researchStudy.getStudyDetails(studyId);
        assertEq(participantCount, 0);
        
        // Verify participant is no longer active
        (,,, bool isActive) = researchStudy.getParticipantDetails(studyId, participant1);
        assertFalse(isActive);
    }
    
    function testLeaveStudyNotParticipant() public {
        // First create study
        vm.prank(investigator);
        uint256 studyId = researchStudy.createStudy(
            INSTITUTION,
            STUDY_TITLE,
            STUDY_DESCRIPTION,
            dataTypes,
            1 ether,
            100,
            12
        );
        
        // Try to leave without joining
        vm.prank(participant1);
        vm.expectRevert("Not a participant in this study");
        researchStudy.leaveStudy(studyId);
    }
    
    function testContributeData() public {
        // First create study and join
        vm.prank(investigator);
        uint256 studyId = researchStudy.createStudy(
            INSTITUTION,
            STUDY_TITLE,
            STUDY_DESCRIPTION,
            dataTypes,
            1 ether,
            100,
            12
        );
        
        vm.prank(participant1);
        researchStudy.joinStudy(studyId, dataTypes);
        
        // Contribute data
        vm.prank(participant1);
        researchStudy.contributeData(
            studyId,
            "lab_results",
            "QmTestHash123",
            5 // contributionValue
        );
        
        // Verify contribution was recorded
        (uint256 joinedAt, uint256 totalContributions, uint256 totalCompensationEarned, bool isActive) = 
            researchStudy.getParticipantDetails(studyId, participant1);
        
        assertEq(totalContributions, 1);
        assertEq(totalCompensationEarned, 0); // Not paid yet
        assertTrue(isActive);
    }
    
    function testContributeDataInvalidType() public {
        // First create study and join
        vm.prank(investigator);
        uint256 studyId = researchStudy.createStudy(
            INSTITUTION,
            STUDY_TITLE,
            STUDY_DESCRIPTION,
            dataTypes,
            1 ether,
            100,
            12
        );
        
        vm.prank(participant1);
        researchStudy.joinStudy(studyId, dataTypes);
        
        // Try to contribute invalid data type
        vm.prank(participant1);
        vm.expectRevert("No consent for this data type");
        researchStudy.contributeData(
            studyId,
            "invalid_type",
            "QmTestHash123",
            5
        );
    }
    
    function testContributeDataNotParticipant() public {
        // First create study
        vm.prank(investigator);
        uint256 studyId = researchStudy.createStudy(
            INSTITUTION,
            STUDY_TITLE,
            STUDY_DESCRIPTION,
            dataTypes,
            1 ether,
            100,
            12
        );
        
        // Try to contribute data without joining
        vm.prank(participant1);
        vm.expectRevert("Not a participant in this study");
        researchStudy.contributeData(
            studyId,
            "lab_results",
            "QmTestHash123",
            5
        );
    }
    
    function testValidateAndPayContribution() public {
        // First create study, join, and contribute data
        vm.prank(investigator);
        uint256 studyId = researchStudy.createStudy(
            INSTITUTION,
            STUDY_TITLE,
            STUDY_DESCRIPTION,
            dataTypes,
            1 ether,
            100,
            12
        );
        
        vm.prank(participant1);
        researchStudy.joinStudy(studyId, dataTypes);
        
        vm.prank(participant1);
        researchStudy.contributeData(
            studyId,
            "lab_results",
            "QmTestHash123",
            5 // contributionValue
        );
        
        // Calculate expected compensation (5 * 1 ether = 5 ether)
        uint256 expectedCompensation = 5 ether;
        
        // Validate and pay contribution
        vm.prank(investigator);
        researchStudy.validateAndPayContribution{value: expectedCompensation}(
            studyId,
            participant1,
            "lab_results",
            keccak256(abi.encodePacked(studyId, participant1, "lab_results", block.timestamp))
        );
        
        // Verify compensation was paid
        (,, uint256 totalCompensationEarned,) = researchStudy.getParticipantDetails(studyId, participant1);
        assertEq(totalCompensationEarned, expectedCompensation);
    }
    
    function testValidateAndPayContributionOnlyInvestigator() public {
        // First create study, join, and contribute data
        vm.prank(investigator);
        uint256 studyId = researchStudy.createStudy(
            INSTITUTION,
            STUDY_TITLE,
            STUDY_DESCRIPTION,
            dataTypes,
            1 ether,
            100,
            12
        );
        
        vm.prank(participant1);
        researchStudy.joinStudy(studyId, dataTypes);
        
        vm.prank(participant1);
        researchStudy.contributeData(
            studyId,
            "lab_results",
            "QmTestHash123",
            5
        );
        
        // Try to validate and pay as non-investigator
        vm.prank(participant1);
        vm.expectRevert("Only principal investigator can perform this action");
        researchStudy.validateAndPayContribution{value: 5 ether}(
            studyId,
            participant1,
            "lab_results",
            keccak256(abi.encodePacked(studyId, participant1, "lab_results", block.timestamp))
        );
    }
    
    function testValidateAndPayContributionInsufficientAmount() public {
        // First create study, join, and contribute data
        vm.prank(investigator);
        uint256 studyId = researchStudy.createStudy(
            INSTITUTION,
            STUDY_TITLE,
            STUDY_DESCRIPTION,
            dataTypes,
            1 ether,
            100,
            12
        );
        
        vm.prank(participant1);
        researchStudy.joinStudy(studyId, dataTypes);
        
        vm.prank(participant1);
        researchStudy.contributeData(
            studyId,
            "lab_results",
            "QmTestHash123",
            5
        );
        
        // Try to pay insufficient amount
        vm.prank(investigator);
        vm.expectRevert("Insufficient compensation amount");
        researchStudy.validateAndPayContribution{value: 1 ether}(
            studyId,
            participant1,
            "lab_results",
            keccak256(abi.encodePacked(studyId, participant1, "lab_results", block.timestamp))
        );
    }
    
    function testCompleteStudy() public {
        // First create study
        vm.prank(investigator);
        uint256 studyId = researchStudy.createStudy(
            INSTITUTION,
            STUDY_TITLE,
            STUDY_DESCRIPTION,
            dataTypes,
            1 ether,
            100,
            1 // 1 week duration
        );
        
        // Fast forward time to end date
        vm.warp(block.timestamp + 1 weeks + 1);
        
        // Complete study
        vm.prank(investigator);
        researchStudy.completeStudy(studyId);
        
        // Verify study is completed
        (,,,,,,, bool isActive,,) = researchStudy.getStudyDetails(studyId);
        assertFalse(isActive);
    }
    
    function testCompleteStudyOnlyInvestigator() public {
        // First create study
        vm.prank(investigator);
        uint256 studyId = researchStudy.createStudy(
            INSTITUTION,
            STUDY_TITLE,
            STUDY_DESCRIPTION,
            dataTypes,
            1 ether,
            100,
            1
        );
        
        // Fast forward time to end date
        vm.warp(block.timestamp + 1 weeks + 1);
        
        // Try to complete study as non-investigator
        vm.prank(participant1);
        vm.expectRevert("Only principal investigator can perform this action");
        researchStudy.completeStudy(studyId);
    }
    
    function testCompleteStudyNotEnded() public {
        // First create study
        vm.prank(investigator);
        uint256 studyId = researchStudy.createStudy(
            INSTITUTION,
            STUDY_TITLE,
            STUDY_DESCRIPTION,
            dataTypes,
            1 ether,
            100,
            12 // 12 weeks duration
        );
        
        // Try to complete study before end date
        vm.prank(investigator);
        vm.expectRevert("Study has not reached its end date");
        researchStudy.completeStudy(studyId);
    }
    
    function testPauseStudy() public {
        // First create study
        vm.prank(investigator);
        uint256 studyId = researchStudy.createStudy(
            INSTITUTION,
            STUDY_TITLE,
            STUDY_DESCRIPTION,
            dataTypes,
            1 ether,
            100,
            12
        );
        
        // Pause study
        vm.prank(investigator);
        researchStudy.pauseStudy(studyId, "Technical issues");
        
        // Verify study is paused
        (,,,,,,, bool isActive,,) = researchStudy.getStudyDetails(studyId);
        assertFalse(isActive);
    }
    
    function testResumeStudy() public {
        // First create and pause study
        vm.prank(investigator);
        uint256 studyId = researchStudy.createStudy(
            INSTITUTION,
            STUDY_TITLE,
            STUDY_DESCRIPTION,
            dataTypes,
            1 ether,
            100,
            12
        );
        
        vm.prank(investigator);
        researchStudy.pauseStudy(studyId, "Technical issues");
        
        // Resume study
        vm.prank(investigator);
        researchStudy.resumeStudy(studyId);
        
        // Verify study is resumed
        (,,,,,,, bool isActive,,) = researchStudy.getStudyDetails(studyId);
        assertTrue(isActive);
    }
    
    function testGetParticipantStudies() public {
        // Create multiple studies and join them
        vm.prank(investigator);
        uint256 studyId1 = researchStudy.createStudy(
            INSTITUTION,
            "Study 1",
            "Description 1",
            dataTypes,
            1 ether,
            100,
            12
        );
        
        vm.prank(investigator);
        uint256 studyId2 = researchStudy.createStudy(
            INSTITUTION,
            "Study 2",
            "Description 2",
            dataTypes,
            2 ether,
            100,
            12
        );
        
        // Join both studies
        vm.startPrank(participant1);
        researchStudy.joinStudy(studyId1, dataTypes);
        researchStudy.joinStudy(studyId2, dataTypes);
        vm.stopPrank();
        
        // Get participant studies
        uint256[] memory participantStudies = researchStudy.getParticipantStudies(participant1);
        
        assertEq(participantStudies.length, 2);
        assertEq(participantStudies[0], studyId1);
        assertEq(participantStudies[1], studyId2);
    }
    
    function testGetInvestigatorStudies() public {
        // Create multiple studies
        vm.startPrank(investigator);
        
        uint256 studyId1 = researchStudy.createStudy(
            INSTITUTION,
            "Study 1",
            "Description 1",
            dataTypes,
            1 ether,
            100,
            12
        );
        
        uint256 studyId2 = researchStudy.createStudy(
            INSTITUTION,
            "Study 2",
            "Description 2",
            dataTypes,
            2 ether,
            100,
            12
        );
        
        vm.stopPrank();
        
        // Get investigator studies
        uint256[] memory investigatorStudies = researchStudy.getInvestigatorStudies(investigator);
        
        assertEq(investigatorStudies.length, 2);
        assertEq(investigatorStudies[0], studyId1);
        assertEq(investigatorStudies[1], studyId2);
    }
    
    function testGetContractStats() public {
        // Create and complete a study
        vm.prank(investigator);
        uint256 studyId = researchStudy.createStudy(
            INSTITUTION,
            STUDY_TITLE,
            STUDY_DESCRIPTION,
            dataTypes,
            1 ether,
            100,
            1
        );
        
        // Fast forward time and complete study
        vm.warp(block.timestamp + 1 weeks + 1);
        vm.prank(investigator);
        researchStudy.completeStudy(studyId);
        
        // Get contract stats
        (uint256 totalStudies, uint256 completedStudies, uint256 totalEarnings) = 
            researchStudy.getContractStats();
        
        assertEq(totalStudies, 1);
        assertEq(completedStudies, 1);
        assertEq(totalEarnings, 0); // No compensation paid yet
    }
    
    function testAddAuthorizedInstitution() public {
        // Add authorized institution
        researchStudy.addAuthorizedInstitution(investigator);
        
        // Verify institution is authorized
        assertTrue(researchStudy.authorizedInstitutions(investigator));
    }
    
    function testRemoveAuthorizedInstitution() public {
        // First add institution
        researchStudy.addAuthorizedInstitution(investigator);
        
        // Remove institution
        researchStudy.removeAuthorizedInstitution(investigator);
        
        // Verify institution is not authorized
        assertFalse(researchStudy.authorizedInstitutions(investigator));
    }
    
    function testStudyInProgress() public {
        // Create study
        vm.prank(investigator);
        uint256 studyId = researchStudy.createStudy(
            INSTITUTION,
            STUDY_TITLE,
            STUDY_DESCRIPTION,
            dataTypes,
            1 ether,
            100,
            12
        );
        
        // Join study
        vm.prank(participant1);
        researchStudy.joinStudy(studyId, dataTypes);
        
        // Try to contribute data (should work during study period)
        vm.prank(participant1);
        researchStudy.contributeData(
            studyId,
            "lab_results",
            "QmTestHash123",
            5
        );
        
        // Verify contribution was recorded
        (,, uint256 totalContributions,) = researchStudy.getParticipantDetails(studyId, participant1);
        assertEq(totalContributions, 1);
    }
    
    function testStudyNotInProgress() public {
        // Create study
        vm.prank(investigator);
        uint256 studyId = researchStudy.createStudy(
            INSTITUTION,
            STUDY_TITLE,
            STUDY_DESCRIPTION,
            dataTypes,
            1 ether,
            100,
            1 // 1 week duration
        );
        
        // Join study
        vm.prank(participant1);
        researchStudy.joinStudy(studyId, dataTypes);
        
        // Fast forward time past end date
        vm.warp(block.timestamp + 1 weeks + 1);
        
        // Try to contribute data (should fail after study period)
        vm.prank(participant1);
        vm.expectRevert("Study is not in progress");
        researchStudy.contributeData(
            studyId,
            "lab_results",
            "QmTestHash123",
            5
        );
    }
}
