// SPDX-License-Identifier: MIT
pragma solidity ^0.8.19;

import "../HealthVault.sol";
import "forge-std/Test.sol";

/**
 * @title SimpleTest
 * @dev Simple test to verify contracts compile and basic functionality works
 */
contract SimpleTest is Test {
    
    HealthVault public healthVault;
    
    function setUp() public {
        healthVault = new HealthVault(
            "Test Vault",
            true,
            true,
            "high"
        );
    }
    
    function testVaultCreation() public {
        assertEq(healthVault.vaultName(), "Test Vault");
        assertTrue(healthVault.encryptionEnabled());
        assertTrue(healthVault.zkProofsEnabled());
        assertEq(healthVault.privacyLevel(), "high");
    }
    
    function testCreateRecord() public {
        bytes32 recordId = healthVault.createRecord(
            "lab_results",
            "QmTestHash123",
            "0x1234567890abcdef"
        );
        
        assertTrue(recordId != bytes32(0));
        assertEq(healthVault.recordCount(), 1);
    }
}
