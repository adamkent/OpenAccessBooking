#!/usr/bin/env python3
"""
Local development setup script for NHS Appointment Booking System.
Creates local DynamoDB tables and seeds initial data for testing.
"""

import boto3
import json
import os
import sys
import time
from botocore.exceptions import ClientError

class LocalSetup:
    """Sets up local development environment."""
    
    def __init__(self, dynamodb_endpoint='http://localhost:8000'):
        self.dynamodb_endpoint = dynamodb_endpoint
        self.dynamodb = boto3.resource(
            'dynamodb',
            endpoint_url=dynamodb_endpoint,
            region_name='us-east-1',
            aws_access_key_id='local',
            aws_secret_access_key='local'
        )
        
    def create_tables(self):
        """Create local DynamoDB tables."""
        print("🏗️ Creating local DynamoDB tables...")
        
        tables_config = [
            {
                'name': 'local-appointments',
                'key_schema': [
                    {'AttributeName': 'appointment_id', 'KeyType': 'HASH'}
                ],
                'attribute_definitions': [
                    {'AttributeName': 'appointment_id', 'AttributeType': 'S'},
                    {'AttributeName': 'patient_id', 'AttributeType': 'S'},
                    {'AttributeName': 'practice_id', 'AttributeType': 'S'},
                    {'AttributeName': 'appointment_date', 'AttributeType': 'S'}
                ],
                'global_secondary_indexes': [
                    {
                        'IndexName': 'PatientIndex',
                        'KeySchema': [
                            {'AttributeName': 'patient_id', 'KeyType': 'HASH'},
                            {'AttributeName': 'appointment_date', 'KeyType': 'RANGE'}
                        ],
                        'Projection': {'ProjectionType': 'ALL'},
                        'ProvisionedThroughput': {'ReadCapacityUnits': 5, 'WriteCapacityUnits': 5}
                    },
                    {
                        'IndexName': 'PracticeIndex',
                        'KeySchema': [
                            {'AttributeName': 'practice_id', 'KeyType': 'HASH'},
                            {'AttributeName': 'appointment_date', 'KeyType': 'RANGE'}
                        ],
                        'Projection': {'ProjectionType': 'ALL'},
                        'ProvisionedThroughput': {'ReadCapacityUnits': 5, 'WriteCapacityUnits': 5}
                    }
                ]
            },
            {
                'name': 'local-patients',
                'key_schema': [
                    {'AttributeName': 'patient_id', 'KeyType': 'HASH'}
                ],
                'attribute_definitions': [
                    {'AttributeName': 'patient_id', 'AttributeType': 'S'},
                    {'AttributeName': 'nhs_number', 'AttributeType': 'S'}
                ],
                'global_secondary_indexes': [
                    {
                        'IndexName': 'NHSNumberIndex',
                        'KeySchema': [
                            {'AttributeName': 'nhs_number', 'KeyType': 'HASH'}
                        ],
                        'Projection': {'ProjectionType': 'ALL'},
                        'ProvisionedThroughput': {'ReadCapacityUnits': 5, 'WriteCapacityUnits': 5}
                    }
                ]
            },
            {
                'name': 'local-practices',
                'key_schema': [
                    {'AttributeName': 'practice_id', 'KeyType': 'HASH'}
                ],
                'attribute_definitions': [
                    {'AttributeName': 'practice_id', 'AttributeType': 'S'}
                ],
                'global_secondary_indexes': []
            }
        ]
        
        for table_config in tables_config:
            try:
                # Check if table exists
                try:
                    table = self.dynamodb.Table(table_config['name'])
                    table.load()
                    print(f"✓ Table {table_config['name']} already exists")
                    continue
                except ClientError as e:
                    if e.response['Error']['Code'] != 'ResourceNotFoundException':
                        raise
                
                # Create table
                create_params = {
                    'TableName': table_config['name'],
                    'KeySchema': table_config['key_schema'],
                    'AttributeDefinitions': table_config['attribute_definitions'],
                    'BillingMode': 'PROVISIONED',
                    'ProvisionedThroughput': {
                        'ReadCapacityUnits': 5,
                        'WriteCapacityUnits': 5
                    }
                }
                
                if table_config['global_secondary_indexes']:
                    create_params['GlobalSecondaryIndexes'] = table_config['global_secondary_indexes']
                
                table = self.dynamodb.create_table(**create_params)
                
                # Wait for table to be created
                print(f"⏳ Creating table {table_config['name']}...")
                table.wait_until_exists()
                print(f"✓ Table {table_config['name']} created successfully")
                
            except Exception as e:
                print(f"✗ Error creating table {table_config['name']}: {e}")
                return False
        
        return True
    
    def seed_local_data(self):
        """Seed local tables with test data."""
        print("\n🌱 Seeding local test data...")
        
        # Set environment variables for local database
        os.environ['APPOINTMENTS_TABLE'] = 'local-appointments'
        os.environ['PATIENTS_TABLE'] = 'local-patients'
        os.environ['PRACTICES_TABLE'] = 'local-practices'
        os.environ['AWS_REGION'] = 'us-east-1'
        
        # Import and use the existing seeder
        sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src', 'utils'))
        
        try:
            from database import DatabaseManager
            
            # Override the database manager to use local endpoint
            class LocalDatabaseManager(DatabaseManager):
                def __init__(self):
                    self.dynamodb = boto3.resource(
                        'dynamodb',
                        endpoint_url='http://localhost:8000',
                        region_name='us-east-1',
                        aws_access_key_id='local',
                        aws_secret_access_key='local'
                    )
                    self.appointments_table = self.dynamodb.Table('local-appointments')
                    self.patients_table = self.dynamodb.Table('local-patients')
                    self.practices_table = self.dynamodb.Table('local-practices')
            
            # Replace the global db instance
            import database
            database.db = LocalDatabaseManager()
            
            # Import and run the seeder
            from seed_data import DataSeeder
            seeder = DataSeeder('local')
            seeder.db = database.db
            seeder.seed_all()
            
            return True
            
        except Exception as e:
            print(f"✗ Error seeding data: {e}")
            return False
    
    def check_dynamodb_local(self):
        """Check if DynamoDB Local is running."""
        try:
            client = boto3.client(
                'dynamodb',
                endpoint_url=self.dynamodb_endpoint,
                region_name='us-east-1',
                aws_access_key_id='local',
                aws_secret_access_key='local'
            )
            client.list_tables()
            return True
        except Exception:
            return False
    
    def setup_local_environment(self):
        """Complete local environment setup."""
        print("🚀 Setting up NHS Appointment Booking local environment")
        print("=" * 60)
        
        # Check if DynamoDB Local is running
        if not self.check_dynamodb_local():
            print("❌ DynamoDB Local is not running!")
            print("\nTo start DynamoDB Local:")
            print("1. Download from: https://docs.aws.amazon.com/amazondynamodb/latest/developerguide/DynamoDBLocal.html")
            print("2. Run: java -Djava.library.path=./DynamoDBLocal_lib -jar DynamoDBLocal.jar -sharedDb -port 8000")
            print("3. Or use Docker: docker run -p 8000:8000 amazon/dynamodb-local")
            return False
        
        print("✓ DynamoDB Local is running")
        
        # Create tables
        if not self.create_tables():
            print("❌ Failed to create tables")
            return False
        
        # Seed data
        if not self.seed_local_data():
            print("❌ Failed to seed data")
            return False
        
        print("\n" + "=" * 60)
        print("✅ Local environment setup completed!")
        print("\nNext steps:")
        print("1. Copy local-config.env to .env.local")
        print("2. Run: sam local start-api --port 3000 --env-vars .env.local")
        print("3. Test API at: http://localhost:3000")
        print("4. Run tests: python scripts/test_api.py http://localhost:3000")
        
        return True

def main():
    """Main function."""
    import argparse
    
    parser = argparse.ArgumentParser(description='Setup local development environment')
    parser.add_argument('--endpoint', default='http://localhost:8000',
                       help='DynamoDB Local endpoint (default: http://localhost:8000)')
    
    args = parser.parse_args()
    
    try:
        setup = LocalSetup(args.endpoint)
        success = setup.setup_local_environment()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n⏹ Setup interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        sys.exit(1)

if __name__ == '__main__':
    main()
