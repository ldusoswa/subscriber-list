"""
Subscriber List Management System
Processes membership data from YouTube, Twitch, and Patreon platforms.
"""
import csv
import glob
import os
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from pathlib import Path
from typing import List, Dict, Tuple, Optional
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Import Twitch API module
try:
    from twitch_api import get_twitch_subscribers_programmatically
    TWITCH_API_AVAILABLE = True
except ImportError:
    TWITCH_API_AVAILABLE = False
    print("Warning: twitch_api module not available. Will fall back to CSV files.")

# Import Patreon API module
try:
    from patreon_api import get_patreon_members_programmatically
    PATREON_API_AVAILABLE = True
except ImportError:
    PATREON_API_AVAILABLE = False
    print("Warning: patreon_api module not available. Will fall back to CSV files.")

# Import YouTube API module
try:
    from youtube_api import get_youtube_members_programmatically
    YOUTUBE_API_AVAILABLE = True
except ImportError:
    YOUTUBE_API_AVAILABLE = False
    print("Warning: youtube_api module not available. Will fall back to CSV files.")


# --- Configuration ---
@dataclass
class Config:
    """Application configuration"""
    sub_lists_dir: Path = Path(r'C:\Users\dusosl\Downloads')
    output_csv: str = 'levels.csv'
    
    # Tier names
    TIER_TEAM_BOSS: str = "Team Boss"
    TIER_CREW_CHIEF: str = "Crew Chief"
    TIER_PIT_CREW: str = "Pit Crew"
    
    # Pricing
    PRICE_TEAM_BOSS: float = 19.99
    PRICE_CREW_CHIEF: float = 9.99
    PRICE_PIT_CREW: float = 4.99
    
    # Platform fee rates
    YOUTUBE_FEE_RATE: float = 0.30
    TWITCH_FEE_RATE: float = 0.50
    PATREON_FEE_RATE_LOW: float = 0.05
    PATREON_FEE_RATE_HIGH: float = 0.029
    PATREON_FIXED_FEE_LOW: float = 0.10
    PATREON_FIXED_FEE_HIGH: float = 0.30
    PATREON_THRESHOLD: float = 3.00


@dataclass
class MembershipData:
    """Container for all membership lists"""
    team_boss_patreon: List[str] = field(default_factory=list)
    team_boss_youtube: List[str] = field(default_factory=list)
    crew_chief_patreon: List[str] = field(default_factory=list)
    crew_chief_youtube: List[str] = field(default_factory=list)
    pit_crew_patreon: List[str] = field(default_factory=list)
    pit_crew_youtube: List[str] = field(default_factory=list)
    pit_crew_youtube_gifted: List[str] = field(default_factory=list)
    pit_crew_twitch_tier1: List[str] = field(default_factory=list)
    pit_crew_twitch_tier1_gifted: List[str] = field(default_factory=list)
    twitch_prime_expiry_info: List[str] = field(default_factory=list)
    tenure_map: Dict[str, int] = field(default_factory=dict)  # Maps member name to months
    
    def _sort_by_tenure(self, members: List[str]) -> List[str]:
        """Sort members by tenure (longest first), then alphabetically"""
        return sorted(members, key=lambda m: (-self.tenure_map.get(m, 0), m.lower()))
    
    @property
    def team_boss_combined(self) -> List[str]:
        combined = self.team_boss_patreon + self.team_boss_youtube
        return self._sort_by_tenure(combined)
    
    @property
    def crew_chief_combined(self) -> List[str]:
        combined = self.crew_chief_patreon + self.crew_chief_youtube
        return self._sort_by_tenure(combined)
    
    @property
    def pit_crew_combined(self) -> List[str]:
        combined = self.pit_crew_patreon + self.pit_crew_youtube
        return self._sort_by_tenure(combined)
    
    @property
    def twitch_combined(self) -> List[str]:
        return self._sort_by_tenure(self.pit_crew_twitch_tier1)
    
    @property
    def gifted_combined(self) -> List[str]:
        combined = self.pit_crew_youtube_gifted + self.pit_crew_twitch_tier1_gifted
        return self._sort_by_tenure(combined)
    
    @property
    def total_member_count(self) -> int:
        return len(
            self.team_boss_patreon + self.team_boss_youtube +
            self.crew_chief_patreon + self.crew_chief_youtube +
            self.pit_crew_patreon + self.pit_crew_youtube +
            self.pit_crew_twitch_tier1 +
            self.pit_crew_youtube_gifted + self.pit_crew_twitch_tier1_gifted
        )


@dataclass
class EarningsReport:
    """Container for earnings calculations"""
    total_gross: float = 0.0
    total_platform_costs: float = 0.0
    total_net: float = 0.0


class TextProcessor:
    """Handles text cleaning and replacements"""
    
    # Character encoding fixes and name standardization
    REPLACEMENTS = {
        'ï¼‡': '\'',
        'Ã¼': 'ü',
        'Å‚': 'l',
        'Ã§': 'ç',
        'â€™': '\'',
        'Ã«': 'ë',
        '＇': '\'',
        '\u2019': '\'',
        'é': 'é',
        'Ã©': 'é',
        '"': '"',
        '"': '"',
        ' ðŸ‡µðŸ‡¸': '',
        # Name standardization
        'Dan Persons': 'Dogoncouch',
        'adam_coolmunky': 'acreekracing_photography',
        'Phelan Pritchard Gaming': 'Phelan Pritchard',
        'astrophotography': 'Geezer3d.com',
        'damien mcmullen': 'Damo McMullen',
    }
    
    @classmethod
    def clean_text(cls, text: str) -> str:
        """Apply all text replacements to clean and standardize names"""
        for old, new in cls.REPLACEMENTS.items():
            text = text.replace(old, new)
        return text


class FileLoader:
    """Handles file discovery and loading"""
    
    @staticmethod
    def find_recent_file(directory: Path, prefix: str) -> str:
        """Find the most recently modified file matching the prefix"""
        file_pattern = str(directory / f"{prefix}*")
        file_list = glob.glob(file_pattern)
        if not file_list:
            raise FileNotFoundError(f"No files found matching: {file_pattern}")
        file_list.sort(key=os.path.getmtime)
        return file_list[-1]


class TwitchProcessor:
    """Processes Twitch subscription data"""
    
    @staticmethod
    def fetch_from_api(data: MembershipData) -> bool:
        """Fetch Twitch subscribers directly from API"""
        if not TWITCH_API_AVAILABLE:
            return False
        
        # Get credentials from environment variables
        client_id = os.getenv('TWITCH_CLIENT_ID')
        client_secret = os.getenv('TWITCH_CLIENT_SECRET')
        redirect_uri = os.getenv('TWITCH_REDIRECT_URI')
        
        if not all([client_id, client_secret, redirect_uri]):
            print("Warning: Twitch API credentials not found in environment variables.")
            print("Required: TWITCH_CLIENT_ID, TWITCH_CLIENT_SECRET, TWITCH_REDIRECT_URI")
            return False
        
        try:
            print("Fetching Twitch subscribers from API...")
            rows = get_twitch_subscribers_programmatically(
                client_id, client_secret, redirect_uri
            )
            
            # Process the rows using the same logic as process_file
            TwitchProcessor._process_rows(rows, data)
            return True
            
        except Exception as e:
            print(f"Error fetching from Twitch API: {e}")
            return False
    
    @staticmethod
    def process_file(file_path: str, data: MembershipData) -> None:
        """Load and process Twitch subscriber data from CSV file"""
        with open(file_path, 'r') as csv_file:
            next(csv_file)  # Skip header
            reader = csv.reader(csv_file)
            rows = list(reader)
        
        TwitchProcessor._process_rows(rows, data)
    
    @staticmethod
    def _process_rows(rows: List[List[str]], data: MembershipData) -> None:
        """Process Twitch subscriber rows (from API or CSV)"""
        sorted_list = sorted(rows, key=lambda row: float(row[3]) if row[3] else 0, reverse=True)
        
        # Remove self-subscription if present
        if sorted_list and sorted_list[0][0] == 'ldusoswa':
            sorted_list.pop(0)
        
        for row in sorted_list:
            username = TextProcessor.clean_text(row[0])
            sub_type = row[5] if len(row) > 5 else 'paid'
            
            # Categorize subscription
            if sub_type == 'gift':
                data.pit_crew_twitch_tier1_gifted.append(username)
            else:
                data.pit_crew_twitch_tier1.append(username)
            
            # Track expiry for prime and gifted subs
            if sub_type in ['prime', 'gift'] and len(row) > 1:
                expiry_info = TwitchProcessor._calculate_expiry(username, row[1], sub_type)
                data.twitch_prime_expiry_info.append(expiry_info)
    
    @staticmethod
    def _calculate_expiry(username: str, sub_date_str: str, sub_type: str) -> str:
        """Calculate and format subscription expiry information"""
        sub_date = datetime.strptime(sub_date_str, "%Y-%m-%dT%H:%M:%SZ")
        expiry_date = sub_date + timedelta(days=31)
        current_date = datetime.utcnow()
        days_left = 31 + (sub_date - current_date).days
        expiry_str = expiry_date.strftime("%B %d, %Y at %I:%M %p")
        return f'{username.ljust(20)}\t{sub_type}\t\t{days_left}\t\t{expiry_str}'


class PatreonProcessor:
    """Processes Patreon membership data"""
    
    @staticmethod
    def fetch_from_api(data: MembershipData, config: Config) -> bool:
        """Fetch Patreon members directly from API"""
        if not PATREON_API_AVAILABLE:
            return False
        
        # Get credentials from environment variables
        client_id = os.getenv('PATREON_CLIENT_ID')
        client_secret = os.getenv('PATREON_CLIENT_SECRET')
        redirect_uri = os.getenv('PATREON_REDIRECT_URI')
        
        if not all([client_id, client_secret, redirect_uri]):
            print("Warning: Patreon API credentials not found in environment variables.")
            print("Required: PATREON_CLIENT_ID, PATREON_CLIENT_SECRET, PATREON_REDIRECT_URI")
            return False
        
        try:
            print("Fetching Patreon members from API...")
            rows = get_patreon_members_programmatically(
                client_id, client_secret, redirect_uri
            )
            
            # Process the rows using the same logic as process_file
            PatreonProcessor._process_rows(rows, data, config)
            return True
            
        except Exception as e:
            print(f"Error fetching from Patreon API: {e}")
            return False
    
    @staticmethod
    def process_file(file_path: str, data: MembershipData, config: Config) -> None:
        """Load and process Patreon member data from CSV file"""
        with open(file_path, 'r') as csv_file:
            next(csv_file)  # Skip header
            reader = csv.reader(csv_file)
            rows = list(reader)
        
        PatreonProcessor._process_rows(rows, data, config)
    
    @staticmethod
    def _process_rows(rows: List[List[str]], data: MembershipData, config: Config) -> None:
        """Process Patreon member rows (from API or CSV)"""
        sorted_list = sorted(rows, key=lambda row: float(row[8]) if row[8] else 0, reverse=True)
        
        for row in sorted_list:
            name = TextProcessor.clean_text(row[0])
            tier = row[10] if len(row) > 10 else ''
            
            if tier == config.TIER_CREW_CHIEF:
                data.crew_chief_patreon.append(name)
            elif tier == config.TIER_TEAM_BOSS:
                data.team_boss_patreon.append(name)
            else:
                data.pit_crew_patreon.append(name)


class YouTubeProcessor:
    """Processes YouTube membership data"""
    
    @staticmethod
    def fetch_from_api(data: MembershipData, config: Config) -> bool:
        """Fetch YouTube members directly from API"""
        if not YOUTUBE_API_AVAILABLE:
            return False
        
        # Get credentials from environment variables
        client_id = os.getenv('YOUTUBE_CLIENT_ID')
        client_secret = os.getenv('YOUTUBE_CLIENT_SECRET')
        redirect_uri = os.getenv('YOUTUBE_REDIRECT_URI')
        
        if not all([client_id, client_secret, redirect_uri]):
            print("Warning: YouTube API credentials not found in environment variables.")
            print("Required: YOUTUBE_CLIENT_ID, YOUTUBE_CLIENT_SECRET, YOUTUBE_REDIRECT_URI")
            return False
        
        try:
            print("Fetching YouTube members from API...")
            rows = get_youtube_members_programmatically(
                client_id, client_secret, redirect_uri
            )
            
            # Process the rows using the same logic as process_file
            YouTubeProcessor._process_rows(rows, data, config)
            return True
            
        except Exception as e:
            print(f"Error fetching from YouTube API: {e}")
            return False
    
    @staticmethod
    def process_file(file_path: str, data: MembershipData, config: Config) -> None:
        """Load and process YouTube member data from CSV file"""
        with open(file_path, 'r', encoding='utf-8') as csv_file:
            next(csv_file)  # Skip header
            reader = csv.reader(csv_file)
            rows = list(reader)
        
        YouTubeProcessor._process_rows(rows, data, config)
    
    @staticmethod
    def _process_rows(rows: List[List[str]], data: MembershipData, config: Config) -> None:
        """Process YouTube member rows (from API or CSV)"""
        sorted_list = sorted(rows, key=lambda row: float(row[4]) if row[4] else 0, reverse=True)
        
        for row in sorted_list:
            name = TextProcessor.clean_text(row[0])
            tier = row[2] if len(row) > 2 else ''
            amount = float(row[4]) if len(row) > 4 and row[4] else 0
            
            if tier == config.TIER_PIT_CREW:
                # Distinguish between paid and gifted based on amount
                if amount > 3:
                    data.pit_crew_youtube.append(name)
                else:
                    data.pit_crew_youtube_gifted.append(name)
            elif tier == config.TIER_CREW_CHIEF:
                data.crew_chief_youtube.append(name)
            elif tier == config.TIER_TEAM_BOSS:
                data.team_boss_youtube.append(name)


class EarningsCalculator:
    """Calculates earnings and platform fees"""
    
    def __init__(self, config: Config):
        self.config = config
        self.report = EarningsReport()
    
    def calculate_tier_earnings(
        self,
        platform: str,
        tier_name: str,
        members: List[str],
        price_per_month: float
    ) -> Tuple[int, float, float, float]:
        """Calculate earnings for a specific tier"""
        member_count = len(members)
        monthly_gross = member_count * price_per_month
        fees = self._calculate_platform_fees(platform, monthly_gross, member_count, price_per_month)
        monthly_net = monthly_gross - fees
        
        # Update totals
        self.report.total_gross += monthly_gross
        self.report.total_platform_costs += fees
        self.report.total_net += monthly_net
        
        return member_count, monthly_gross, fees, monthly_net
    
    def _calculate_platform_fees(
        self,
        platform: str,
        gross: float,
        member_count: int,
        price: float
    ) -> float:
        """Calculate platform-specific fees"""
        if platform == 'YouTube':
            return gross * self.config.YOUTUBE_FEE_RATE
        elif platform == 'Twitch':
            return gross * self.config.TWITCH_FEE_RATE
        elif platform == 'Patreon':
            if price < self.config.PATREON_THRESHOLD:
                return (gross * self.config.PATREON_FEE_RATE_LOW +
                       member_count * self.config.PATREON_FIXED_FEE_LOW)
            else:
                return (gross * self.config.PATREON_FEE_RATE_HIGH +
                       member_count * self.config.PATREON_FIXED_FEE_HIGH)
        return 0.0


class ReportGenerator:
    """Generates various output reports"""
    
    @staticmethod
    def format_for_photoshop(members: List[str], padding: int) -> str:
        """Format member list for Photoshop import"""
        if not members:
            return 'None at this time'
        return ' '.join(member.ljust(padding) for member in members)
    
    @staticmethod
    def print_member_lists(data: MembershipData) -> None:
        """Print categorized member lists"""
        print(f'\nTeam Boss\t{", ".join(data.team_boss_combined)}')
        print(f'Crew Chief\t{", ".join(data.crew_chief_combined)}')
        print(f'Pit Crew\t{", ".join(data.pit_crew_combined)}')
        print(f'TWITCH\t\t{", ".join(data.twitch_combined)}')
    
    @staticmethod
    def create_photoshop_csv(data: MembershipData, output_file: str) -> None:
        """Create CSV file for Photoshop import"""
        csv_data = [
            ['teamBoss', 'crewChief', 'pitCrew', 'twitchSubs', 'newGifted'],
            [
                ReportGenerator.format_for_photoshop(data.team_boss_combined, 45),
                ReportGenerator.format_for_photoshop(data.crew_chief_combined, 30),
                ReportGenerator.format_for_photoshop(data.pit_crew_combined, 30),
                ReportGenerator.format_for_photoshop(data.pit_crew_twitch_tier1, 30),
                ReportGenerator.format_for_photoshop(data.gifted_combined, 24)
            ]
        ]
        
        with open(output_file, 'w', newline='', encoding='utf-8-sig') as f:
            writer = csv.writer(f)
            writer.writerows(csv_data)
        
        print(f'\nCSV file created successfully for Photoshop import: {output_file}')
    
    @staticmethod
    def print_earnings_report(
        data: MembershipData,
        calculator: EarningsCalculator,
        config: Config
    ) -> None:
        """Print detailed earnings report"""
        print(f'\n############################# MONTHLY EARNINGS REPORT #####################################')
        print(f'level\t\t\tmembers\trate\tgross income\tplatform costs\ttotal (before tax)')
        print(f'_____________________\t______\t______\t______________\t______________\t__________________')
        
        # Define all tiers to report
        tiers = [
            ('YouTube', 'Team Boss', data.team_boss_youtube, config.PRICE_TEAM_BOSS),
            ('YouTube', 'Crew Chief', data.crew_chief_youtube, config.PRICE_CREW_CHIEF),
            ('YouTube', 'Pit Crew', data.pit_crew_youtube, config.PRICE_PIT_CREW),
            ('YouTube', 'Gifted', data.pit_crew_youtube_gifted, config.PRICE_PIT_CREW),
            ('Twitch', 'Tier 1 member', data.pit_crew_twitch_tier1, config.PRICE_PIT_CREW),
            ('Twitch', 'Gifted sub', data.pit_crew_twitch_tier1_gifted, config.PRICE_PIT_CREW),
            ('Patreon', 'Team Boss', data.team_boss_patreon, config.PRICE_TEAM_BOSS),
            ('Patreon', 'Crew Chief', data.crew_chief_patreon, config.PRICE_CREW_CHIEF),
            ('Patreon', 'Pit Crew', data.pit_crew_patreon, config.PRICE_PIT_CREW),
        ]
        
        for platform, tier_name, members, price in tiers:
            if members:
                count, gross, fees, net = calculator.calculate_tier_earnings(
                    platform, tier_name, members, price
                )
                print(f'{platform} - {tier_name}\t{count}\t€{price}\t€{gross:.2f}\t\t€{fees:.2f}\t\t€{net:.2f}')
        
        # Print totals
        report = calculator.report
        print('===========================================================================================')
        print(f'TOTAL\t\t\t{data.total_member_count}\t\t€{report.total_gross:.2f}\t\t€{report.total_platform_costs:.2f}\t\t€{report.total_net:.2f}')
        print(f'###########################################################################################')


class SubscriberListManager:
    """Main application coordinator"""
    
    def __init__(self, config: Config):
        self.config = config
        self.data = MembershipData()
        self.calculator = EarningsCalculator(config)
    
    def check_csv_age(self, file_path: str, platform_name: str) -> bool:
        """Check if CSV file is older than 24 hours and prompt user if needed.
        Returns True if file is acceptable to use, False otherwise."""
        try:
            file_age = datetime.now() - datetime.fromtimestamp(os.path.getmtime(file_path))
            if file_age > timedelta(hours=24):
                print(f"\n⚠️  WARNING: {platform_name} CSV file is {file_age.days} days old!")
                print(f"   File: {file_path}")
                print(f"   Last modified: {datetime.fromtimestamp(os.path.getmtime(file_path)).strftime('%Y-%m-%d %H:%M:%S')}")
                response = input(f"\n   Download fresh {platform_name} CSV manually? (y/n): ")
                if response.lower() == 'y':
                    print(f"   Please download the latest {platform_name} CSV and run this script again.")
                    return False
                else:
                    print(f"   Continuing with old {platform_name} data...")
                    return True
            return True
        except Exception as e:
            print(f"Warning: Could not check age of {file_path}: {e}")
            return True
    
    def load_tenure_data(self, tenure_file: str = 'all_members_months.csv') -> None:
        """Load member tenure data from CSV file"""
        try:
            with open(tenure_file, 'r', encoding='utf-8') as f:
                next(f)  # Skip header
                reader = csv.reader(f)
                for row in reader:
                    if len(row) >= 3:
                        name = TextProcessor.clean_text(row[0])
                        try:
                            months = int(row[2])
                            self.data.tenure_map[name] = months
                        except (ValueError, IndexError):
                            pass
        except FileNotFoundError:
            print(f"Warning: {tenure_file} not found. Sorting by name only.")
    
    def load_all_data(self) -> None:
        """Load data from all platforms"""
        loader = FileLoader()
        
        # Load tenure data first for sorting
        self.load_tenure_data()
        
        # Try to fetch Twitch data from API first
        twitch_from_api = TwitchProcessor.fetch_from_api(self.data)
        
        if not twitch_from_api:
            # Fall back to CSV file
            print("Falling back to Twitch CSV file...")
            try:
                twitch_file = loader.find_recent_file(self.config.sub_lists_dir, 'subscriber-list')
                if self.check_csv_age(twitch_file, 'Twitch'):
                    TwitchProcessor.process_file(twitch_file, self.data)
                else:
                    print("Skipping Twitch data due to user request.")
            except FileNotFoundError:
                print("Warning: No Twitch data available (neither API nor CSV file)")
        
        # Try to fetch Patreon data from API first
        patreon_from_api = PatreonProcessor.fetch_from_api(self.data, self.config)
        
        if not patreon_from_api:
            # Fall back to CSV file
            print("Falling back to Patreon CSV file...")
            try:
                patreon_file = loader.find_recent_file(self.config.sub_lists_dir, 'Members_')
                if self.check_csv_age(patreon_file, 'Patreon'):
                    PatreonProcessor.process_file(patreon_file, self.data, self.config)
                else:
                    print("Skipping Patreon data due to user request.")
            except FileNotFoundError:
                print("Warning: No Patreon data available (neither API nor CSV file)")
        
        # Try to fetch YouTube data from API first
        youtube_from_api = YouTubeProcessor.fetch_from_api(self.data, self.config)
        
        if not youtube_from_api:
            # Fall back to CSV file
            print("Falling back to YouTube CSV file...")
            try:
                youtube_file = loader.find_recent_file(self.config.sub_lists_dir, 'Your members ')
                if self.check_csv_age(youtube_file, 'YouTube'):
                    YouTubeProcessor.process_file(youtube_file, self.data, self.config)
                else:
                    print("Skipping YouTube data due to user request.")
            except FileNotFoundError:
                print("Warning: No YouTube data available (neither API nor CSV file)")
    
    def generate_reports(self) -> None:
        """Generate all output reports"""
        ReportGenerator.print_member_lists(self.data)
        ReportGenerator.create_photoshop_csv(self.data, self.config.output_csv)
        ReportGenerator.print_earnings_report(self.data, self.calculator, self.config)
        
        # Debug output
        print(f'newGifted: {self.data.gifted_combined}')
    
    def run(self) -> None:
        """Execute the full workflow"""
        self.load_all_data()
        self.generate_reports()


def main():
    """Application entry point"""
    config = Config()
    manager = SubscriberListManager(config)
    manager.run()


if __name__ == '__main__':
    main()
