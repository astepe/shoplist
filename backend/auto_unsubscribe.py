"""
Automated unsubscribe responder for political text messages.
Monitors incoming SMS messages and automatically replies with STOP or QUIT
when political keywords are detected.

Supports:
- macOS: Reads from Messages.app database, sends via Messages.app or Twilio
- Other platforms: Can use Twilio for sending (requires separate message monitoring)
"""
import sqlite3
import re
import time
import os
import platform
from datetime import datetime, timedelta
from typing import Optional, List, Dict


class AutoUnsubscribeMonitor:
    """Monitor and auto-respond to political text messages."""
    
    # Regex patterns to detect political messages
    POLITICAL_KEYWORDS = [
        r'\b(campaign|candidate|election|vote|voting|poll|polls|ballot|primary|caucus)\b',
        r'\b(democrat|republican|gop|dems|liberal|conservative)\b',
        r'\b(presidential|senate|congress|congressional|mayor|governor)\b',
        r'\b(political action committee|pac|super pac)\b',
        r'\b(endorse|endorsement|fundraiser|fundraising|donate|donation)\b',
        r'\b(volunteer|canvass|knock|doors|phone bank|text bank)\b',
        r'\b(trump|biden|harris|desantis|pence|newsom|abrams|warren|sanders)\b',
        r'\b(support|oppose|defeat|elect|re-elect|reelect)\b',
        r'\b(progressive|moderate|independent|libertarian|green party)\b',
        r'\b(ballot measure|proposition|initiative|referendum)\b',
        r'\b(text.*stop|reply.*stop|unsubscribe|opt.*out|opt-out)\b',
    ]
    
    # Keywords that indicate STOP should be used
    STOP_KEYWORDS = [
        r'\b(stop|unsubscribe|opt.*out|opt-out|remove|end)\b',
        r'\b(reply.*stop|text.*stop|to.*stop)\b',
    ]
    
    # Keywords that indicate QUIT should be used
    QUIT_KEYWORDS = [
        r'\b(quit|end|cancel)\b',
        r'\b(reply.*quit|text.*quit|to.*quit)\b',
    ]
    
    def __init__(self, messages_db_path: Optional[str] = None, use_twilio: bool = False):
        """
        Initialize the monitor.
        
        Args:
            messages_db_path: Path to Messages database. Defaults to ~/Library/Messages/chat.db
            use_twilio: Force use of Twilio instead of Messages.app (useful for non-iPhone platforms)
        """
        if messages_db_path is None:
            messages_db_path = os.path.expanduser('~/Library/Messages/chat.db')
        
        self.messages_db_path = messages_db_path
        self.use_twilio = use_twilio
        self.processed_messages = set()  # Track processed message IDs
        self.political_pattern = re.compile(
            '|'.join(self.POLITICAL_KEYWORDS),
            re.IGNORECASE
        )
        self.stop_pattern = re.compile(
            '|'.join(self.STOP_KEYWORDS),
            re.IGNORECASE
        )
        self.quit_pattern = re.compile(
            '|'.join(self.QUIT_KEYWORDS),
            re.IGNORECASE
        )
    
    def is_political_message(self, text: str) -> bool:
        """Check if message contains political keywords."""
        if not text:
            return False
        return bool(self.political_pattern.search(text))
    
    def get_unsubscribe_command(self, text: str) -> str:
        """
        Determine whether to reply with STOP or QUIT.
        Defaults to STOP if unclear.
        """
        if not text:
            return "STOP"
        
        # Check for explicit QUIT instructions
        if self.quit_pattern.search(text):
            return "QUIT"
        
        # Check for explicit STOP instructions
        if self.stop_pattern.search(text):
            return "STOP"
        
        # Default to STOP (most common)
        return "STOP"
    
    def get_recent_messages(self, since_minutes: int = 5) -> List[Dict]:
        """
        Get recent incoming SMS messages from Messages database.
        
        Args:
            since_minutes: How many minutes back to look for messages
            
        Returns:
            List of message dictionaries with id, text, phone_number, date
        """
        if not os.path.exists(self.messages_db_path):
            raise FileNotFoundError(
                f"Messages database not found at {self.messages_db_path}. "
                "Make sure you have Messages.app set up and have received at least one message."
            )
        
        conn = sqlite3.connect(self.messages_db_path)
        conn.row_factory = sqlite3.Row
        
        try:
            cursor = conn.cursor()
            
            # Calculate cutoff time
            cutoff_time = datetime.now() - timedelta(minutes=since_minutes)
            # Messages database uses nanoseconds since 2001-01-01
            # Convert to nanoseconds since 2001-01-01
            epoch_2001 = datetime(2001, 1, 1)
            cutoff_ns = int((cutoff_time - epoch_2001).total_seconds() * 1_000_000_000)
            
            # Query for recent incoming SMS messages
            # is_from_me = 0 means incoming message
            # text is not null means it has content
            query = """
                SELECT 
                    message.ROWID as message_id,
                    message.text,
                    message.date,
                    message.is_from_me,
                    handle.id as phone_number
                FROM message
                LEFT JOIN handle ON message.handle_id = handle.ROWID
                WHERE 
                    message.date > ?
                    AND message.is_from_me = 0
                    AND message.text IS NOT NULL
                    AND message.text != ''
                    AND handle.id IS NOT NULL
                    AND LENGTH(handle.id) >= 10  -- Filter out invalid phone numbers
                ORDER BY message.date DESC
            """
            
            cursor.execute(query, (cutoff_ns,))
            rows = cursor.fetchall()
            
            messages = []
            for row in rows:
                # Convert date from nanoseconds to datetime
                date_ns = row['date']
                date_seconds = date_ns / 1_000_000_000
                message_date = epoch_2001 + timedelta(seconds=date_seconds)
                
                messages.append({
                    'id': row['message_id'],
                    'text': row['text'],
                    'phone_number': row['phone_number'],
                    'date': message_date,
                    'is_from_me': row['is_from_me']
                })
            
            return messages
        
        finally:
            conn.close()
    
    def send_sms_reply(self, phone_number: str, text: str) -> Dict:
        """
        Send SMS reply using Messages.app or Twilio.
        
        Args:
            phone_number: Phone number to reply to
            text: Message text to send
            
        Returns:
            Dictionary with 'success' (bool) and 'error' (str if failed)
        """
        # Use Twilio if explicitly requested or not on macOS
        if self.use_twilio or platform.system() != 'Darwin':
            return self._send_via_twilio(phone_number, text)
        
        # Try Messages.app first (macOS only)
        try:
            from backend.mac_messages import send_sms_via_messages_app
            result = send_sms_via_messages_app(phone_number, text)
            
            # If Messages.app failed but can fallback, try Twilio
            if not result.get('success') and result.get('can_fallback'):
                print(f"  Messages.app failed, trying Twilio...")
                return self._send_via_twilio(phone_number, text)
            
            return result
        except ImportError:
            # Messages.app not available, fallback to Twilio
            return self._send_via_twilio(phone_number, text)
    
    def _send_via_twilio(self, phone_number: str, text: str) -> Dict:
        """Send SMS via Twilio."""
        try:
            from twilio.rest import Client
        except ImportError:
            return {
                'success': False,
                'error': 'Twilio package not installed. Install with: pip install twilio'
            }
        
        import os
        account_sid = os.environ.get('TWILIO_ACCOUNT_SID')
        auth_token = os.environ.get('TWILIO_AUTH_TOKEN')
        from_number = os.environ.get('TWILIO_PHONE_NUMBER')
        
        if not account_sid or not auth_token:
            return {
                'success': False,
                'error': 'Twilio credentials not configured. Set TWILIO_ACCOUNT_SID and TWILIO_AUTH_TOKEN.'
            }
        
        if not from_number:
            return {
                'success': False,
                'error': 'TWILIO_PHONE_NUMBER not configured.'
            }
        
        try:
            client = Client(account_sid, auth_token)
            message = client.messages.create(
                body=text,
                from_=from_number,
                to=phone_number
            )
            return {
                'success': True,
                'message_sid': message.sid,
                'method': 'twilio'
            }
        except Exception as e:
            return {
                'success': False,
                'error': f'Twilio send failed: {str(e)}'
            }
    
    def process_message(self, message: Dict) -> bool:
        """
        Process a single message and auto-reply if it's political.
        
        Args:
            message: Message dictionary with id, text, phone_number
            
        Returns:
            True if message was processed and replied to, False otherwise
        """
        message_id = message['id']
        text = message.get('text', '')
        phone_number = message.get('phone_number', '')
        
        # Skip if already processed
        if message_id in self.processed_messages:
            return False
        
        # Check if it's a political message
        if not self.is_political_message(text):
            self.processed_messages.add(message_id)  # Mark as processed even if not political
            return False
        
        # Determine unsubscribe command
        unsubscribe_cmd = self.get_unsubscribe_command(text)
        
        # Send auto-reply
        print(f"[{datetime.now()}] Auto-replying {unsubscribe_cmd} to {phone_number}")
        print(f"  Message: {text[:100]}...")
        
        result = self.send_sms_reply(phone_number, unsubscribe_cmd)
        
        if result.get('success'):
            method = result.get('method', 'unknown')
            print(f"  ✓ Successfully sent {unsubscribe_cmd} via {method}")
            self.processed_messages.add(message_id)
            return True
        else:
            print(f"  ✗ Failed to send: {result.get('error', 'Unknown error')}")
            # Don't mark as processed if sending failed - will retry next time
            return False
    
    def run_once(self) -> Dict:
        """
        Check for new messages and process them once.
        
        Returns:
            Dictionary with stats about processed messages
        """
        try:
            messages = self.get_recent_messages(since_minutes=10)
            stats = {
                'total_messages': len(messages),
                'political_messages': 0,
                'replied': 0,
                'failed': 0
            }
            
            for message in messages:
                if self.is_political_message(message['text']):
                    stats['political_messages'] += 1
                    
                    if self.process_message(message):
                        stats['replied'] += 1
                    else:
                        stats['failed'] += 1
            
            return stats
        
        except FileNotFoundError as e:
            print(f"Error: {e}")
            return {'error': str(e)}
        except Exception as e:
            print(f"Error processing messages: {e}")
            return {'error': str(e)}
    
    def run_continuously(self, check_interval: int = 30):
        """
        Continuously monitor for new messages and auto-reply.
        
        Args:
            check_interval: Seconds between checks (default: 30)
        """
        print(f"Starting auto-unsubscribe monitor...")
        print(f"Checking every {check_interval} seconds")
        print(f"Monitoring database: {self.messages_db_path}")
        print("Press Ctrl+C to stop\n")
        
        try:
            while True:
                stats = self.run_once()
                
                if 'error' not in stats:
                    if stats['political_messages'] > 0:
                        print(f"[{datetime.now()}] Processed {stats['political_messages']} political message(s), "
                              f"replied to {stats['replied']}, failed {stats['failed']}")
                
                time.sleep(check_interval)
        
        except KeyboardInterrupt:
            print("\n\nStopping monitor...")


def main():
    """Command-line interface for the auto-unsubscribe monitor."""
    import argparse
    
    parser = argparse.ArgumentParser(
        description='Automatically reply STOP/QUIT to political text messages'
    )
    parser.add_argument(
        '--once',
        action='store_true',
        help='Check once and exit (for testing or cron jobs)'
    )
    parser.add_argument(
        '--interval',
        type=int,
        default=30,
        help='Seconds between checks when running continuously (default: 30)'
    )
    parser.add_argument(
        '--db-path',
        type=str,
        default=None,
        help='Path to Messages database (default: ~/Library/Messages/chat.db)'
    )
    parser.add_argument(
        '--use-twilio',
        action='store_true',
        help='Force use of Twilio instead of Messages.app (useful for non-iPhone platforms)'
    )
    
    args = parser.parse_args()
    
    monitor = AutoUnsubscribeMonitor(messages_db_path=args.db_path, use_twilio=args.use_twilio)
    
    if args.once:
        print("Checking for political messages...\n")
        stats = monitor.run_once()
        if 'error' not in stats:
            print(f"\nSummary:")
            print(f"  Total messages checked: {stats['total_messages']}")
            print(f"  Political messages found: {stats['political_messages']}")
            print(f"  Auto-replied: {stats['replied']}")
            print(f"  Failed: {stats['failed']}")
    else:
        monitor.run_continuously(check_interval=args.interval)


if __name__ == '__main__':
    main()

