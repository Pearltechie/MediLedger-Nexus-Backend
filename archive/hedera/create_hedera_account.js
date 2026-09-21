const { 
    Client, 
    PrivateKey, 
    AccountCreateTransaction, 
    Hbar,
    AccountId
} = require("@hashgraph/sdk");

// Configuration
const NETWORK = "testnet"; // or "mainnet"
const OPERATOR_ID = process.env.HEDERA_OPERATOR_ID;
const OPERATOR_KEY = process.env.HEDERA_OPERATOR_KEY;

if (!OPERATOR_ID || !OPERATOR_KEY) {
    throw new Error("HEDERA_OPERATOR_ID and HEDERA_OPERATOR_KEY must be set");
}

async function createHederaAccount() {
    try {
        // Create client
        const client = Client.forName(NETWORK);
        client.setOperator(AccountId.fromString(OPERATOR_ID), PrivateKey.fromString(OPERATOR_KEY));

        console.log("=== Creating Hedera Account ===");
        console.log(`Network: ${NETWORK}`);
        console.log(`Operator Account: ${OPERATOR_ID}`);

        // Generate new key pair
        const newPrivateKey = PrivateKey.generateED25519();
        const newPublicKey = newPrivateKey.publicKey;

        console.log("\n=== Generated Key Pair ===");
        console.log("Private Key (DER):", newPrivateKey.toStringDer());
        console.log("Public Key (DER):", newPublicKey.toStringDer());

        // Create account transaction
        const accountCreateTransaction = new AccountCreateTransaction()
            .setKey(newPublicKey)
            .setInitialBalance(Hbar.fromTinybars(1000)) // 1000 tinybars initial balance
            .setAccountMemo("MediLedger Nexus Test Account");

        // Execute transaction
        console.log("\n=== Creating Account ===");
        const accountCreateResponse = await accountCreateTransaction.execute(client);
        const accountCreateReceipt = await accountCreateResponse.getReceipt(client);
        const newAccountId = accountCreateReceipt.accountId;

        console.log("✅ Account created successfully!");
        console.log("New Account ID:", newAccountId.toString());
        console.log("Account Balance:", (await client.getAccountBalance(newAccountId)).toString());

        // Save account information
        const accountInfo = {
            accountId: newAccountId.toString(),
            privateKey: newPrivateKey.toStringDer(),
            publicKey: newPublicKey.toStringDer(),
            network: NETWORK,
            createdAt: new Date().toISOString()
        };

        console.log("\n=== Account Information ===");
        console.log(JSON.stringify(accountInfo, null, 2));

        // Save to file
        const fs = require('fs');
        fs.writeFileSync('hedera_account.json', JSON.stringify(accountInfo, null, 2));
        console.log("\n✅ Account information saved to hedera_account.json");

        return accountInfo;

    } catch (error) {
        console.error("❌ Error creating account:", error.message);
        throw error;
    }
}

// Function to generate keys only (without creating account)
function generateKeysOnly() {
    console.log("=== Generating Hedera Keys Only ===");
    
    const privateKey = PrivateKey.generateED25519();
    const publicKey = privateKey.publicKey;

    console.log("Private Key (DER):", privateKey.toStringDer());
    console.log("Public Key (DER):", publicKey.toStringDer());
    console.log("Private Key (Raw):", privateKey.toStringRaw());
    console.log("Public Key (Raw):", publicKey.toStringRaw());

    return {
        privateKey: privateKey.toStringDer(),
        publicKey: publicKey.toStringDer(),
        privateKeyRaw: privateKey.toStringRaw(),
        publicKeyRaw: publicKey.toStringRaw()
    };
}

// Main execution
async function main() {
    const args = process.argv.slice(2);
    
    if (args.includes('--create-account')) {
        await createHederaAccount();
    } else {
        generateKeysOnly();
    }
}

// Run if called directly
if (require.main === module) {
    main().catch(console.error);
}

module.exports = { createHederaAccount, generateKeysOnly };
