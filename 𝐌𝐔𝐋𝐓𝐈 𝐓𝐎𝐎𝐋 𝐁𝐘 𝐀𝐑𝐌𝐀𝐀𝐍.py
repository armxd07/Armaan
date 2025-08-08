import os
import requests
import re
import time
import random
import sys
import threading
from colorama import init, Fore, Style, Back
from queue import Queue

# Initialize colorama for colored output
init(autoreset=True)

class InstagramSession:
    def __init__(self, username, password, session_id):
        self.session = requests.Session()
        self.username = username
        self.password = password
        self.session_id = session_id
        self.success_count = 0
        self.failure_count = 0
        self.csrftoken = None
        self.cookies = None
        self.lock = threading.Lock()
        self.is_logged_in = False
        
    def login(self):
        """Login to Instagram using username and password"""
        print(f"{Fore.YELLOW}🔄 Session {self.session_id}: Logging in as {self.username}...{Style.RESET_ALL}")
        
        try:
            # Get initial page to get CSRF token
            response = self.session.get("https://www.instagram.com/")
            csrf_token = re.search(r'"csrf_token":"(.*?)"', response.text).group(1)
            
            # Prepare login data
            login_data = {
                'username': self.username,
                'enc_password': f'#PWD_INSTAGRAM_BROWSER:0:{int(time.time())}:{self.password}',
                'queryParams': {},
                'optIntoOneTap': 'false',
                'stopDeletion': 'false',
                'trustedDevice': 'false',
            }
            
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
                'X-CSRFToken': csrf_token,
                'X-Requested-With': 'XMLHttpRequest',
                'Referer': 'https://www.instagram.com/',
            }
            
            # Send login request
            response = self.session.post(
                "https://www.instagram.com/accounts/login/ajax/",
                headers=headers,
                data=login_data
            )
            
            if response.json().get('authenticated'):
                print(f"{Fore.GREEN}✅ Session {self.session_id}: Login successful!{Style.RESET_ALL}")
                self.csrftoken = csrf_token
                self.cookies = self.session.cookies.get_dict()
                self.is_logged_in = True
                return True
            else:
                print(f"{Fore.RED}❌ Session {self.session_id}: Login failed! Check credentials.{Style.RESET_ALL}")
                return False
        except Exception as e:
            print(f"{Fore.RED}❌ Session {self.session_id}: Login error: {str(e)}{Style.RESET_ALL}")
            return False
            
    def get_user_id(self, username):
        print(f"{Fore.YELLOW}🔍 Session {self.session_id}: Getting user ID for {username}...{Style.RESET_ALL}")
        url = f'https://www.instagram.com/api/v1/users/web_profile_info/?username={username}'
        headers = {'x-ig-app-id': '936619743392459'}
        try:
            response = self.session.get(url, headers=headers)
            user_data = response.json().get('data', {}).get('user', {})
            user_id = user_data.get('id')
            print(f"{Fore.GREEN}✅ Session {self.session_id}: User ID found: {user_id}{Style.RESET_ALL}")
            return user_id
        except Exception as e:
            print(f'{Fore.RED}❌ Session {self.session_id}: Error getting user ID: {str(e)}{Style.RESET_ALL}')
            return None
        
    def get_story_id(self, user_id):
        print(f"{Fore.YELLOW}📷 Session {self.session_id}: Fetching story information...{Style.RESET_ALL}")
        headers = {
            'accept-language': 'en-US,en;q=0.9',
            'User-Agent': 'Mozilla/5.0 (Linux; Android 12; X) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Mobile Safari/537.36',
            'x-asbd-id': str(random.randint(30000, 79999)),
            'x-csrftoken': self.csrftoken,
            'x-ig-app-id': str(random.randint(1000,3337)),
            'x-ig-www-claim': 'hmac.AR1qzeEVPBuPPsJxBMlPlU19lLRm0LG3bSnly_p3mz0aRW2P',
            'x-instagram-ajax': str(random.randint(100, 3939)),
            'x-requested-with': 'XMLHttpRequest'
        }    	
        
        data = {
            'fb_api_req_friendly_name': 'PolarisStoriesV3ReelPageGalleryQuery',
            'variables': f'{{"initial_reel_id":"{user_id}","reel_ids":["{user_id}","65467266760"],"first":1}}',
            'server_timestamps': 'true',
            'doc_id': '8481088891928753'
        }
        
        try:
            response = self.session.post(
                'https://www.instagram.com/graphql/query',
                cookies=self.cookies,
                headers=headers,
                data=data
            ).text   
            
            if 'organic_tracking_token' in response:
                pattern = r'"pk":"(\d{19})"'
                match = re.search(pattern, response)
                if match:
                    story_id = match.group(1)
                    print(f"{Fore.GREEN}✅ Session {self.session_id}: Story ID found: {story_id}{Style.RESET_ALL}")
                    return story_id
            print(f'{Fore.RED}❌ Session {self.session_id}: No stories found or account is private{Style.RESET_ALL}')
            return None
        except Exception as e:
            print(f'{Fore.RED}❌ Session {self.session_id}: Error getting story ID: {str(e)}{Style.RESET_ALL}')
            return None
    
    def get_post_id(self, user_id):
        print(f"{Fore.YELLOW}📸 Session {self.session_id}: Fetching post information...{Style.RESET_ALL}")
        headers = {
            'accept-language': 'en-US,en;q=0.9',
            'User-Agent': 'Mozilla/5.0 (Linux; Android 12; X) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Mobile Safari/537.36',
            'x-asbd-id': str(random.randint(30000, 79999)),
            'x-csrftoken': self.csrftoken,
            'x-ig-app-id': str(random.randint(1000,3337)),
            'x-ig-www-claim': 'hmac.AR1qzeEVPBuPPsJxBMlPlU19lLRm0LG3bSnly_p3mz0aRW2P',
            'x-instagram-ajax': str(random.randint(100, 3939)),
            'x-requested-with': 'XMLHttpRequest'
        }    	
        
        data = {
            'fb_api_req_friendly_name': 'PolarisProfileFeedQuery',
            'variables': f'{{"id":"{user_id}","first":1}}',
            'server_timestamps': 'true',
            'doc_id': '8481088891928753'
        }
        
        try:
            response = self.session.post(
                'https://www.instagram.com/graphql/query',
                cookies=self.cookies,
                headers=headers,
                data=data
            ).text   
            
            if 'shortcode' in response:
                pattern = r'"shortcode":"([^"]+)"'
                match = re.search(pattern, response)
                if match:
                    post_id = match.group(1)
                    print(f"{Fore.GREEN}✅ Session {self.session_id}: Post ID found: {post_id}{Style.RESET_ALL}")
                    return post_id
            print(f'{Fore.RED}❌ Session {self.session_id}: No posts found or account is private{Style.RESET_ALL}')
            return None
        except Exception as e:
            print(f'{Fore.RED}❌ Session {self.session_id}: Error getting post ID: {str(e)}{Style.RESET_ALL}')
            return None
    
    def get_report_info(self, object_id, object_type):    
        print(f"{Fore.YELLOW}📋 Session {self.session_id}: Getting report information for {object_type}...{Style.RESET_ALL}")
        headers = {
            'accept-language': 'en-US,en;q=0.9',
            'User-Agent': 'Mozilla/5.0 (Linux; Android 12; X) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Mobile Safari/537.36',
            'x-asbd-id': str(random.randint(30000, 79999)),
            'x-csrftoken': self.csrftoken,
            'x-ig-app-id': str(random.randint(1000,3337)),
            'x-ig-www-claim': 'hmac.AR1qzeEVPBuPPsJxBMlPlU19lLRm0LG3bSnly_p3mz0aRW2P',
            'x-instagram-ajax': str(random.randint(100, 3939)),
            'x-requested-with': 'XMLHttpRequest'
        }
        
        # Different container_module based on object type
        container_modules = {
            'story': 'StoriesPage',
            'post': 'feed_timeline',
            'account': 'profile'
        }
        
        data = {
            'container_module': container_modules.get(object_type, 'feed_timeline'),
            'entry_point': '1',
            'location': '4',
            'object_id': object_id,
            'object_type': '1',
            'frx_prompt_request_type': '1'
        }
        
        try:
            response = self.session.post(
                'https://www.instagram.com/api/v1/web/reports/get_frx_prompt/',
                headers=headers,
                data=data,
                cookies=self.cookies
            )    
            
            response_json = response.json()
            report_info = response_json.get('response', {}).get('report_info', {})
            context = response_json.get('response', {}).get('context', {})
            object_id = report_info.get("object_id", "").strip('"')       
            print(f"{Fore.GREEN}✅ Session {self.session_id}: Report information retrieved{Style.RESET_ALL}")
            return object_id, context
        except Exception as e:
            print(f'{Fore.RED}❌ Session {self.session_id}: Error getting report info: {str(e)}{Style.RESET_ALL}')
            return None, None
        
    def submit_report(self, object_id, context, report_reason='ig_i_dont_like_it_v3', object_type='story'):
        headers = {
            'accept-language': 'en-US,en;q=0.9',
            'User-Agent': 'Mozilla/5.0 (Linux; Android 12; X) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Mobile Safari/537.36',
            'x-asbd-id': str(random.randint(30000, 79999)),
            'x-csrftoken': self.csrftoken,
            'x-ig-app-id': str(random.randint(1000,3337)),
            'x-ig-www-claim': 'hmac.AR1qzeEVPBuPPsJxBMlPlU19lLRm0LG3bSnly_p3mz0aRW2P',
            'x-instagram-ajax': str(random.randint(100, 3939)),
            'x-requested-with': 'XMLHttpRequest'
        }
        
        # Different container_module based on object type
        container_modules = {
            'story': 'StoriesPage',
            'post': 'feed_timeline',
            'account': 'profile'
        }
        
        data = {
            'container_module': container_modules.get(object_type, 'feed_timeline'),
            'entry_point': '1',
            'location': '4',
            'object_id': object_id,
            'object_type': '1',
            'context': context,
            'selected_tag_types': f'["{report_reason}"]',
            'frx_prompt_request_type': '2',
        }
    
        try:
            response = self.session.post(
                'https://www.instagram.com/api/v1/web/reports/get_frx_prompt/',
                headers=headers,
                data=data,
                cookies=self.cookies
            )       
            
            if '"text":"Done"' in response.text:
                with self.lock:
                    self.success_count += 1
                print(f"{Fore.GREEN}✅ Session {self.session_id}: Report sent successfully! (Total: {self.success_count}){Style.RESET_ALL}")
                return True
            else:
                with self.lock:
                    self.failure_count += 1
                print(f"{Fore.RED}❌ Session {self.session_id}: Report failed! (Total failures: {self.failure_count}){Style.RESET_ALL}")
                if 'Try Again Later' in response.text:
                    print(f"{Fore.YELLOW}⚠️ Session {self.session_id}: Rate limited. Consider increasing delay.{Style.RESET_ALL}")
                return False
        except Exception as e:
            with self.lock:
                self.failure_count += 1
            print(f"{Fore.RED}❌ Session {self.session_id}: Error submitting report: {str(e)}{Style.RESET_ALL}")
            return False

class InstagramReporter:
    def __init__(self):
        self.sessions = []
        self.display_banner()
        self.main_menu()
        
    def display_banner(self):
        banner = """
╔══════════════════════════════════════════════════════════════╗⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢠⠀⠀⠀⠀⠀⠀⠀⠀⡀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
⢸⣄⠀⠀⠀⠀⠀⠀⠀⠀⠈⣧⡀⠀⠀⠀⠀⢀⣼⠀⠀⠀⠀⠀⠀⠀⠀⠀⣠⠂
⠀⣿⣧⣀⡀⠀⠀⠀⠀⠀⠀⣿⣷⡀⠀⠀⢀⣾⡟⠀⠀⠀⠀⠀⠀⢀⣀⣴⣿⠀
⠀⣿⣿⣿⣿⣿⣷⣶⣤⣤⠀⢸⣿⣿⣿⣿⣿⣿⡇⠀⣠⣤⣶⣶⣿⣿⣿⣿⡟⠀
⠀⢹⣿⣿⣤⣈⣉⠛⠛⠿⠆⠸⣿⣷⠀⠀⣾⣿⠀⠸⠿⠟⠛⠋⣉⣁⣿⣿⡇⠀
⠀⢸⣿⣿⡟⠛⠿⠿⣷⣶⡄⠀⣿⣿⣇⣸⣿⡟⠀⣤⣴⣶⡾⠿⠟⢻⣿⣿⠁⠀
⠀⠘⣿⣿⣿⣷⣶⣤⣤⣀⠁⠀⠻⣿⣿⣿⣿⠇⠀⠉⣁⣠⣤⣴⣶⣾⣿⡿⠀⠀
⠀⠀⠈⢿⣿⡿⢿⣿⣿⣿⣿⣷⣄⠈⠻⠟⠁⣠⣾⣿⣿⣿⣿⣿⣿⣿⠟⠁⠀⠀
⠀⠀⣧⡀⠻⣿⣄⠈⠉⠛⠛⠿⢿⣷⣄⣴⣾⡿⠿⠟⠛⠉⢉⣴⣿⠋⢠⡎⠀⠀
⠀⠀⣿⣷⡄⠘⢿⣷⣄⠀⠀⠀⢠⣿⣿⣿⣧⠀⠀⠀⢀⣴⣿⡟⠁⣰⣿⡇⠀⠀
⠀⠀⢻⣿⣿⣦⠈⢻⣿⣷⣄⢀⣿⣿⣿⣿⣿⣧⠀⣰⣿⣿⠏⢀⣾⣿⣿⠇⠀⠀
⠀⠀⢸⣿⣿⣿⣷⡀⠙⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⡿⠁⣠⣿⣿⣿⣿⠀⠀⠀
⠀⠀⢸⣿⣿⣿⣿⣿⣄⠈⢿⣿⣿⣿⣿⣿⣿⣿⣿⠟⢀⣴⣿⣿⣿⣿⣿⠀⠀⠀
⠀⠀⠘⠿⣿⣿⣿⣿⣿⣧⡀⠻⣿⣿⣿⣿⣿⡿⠃⢠⣾⣿⣿⣿⣿⣿⠏⠀⠀⠀
⠀⠀⠀⠀⠀⠉⠙⠻⢿⣿⣷⡄⠘⢿⣿⣿⠟⠀⣴⣿⣿⠿⠟⠋⠁⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠈⠉⠛⠦⠈⠻⠋⠀⠞⠋⠉⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
║                                                              ║
║                 Instagram Multi-Reporter Tool              ║
║                         by ARMAAN                           ║
║              Story/Post/Account Reporting Edition          ║
║                 Multi-Session Login (10+)                  ║
╚══════════════════════════════════════════════════════════════╝
        """
        print(f"{Fore.MAGENTA}{banner}{Style.RESET_ALL}")
        print(f"{Fore.YELLOW}{'='*60}{Style.RESET_ALL}")
        
    def main_menu(self):
        while True:
            print(f"\n{Fore.CYAN}📋 Main Menu:{Style.RESET_ALL}")
            print(f"{Fore.WHITE}1. Mass Reporting (Multiple Targets){Style.RESET_ALL}")
            print(f"{Fore.WHITE}2. Single Target Reporting{Style.RESET_ALL}")
            print(f"{Fore.WHITE}3. Account Management (Login/Logout){Style.RESET_ALL}")
            print(f"{Fore.WHITE}4. Exit{Style.RESET_ALL}")
            
            choice = input(f"{Fore.CYAN}Enter your choice (1-4): {Style.RESET_ALL}")
            
            if choice == '1':
                self.mass_reporting_menu()
            elif choice == '2':
                self.single_target_reporting()
            elif choice == '3':
                self.account_management()
            elif choice == '4':
                print(f"{Fore.YELLOW}👋 Exiting...{Style.RESET_ALL}")
                sys.exit(0)
            else:
                print(f"{Fore.RED}❌ Invalid choice. Please try again.{Style.RESET_ALL}")
    
    def mass_reporting_menu(self):
        print(f"\n{Fore.CYAN}📋 Mass Reporting Menu:{Style.RESET_ALL}")
        print(f"{Fore.WHITE}1. Report Stories{Style.RESET_ALL}")
        print(f"{Fore.WHITE}2. Report Posts{Style.RESET_ALL}")
        print(f"{Fore.WHITE}3. Report Accounts{Style.RESET_ALL}")
        print(f"{Fore.WHITE}4. Back to Main Menu{Style.RESET_ALL}")
        
        choice = input(f"{Fore.CYAN}Enter your choice (1-4): {Style.RESET_ALL}")
        
        if choice == '1':
            self.start_mass_reporting('story')
        elif choice == '2':
            self.start_mass_reporting('post')
        elif choice == '3':
            self.start_mass_reporting('account')
        elif choice == '4':
            return
        else:
            print(f"{Fore.RED}❌ Invalid choice. Please try again.{Style.RESET_ALL}")
            self.mass_reporting_menu()
    
    def single_target_reporting(self):
        print(f"\n{Fore.CYAN}📋 Single Target Reporting Menu:{Style.RESET_ALL}")
        print(f"{Fore.WHITE}1. Report Story{Style.RESET_ALL}")
        print(f"{Fore.WHITE}2. Report Post{Style.RESET_ALL}")
        print(f"{Fore.WHITE}3. Report Account{Style.RESET_ALL}")
        print(f"{Fore.WHITE}4. Back to Main Menu{Style.RESET_ALL}")
        
        choice = input(f"{Fore.CYAN}Enter your choice (1-4): {Style.RESET_ALL}")
        
        if choice == '1':
            self.start_single_target_reporting('story')
        elif choice == '2':
            self.start_single_target_reporting('post')
        elif choice == '3':
            self.start_single_target_reporting('account')
        elif choice == '4':
            return
        else:
            print(f"{Fore.RED}❌ Invalid choice. Please try again.{Style.RESET_ALL}")
            self.single_target_reporting()
    
    def account_management(self):
        print(f"\n{Fore.CYAN}📋 Account Management Menu:{Style.RESET_ALL}")
        print(f"{Fore.WHITE}1. Login to Accounts{Style.RESET_ALL}")
        print(f"{Fore.WHITE}2. View Active Sessions{Style.RESET_ALL}")
        print(f"{Fore.WHITE}3. Logout All Sessions{Style.RESET_ALL}")
        print(f"{Fore.WHITE}4. Back to Main Menu{Style.RESET_ALL}")
        
        choice = input(f"{Fore.CYAN}Enter your choice (1-4): {Style.RESET_ALL}")
        
        if choice == '1':
            self.setup_sessions()
        elif choice == '2':
            self.view_active_sessions()
        elif choice == '3':
            self.logout_all_sessions()
        elif choice == '4':
            return
        else:
            print(f"{Fore.RED}❌ Invalid choice. Please try again.{Style.RESET_ALL}")
            self.account_management()
    
    def setup_sessions(self):
        print(f"{Fore.CYAN}Setting up Instagram sessions...{Style.RESET_ALL}")
        
        # Try to load accounts from file
        accounts = []
        if os.path.exists('accounts.txt'):
            try:
                with open('accounts.txt', 'r') as f:
                    for line in f:
                        if ':' in line:
                            username, password = line.strip().split(':', 1)
                            accounts.append((username, password))
                print(f"{Fore.GREEN}✅ Loaded {len(accounts)} accounts from accounts.txt{Style.RESET_ALL}")
            except Exception as e:
                print(f"{Fore.RED}❌ Error loading accounts: {str(e)}{Style.RESET_ALL}")
                accounts = []
        
        # Ask how many sessions to set up
        try:
            num_sessions = int(input(f"{Fore.CYAN}How many sessions to set up? (1-50): {Style.RESET_ALL}"))
            num_sessions = min(max(1, num_sessions), 50)
        except ValueError:
            print(f"{Fore.YELLOW}Invalid input. Using 10 sessions.{Style.RESET_ALL}")
            num_sessions = 10
        
        # If we don't have enough accounts, ask for input
        while len(accounts) < num_sessions:
            print(f"{Fore.YELLOW}Need {num_sessions - len(accounts)} more accounts...{Style.RESET_ALL}")
            username = input(f"{Fore.CYAN}Enter Instagram username {len(accounts)+1}/{num_sessions}: {Style.RESET_ALL}")
            password = input(f"{Fore.CYAN}Enter password (default: armaanpapa): {Style.RESET_ALL}") or "armaanpapa"
            accounts.append((username, password))
            
            # Save to file for future use
            with open('accounts.txt', 'a') as f:
                f.write(f"{username}:{password}\n")
            print(f"{Fore.GREEN}✅ Account saved to accounts.txt{Style.RESET_ALL}")
        
        # Create and login sessions
        self.sessions = []
        successful_logins = 0
        
        for i, (username, password) in enumerate(accounts[:num_sessions]):
            session = InstagramSession(username, password, i+1)
            if session.login():
                self.sessions.append(session)
                successful_logins += 1
            else:
                print(f"{Fore.RED}❌ Session {i+1} failed to login{Style.RESET_ALL}")
                
        print(f"{Fore.GREEN}✅ {successful_logins} out of {num_sessions} sessions successfully logged in{Style.RESET_ALL}")
        
        if successful_logins < num_sessions:
            print(f"{Fore.YELLOW}⚠️ Only {successful_logins} sessions are available for reporting{Style.RESET_ALL}")
        
        # Show login summary
        print(f"\n{Fore.CYAN}Login Summary:{Style.RESET_ALL}")
        print(f"{Fore.GREEN}Successful: {successful_logins}{Style.RESET_ALL}")
        print(f"{Fore.RED}Failed: {num_sessions - successful_logins}{Style.RESET_ALL}")
        
        # Ask if user wants to retry failed logins
        if successful_logins < num_sessions:
            retry = input(f"{Fore.YELLOW}Do you want to retry failed logins? (y/n): {Style.RESET_ALL}")
            if retry.lower() == 'y':
                self.retry_failed_logins(accounts, num_sessions)
    
    def retry_failed_logins(self, accounts, num_sessions):
        print(f"\n{Fore.CYAN}Retrying failed logins...{Style.RESET_ALL}")
        
        # Find which accounts failed
        successful_usernames = [session.username for session in self.sessions]
        failed_accounts = []
        
        for i, (username, password) in enumerate(accounts[:num_sessions]):
            if username not in successful_usernames:
                failed_accounts.append((username, password, i+1))
        
        # Retry each failed account
        for username, password, session_id in failed_accounts:
            print(f"{Fore.YELLOW}Retrying login for {username} (Session {session_id})...{Style.RESET_ALL}")
            
            # Ask if user wants to update credentials
            update = input(f"{Fore.CYAN}Update credentials for {username}? (y/n): {Style.RESET_ALL}")
            if update.lower() == 'y':
                username = input(f"{Fore.CYAN}Enter new username: {Style.RESET_ALL}")
                password = input(f"{Fore.CYAN}Enter new password: {Style.RESET_ALL}")
                
                # Update the accounts list
                for i, (u, p) in enumerate(accounts):
                    if u == username:
                        accounts[i] = (username, password)
                        break
                
                # Update the file
                with open('accounts.txt', 'w') as f:
                    for u, p in accounts:
                        f.write(f"{u}:{p}\n")
            
            # Try to login again
            session = InstagramSession(username, password, session_id)
            if session.login():
                self.sessions.append(session)
                print(f"{Fore.GREEN}✅ Retry successful for {username}{Style.RESET_ALL}")
            else:
                print(f"{Fore.RED}❌ Retry failed for {username}{Style.RESET_ALL}")
        
        # Print updated summary
        print(f"\n{Fore.CYAN}Updated Login Summary:{Style.RESET_ALL}")
        print(f"{Fore.GREEN}Total successful: {len(self.sessions)}{Style.RESET_ALL}")
        print(f"{Fore.RED}Total failed: {num_sessions - len(self.sessions)}{Style.RESET_ALL}")
    
    def view_active_sessions(self):
        if not self.sessions:
            print(f"{Fore.YELLOW}⚠️ No active sessions found.{Style.RESET_ALL}")
            return
            
        print(f"\n{Fore.CYAN}Active Sessions ({len(self.sessions)}):{Style.RESET_ALL}")
        for session in self.sessions:
            status = f"{Fore.GREEN}Active{Style.RESET_ALL}" if session.is_logged_in else f"{Fore.RED}Inactive{Style.RESET_ALL}"
            print(f"Session {session.session_id}: {session.username} - {status}")
            print(f"  Success: {session.success_count}, Failures: {session.failure_count}")
    
    def logout_all_sessions(self):
        if not self.sessions:
            print(f"{Fore.YELLOW}⚠️ No active sessions found.{Style.RESET_ALL}")
            return
            
        confirm = input(f"{Fore.YELLOW}Are you sure you want to logout all sessions? (y/n): {Style.RESET_ALL}")
        if confirm.lower() == 'y':
            self.sessions = []
            print(f"{Fore.GREEN}✅ All sessions logged out.{Style.RESET_ALL}")
        else:
            print(f"{Fore.YELLOW}Operation cancelled.{Style.RESET_ALL}")
    
    def get_targets(self):
        print(f"\n{Fore.CYAN}📋 How would you like to input target usernames?{Style.RESET_ALL}")
        print(f"{Fore.WHITE}1. Enter manually{Style.RESET_ALL}")
        print(f"{Fore.WHITE}2. Load from file (targets.txt){Style.RESET_ALL}")
        print(f"{Fore.WHITE}3. Generate random targets{Style.RESET_ALL}")
        
        choice = input(f"{Fore.CYAN}Enter your choice (1-3): {Style.RESET_ALL}")
        
        targets = []
        
        if choice == '1':
            print(f"{Fore.YELLOW}Enter target usernames (one per line, type 'done' when finished):{Style.RESET_ALL}")
            while True:
                username = input(f"{Fore.CYAN}Target username: {Style.RESET_ALL}")
                if username.lower() == 'done':
                    break
                if username.strip():
                    targets.append(username.strip())
                    
        elif choice == '2':
            if os.path.exists('targets.txt'):
                try:
                    with open('targets.txt', 'r') as f:
                        targets = [line.strip() for line in f if line.strip() and not line.startswith('#')]
                    print(f"{Fore.GREEN}✅ Loaded {len(targets)} targets from targets.txt{Style.RESET_ALL}")
                except Exception as e:
                    print(f"{Fore.RED}❌ Error loading targets: {str(e)}{Style.RESET_ALL}")
                    targets = []
            else:
                print(f"{Fore.YELLOW}targets.txt not found. Creating a new one...{Style.RESET_ALL}")
                with open('targets.txt', 'w') as f:
                    f.write("# Add one Instagram username per line\n")
                    f.write("# Example:\n")
                    f.write("target1\n")
                    f.write("target2\n")
                print(f"{Fore.GREEN}✅ Created targets.txt. Please add targets and run again.{Style.RESET_ALL}")
                return targets
                
        elif choice == '3':
            try:
                num_targets = int(input(f"{Fore.CYAN}How many random targets to generate? {Style.RESET_ALL}"))
                prefix = input(f"{Fore.CYAN}Username prefix (default: user): {Style.RESET_ALL}") or "user"
                for i in range(1, num_targets + 1):
                    targets.append(f"{prefix}{random.randint(1000, 9999)}")
                print(f"{Fore.GREEN}✅ Generated {len(targets)} random targets{Style.RESET_ALL}")
            except ValueError:
                print(f"{Fore.RED}❌ Invalid input. Using 5 random targets.{Style.RESET_ALL}")
                targets = [f"user{random.randint(1000, 9999)}" for _ in range(5)]
        else:
            print(f"{Fore.RED}❌ Invalid choice. Using manual input.{Style.RESET_ALL}")
            return self.get_targets()
            
        if not targets:
            print(f"{Fore.RED}❌ No targets provided.{Style.RESET_ALL}")
            return targets
            
        # Save targets to file
        with open('targets.txt', 'w') as f:
            f.write("# Instagram targets for reporting\n")
            for target in targets:
                f.write(f"{target}\n")
        print(f"{Fore.GREEN}✅ Saved {len(targets)} targets to targets.txt{Style.RESET_ALL}")
        
        return targets
    
    def get_single_target(self):
        target = input(f"{Fore.CYAN}Enter target username: {Style.RESET_ALL}")
        if not target.strip():
            print(f"{Fore.RED}❌ No target provided.{Style.RESET_ALL}")
            return None
        return target.strip()
    
    def get_report_reason(self):
        print(f"\n{Fore.CYAN}📝 Select report reason:{Style.RESET_ALL}")
        print(f"{Fore.WHITE}1. I don't like this{Style.RESET_ALL}")
        print(f"{Fore.WHITE}2. Harassment/Bullying{Style.RESET_ALL}")
        print(f"{Fore.WHITE}3. Suicide/Self-harm{Style.RESET_ALL}")
        print(f"{Fore.WHITE}4. Violence/Hate{Style.RESET_ALL}")
        print(f"{Fore.WHITE}5. Sale/Promotion{Style.RESET_ALL}")
        print(f"{Fore.WHITE}6. Nudity/Sexual{Style.RESET_ALL}")
        print(f"{Fore.WHITE}7. Scam/Spam{Style.RESET_ALL}")
        print(f"{Fore.WHITE}8. False Information{Style.RESET_ALL}")
        
        reason_choice = input(f"{Fore.CYAN}Enter your choice (1-8): {Style.RESET_ALL}")
        
        report_reasons = {
            '1': 'ig_i_dont_like_it_v3',
            '2': 'adult_content-threat_to_share_nude_images-u18-yes',
            '3': 'suicide_or_self_harm_concern-suicide_or_self_injury',
            '4': 'violent_hateful_or_disturbing-violence',
            '5': 'selling_or_promoting_restricted_items-drugs-high-risk',
            '6': 'adult_content-nudity_or_sexual_activity',
            '7': 'misleading_annoying_or_scam-fraud_or_scam',
            '8': 'misleading_annoying_or_scam-false_information-health'
        }
        
        return report_reasons.get(reason_choice, 'ig_i_dont_like_it_v3')
    
    def start_mass_reporting(self, report_type):
        if not self.sessions:
            print(f"{Fore.RED}❌ No active sessions available. Please login first.{Style.RESET_ALL}")
            return
            
        targets = self.get_targets()
        if not targets:
            return
        
        # Get report parameters
        try:
            reports_per_target = int(input(f'{Fore.CYAN}Enter number of reports per target: {Style.RESET_ALL}'))
        except ValueError:
            print(f"{Fore.YELLOW}Invalid input. Using default: 10 reports per target{Style.RESET_ALL}")
            reports_per_target = 10
            
        try:
            delay = float(input(f'{Fore.CYAN}Enter delay between reports in seconds (default: 0.5): {Style.RESET_ALL}') or "0.5")
        except ValueError:
            print(f"{Fore.YELLOW}Invalid input. Using default: 0.5 seconds{Style.RESET_ALL}")
            delay = 0.5
        
        report_reason = self.get_report_reason()
        
        print(f"\n{Fore.GREEN}🚀 Starting mass {report_type} reporting for {len(targets)} targets...{Style.RESET_ALL}")
        print(f"{Fore.WHITE}Sending {reports_per_target} reports per target with {delay}s delay between each{Style.RESET_ALL}")
        print(f"{Fore.WHITE}Report reason: {report_reason}{Style.RESET_ALL}")
        print(f"{Fore.WHITE}Total reports to send: {len(targets) * reports_per_target}{Style.RESET_ALL}")
        print(f"{Fore.WHITE}Using {len(self.sessions)} sessions{Style.RESET_ALL}\n")
        
        # Create a queue for targets
        target_queue = Queue()
        for target in targets:
            target_queue.put(target)
        
        # Start worker threads for each session
        threads = []
        for session in self.sessions:
            thread = threading.Thread(
                target=self.mass_report_worker,
                args=(session, target_queue, reports_per_target, delay, report_reason, report_type)
            )
            thread.daemon = True
            thread.start()
            threads.append(thread)
        
        # Wait for all targets to be processed
        target_queue.join()
        
        # Print summary
        total_success = sum(session.success_count for session in self.sessions)
        total_failure = sum(session.failure_count for session in self.sessions)
        
        print(f"\n{Fore.GREEN}{'='*60}{Style.RESET_ALL}")
        print(f"{Fore.GREEN}🏁 Mass {report_type} reporting completed!{Style.RESET_ALL}")
        print(f"{Fore.GREEN}✅ Total successful reports: {total_success}{Style.RESET_ALL}")
        print(f"{Fore.RED}❌ Total failed reports: {total_failure}{Style.RESET_ALL}")
        print(f"{Fore.GREEN}{'='*60}{Style.RESET_ALL}")
        
        # Print per-session stats
        print(f"\n{Fore.CYAN}Per-session statistics:{Style.RESET_ALL}")
        for session in self.sessions:
            print(f"Session {session.session_id} ({session.username}): "
                  f"{Fore.GREEN}{session.success_count} success{Style.RESET_ALL}, "
                  f"{Fore.RED}{session.failure_count} failures{Style.RESET_ALL}")
    
    def start_single_target_reporting(self, report_type):
        if not self.sessions:
            print(f"{Fore.RED}❌ No active sessions available. Please login first.{Style.RESET_ALL}")
            return
            
        target = self.get_single_target()
        if not target:
            return
        
        # Get report parameters
        try:
            reports_count = int(input(f'{Fore.CYAN}Enter number of reports to send: {Style.RESET_ALL}'))
        except ValueError:
            print(f"{Fore.YELLOW}Invalid input. Using default: 10 reports{Style.RESET_ALL}")
            reports_count = 10
            
        try:
            delay = float(input(f'{Fore.CYAN}Enter delay between reports in seconds (default: 0.5): {Style.RESET_ALL}') or "0.5")
        except ValueError:
            print(f"{Fore.YELLOW}Invalid input. Using default: 0.5 seconds{Style.RESET_ALL}")
            delay = 0.5
        
        report_reason = self.get_report_reason()
        
        print(f"\n{Fore.GREEN}🚀 Starting single target {report_type} reporting for {target}...{Style.RESET_ALL}")
        print(f"{Fore.WHITE}Sending {reports_count} reports with {delay}s delay between each{Style.RESET_ALL}")
        print(f"{Fore.WHITE}Report reason: {report_reason}{Style.RESET_ALL}")
        print(f"{Fore.WHITE}Using {len(self.sessions)} sessions{Style.RESET_ALL}\n")
        
        # Create a queue for targets
        target_queue = Queue()
        target_queue.put(target)
        
        # Start worker threads for each session
        threads = []
        for session in self.sessions:
            thread = threading.Thread(
                target=self.mass_report_worker,
                args=(session, target_queue, reports_count, delay, report_reason, report_type)
            )
            thread.daemon = True
            thread.start()
            threads.append(thread)
        
        # Wait for all targets to be processed
        target_queue.join()
        
        # Print summary
        total_success = sum(session.success_count for session in self.sessions)
        total_failure = sum(session.failure_count for session in self.sessions)
        
        print(f"\n{Fore.GREEN}{'='*60}{Style.RESET_ALL}")
        print(f"{Fore.GREEN}🏁 Single target {report_type} reporting completed!{Style.RESET_ALL}")
        print(f"{Fore.GREEN}✅ Total successful reports: {total_success}{Style.RESET_ALL}")
        print(f"{Fore.RED}❌ Total failed reports: {total_failure}{Style.RESET_ALL}")
        print(f"{Fore.GREEN}{'='*60}{Style.RESET_ALL}")
        
        # Print per-session stats
        print(f"\n{Fore.CYAN}Per-session statistics:{Style.RESET_ALL}")
        for session in self.sessions:
            print(f"Session {session.session_id} ({session.username}): "
                  f"{Fore.GREEN}{session.success_count} success{Style.RESET_ALL}, "
                  f"{Fore.RED}{session.failure_count} failures{Style.RESET_ALL}")
    
    def mass_report_worker(self, session, target_queue, reports_per_target, delay, report_reason, report_type):
        while not target_queue.empty():
            try:
                target = target_queue.get_nowait()
            except:
                break
                
            print(f"{Fore.CYAN}🎯 Session {session.session_id}: Processing target {target}...{Style.RESET_ALL}")
            
            # Get user ID for this target
            user_id = session.get_user_id(target)
            if not user_id:
                target_queue.task_done()
                continue
            
            # Get object ID based on report type
            object_id = None
            if report_type == 'story':
                object_id = session.get_story_id(user_id)
            elif report_type == 'post':
                object_id = session.get_post_id(user_id)
            elif report_type == 'account':
                object_id = user_id  # For account reporting, we use user_id directly
            
            if not object_id:
                target_queue.task_done()
                continue
                
            # Send multiple reports for this target
            for i in range(reports_per_target):
                print(f"{Fore.YELLOW}📤 Session {session.session_id}: Sending report {i+1}/{reports_per_target} for {target}...{Style.RESET_ALL}")
                
                # Get report info for this session
                obj_id, context = session.get_report_info(object_id, report_type)
                if not obj_id or not context:
                    continue
                    
                # Submit report
                session.submit_report(obj_id, context, report_reason, report_type)
                
                # Delay before next report
                if i < reports_per_target - 1:
                    time.sleep(delay)
            
            # Mark target as processed
            target_queue.task_done()
            
            # Small delay before next target
            time.sleep(delay * 2)

if __name__ == "__main__":
    reporter = InstagramReporter()