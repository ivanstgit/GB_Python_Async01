"""Реализация паттерна 'Наблюдатель'"""


from abc import abstractmethod
from typing import List


class Observer():
    """Наблюдатель"""
    @abstractmethod
    def model_changed(self, notifier=None):
        """Необходимо реализовать данный метод для получения уведомлений"""
        raise NotImplementedError


class ObserverNotifier():
    """Объект, за которым ведется наблюдение"""
    _observers: List[Observer]

    def __init__(self) -> None:
        self._observers = list()

    def add_observer(self, observer: Observer):
        """Добавить наблюдателя"""
        self._observers.append(observer)

    def remove_observer(self, observer: Observer):
        """Удалить наблюдателя"""
        self._observers.remove(observer)

    def notify_observers(self):
        """Уведомить наблюдателей"""
        for observer in self._observers:
            observer.model_changed(self)
