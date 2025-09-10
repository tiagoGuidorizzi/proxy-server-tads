# observer.py
from typing import List, Dict, Any

class Observer:
    def update(self, event: Dict[str, Any]):
        raise NotImplementedError("Observer subclasses must implement update()")

class Observable:
    def __init__(self):
        self._observers: List[Observer] = []

    def attach(self, observer: Observer):
        if observer not in self._observers:
            self._observers.append(observer)

    def detach(self, observer: Observer):
        if observer in self._observers:
            self._observers.remove(observer)

    def notify(self, event: Dict[str, Any]):
        for observer in self._observers:
            observer.update(event)
