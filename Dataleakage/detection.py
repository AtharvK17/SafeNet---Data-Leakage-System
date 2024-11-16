from typing import Dict, List, Union, Optional, Tuple
import re
import pandas as pd
from pathlib import Path
from datetime import datetime, timedelta
import logging
from concurrent.futures import ThreadPoolExecutor, Future
from django.core.cache import cache
from enum import Enum
from dataclasses import dataclass
import json  # Ensure this import is present

from Accounts.models import UserActivityLog


class SensitivityLevel(Enum):
    MINIMAL = 1
    LOW = 2
    MEDIUM = 3
    HIGH = 4
    CRITICAL = 5


@dataclass
class ScanResult:
    score: float  # Now ranges from 0 (highly sensitive) to 100 (safe)
    findings: List[Dict]
    risk_level: SensitivityLevel
    anomaly_score: float
    context_score: float
    user_behavior_score: float
    metadata: Dict
    timestamp: datetime


@dataclass
class Alert:
    message: str
    severity: SensitivityLevel
    timestamp: datetime
    recipients: List[str]
    status: str = "Pending"  # Track if alert is resolved, pending, or escalated


class AdvancedDataLeakDetector:
    SENSITIVITY_PATTERNS = {
        'AADHAAR': {
            'patterns': [r'\b[2-9]{1}[0-9]{3}\s[0-9]{4}\s[0-9]{4}\b', r'\b[2-9]{1}[0-9]{11}\b'],
            'score': 10,
            'level': SensitivityLevel.CRITICAL,
            'context_keywords': ['unique', 'id', 'identity', 'number', 'uid']
        },
        'PAN': {
            'patterns': [r'[A-Z]{5}[0-9]{4}[A-Z]{1}'],
            'score': 8,
            'level': SensitivityLevel.HIGH,
            'context_keywords': ['permanent', 'account', 'number', 'tax', 'income']
        },
        'PASSPORT': {
            'patterns': [r'\b[A-PR-WY][1-9]\d\s?\d{4}[1-9]\b'],
            'score': 7,
            'level': SensitivityLevel.HIGH,
            'context_keywords': ['passport', 'travel', 'document']
        },
        'DRIVERS_LICENSE': {
            'patterns': [r'\b[A-Z]{1,2}\d{4,9}\b'],
            'score': 6,
            'level': SensitivityLevel.MEDIUM,
            'context_keywords': ['driver', 'license', 'dl', 'identification']
        },
        'SSN': {
            'patterns': [
                r'\b(?!0{3}|666|9\d{2})\d{3}[-\s]?(?!00)\d{2}[-\s]?(?!0{4})\d{4}\b',  # More specific SSN pattern
            ],
            'score': 8,
            'level': SensitivityLevel.CRITICAL,
            'context_keywords': ['ssn', 'social security', 'social', 'security', 'number'],
            'validators': [
                lambda x: not x.replace('-','').isdigit() or (100000000 <= int(x.replace('-','')) <= 999999999)
            ]
        },
        'PHONE_NUMBER': {
            'patterns': [
                r'\b(?:\+?1[-\s.]?)?\(?([0-9]{3})\)?[-\s.]?([0-9]{3})[-\s.]?([0-9]{4})\b'  # More specific phone pattern
            ],
            'score': 5,
            'level': SensitivityLevel.MEDIUM,
            'context_keywords': ['phone', 'cell', 'mobile', 'telephone', 'contact'],
            'validators': [
                lambda x: not any(c.isalpha() for c in x)
            ]
        },
        'DOB': {
            'patterns': [r'\b\d{2}[-/]\d{2}[-/]\d{4}\b', r'\b\d{4}[-/]\d{2}[-/]\d{2}\b'],
            'score': 4,
            'level': SensitivityLevel.MEDIUM,
            'context_keywords': ['dob', 'birth', 'date of birth', 'birthday']
        },
    }

    COLUMN_NAME_PATTERNS = {
        'AADHAAR': ['aadhaar', 'uid', 'unique_id', 'identity_number'],
        'PAN': ['pan', 'permanent_account', 'tax_id'],
        'PASSPORT': ['passport', 'travel_document', 'passport_no'],
        'DRIVERS_LICENSE': ['license', 'dl', 'driving_license', 'driver_id'],
        'SSN': ['ssn', 'social_security', 'social_security_number'],
        'PHONE_NUMBER': ['phone', 'mobile', 'contact', 'telephone', 'cell'],
        'DOB': ['dob', 'birth_date', 'date_of_birth', 'birthday']
    }

    def __init__(self):
        self.anomaly_detector = None  # Initialize as None
        self.behavior_analyzer = None  # Initialize as None
        self.executor = ThreadPoolExecutor(max_workers=4)  # Adjust based on your server capacity
        logging.basicConfig(level=logging.INFO)
        self.logger = logging.getLogger(__name__)

    def analyze_file(self, file_content: Union[str, pd.DataFrame], metadata: Dict) -> ScanResult:
        # Removed unnecessary try-except block
        # If a file path is provided, read it
        if isinstance(file_content, str) and Path(file_content).exists():
            file_content = self._read_file(Path(file_content))

        # Convert content to analyzable string format
        if isinstance(file_content, pd.DataFrame):
            content_str = self._prepare_dataframe_content(file_content)
        else:
            content_str = file_content

        # Ensure metadata is a dictionary
        if not isinstance(metadata, dict):
            metadata = {'filename': metadata}

        # Initialize detectors with user if available
        user_id = metadata.get('user_id')
        if user_id:
            if not self.anomaly_detector:
                self.anomaly_detector = AnomalyDetector(user=user_id)
            if not self.behavior_analyzer:
                self.behavior_analyzer = UserBehaviorAnalyzer(user=user_id)

        # Calculate scores
        sensitivity_score = self._calculate_sensitivity_score(content_str)
        context_score = self._analyze_context(content_str, metadata)

        anomaly_score = 0
        if self.anomaly_detector:
            _, anomaly_score = self.anomaly_detector.detect_anomalies()

        user_behavior_score = 0
        if self.behavior_analyzer:
            user_behavior_score = self.behavior_analyzer.analyze_behavior()

        # Calculate total score and generate findings
        total_score = self._combine_scores(
            sensitivity_score=sensitivity_score,
            context_score=context_score,
            anomaly_score=anomaly_score,
            user_behavior_score=user_behavior_score
        )
        findings = self._generate_findings(content_str)
        risk_level = self._determine_risk_level(total_score, findings)

        # Cache the result
        cache_key = f"file_scan_{metadata.get('filename', 'unknown')}"
        cache_data = {
            "score": total_score,
            "findings": findings,
            "risk_level": risk_level.name
        }
        cache.set(cache_key, cache_data, timeout=60 * 60)

        return ScanResult(
            score=total_score,
            findings=findings,
            risk_level=risk_level,
            timestamp=datetime.now(),
            anomaly_score=anomaly_score,
            context_score=context_score,
            user_behavior_score=user_behavior_score,
            metadata=metadata
        )

    def _read_file(self, file_path: Path) -> Union[str, pd.DataFrame]:
        # Removed unnecessary try-except block
        if file_path.suffix.lower() == '.csv':
            return pd.read_csv(file_path)
        elif file_path.suffix.lower() in ['.xls', '.xlsx']:
            return pd.read_excel(file_path)
        else:
            with open(file_path, 'r', encoding='utf-8') as f:
                return f.read()

    def _prepare_dataframe_content(self, df: pd.DataFrame) -> str:
        # Removed unnecessary try-except block
        content_parts = []
        sensitive_columns = {}

        # Identify potentially sensitive columns
        for col in df.columns:
            col_lower = str(col).lower()
            for data_type, patterns in self.COLUMN_NAME_PATTERNS.items():
                if any(pattern in col_lower.replace('_', '') for pattern in patterns):
                    sensitive_columns[col] = data_type

        # Process columns identified as potentially sensitive
        for col, data_type in sensitive_columns.items():
            for _, value in df[col].items():
                if pd.notna(value):
                    value_str = str(value).strip()
                    if value_str:
                        content_parts.append(f"{col}:{value_str}")

        return "\n".join(content_parts)

    def _calculate_sensitivity_score(self, content: str) -> float:
        """Calculate sensitivity score: 100 (safe) to 0 (highly sensitive)"""
        total_weight = 0
        max_weight = 0
        findings_count = 0

        for sensitivity_type, config in self.SENSITIVITY_PATTERNS.items():
            max_weight += config['score']  # Sum of all possible scores

        for sensitivity_type, config in self.SENSITIVITY_PATTERNS.items():
            matches = []
            for pattern in config['patterns']:
                found = re.finditer(pattern, content, re.IGNORECASE)
                for match in found:
                    if self._validate_match_context(match, content, config):
                        matches.append(match.group())
                        findings_count += 1

            if matches:
                occurrences = len(matches)
                weight = config['score'] * occurrences
                total_weight += weight

        # If no findings, return maximum safety score
        if findings_count == 0:
            return 100.0

        # Calculate base sensitivity score
        sensitivity_ratio = min(total_weight / max_weight, 1.0) if max_weight > 0 else 0
        base_score = (1 - sensitivity_ratio) * 100

        # Adjust score based on number of findings
        # Few findings (1-2) should still result in a relatively high score
        findings_modifier = min(findings_count * 5, 40)  # Cap the penalty at 40 points
        adjusted_score = min(max(base_score - findings_modifier, 0), 100)

        return round(adjusted_score, 2)

    def _is_numeric_content(self, content: str, column_name: str = None) -> bool:
        """Enhanced check if content appears to be numerical data"""
        if column_name:
            col_lower = column_name.lower()
            # Skip numeric check for columns that are explicitly marked as sensitive
            for patterns in self.COLUMN_NAME_PATTERNS.values():
                if any(pattern in col_lower.replace('_', '') for pattern in patterns):
                    return False

        try:
            # Check if line contains mostly numbers or decimal values
            parts = content.strip().split()
            numeric_parts = sum(1 for p in parts if p.replace('.','').replace('-','').isdigit())
            return numeric_parts / len(parts) > 0.5  # More than 50% numbers
        except:
            return False

    def _validate_match_context(self, match: re.Match, content: str, pattern_config: Dict) -> bool:
        """Enhanced context validation with column name awareness"""
        if not pattern_config.get('context_keywords'):
            return True

        # Get surrounding context
        start = max(0, match.start() - 100)
        end = min(len(content), match.end() + 100)
        context = content[start:end].lower()
        
        # Extract column name if present (format: "column_name:value")
        column_name = None
        context_parts = context.split(':')
        if len(context_parts) > 1:
            column_name = context_parts[0].strip()
        
        # Skip numeric check if column name indicates sensitive data
        if not column_name or not self._is_numeric_content(context, column_name):
            # Check context keywords
            keyword_count = sum(1 for keyword in pattern_config['context_keywords'] 
                              if keyword.lower() in context)
            
            # Run custom validators if defined
            validators = pattern_config.get('validators', [])
            validation_passed = all(v(match.group()) for v in validators)
            
            return keyword_count >= 1 and validation_passed
        
        return False

    def _analyze_context(self, content: str, metadata: Dict) -> float:
        """Analyze file context based on indicators in filename"""
        indicators = ['confidential', 'private', 'sensitive']
        score = 0
        filename = metadata.get('filename', '').lower()

        for indicator in indicators:
            if indicator in filename:
                score += 5

        return score

    def _generate_findings(self, content: str) -> List[Dict]:
        """Generate findings from patterns"""
        findings = []
        for sensitivity_type, config in self.SENSITIVITY_PATTERNS.items():
            for pattern in config['patterns']:
                matches = re.finditer(pattern, content, re.IGNORECASE)
                for match in matches:
                    findings.append({
                        "type": sensitivity_type,
                        "match": match.group(),
                        "location": match.start()
                    })
        return findings

    def _combine_scores(self, sensitivity_score: float, context_score: float,
                       anomaly_score: float, user_behavior_score: float) -> float:
        """Combine different scores with adjusted weights based on findings"""
        weights = {
            'sensitivity_score': 0.5,
            'context_score': 0.2,
            'anomaly_score': 0.15,
            'user_behavior_score': 0.15
        }

        # If sensitivity_score is 100 (no findings), increase its weight
        if sensitivity_score >= 95:
            weights['sensitivity_score'] = 0.7
            weights['context_score'] = 0.15
            weights['anomaly_score'] = 0.1
            weights['user_behavior_score'] = 0.05

        combined_score = (
            sensitivity_score * weights['sensitivity_score'] +
            context_score * weights['context_score'] +
            anomaly_score * weights['anomaly_score'] +
            user_behavior_score * weights['user_behavior_score']
        )
        return round(combined_score, 2)

    def _determine_risk_level(self, score: float, findings: List[Dict]) -> SensitivityLevel:
        """Determine risk level with consideration for number of findings"""
        if len(findings) == 0:
            return SensitivityLevel.MINIMAL
        elif len(findings) <= 2 and score >= 75:
            return SensitivityLevel.LOW
        elif score >= 85:
            return SensitivityLevel.MINIMAL
        elif score >= 70:
            return SensitivityLevel.LOW
        elif score >= 50:
            return SensitivityLevel.MEDIUM
        elif score >= 30:
            return SensitivityLevel.HIGH
        else:
            return SensitivityLevel.CRITICAL

    def get_recent_sensitivity_scans(self):
        scans = [
            {'type': 'Personal Information', 'risk': 'High'},
            {'type': 'Financial Data', 'risk': 'Medium'},
            {'type': 'Confidential Documents', 'risk': 'Low'},
        ]
        return scans


class AnomalyDetector:
    def __init__(self, user):
        from django.contrib.auth.models import User
        self.user = user if isinstance(user, User) else User.objects.get(id=user)
        self.logger = logging.getLogger(__name__)

    def detect_anomalies(self) -> Tuple[List[str], float]:
        # Removed unnecessary try-except block
        anomalies = []
        risk_points = 0

        # Example: Rapid login attempts
        login_logs = UserActivityLog.objects.filter(
            user=self.user, action='Logged in'
        ).order_by('-timestamp')[:5]
        if len(login_logs) > 1:
            time_diff = login_logs[0].timestamp - login_logs[1].timestamp
            if time_diff < timedelta(minutes=2):
                anomalies.append("Rapid login attempts detected.")
                risk_points += 20

        # Check for suspicious file deletion spree
        delete_logs = list(UserActivityLog.objects.filter(
            user=self.user, action='Deleted file'
        ).order_by('-timestamp')[:5])
        if len(delete_logs) >= 3:
            time_diff = delete_logs[0].timestamp - delete_logs[-1].timestamp
            if time_diff < timedelta(minutes=5):  # Multiple deletions within 5 minutes
                anomalies.append("Suspicious file deletion spree detected.")
                risk_points += 10  # Assign score for this anomaly

        # Check for rapid uploads
        upload_logs = list(UserActivityLog.objects.filter(
            user=self.user, action='Uploaded file'
        ).order_by('-timestamp')[:5])
        if len(upload_logs) >= 3:
            time_diff = upload_logs[0].timestamp - upload_logs[-1].timestamp
            if time_diff < timedelta(minutes=10):  # Multiple uploads in under 10 minutes
                anomalies.append("Multiple file uploads in a short time detected.")
                risk_points += 10  # Assign score for this anomaly

        # Check for sudden activity spikes in task creation or deletion
        task_logs = list(UserActivityLog.objects.filter(
            user=self.user, action__in=['Created task', 'Deleted task']
        ).order_by('-timestamp')[:5])
        if len(task_logs) >= 3:
            time_diff = task_logs[0].timestamp - task_logs[-1].timestamp
            if time_diff < timedelta(minutes=15):  # Task creation/deletion spree in 15 minutes
                anomalies.append("Rapid task creation or deletion detected.")
                risk_points += 10  # Assign score for this anomaly

        # Check for project creation and deletion spikes
        project_logs = list(UserActivityLog.objects.filter(
            user=self.user, action__in=['Created project', 'Deleted project']
        ).order_by('-timestamp')[:5])
        if len(project_logs) >= 3:
            time_diff = project_logs[0].timestamp - project_logs[-1].timestamp
            if time_diff < timedelta(minutes=15):  # Multiple project actions within 15 minutes
                anomalies.append("Suspicious project creation or deletion detected.")
                risk_points += 10  # Assign score for this anomaly

        # Check for multiple OTP requests or password resets
        otp_logs = UserActivityLog.objects.filter(
            user=self.user, action='Requested OTP for password reset'
        ).order_by('-timestamp')[:5]
        if len(otp_logs) >= 2:
            time_diff = otp_logs[0].timestamp - otp_logs[1].timestamp
            if time_diff < timedelta(minutes=2):  # OTP requests in under 2 minutes
                anomalies.append("Multiple OTP requests detected.")
                risk_points += 10  # Assign score for this anomaly

        # Check for multiple password resets in a short time
        reset_logs = UserActivityLog.objects.filter(
            user=self.user, action='Reset password'
        ).order_by('-timestamp')[:5]
        if len(reset_logs) >= 2:
            time_diff = reset_logs[0].timestamp - reset_logs[1].timestamp
            if time_diff < timedelta(minutes=5):  # Multiple password resets within 5 minutes
                anomalies.append("Multiple password resets detected.")
                risk_points += 10  # Assign score for this anomaly

        # Normalize the anomaly score out of 100
        max_anomaly_score = 70  # Maximum possible score (based on the number of checks and severity)
        normalized_anomaly_score = min((risk_points / max_anomaly_score) * 100, 100)

        return anomalies, normalized_anomaly_score

    def get_anomalous_users(self):
        from Accounts.models import Profile
        anomalous_users = Profile.objects.filter(sensitivity_score__gte=50.0)
        return anomalous_users


class UserBehaviorAnalyzer:
    def __init__(self, user):
        from django.contrib.auth.models import User
        self.user = user if isinstance(user, User) else User.objects.get(id=user)
        self.logger = logging.getLogger(__name__)

    def analyze_behavior(self) -> float:
        # Removed unnecessary try-except block
        risk_points = 0
        username = self.user.username

        # Example: Multiple uploads of sensitive files
        recent_uploads = UserActivityLog.objects.filter(
            user=self.user,
            action='Uploaded file',
            timestamp__gte=datetime.now() - timedelta(hours=1)
        )
        for log in recent_uploads:
            # Process upload logs without unnecessary try-except
            if log.details:
                try:
                    details_dict = json.loads(log.details)
                    file_path = details_dict.get('file_path')
                except json.JSONDecodeError:
                    # Handle non-JSON details
                    file_path = None
                    self.logger.warning(f"Could not parse JSON from details: {log.details}")

                if file_path:
                    file_content = self._read_file(Path(file_path))
                    file_score = self._get_file_sensitivity_score(file_content)
                    if file_score < 50:
                        risk_points += (50 - file_score) * 0.2

        # Example: Multiple failed login attempts
        failed_logins = UserActivityLog.objects.filter(
            user=self.user,
            action='Failed login',
            timestamp__gte=datetime.now() - timedelta(hours=1)
        ).count()
        if failed_logins >= 3:
            risk_points += (failed_logins - 2) * 10  # Add risk points for each failed attempt beyond 2

        # Check time between uploads
        if recent_uploads.count() >= 2:
            latest_uploads = list(recent_uploads[:2])
            time_diff = latest_uploads[0].timestamp - latest_uploads[1].timestamp
            if time_diff < timedelta(minutes=5):
                risk_points += 10  # Additional score for rapid successive uploads
                self.logger.warning(f"Rapid successive uploads detected for {username}")

        # Normalize and return the final score
        max_behavior_score = 60
        normalized_behavior_score = min((risk_points / max_behavior_score) * 100, 100)

        self.logger.info(f"Final behavior score for {username}: {normalized_behavior_score}")
        return round(normalized_behavior_score, 2)

    def _read_file(self, file_path: Path) -> str:
        # Removed unnecessary try-except block
        if file_path.suffix.lower() == '.csv':
            df = pd.read_csv(file_path)
            return self._prepare_dataframe_content(df)
        elif file_path.suffix.lower() in ['.xls', '.xlsx']:
            df = pd.read_excel(file_path)
            return self._prepare_dataframe_content(df)
        else:
            with open(file_path, 'r', encoding='utf-8') as f:
                return f.read()
    
    def _prepare_dataframe_content(self, df: pd.DataFrame) -> str:
        """Convert DataFrame to searchable string format."""
        # Reuse the method from AdvancedDataLeakDetector
        detector = AdvancedDataLeakDetector()
        return detector._prepare_dataframe_content(df)
    
    def _get_file_sensitivity_score(self, content: str) -> float:
        """Compute the sensitivity score of the file content."""
        detector = AdvancedDataLeakDetector()
        return detector._calculate_sensitivity_score(content)
