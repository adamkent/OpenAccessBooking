"""
Notification utilities for the NHS appointment booking system.
Handles email and SMS notifications for appointments and reminders.
"""

import boto3
import os
import logging
from typing import Dict, Any, Optional
from datetime import datetime, timezone
from botocore.exceptions import ClientError

logger = logging.getLogger(__name__)

class NotificationManager:
    """Manages email and SMS notifications."""
    
    def __init__(self):
        self.ses_client = boto3.client('ses', region_name=os.getenv('AWS_REGION', 'eu-west-2'))
        self.sns_client = boto3.client('sns', region_name=os.getenv('AWS_REGION', 'eu-west-2'))
        self.from_email = os.getenv('FROM_EMAIL', 'noreply@nhsappointments.nhs.uk')
    
    def send_appointment_confirmation(
        self, 
        patient_email: str, 
        patient_name: str,
        appointment_details: Dict[str, Any]
    ) -> bool:
        """Send appointment confirmation email."""
        try:
            subject = "NHS Appointment Confirmation"
            
            # Format appointment datetime
            appt_datetime = datetime.fromisoformat(
                appointment_details['appointment_datetime'].replace('Z', '+00:00')
            )
            formatted_datetime = appt_datetime.strftime('%A, %d %B %Y at %I:%M %p')
            
            html_body = f"""
            <html>
            <head></head>
            <body>
                <h2>Appointment Confirmation</h2>
                <p>Dear {patient_name},</p>
                
                <p>Your appointment has been confirmed with the following details:</p>
                
                <div style="background-color: #f0f8ff; padding: 15px; border-left: 4px solid #0078d4;">
                    <p><strong>Date & Time:</strong> {formatted_datetime}</p>
                    <p><strong>Type:</strong> {appointment_details.get('appointment_type', '').title()}</p>
                    <p><strong>Duration:</strong> {appointment_details.get('duration_minutes', 30)} minutes</p>
                    {f"<p><strong>Reason:</strong> {appointment_details.get('reason', '')}</p>" if appointment_details.get('reason') else ""}
                    <p><strong>Appointment ID:</strong> {appointment_details['appointment_id']}</p>
                </div>
                
                <h3>Important Information:</h3>
                <ul>
                    <li>Please arrive 10 minutes before your appointment time</li>
                    <li>Bring a valid form of ID and your NHS number if you have it</li>
                    <li>If you need to cancel or reschedule, please do so at least 24 hours in advance</li>
                </ul>
                
                <p>If you have any questions, please contact the practice directly.</p>
                
                <p>Best regards,<br>
                NHS Appointment Service</p>
            </body>
            </html>
            """
            
            text_body = f"""
            Appointment Confirmation
            
            Dear {patient_name},
            
            Your appointment has been confirmed:
            
            Date & Time: {formatted_datetime}
            Type: {appointment_details.get('appointment_type', '').title()}
            Duration: {appointment_details.get('duration_minutes', 30)} minutes
            {f"Reason: {appointment_details.get('reason', '')}" if appointment_details.get('reason') else ""}
            Appointment ID: {appointment_details['appointment_id']}
            
            Important:
            - Arrive 10 minutes early
            - Bring ID and NHS number
            - Cancel/reschedule at least 24 hours in advance
            
            Best regards,
            NHS Appointment Service
            """
            
            response = self.ses_client.send_email(
                Source=self.from_email,
                Destination={'ToAddresses': [patient_email]},
                Message={
                    'Subject': {'Data': subject, 'Charset': 'UTF-8'},
                    'Body': {
                        'Text': {'Data': text_body, 'Charset': 'UTF-8'},
                        'Html': {'Data': html_body, 'Charset': 'UTF-8'}
                    }
                }
            )
            
            logger.info(f"Confirmation email sent to {patient_email}: {response['MessageId']}")
            return True
            
        except ClientError as e:
            logger.error(f"Error sending confirmation email: {e}")
            return False
    
    def send_appointment_reminder(
        self, 
        patient_email: str, 
        patient_name: str,
        appointment_details: Dict[str, Any]
    ) -> bool:
        """Send appointment reminder email."""
        try:
            subject = "NHS Appointment Reminder - Tomorrow"
            
            appt_datetime = datetime.fromisoformat(
                appointment_details['appointment_datetime'].replace('Z', '+00:00')
            )
            formatted_datetime = appt_datetime.strftime('%A, %d %B %Y at %I:%M %p')
            
            html_body = f"""
            <html>
            <head></head>
            <body>
                <h2>Appointment Reminder</h2>
                <p>Dear {patient_name},</p>
                
                <p>This is a reminder that you have an appointment scheduled for tomorrow:</p>
                
                <div style="background-color: #fff3cd; padding: 15px; border-left: 4px solid #ffc107;">
                    <p><strong>Date & Time:</strong> {formatted_datetime}</p>
                    <p><strong>Type:</strong> {appointment_details.get('appointment_type', '').title()}</p>
                    <p><strong>Appointment ID:</strong> {appointment_details['appointment_id']}</p>
                </div>
                
                <p>Please remember to:</p>
                <ul>
                    <li>Arrive 10 minutes before your appointment</li>
                    <li>Bring valid ID and your NHS number</li>
                    <li>Contact the practice if you need to cancel or reschedule</li>
                </ul>
                
                <p>Thank you,<br>
                NHS Appointment Service</p>
            </body>
            </html>
            """
            
            response = self.ses_client.send_email(
                Source=self.from_email,
                Destination={'ToAddresses': [patient_email]},
                Message={
                    'Subject': {'Data': subject, 'Charset': 'UTF-8'},
                    'Body': {'Html': {'Data': html_body, 'Charset': 'UTF-8'}}
                }
            )
            
            logger.info(f"Reminder email sent to {patient_email}: {response['MessageId']}")
            return True
            
        except ClientError as e:
            logger.error(f"Error sending reminder email: {e}")
            return False
    
    def send_appointment_cancellation(
        self, 
        patient_email: str, 
        patient_name: str,
        appointment_details: Dict[str, Any]
    ) -> bool:
        """Send appointment cancellation email."""
        try:
            subject = "NHS Appointment Cancelled"
            
            appt_datetime = datetime.fromisoformat(
                appointment_details['appointment_datetime'].replace('Z', '+00:00')
            )
            formatted_datetime = appt_datetime.strftime('%A, %d %B %Y at %I:%M %p')
            
            html_body = f"""
            <html>
            <head></head>
            <body>
                <h2>Appointment Cancelled</h2>
                <p>Dear {patient_name},</p>
                
                <p>Your appointment has been cancelled:</p>
                
                <div style="background-color: #f8d7da; padding: 15px; border-left: 4px solid #dc3545;">
                    <p><strong>Original Date & Time:</strong> {formatted_datetime}</p>
                    <p><strong>Type:</strong> {appointment_details.get('appointment_type', '').title()}</p>
                    <p><strong>Appointment ID:</strong> {appointment_details['appointment_id']}</p>
                </div>
                
                <p>If you need to book a new appointment, please contact the practice or use the NHS appointment booking system.</p>
                
                <p>Best regards,<br>
                NHS Appointment Service</p>
            </body>
            </html>
            """
            
            response = self.ses_client.send_email(
                Source=self.from_email,
                Destination={'ToAddresses': [patient_email]},
                Message={
                    'Subject': {'Data': subject, 'Charset': 'UTF-8'},
                    'Body': {'Html': {'Data': html_body, 'Charset': 'UTF-8'}}
                }
            )
            
            logger.info(f"Cancellation email sent to {patient_email}: {response['MessageId']}")
            return True
            
        except ClientError as e:
            logger.error(f"Error sending cancellation email: {e}")
            return False
    
    def send_sms_reminder(
        self, 
        phone_number: str, 
        patient_name: str,
        appointment_details: Dict[str, Any]
    ) -> bool:
        """Send SMS appointment reminder."""
        try:
            appt_datetime = datetime.fromisoformat(
                appointment_details['appointment_datetime'].replace('Z', '+00:00')
            )
            formatted_datetime = appt_datetime.strftime('%d/%m/%Y at %H:%M')
            
            message = f"""NHS Appointment Reminder
            
Hello {patient_name}, you have an appointment tomorrow {formatted_datetime}.
            
Please arrive 10 minutes early and bring ID.
            
To cancel/reschedule, contact your practice.
            
Appointment ID: {appointment_details['appointment_id'][:8]}"""
            
            response = self.sns_client.publish(
                PhoneNumber=phone_number,
                Message=message
            )
            
            logger.info(f"SMS reminder sent to {phone_number}: {response['MessageId']}")
            return True
            
        except ClientError as e:
            logger.error(f"Error sending SMS reminder: {e}")
            return False

# Global notification manager instance
notifications = NotificationManager()
