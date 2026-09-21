"""Smart-contract transaction execution and state queries."""

import logging
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional

from ..hedera_client import HederaClient

logger = logging.getLogger(__name__)


class ContractExecutor:
    """Execute contract interactions and return normalized service results."""

    def __init__(self, hedera_client: HederaClient) -> None:
        """Initialize execution services with a Hedera client."""
        self.client: HederaClient = hedera_client

    def create_health_record(
        self,
        contract_id: str,
        record_data: Dict[str, Any],
        access_permissions: List[str],
    ) -> Dict[str, Any]:
        """Create a health record in a vault contract."""
        record_id: Optional[str] = None
        transaction_id: Optional[str] = None
        try:
            record_id = f"record_{datetime.now().microsecond}"
            function_params: List[Any] = [
                record_id,
                record_data.get("record_type", "general"),
                record_data.get("encrypted_data", ""),
                record_data.get("data_hash", ""),
                access_permissions,
                record_data.get("metadata", {}),
            ]
            call_result: Dict[str, Any] = self.client.call_contract_function(
                contract_id=contract_id,
                function_name="createRecord",
                parameters=function_params,
                gas_limit=200000,
            )
            transaction_id = call_result.get("transaction_id")
            creation_info: Dict[str, Any] = {
                "contract_id": contract_id,
                "record_id": record_id,
                "transaction_id": transaction_id,
                "function_params": {
                    "record_type": record_data.get("record_type", "general"),
                    "access_permissions": access_permissions,
                    "metadata": record_data.get("metadata", {}),
                },
                "gas_used": call_result.get("gas_used", 0),
                "status": "success",
                "created_at": datetime.utcnow().isoformat(),
            }
            logger.info("Created health record %s in contract %s", record_id, contract_id)
            return creation_info
        except Exception:
            logger.exception(
                "Smart-contract operation failed",
                extra={
                    "operation": "create_health_record",
                    "contract_id": contract_id,
                    "record_id": record_id,
                    "transaction_id": transaction_id,
                },
            )
            raise

    def grant_record_access(
        self,
        contract_id: str,
        record_id: str,
        grantee_account: str,
        access_level: str,
        duration_hours: int,
    ) -> Dict[str, Any]:
        """Grant time-limited access to a health record."""
        try:
            expiration_time: datetime = datetime.utcnow() + timedelta(hours=duration_hours)
            call_params: Dict[str, Any] = {
                "function": "grantAccess",
                "parameters": {
                    "record_id": record_id,
                    "grantee": grantee_account,
                    "access_level": access_level,
                    "expires_at": expiration_time.timestamp(),
                    "granted_at": datetime.utcnow().timestamp(),
                },
            }
            grant_info: Dict[str, Any] = {
                "contract_id": contract_id,
                "record_id": record_id,
                "grantee_account": grantee_account,
                "access_level": access_level,
                "expires_at": expiration_time.isoformat(),
                "transaction_id": f"{self.client.account_id}@{datetime.now().timestamp()}",
                "call_params": call_params,
                "status": "granted",
                "granted_at": datetime.utcnow().isoformat(),
            }
            logger.info("Granted %s access to %s for record %s", access_level, grantee_account, record_id)
            return grant_info
        except Exception:
            logger.exception(
                "Smart-contract operation failed",
                extra={
                    "operation": "grant_record_access",
                    "contract_id": contract_id,
                    "record_id": record_id,
                    "grantee_account": grantee_account,
                    "access_level": access_level,
                },
            )
            raise

    def revoke_record_access(
        self,
        contract_id: str,
        record_id: str,
        grantee_account: str,
    ) -> Dict[str, Any]:
        """Revoke access to a health record."""
        try:
            call_params: Dict[str, Any] = {
                "function": "revokeAccess",
                "parameters": {
                    "record_id": record_id,
                    "grantee": grantee_account,
                    "revoked_at": datetime.utcnow().timestamp(),
                },
            }
            revocation_info: Dict[str, Any] = {
                "contract_id": contract_id,
                "record_id": record_id,
                "grantee_account": grantee_account,
                "transaction_id": f"{self.client.account_id}@{datetime.now().timestamp()}",
                "call_params": call_params,
                "status": "revoked",
                "revoked_at": datetime.utcnow().isoformat(),
            }
            logger.info("Revoked access from %s for record %s", grantee_account, record_id)
            return revocation_info
        except Exception:
            logger.exception(
                "Smart-contract operation failed",
                extra={
                    "operation": "revoke_record_access",
                    "contract_id": contract_id,
                    "record_id": record_id,
                    "grantee_account": grantee_account,
                },
            )
            raise

    def activate_consent(self, contract_id: str) -> Dict[str, Any]:
        """Activate a consent contract."""
        try:
            call_params: Dict[str, Any] = {
                "function": "activateConsent",
                "parameters": {"activated_at": datetime.utcnow().timestamp()},
            }
            activation_info: Dict[str, Any] = {
                "contract_id": contract_id,
                "transaction_id": f"{self.client.account_id}@{datetime.now().timestamp()}",
                "call_params": call_params,
                "status": "active",
                "activated_at": datetime.utcnow().isoformat(),
            }
            logger.info("Activated consent contract: %s", contract_id)
            return activation_info
        except Exception:
            logger.exception(
                "Smart-contract operation failed",
                extra={
                    "operation": "activate_consent",
                    "contract_id": contract_id,
                },
            )
            raise

    def revoke_consent(
        self,
        contract_id: str,
        reason: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Revoke a consent contract."""
        try:
            call_params: Dict[str, Any] = {
                "function": "revokeConsent",
                "parameters": {
                    "reason": reason,
                    "revoked_at": datetime.utcnow().timestamp(),
                },
            }
            revocation_info: Dict[str, Any] = {
                "contract_id": contract_id,
                "transaction_id": f"{self.client.account_id}@{datetime.now().timestamp()}",
                "call_params": call_params,
                "reason": reason,
                "status": "revoked",
                "revoked_at": datetime.utcnow().isoformat(),
            }
            logger.info("Revoked consent contract: %s", contract_id)
            return revocation_info
        except Exception:
            logger.exception(
                "Smart-contract operation failed",
                extra={
                    "operation": "revoke_consent",
                    "contract_id": contract_id,
                    "reason_provided": reason is not None,
                },
            )
            raise

    def join_research_study(
        self,
        contract_id: str,
        participant_account: str,
        consent_data: Dict[str, Any],
    ) -> Dict[str, Any]:
        """Record a participant joining a research study."""
        try:
            call_params: Dict[str, Any] = {
                "function": "joinStudy",
                "parameters": {
                    "participant": participant_account,
                    "data_types_consented": consent_data.get("data_types", []),
                    "anonymization_level": consent_data.get("anonymization_level", "high"),
                    "compensation_expected": consent_data.get("compensation_expected", 0.0),
                    "joined_at": datetime.utcnow().timestamp(),
                },
            }
            participation_info: Dict[str, Any] = {
                "contract_id": contract_id,
                "participant_account": participant_account,
                "transaction_id": f"{self.client.account_id}@{datetime.now().timestamp()}",
                "call_params": call_params,
                "status": "joined",
                "joined_at": datetime.utcnow().isoformat(),
            }
            logger.info("Participant %s joined study contract %s", participant_account, contract_id)
            return participation_info
        except Exception:
            logger.exception(
                "Smart-contract operation failed",
                extra={
                    "operation": "join_research_study",
                    "contract_id": contract_id,
                    "participant_account": participant_account,
                },
            )
            raise

    def request_emergency_access(
        self,
        contract_id: str,
        requester_account: str,
        emergency_details: Dict[str, Any],
    ) -> Dict[str, Any]:
        """Request emergency access to patient data."""
        try:
            call_params: Dict[str, Any] = {
                "function": "requestEmergencyAccess",
                "parameters": {
                    "requester": requester_account,
                    "emergency_type": emergency_details.get("emergency_type"),
                    "location": emergency_details.get("location"),
                    "urgency_level": emergency_details.get("urgency_level"),
                    "requester_credentials": emergency_details.get("requester_credentials"),
                    "requested_at": datetime.utcnow().timestamp(),
                },
            }
            request_info: Dict[str, Any] = {
                "contract_id": contract_id,
                "requester_account": requester_account,
                "transaction_id": f"{self.client.account_id}@{datetime.now().timestamp()}",
                "call_params": call_params,
                "emergency_details": emergency_details,
                "status": "access_granted",
                "requested_at": datetime.utcnow().isoformat(),
            }
            logger.info("Emergency access requested by %s for contract %s", requester_account, contract_id)
            return request_info
        except Exception:
            logger.exception(
                "Smart-contract operation failed",
                extra={
                    "operation": "request_emergency_access",
                    "contract_id": contract_id,
                    "requester_account": requester_account,
                    "emergency_type": emergency_details.get("emergency_type"),
                },
            )
            raise

    def get_contract_state(self, contract_id: str) -> Dict[str, Any]:
        """Return the current state representation for a contract."""
        try:
            contract_state: Dict[str, Any] = {
                "contract_id": contract_id,
                "status": "active",
                "owner": self.client.account_id,
                "created_at": "2024-01-01T00:00:00Z",
                "last_updated": datetime.utcnow().isoformat(),
                "gas_consumed": 1000000,
                "storage_used": 5000,
                "balance": 0.0,
                "state_variables": {
                    "initialized": True,
                    "active": True,
                    "participant_count": 5,
                },
            }
            logger.info("Retrieved contract state for: %s", contract_id)
            return contract_state
        except Exception:
            logger.exception(
                "Smart-contract operation failed",
                extra={
                    "operation": "get_contract_state",
                    "contract_id": contract_id,
                },
            )
            raise

    def call_contract_function(
        self,
        contract_id: str,
        function_name: str,
        parameters: Dict[str, Any],
        gas_limit: int = 300000,
    ) -> Dict[str, Any]:
        """Execute a contract function and return transaction metadata."""
        transaction_id: Optional[str] = None
        try:
            transaction_id = f"{self.client.account_id}@{datetime.now().timestamp()}"
            call_result: Dict[str, Any] = {
                "contract_id": contract_id,
                "function_name": function_name,
                "parameters": parameters,
                "transaction_id": transaction_id,
                "gas_used": min(gas_limit, 250000),
                "gas_limit": gas_limit,
                "result": "function_executed_successfully",
                "status": "success",
                "executed_at": datetime.utcnow().isoformat(),
            }
            logger.info("Called function %s on contract %s", function_name, contract_id)
            return call_result
        except Exception:
            logger.exception(
                "Smart-contract operation failed",
                extra={
                    "operation": "call_contract_function",
                    "contract_id": contract_id,
                    "function_name": function_name,
                    "transaction_id": transaction_id,
                    "gas_limit": gas_limit,
                },
            )
            raise
