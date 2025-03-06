"""설정 관리 모듈

애플리케이션 설정을 관리합니다.
"""
import os
import json
from typing import Dict, Any, Optional
from dotenv import load_dotenv


class ConfigManager:
    """설정 관리 클래스
    
    애플리케이션 설정을 로드하고 관리합니다.
    기존 config.py와 .env 파일의 설정을 통합하여 관리합니다.
    """
    
    _instance = None
    _config = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._load_config()
        return cls._instance
    
    def _load_config(self) -> None:
        """설정 파일과 환경 변수에서 설정을 로드합니다."""
        # 환경 변수 로드
        load_dotenv()
        
        # 기본 설정
        self._config = {
            "window": {
                "title": "Macro",
                "geometry": [100, 100, 500, 400]
            },
            "tree": {
                "columns": ["Name", "M/K", "Value", "Act", ""],
                "column_width": 10
            },
            "database": {
                "name": os.getenv("DB_NAME"),
                "user": os.getenv("DB_USER"),
                "host": os.getenv("DB_HOST"),
                "port": os.getenv("DB_PORT")
            }
        }
        
        # 설정 파일이 있으면 로드 (민감하지 않은 정보만)
        config_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "config.json")
        if os.path.exists(config_path):
            try:
                with open(config_path, "r", encoding="utf-8") as f:
                    file_config = json.load(f)
                    # 데이터베이스 정보는 제외하고 업데이트
                    if "database" in file_config:
                        del file_config["database"]
                    # 기본 설정을 파일 설정으로 업데이트
                    self._update_config(self._config, file_config)
            except Exception as e:
                print(f"설정 파일 로드 오류: {e}")
                
        # 기존 config.py에서 추가 설정 로드 (필요한 경우)
        try:
            import config as app_config
            # config.py에서 필요한 설정 가져오기
            if hasattr(app_config, 'PROJECT_ROOT'):
                self._config["project"] = {"root": app_config.PROJECT_ROOT}
        except ImportError:
            pass
    
    def _update_config(self, target: Dict[str, Any], source: Dict[str, Any]) -> None:
        """설정 딕셔너리를 재귀적으로 업데이트합니다.
        
        Args:
            target: 업데이트할 대상 딕셔너리
            source: 업데이트 소스 딕셔너리
        """
        for key, value in source.items():
            if key in target and isinstance(target[key], dict) and isinstance(value, dict):
                self._update_config(target[key], value)
            else:
                target[key] = value
    
    def get(self, section: str, key: Optional[str] = None) -> Any:
        """설정 값을 반환합니다.
        
        Args:
            section: 설정 섹션
            key: 설정 키 (None이면 섹션 전체 반환)
            
        Returns:
            설정 값 또는 섹션 딕셔너리
            
        Raises:
            KeyError: 존재하지 않는 섹션이나 키인 경우
        """
        if section not in self._config:
            raise KeyError(f"존재하지 않는 설정 섹션: {section}")
        
        if key is None:
            return self._config[section]
        
        if key not in self._config[section]:
            raise KeyError(f"존재하지 않는 설정 키: {section}.{key}")
        
        return self._config[section][key]
    
    def set(self, section: str, key: str, value: Any) -> None:
        """설정 값을 설정합니다.
        
        Args:
            section: 설정 섹션
            key: 설정 키
            value: 설정 값
            
        Raises:
            KeyError: 존재하지 않는 섹션인 경우
        """
        if section not in self._config:
            self._config[section] = {}
        
        self._config[section][key] = value
    
    def save(self) -> None:
        """현재 설정을 파일에 저장합니다.
        민감한 정보(데이터베이스 정보)는 저장하지 않습니다.
        """
        config_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "config.json")
        try:
            # 저장할 설정 복사
            save_config = {}
            for section, values in self._config.items():
                if section != "database":  # 데이터베이스 정보는 제외
                    save_config[section] = values
                    
            with open(config_path, "w", encoding="utf-8") as f:
                json.dump(save_config, f, indent=4)
        except Exception as e:
            print(f"설정 파일 저장 오류: {e}")