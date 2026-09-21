// SPDX-License-Identifier: MIT
pragma solidity ^0.8.19;

import "forge-std/Script.sol";
import "../HealthVault.sol";
import "../ConsentManager.sol";
import "../ResearchStudy.sol";
import "../EmergencyAccess.sol";

contract DeployScript is Script {
    function run() external {
        uint256 deployerPrivateKey = vm.envUint("HEDERA_PRIVATE_KEY");
        address deployer = vm.addr(deployerPrivateKey);
        
        console.log("Deploying contracts with account:", deployer);
        console.log("Account balance:", deployer.balance);
        
        vm.startBroadcast(deployerPrivateKey);
        
        // Deploy HealthVault contract
        HealthVault healthVault = new HealthVault(
            "MediLedger Health Vault",
            true,  // encryptionEnabled
            true,  // zkProofsEnabled
            "high" // privacyLevel
        );
        
        // Deploy ConsentManager contract
        ConsentManager consentManager = new ConsentManager();
        
        // Deploy ResearchStudy contract
        ResearchStudy researchStudy = new ResearchStudy();
        
        // Deploy EmergencyAccess contract
        EmergencyAccess emergencyAccess = new EmergencyAccess();
        
        vm.stopBroadcast();
        
        // Log deployment addresses
        console.log("HealthVault deployed at:", address(healthVault));
        console.log("ConsentManager deployed at:", address(consentManager));
        console.log("ResearchStudy deployed at:", address(researchStudy));
        console.log("EmergencyAccess deployed at:", address(emergencyAccess));
        
        // Save addresses to file for backend integration
        string memory addresses = string(abi.encodePacked(
            "HEALTH_VAULT_CONTRACT=", vm.toString(address(healthVault)), "\n",
            "CONSENT_MANAGER_CONTRACT=", vm.toString(address(consentManager)), "\n",
            "RESEARCH_STUDY_CONTRACT=", vm.toString(address(researchStudy)), "\n",
            "EMERGENCY_ACCESS_CONTRACT=", vm.toString(address(emergencyAccess)), "\n"
        ));
        
        vm.writeFile("deployed_addresses.env", addresses);
        console.log("Contract addresses saved to deployed_addresses.env");
    }
}
