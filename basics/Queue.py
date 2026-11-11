import math

class EmptyQueueException(Exception):
    pass


class FullQueueException(Exception):
    pass


class IncorrectQueueJob(Exception):
    pass


class Queue:
    _data = None
    _size = None
    _front = None
    _rear = None
    _data = None
    _dynamic = True

    def __init__(self) -> None:
        self._size = 0
        self._front = 0
        self._rear = 0
        self._capacity = 20
        self._data = [None] * self._capacity
        self._dynamic = True

    def length(self):
        return self._size

    def is_empty(self):
        return self._size == 0

    def is_full(self):
        return self._size == self._capacity

    def first(self):
        if self.is_empty():
            raise EmptyQueueException("Queue is Empty")
        return self._data[self._front]

    def last(self):
        if self.is_empty():
            raise EmptyQueueException("Queue is Empty")
        return self._data[self._rear - 1]

    def enqueue(self, value):
        if self.is_full():
            if self._dynamic:
                self._resize(self._capacity * 2)
            else:
                raise FullQueueException("Queue is full")
        self._data[self._rear] = value
        self._rear = (self._rear + 1) % self._capacity
        self._size += 1

    def dequeue(self):
        if self.is_empty():
            raise EmptyQueueException("Cannot dequeue an empty Queue")
        value = self._data[self._front]
        self._data[self._front] = None
        self._front = (self._front + 1) % self._capacity
        self._size -= 1
        return value

    def _resize(self, new_cap):
        new_data = [None] * new_cap
        for i in range(self.size):
            new_data[i] = self._data[(self._front + i) % self._capacity]
        self._data = new_data
        self._capacity = new_cap
        self._front = 0
        self._rear = self.size

    def __str__(self) -> str:
        return str(self._data)




class ScanQueue(Queue):
    def __init__(self, average_time_per_frame=1.5) -> None:
        self._average_time_per_frame = average_time_per_frame
        self._active = None
        super().__init__()

    def set_active(self, job) -> None:
        self._active = job

    def _job_minutes(self, job) -> int:
        return math.ceil(self._average_time_per_frame * job.frame_count / 60)

    def estimated_wait(self, position: int) -> int:
        if position < 1 or position > self._size:
            raise ValueError(f"position {position} is outside the queue")
        total = 0
        for job in self._data:
            if job is not None:
                total += self._job_minutes(job) 

        return total

        
