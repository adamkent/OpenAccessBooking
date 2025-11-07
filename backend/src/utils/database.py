"""
DynamoDB database utilities and connection management.
Provides centralized database operations for the NHS appointment booking system.
"""

import boto3
import os
import logging
from typing import Dict, List, Optional, Any
from botocore.exceptions import ClientError
from datetime import datetime, timezone

logger = logging.getLogger(__name__)

class DatabaseManager:
    """Centralized DynamoDB operations manager."""
    
    def __init__(self):
        # Configure DynamoDB connection (local or AWS)
        dynamodb_config = {
            'region_name': os.getenv('AWS_REGION', 'eu-west-2')
        }
        
        # Use local endpoint if specified (for local development)
        if os.getenv('DYNAMODB_ENDPOINT'):
            dynamodb_config['endpoint_url'] = os.getenv('DYNAMODB_ENDPOINT')
            # Use dummy credentials for local DynamoDB
            dynamodb_config['aws_access_key_id'] = os.getenv('AWS_ACCESS_KEY_ID', 'local')
            dynamodb_config['aws_secret_access_key'] = os.getenv('AWS_SECRET_ACCESS_KEY', 'local')
        
        self.dynamodb = boto3.resource('dynamodb', **dynamodb_config)
        self.appointments_table = self.dynamodb.Table(os.getenv('APPOINTMENTS_TABLE'))
        self.patients_table = self.dynamodb.Table(os.getenv('PATIENTS_TABLE'))
        self.practices_table = self.dynamodb.Table(os.getenv('PRACTICES_TABLE'))
    
    def create_item(self, table_name: str, item: Dict[str, Any]) -> Dict[str, Any]:
        """Create a new item in the specified table."""
        try:
            table = getattr(self, f"{table_name}_table")
            
            # Add timestamps
            now = datetime.now(timezone.utc).isoformat()
            item['created_at'] = now
            item['updated_at'] = now
            
            response = table.put_item(Item=item)
            logger.info(f"Created item in {table_name}: {item.get('id', 'unknown')}")
            return item
            
        except ClientError as e:
            logger.error(f"Error creating item in {table_name}: {e}")
            raise
    
    def get_item(self, table_name: str, key: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Get an item from the specified table."""
        try:
            table = getattr(self, f"{table_name}_table")
            response = table.get_item(Key=key)
            return response.get('Item')
            
        except ClientError as e:
            logger.error(f"Error getting item from {table_name}: {e}")
            raise
    
    def update_item(self, table_name: str, key: Dict[str, Any], 
                   update_expression: str, expression_values: Dict[str, Any]) -> Dict[str, Any]:
        """Update an item in the specified table."""
        try:
            table = getattr(self, f"{table_name}_table")
            
            # Add updated timestamp
            expression_values[':updated_at'] = datetime.now(timezone.utc).isoformat()
            update_expression += ", updated_at = :updated_at"
            
            response = table.update_item(
                Key=key,
                UpdateExpression=update_expression,
                ExpressionAttributeValues=expression_values,
                ReturnValues="ALL_NEW"
            )
            return response['Attributes']
            
        except ClientError as e:
            logger.error(f"Error updating item in {table_name}: {e}")
            raise
    
    def delete_item(self, table_name: str, key: Dict[str, Any]) -> bool:
        """Delete an item from the specified table."""
        try:
            table = getattr(self, f"{table_name}_table")
            table.delete_item(Key=key)
            logger.info(f"Deleted item from {table_name}: {key}")
            return True
            
        except ClientError as e:
            logger.error(f"Error deleting item from {table_name}: {e}")
            raise
    
    def query_items(self, table_name: str, index_name: Optional[str] = None,
                   key_condition: str = None, expression_values: Dict[str, Any] = None,
                   filter_expression: str = None, limit: int = None) -> List[Dict[str, Any]]:
        """Query items from the specified table."""
        try:
            table = getattr(self, f"{table_name}_table")
            
            query_params = {}
            if key_condition:
                query_params['KeyConditionExpression'] = key_condition
            if expression_values:
                query_params['ExpressionAttributeValues'] = expression_values
            if filter_expression:
                query_params['FilterExpression'] = filter_expression
            if index_name:
                query_params['IndexName'] = index_name
            if limit:
                query_params['Limit'] = limit
            
            response = table.query(**query_params)
            return response.get('Items', [])
            
        except ClientError as e:
            logger.error(f"Error querying items from {table_name}: {e}")
            raise
    
    def scan_items(self, table_name: str, filter_expression: str = None,
                  expression_values: Dict[str, Any] = None, limit: int = None) -> List[Dict[str, Any]]:
        """Scan items from the specified table."""
        try:
            table = getattr(self, f"{table_name}_table")
            
            scan_params = {}
            if filter_expression:
                scan_params['FilterExpression'] = filter_expression
            if expression_values:
                scan_params['ExpressionAttributeValues'] = expression_values
            if limit:
                scan_params['Limit'] = limit
            
            response = table.scan(**scan_params)
            return response.get('Items', [])
            
        except ClientError as e:
            logger.error(f"Error scanning items from {table_name}: {e}")
            raise

# Global database manager instance
db = DatabaseManager()
