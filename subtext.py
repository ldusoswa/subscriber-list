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
from typing import List, Dict, Tuple


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
    def process_file(file_path: str, data: MembershipData) -> None:
        """Load and process Twitch subscriber data"""
        with open(file_path, 'r') as csv_file:
            next(csv_file)  # Skip header
            reader = csv.reader(csv_file)
            sorted_list = sorted(reader, key=lambda row: float(row[3]), reverse=True)
            
            # Remove self-subscription if present
            if sorted_list and sorted_list[0][0] == 'ldusoswa':
                sorted_list.pop(0)
            
            for row in sorted_list:
                username = TextProcessor.clean_text(row[0])
                sub_type = row[5]
                
                # Categorize subscription
                if sub_type == 'gift':
                    data.pit_crew_twitch_tier1_gifted.append(username)
                else:
                    data.pit_crew_twitch_tier1.append(username)
                
                # Track expiry for prime and gifted subs
                if sub_type in ['prime', 'gift']:
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
    def process_file(file_path: str, data: MembershipData, config: Config) -> None:
        """Load and process Patreon member data"""
        with open(file_path, 'r') as csv_file:
            next(csv_file)  # Skip header
            reader = csv.reader(csv_file)
            sorted_list = sorted(reader, key=lambda row: float(row[8]), reverse=True)
            
            for row in sorted_list:
                name = TextProcessor.clean_text(row[0])
                tier = row[10]
                
                if tier == config.TIER_CREW_CHIEF:
                    data.crew_chief_patreon.append(name)
                elif tier == config.TIER_TEAM_BOSS:
                    data.team_boss_patreon.append(name)
                else:
                    data.pit_crew_patreon.append(name)


class YouTubeProcessor:
    """Processes YouTube membership data"""
    
    @staticmethod
    def process_file(file_path: str, data: MembershipData, config: Config) -> None:
        """Load and process YouTube member data"""
        with open(file_path, 'r', encoding='utf-8') as csv_file:
            next(csv_file)  # Skip header
            reader = csv.reader(csv_file)
            sorted_list = sorted(reader, key=lambda row: float(row[4]), reverse=True)
            
            for row in sorted_list:
                name = TextProcessor.clean_text(row[0])
                tier = row[2]
                amount = float(row[4])
                
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
        
        # Find most recent files
        youtube_file = loader.find_recent_file(self.config.sub_lists_dir, 'Your members ')
        twitch_file = loader.find_recent_file(self.config.sub_lists_dir, 'subscriber-list')
        patreon_file = loader.find_recent_file(self.config.sub_lists_dir, 'Members_')
        
        # Process each platform
        TwitchProcessor.process_file(twitch_file, self.data)
        PatreonProcessor.process_file(patreon_file, self.data, self.config)
        YouTubeProcessor.process_file(youtube_file, self.data, self.config)
    
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
