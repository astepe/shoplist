"""
macOS Messages.app integration for sending SMS via AppleScript.
This allows sending SMS through the native Messages app on Mac,
which forwards messages through your iPhone when Text Message Forwarding is enabled.
"""
import subprocess
import json
import os


def send_sms_via_messages_app(phone_number, text):
    """
    Send SMS through macOS Messages.app using AppleScript.
    
    Requirements:
    - macOS with Messages.app
    - iPhone with Text Message Forwarding enabled
    - Phone number must be in E.164 format or standard format
    - RECOMMENDED: Add recipient to Contacts.app first for best reliability
    
    Args:
        phone_number: Phone number in E.164 format (e.g., "+15551234567")
        text: Message text to send
        
    Returns:
        Dictionary with 'success' (bool) and 'error' (str if failed)
        
    Note: Messages.app works most reliably when the recipient is already in Contacts.app.
    If sending fails, try adding the phone number to Contacts first.
    """
    try:
        # AppleScript to send message via Messages.app
        # Messages.app can accept various phone number formats
        # Try to format the number in a way Messages.app recognizes
        
        # Remove + and any formatting for Messages.app
        clean_number = phone_number.replace('+', '').replace(' ', '').replace('-', '').replace('(', '').replace(')', '')
        
        # For US numbers, try different formats that Messages.app might accept
        # Format 1: With country code formatted: "+1 (555) 123-4567"
        # Format 2: Just digits: "15551234567"
        # Format 3: Without country code: "5551234567"
        
        # Try the formatted version first (most likely to work)
        if clean_number.startswith('1') and len(clean_number) == 11:
            # US number with country code - format it nicely
            formatted_number = f"+1 ({clean_number[1:4]}) {clean_number[4:7]}-{clean_number[7:]}"
        elif len(clean_number) == 10:
            # 10-digit US number - add country code
            formatted_number = f"+1 ({clean_number[0:3]}) {clean_number[3:6]}-{clean_number[6:]}"
        else:
            # Try keeping original format
            formatted_number = phone_number
        
        # Escape the text for AppleScript (handle quotes, newlines, etc.)
        escaped_text = text.replace('\\', '\\\\').replace('"', '\\"').replace('\n', '\\n')
        
        # AppleScript command
        # Messages.app requires the phone number to be added as a contact first OR use a different approach
        # Let's try using the "open" URL scheme which is more reliable
        
        # Method 1: Try using Messages URL scheme (most reliable)
        # Format: messages://[phone number]/?body=[message]
        import urllib.parse
        encoded_message = urllib.parse.quote(text)
        url_message = f"messages://{clean_number}/?body={encoded_message}"
        
        # Try URL scheme first (opens Messages.app with pre-filled message)
        try:
            result_url = subprocess.run(
                ['open', url_message],
                capture_output=True,
                text=True,
                timeout=5
            )
            if result_url.returncode == 0:
                # URL scheme opened successfully - user will need to click send in Messages.app
                # But this isn't automatic, so let's try the AppleScript approach
                pass
        except:
            pass
        
        # Method 2: AppleScript with buddy (more reliable than participant)
        # Try multiple formats
        applescript_formats = [
            # Format 1: Just digits with country code
            f'''
            tell application "Messages"
                activate
                set targetService to 1st account whose service type = SMS
                set targetBuddy to buddy "{clean_number}" of targetService
                send "{escaped_text}" to targetBuddy
            end tell
            ''',
            # Format 2: Formatted number
            f'''
            tell application "Messages"
                activate
                set targetService to 1st account whose service type = SMS
                set targetBuddy to buddy "{formatted_number}" of targetService
                send "{escaped_text}" to targetBuddy
            end tell
            ''',
            # Format 3: Using participant with formatted number
            f'''
            tell application "Messages"
                activate
                set targetService to 1st account whose service type = SMS
                set targetBuddy to participant "{formatted_number}" of targetService
                send "{escaped_text}" to targetBuddy
            end tell
            ''',
            # Format 4: Using participant with clean number
            f'''
            tell application "Messages"
                activate
                set targetService to 1st account whose service type = SMS
                set targetBuddy to participant "{clean_number}" of targetService
                send "{escaped_text}" to targetBuddy
            end tell
            '''
        ]
        
        # Try each format until one works
        last_error = None
        for applescript in applescript_formats:
            try:
                result = subprocess.run(
                    ['osascript', '-e', applescript],
                    capture_output=True,
                    text=True,
                    timeout=10
                )
                
                if result.returncode == 0:
                    return {
                        'success': True,
                        'message': 'SMS sent successfully via Messages.app',
                        'method': 'macos_messages'
                    }
                else:
                    # Store error but try next format
                    error_msg = result.stderr.strip() or result.stdout.strip()
                    last_error = error_msg
                    continue
                    
            except subprocess.TimeoutExpired:
                last_error = 'Messages.app command timed out'
                continue
            except Exception as e:
                last_error = str(e)
                continue
        
        # If all formats failed, return error with helpful message
        error_message = f'Messages.app created the message but it failed to send. Last error: {last_error}'
        
        # Add helpful troubleshooting info
        troubleshooting = (
            'Common fixes: 1) Add the phone number to Contacts.app first, '
            '2) Verify Text Message Forwarding is enabled on your iPhone, '
            '3) Try sending manually from Messages.app first to verify SMS forwarding works. '
            'The app will automatically try Twilio as a fallback.'
        )
        
        return {
            'success': False,
            'error': f'{error_message}. {troubleshooting}',
            'can_fallback': True  # Indicate that fallback to Twilio is possible
        }
    
    except Exception as e:
        return {
            'success': False,
            'error': f'Failed to send SMS via Messages.app: {str(e)}'
        }


def check_messages_app_available():
    """
    Check if Messages.app and SMS forwarding are available.
    
    Returns:
        Dictionary with 'available' (bool) and 'reason' (str)
    """
    # Check if running on macOS
    if os.uname().sysname != 'Darwin':
        return {
            'available': False,
            'reason': 'Not running on macOS'
        }
    
    # Check if Messages.app exists (try multiple locations)
    messages_app_paths = [
        '/Applications/Messages.app',
        '/System/Applications/Messages.app',  # macOS Big Sur+
        os.path.expanduser('~/Applications/Messages.app')  # User Applications
    ]
    
    messages_app_exists = any(os.path.exists(path) for path in messages_app_paths)
    
    if not messages_app_exists:
        # Try checking via AppleScript instead (more reliable)
        try:
            applescript_check = '''
            tell application "System Events"
                if exists application process "Messages" then
                    return "exists"
                else
                    try
                        set messagesApp to application "Messages"
                        return "exists"
                    on error
                        return "not_found"
                    end try
                end if
            end tell
            '''
            result = subprocess.run(
                ['osascript', '-e', applescript_check],
                capture_output=True,
                text=True,
                timeout=5
            )
            if 'exists' not in result.stdout:
                return {
                    'available': False,
                    'reason': 'Messages.app not found. Please ensure Messages.app is installed.'
                }
        except:
            return {
                'available': False,
                'reason': 'Could not verify Messages.app installation'
            }
    
    # Try to check if SMS service is available
    try:
        applescript = '''
        tell application "Messages"
            try
                set smsService to 1st account whose service type = SMS
                return "available"
            on error
                return "not_available"
            end try
        end tell
        '''
        
        result = subprocess.run(
            ['osascript', '-e', applescript],
            capture_output=True,
            text=True,
            timeout=5
        )
        
        if result.returncode == 0 and 'available' in result.stdout:
            return {
                'available': True,
                'reason': 'Messages.app and SMS forwarding are configured'
            }
        else:
            return {
                'available': False,
                'reason': 'SMS service not available. Please enable Text Message Forwarding on your iPhone.'
            }
    
    except Exception as e:
        return {
            'available': False,
            'reason': f'Could not check Messages.app: {str(e)}'
        }

