from abc import ABC, abstractmethod

class ITreeStore(ABC):
    @abstractmethod
    def save(self, tree):
        """
        트리 데이터를 저장합니다.
        Args:
            tree: 저장할 트리 객체
        """
        pass

    @abstractmethod
    def load(self):
        """
        트리 데이터를 불러옵니다.
        Returns:
            dict 또는 트리 객체
        """
        pass 