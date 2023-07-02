class Observer():

    def modelChanged(self):
        raise NotImplemented


class ObserverExt(Observer):

    def modelChanged(self, notifier):
        raise NotImplemented


class ObserverNotifier():

    def __init__(self) -> None:
        self._observers = list()  # список наблюдателей

    def addObserver(self, inObserver: Observer):
        self._observers.append(inObserver)

    def removeObserver(self, inObserver: Observer):
        self._observers.remove(inObserver)

    def notifyObservers(self):
        for x in self._observers:
            if isinstance(x, ObserverExt):
                x.modelChanged(self)
            else:
                x.modelChanged()
