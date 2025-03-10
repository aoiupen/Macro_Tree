"""설정 관리 모듈

애플리케이션 설정을 관리하는 기능을 제공합니다.
"""
import os
import json
import configparser
from typing import Any, Optional
from dotenv import load_dotenv


# 환경 변수 로드
load_dotenv()

# 기본 설정 값
DEFAULT_PROJECT_ROOT = os.path.abspath(".")
DEFAULT_DEBUG = False
DEFAULT_DB_NAME = "macro_tree"
DEFAULT_DB_USER = "postgres"
DEFAULT_DB_HOST = "localhost"
DEFAULT_DB_PORT = "5432"


class ConfigManager:
    """설정 관리 클래스
    
    애플리케이션 설정을 로드하고 관리하는 싱글톤 패턴 클래스입니다.
    """
    
    _instance = None
    _config = None
    _json_config = None
    
    def __new__(cls, config_path: Optional[str] = None):
        if cls._instance is None:
            cls._instance = super(ConfigManager, cls).__new__(cls)
            cls._instance._init(config_path)
        return cls._instance
    
    def _init(self, config_path: Optional[str] = None) -> None:
        """설정을 초기화합니다.
        
        Args:
            config_path: 설정 파일 경로 (선택적)
        """
        self._config = configparser.ConfigParser()
        self._json_config = {}
        
        # 기본 설정 파일 경로
        default_paths = [
            config_path,
            os.path.join(os.getcwd(), 'config.ini'),
            os.path.join(os.getcwd(), 'config.cfg'),
            os.path.join(os.getcwd(), 'config.json'),
            os.path.expanduser('~/.macro_tree/config.ini')
        ]
        
        # 설정 파일 로드 시도
        loaded = False
        for path in default_paths:
            if path and os.path.exists(path):
                try:
                    if path.endswith('.json'):
                        with open(path, 'r', encoding='utf-8') as f:
                            self._json_config = json.load(f)
                        loaded = True
                        break
                    else:
                        self._config.read(path)
                        loaded = True
                        break
                except Exception as e:
                    print(f"설정 파일 로드 오류: {e}")
        
        # 환경 변수에서 설정 로드
        self._load_from_env()
        
        # 기본 섹션 생성
        if 'database' not in self._config:
            self._config['database'] = {}
        if 'paths' not in self._config:
            self._config['paths'] = {}
            self._config['paths']['project_root'] = DEFAULT_PROJECT_ROOT
        if 'debug' not in self._config:
            self._config['debug'] = {}
            self._config['debug']['enabled'] = str(DEFAULT_DEBUG)
    
    def _load_from_env(self) -> None:
        """환경 변수에서 설정을 로드합니다."""
        # 데이터베이스 설정
        if 'database' not in self._config:
            self._config['database'] = {}
            
        db_section = self._config['database']
        
        if 'DB_NAME' in os.environ:
            db_section['name'] = os.environ['DB_NAME']
        else:
            db_section.setdefault('name', DEFAULT_DB_NAME)
            
        if 'DB_USER' in os.environ:
            db_section['user'] = os.environ['DB_USER']
        else:
            db_section.setdefault('user', DEFAULT_DB_USER)
            
        if 'DB_HOST' in os.environ:
            db_section['host'] = os.environ['DB_HOST']
        else:
            db_section.setdefault('host', DEFAULT_DB_HOST)
            
        if 'DB_PORT' in os.environ:
            db_section['port'] = os.environ['DB_PORT']
        else:
            db_section.setdefault('port', DEFAULT_DB_PORT)
        
        # 프로젝트 경로 설정
        if 'paths' not in self._config:
            self._config['paths'] = {}
            
        if 'PROJECT_ROOT' in os.environ:
            project_root = os.path.abspath(os.environ['PROJECT_ROOT'])
            if os.path.exists(project_root):
                self._config['paths']['project_root'] = project_root
            else:
                print(f"Error: PROJECT_ROOT '{project_root}' does not exist.")
                self._config['paths']['project_root'] = DEFAULT_PROJECT_ROOT
        else:
            self._config['paths'].setdefault('project_root', DEFAULT_PROJECT_ROOT)
            
        # 디버그 모드 설정
        if 'debug' not in self._config:
            self._config['debug'] = {}
            
        if 'DEBUG' in os.environ:
            self._config['debug']['enabled'] = str(os.environ['DEBUG'].lower() == 'true')
        else:
            self._config['debug'].setdefault('enabled', str(DEFAULT_DEBUG))
    
    def get(self, section: str, option: str, fallback: Any = None) -> Any:
        """설정 값을 가져옵니다.
        
        Args:
            section: 설정 섹션
            option: 설정 옵션
            fallback: 기본값 (선택적)
            
        Returns:
            설정 값 또는 기본값
        """
        # JSON 설정에서 값 가져오기 시도
        if self._json_config and section in self._json_config:
            if option in self._json_config[section]:
                return self._json_config[section][option]
        
        # INI 설정에서 값 가져오기 시도
        if section not in self._config:
            return fallback
        
        if option not in self._config[section]:
            return fallback
            
        return self._config[section][option]
    
    def set(self, section: str, option: str, value: Any) -> None:
        """설정 값을 설정합니다.
        
        Args:
            section: 설정 섹션
            option: 설정 옵션
            value: 설정 값
        """
        # JSON 설정에 값 설정
        if self._json_config:
            if section not in self._json_config:
                self._json_config[section] = {}
            self._json_config[section][option] = value
        
        # INI 설정에 값 설정
        if section not in self._config:
            self._config[section] = {}
            
        self._config[section][option] = str(value)
    
    def save(self, config_path: Optional[str] = None) -> bool:
        """현재 설정을 파일에 저장합니다.
        
        Args:
            config_path: 저장할 파일 경로 (선택적)
            
        Returns:
            저장 성공 여부
        """
        if not config_path:
            config_path = os.path.join(os.getcwd(), 'config.ini')
            
        try:
            os.makedirs(os.path.dirname(config_path), exist_ok=True)
            
            # JSON 파일로 저장
            if config_path.endswith('.json') and self._json_config:
                with open(config_path, 'w', encoding='utf-8') as f:
                    json.dump(self._json_config, f, indent=4)
            # INI 파일로 저장
            else:
                with open(config_path, 'w') as f:
                    self._config.write(f)
                    
            return True
        except Exception as e:
            print(f"설정 저장 오류: {e}")
            return False
            
    @property
    def project_root(self) -> str:
        """프로젝트 루트 디렉토리를 반환합니다.
        
        Returns:
            프로젝트 루트 디렉토리 경로
        """
        return self.get('paths', 'project_root', DEFAULT_PROJECT_ROOT)
        
    @property
    def debug_mode(self) -> bool:
        """디버그 모드 활성화 여부를 반환합니다.
        
        Returns:
            디버그 모드 활성화 여부
        """
        return self.get('debug', 'enabled', DEFAULT_DEBUG) == 'True'
        
    @property
    def db_name(self) -> str:
        """데이터베이스 이름을 반환합니다.
        
        Returns:
            데이터베이스 이름
        """
        return self.get('database', 'name', DEFAULT_DB_NAME)
        
    @property
    def db_user(self) -> str:
        """데이터베이스 사용자 이름을 반환합니다.
        
        Returns:
            데이터베이스 사용자 이름
        """
        return self.get('database', 'user', DEFAULT_DB_USER)
        
    @property
    def db_host(self) -> str:
        """데이터베이스 호스트를 반환합니다.
        
        Returns:
            데이터베이스 호스트
        """
        return self.get('database', 'host', DEFAULT_DB_HOST)
        
    @property
    def db_port(self) -> str:
        """데이터베이스 포트를 반환합니다.
        
        Returns:
            데이터베이스 포트
        """
        return self.get('database', 'port', DEFAULT_DB_PORT) 