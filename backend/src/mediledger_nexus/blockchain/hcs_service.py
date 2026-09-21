"""
Hedera Consensus Service (HCS) integration for MediLedger Nexus

Provides functionality for:
- Topic creation and management
- Message submission and retrieval
- HCS-10 OpenConvAI agent communication
- Consensus-based data integrity
"""

import json
import logging
from typing import Dict, Any, List, Optional
from datetime import datetime
import uuid

from .hedera_client import HederaClient
from ..utils.formatters import DataFormatter

logger = logging.getLogger(__name__)


class HCSService:
    """
    Service for interacting with Hedera Consensus Service
    
    Handles topic management, message submission, and retrieval
    for consensus-based data storage and AI agent communication.
    """
    
    def __init__(self, hedera_client: Optional[HederaClient] = None):
        """Initialize HCS service"""
        self.client = hedera_client or HederaClient()
        self.formatter = DataFormatter()
        
    def create_topic(self, 
                    topic_memo: str,
                    admin_key: Optional[str] = None,
                    submit_key: Optional[str] = None,
                    auto_renew_period: int = 7776000) -> Dict[str, Any]:
        """
        Create a new HCS topic
        
        Args:
            topic_memo: Memo describing the topic purpose
            admin_key: Optional admin key for topic management
            submit_key: Optional submit key for message submission
            auto_renew_period: Auto-renewal period in seconds (default: 90 days)
            
        Returns:
            Dict containing topic creation information
        """
        try:
            # Mock implementation - replace with actual HCS calls
            topic_id = f"0.0.{datetime.now().microsecond}"
            
            topic_info = {
                "topic_id": topic_id,
                "memo": topic_memo,
                "admin_key": admin_key,
                "submit_key": submit_key,
                "auto_renew_period": auto_renew_period,
                "created_at": datetime.utcnow().isoformat(),
                "sequence_number": 0,
                "running_hash": "initial_hash"
            }
            
            logger.info(f"Created HCS topic: {topic_id}")
            return topic_info
            
        except Exception as e:
            logger.error(f"Failed to create HCS topic: {e}")
            raise
    
    def get_topic_info(self, topic_id: str) -> Dict[str, Any]:
        """
        Get information about an HCS topic
        
        Args:
            topic_id: Topic ID to query
            
        Returns:
            Dict containing topic information
        """
        try:
            # Mock implementation
            topic_info = {
                "topic_id": topic_id,
                "memo": "MediLedger Topic",
                "admin_key": None,
                "submit_key": None,
                "auto_renew_period": 7776000,
                "expiration_time": None,
                "sequence_number": 100,
                "running_hash": "current_running_hash",
                "created_at": "2024-01-01T00:00:00Z"
            }
            
            logger.info(f"Retrieved topic info for: {topic_id}")
            return topic_info
            
        except Exception as e:
            logger.error(f"Failed to get topic info: {e}")
            raise
    
    def submit_message(self, 
                      topic_id: str, 
                      message: Dict[str, Any],
                      chunk_info: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Submit a message to an HCS topic
        
        Args:
            topic_id: Target topic ID
            message: Message data to submit
            chunk_info: Optional chunking information for large messages
            
        Returns:
            Dict containing submission information
        """
        try:
            # Format message for HCS
            formatted_message = self.formatter.format_hcs_message(message, topic_id)
            message_json = json.dumps(formatted_message)
            
            # Mock implementation
            transaction_id = f"{self.client.account_id}@{datetime.now().timestamp()}"
            sequence_number = 101  # Mock sequence number
            
            submission_info = {
                "transaction_id": transaction_id,
                "topic_id": topic_id,
                "sequence_number": sequence_number,
                "consensus_timestamp": datetime.utcnow().isoformat(),
                "message_size": len(message_json),
                "running_hash": "new_running_hash",
                "chunk_info": chunk_info
            }
            
            logger.info(f"Submitted message to topic {topic_id}, sequence: {sequence_number}")
            return submission_info
            
        except Exception as e:
            logger.error(f"Failed to submit message to HCS: {e}")
            raise
    
    def get_topic_messages(self, 
                          topic_id: str,
                          start_time: Optional[datetime] = None,
                          end_time: Optional[datetime] = None,
                          limit: int = 100) -> List[Dict[str, Any]]:
        """
        Retrieve messages from an HCS topic
        
        Args:
            topic_id: Topic ID to query
            start_time: Optional start time filter
            end_time: Optional end time filter
            limit: Maximum number of messages to retrieve
            
        Returns:
            List of message dictionaries
        """
        try:
            # Mock implementation
            messages = []
            
            for i in range(min(limit, 10)):  # Mock 10 messages
                message = {
                    "sequence_number": i + 1,
                    "consensus_timestamp": datetime.utcnow().isoformat(),
                    "topic_id": topic_id,
                    "message": {
                        "type": "test_message",
                        "data": f"Mock message {i + 1}",
                        "timestamp": datetime.utcnow().isoformat()
                    },
                    "running_hash": f"hash_{i + 1}",
                    "payer_account_id": self.client.account_id
                }
                messages.append(message)
            
            logger.info(f"Retrieved {len(messages)} messages from topic {topic_id}")
            return messages
            
        except Exception as e:
            logger.error(f"Failed to get topic messages: {e}")
            raise
    
    def create_ai_agent_topic(self, agent_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Create HCS topic for AI agent communication (HCS-10 standard)
        
        Args:
            agent_data: AI agent configuration data
            
        Returns:
            Dict containing agent topic information
        """
        try:
            agent_id = agent_data.get("agent_id", str(uuid.uuid4()))
            topic_memo = f"HCS-10 AI Agent: {agent_data.get('name', 'Unnamed Agent')}"
            
            # Create main agent topic
            agent_topic = self.create_topic(
                topic_memo=topic_memo,
                submit_key=self.client.account_id  # Agent can submit messages
            )
            
            # Create inbound and outbound communication topics
            inbound_topic = self.create_topic(
                topic_memo=f"HCS-10 Inbound: {agent_id}",
                submit_key=None  # Others can submit to inbound
            )
            
            outbound_topic = self.create_topic(
                topic_memo=f"HCS-10 Outbound: {agent_id}",
                submit_key=self.client.account_id  # Only agent can submit to outbound
            )
            
            # Register agent in HCS-2 registry
            registry_message = {
                "standard": "HCS-10",
                "version": "1.0",
                "agent_id": agent_id,
                "name": agent_data.get("name"),
                "agent_type": agent_data.get("agent_type"),
                "capabilities": agent_data.get("capabilities", []),
                "topics": {
                    "agent_topic": agent_topic["topic_id"],
                    "inbound_topic": inbound_topic["topic_id"],
                    "outbound_topic": outbound_topic["topic_id"]
                },
                "registration_timestamp": datetime.utcnow().isoformat()
            }
            
            # Submit to registry topic (mock)
            registry_topic_id = "0.0.registry"  # Mock registry topic
            self.submit_message(registry_topic_id, registry_message)
            
            agent_info = {
                "agent_id": agent_id,
                "agent_topic": agent_topic,
                "inbound_topic": inbound_topic,
                "outbound_topic": outbound_topic,
                "registry_entry": registry_message
            }
            
            logger.info(f"Created HCS-10 AI agent topics for: {agent_id}")
            return agent_info
            
        except Exception as e:
            logger.error(f"Failed to create AI agent topic: {e}")
            raise
    
    def send_agent_message(self, 
                          from_agent_id: str,
                          to_agent_id: str,
                          message_type: str,
                          message_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Send message between AI agents using HCS-10 protocol
        
        Args:
            from_agent_id: Sending agent ID
            to_agent_id: Receiving agent ID
            message_type: Type of message (diagnosis_request, health_insight, etc.)
            message_data: Message payload
            
        Returns:
            Dict containing message sending information
        """
        try:
            # Create HCS-10 compliant message
            hcs10_message = {
                "standard": "HCS-10",
                "version": "1.0",
                "message_id": str(uuid.uuid4()),
                "from_agent": from_agent_id,
                "to_agent": to_agent_id,
                "message_type": message_type,
                "timestamp": datetime.utcnow().isoformat(),
                "data": message_data,
                "requires_response": message_data.get("requires_response", False)
            }
            
            # Get target agent's inbound topic (mock lookup)
            target_inbound_topic = f"0.0.{to_agent_id}_inbound"
            
            # Submit message to target agent's inbound topic
            submission_info = self.submit_message(target_inbound_topic, hcs10_message)
            
            logger.info(f"Sent HCS-10 message from {from_agent_id} to {to_agent_id}")
            return {
                "message_id": hcs10_message["message_id"],
                "submission_info": submission_info,
                "target_topic": target_inbound_topic
            }
            
        except Exception as e:
            logger.error(f"Failed to send agent message: {e}")
            raise
    
    def get_agent_messages(self, 
                          agent_id: str,
                          message_type: Optional[str] = None,
                          unread_only: bool = True) -> List[Dict[str, Any]]:
        """
        Get messages for an AI agent from its inbound topic
        
        Args:
            agent_id: Agent ID to get messages for
            message_type: Optional filter by message type
            unread_only: Whether to return only unread messages
            
        Returns:
            List of agent messages
        """
        try:
            # Get agent's inbound topic (mock lookup)
            inbound_topic = f"0.0.{agent_id}_inbound"
            
            # Retrieve messages from inbound topic
            all_messages = self.get_topic_messages(inbound_topic)
            
            # Filter messages
            filtered_messages = []
            for msg in all_messages:
                message_data = msg.get("message", {})
                
                # Filter by message type if specified
                if message_type and message_data.get("message_type") != message_type:
                    continue
                
                # Filter by read status if specified
                if unread_only and message_data.get("read", False):
                    continue
                
                filtered_messages.append(msg)
            
            logger.info(f"Retrieved {len(filtered_messages)} messages for agent {agent_id}")
            return filtered_messages
            
        except Exception as e:
            logger.error(f"Failed to get agent messages: {e}")
            raise
    
    def create_connection_topic(self, agent1_id: str, agent2_id: str) -> Dict[str, Any]:
        """
        Create private connection topic between two AI agents
        
        Args:
            agent1_id: First agent ID
            agent2_id: Second agent ID
            
        Returns:
            Dict containing connection topic information
        """
        try:
            connection_id = f"{agent1_id}_{agent2_id}_{uuid.uuid4().hex[:8]}"
            topic_memo = f"HCS-10 Connection: {agent1_id} <-> {agent2_id}"
            
            # Create private topic with both agents as submit keys
            connection_topic = self.create_topic(
                topic_memo=topic_memo,
                submit_key=f"{agent1_id},{agent2_id}"  # Both agents can submit
            )
            
            # Notify both agents of the connection
            connection_message = {
                "standard": "HCS-10",
                "message_type": "connection_established",
                "connection_id": connection_id,
                "participants": [agent1_id, agent2_id],
                "connection_topic": connection_topic["topic_id"],
                "established_at": datetime.utcnow().isoformat()
            }
            
            # Send to both agents' inbound topics
            self.send_agent_message(
                "system", agent1_id, "connection_established", connection_message
            )
            self.send_agent_message(
                "system", agent2_id, "connection_established", connection_message
            )
            
            logger.info(f"Created connection topic between {agent1_id} and {agent2_id}")
            return {
                "connection_id": connection_id,
                "connection_topic": connection_topic,
                "participants": [agent1_id, agent2_id]
            }
            
        except Exception as e:
            logger.error(f"Failed to create connection topic: {e}")
            raise
    
    def update_topic(self, 
                    topic_id: str,
                    new_memo: Optional[str] = None,
                    new_admin_key: Optional[str] = None,
                    new_submit_key: Optional[str] = None,
                    new_auto_renew_period: Optional[int] = None) -> Dict[str, Any]:
        """
        Update HCS topic properties
        
        Args:
            topic_id: Topic ID to update
            new_memo: New topic memo
            new_admin_key: New admin key
            new_submit_key: New submit key
            new_auto_renew_period: New auto-renewal period
            
        Returns:
            Dict containing update information
        """
        try:
            # Mock implementation
            update_info = {
                "topic_id": topic_id,
                "updated_at": datetime.utcnow().isoformat(),
                "changes": {}
            }
            
            if new_memo:
                update_info["changes"]["memo"] = new_memo
            if new_admin_key:
                update_info["changes"]["admin_key"] = new_admin_key
            if new_submit_key:
                update_info["changes"]["submit_key"] = new_submit_key
            if new_auto_renew_period:
                update_info["changes"]["auto_renew_period"] = new_auto_renew_period
            
            logger.info(f"Updated HCS topic: {topic_id}")
            return update_info
            
        except Exception as e:
            logger.error(f"Failed to update topic: {e}")
            raise
    
    def delete_topic(self, topic_id: str) -> Dict[str, Any]:
        """
        Delete an HCS topic
        
        Args:
            topic_id: Topic ID to delete
            
        Returns:
            Dict containing deletion information
        """
        try:
            # Mock implementation
            deletion_info = {
                "topic_id": topic_id,
                "deleted_at": datetime.utcnow().isoformat(),
                "status": "deleted"
            }
            
            logger.info(f"Deleted HCS topic: {topic_id}")
            return deletion_info
            
        except Exception as e:
            logger.error(f"Failed to delete topic: {e}")
            raise
