from typing import Optional


class ObjList:
    def __init__(self, data: str) -> None:
        self.__data: str = data
        self.__prev: Optional[ObjList] = None
        self.__next: Optional[ObjList] = None

    @property
    def get_data(self) -> str:
        return self.__data

    def set_data(self, data: str) -> None:
        self.__data = data

    @property
    def get_prev(self) -> Optional['ObjList']:
        return self.__prev

    def set_prev(self, obj: Optional['ObjList']) -> None:
        self.__prev = obj

    @property
    def get_next(self) -> Optional['ObjList']:
        return self.__next

    def set_next(self, obj: Optional['ObjList']) -> None:
        self.__next = obj


class LinkedList:
    def __init__(self):
        self.head: ObjList | None = None
        self.tail: ObjList | None = None

    def get_data(self) -> list[str]:
        result = []
        if self.head:
            current_obj = self.head
            while current_obj:
                result.append(current_obj.get_data)
                current_obj = current_obj.get_next
        return result

    def add_obj(self, obj: ObjList) -> None:
        if self.head is None:
            self.head = obj
            self.tail = obj
        else:
            current_obj = self.tail
            current_obj.set_next(obj)
            obj.set_prev(current_obj)
            self.tail = obj

    def remove_obj(self) -> None:
        if self.tail:
            current_obj = self.tail
            if current_obj.get_prev:
                self.tail = current_obj.get_prev
                self.tail.set_next(None)
            else:
                self.head = None
                self.tail = None


res = LinkedList()
ob1 = ObjList("Data1")
ob2 = ObjList("Data2")
ob3 = ObjList("Data3")
ob4 = ObjList("Data4")
ob5 = ObjList("Data5")
res.add_obj(ob1)
res.add_obj(ob2)
res.add_obj(ob3)
res.remove_obj()
res.add_obj(ob4)
res.add_obj(ob5)
print(res.get_data())
