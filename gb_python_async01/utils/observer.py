class Observer():

    def modelChanged(self):
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
            x.modelChanged()
