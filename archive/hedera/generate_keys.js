const { PrivateKey } = require("@hashgraph/sdk");

// Generate a new ED25519 private key
const privateKey = PrivateKey.generateED25519();
const publicKey = privateKey.publicKey;

console.log("=== Hedera Key Generation ===");
console.log("Private Key (DER):", privateKey.toStringDer());
console.log("Public Key (DER):", publicKey.toStringDer());
console.log("Private Key (Raw):", privateKey.toStringRaw());
console.log("Public Key (Raw):", publicKey.toStringRaw());

// Generate account ID (this would be assigned by Hedera network)
console.log("\n=== Account Information ===");
console.log("Note: Account ID will be assigned by Hedera network when account is created");
console.log("Format: 0.0.XXXXXX");

// Generate multiple key pairs for testing
console.log("\n=== Multiple Key Pairs for Testing ===");
for (let i = 1; i <= 3; i++) {
    const testPrivateKey = PrivateKey.generateED25519();
    const testPublicKey = testPrivateKey.publicKey;
    
    console.log(`\nKey Pair ${i}:`);
    console.log(`  Private: ${testPrivateKey.toStringDer()}`);
    console.log(`  Public:  ${testPublicKey.toStringDer()}`);
}

console.log("\n=== Usage Instructions ===");
console.log("1. Save these keys securely");
console.log("2. Use private key for signing transactions");
console.log("3. Use public key for account creation");
console.log("4. Never share private keys publicly");
console.log("5. Store private keys in environment variables");
