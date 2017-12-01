# coding=utf-8
import sys;
# reload(sys) # Python2.5 初始化后会删除 sys.setdefaultencoding 这个方法，我们需要重新载入
# sys.setdefaultencoding('utf-8')
import threading


class Task(object):
    def run(self, args):
        pass


class Schedule(object):
    def __init__(self, thread_num=None,finish=None):
        self.buffer_schedule = []
        self.thread_num = thread_num
        self.execute_num = 0
        self._finish = finish

    def finish(self):
        self._finish and self._finish()

    def schedule_end(self):
        self.execute_num = self.execute_num-1
        if len(self.buffer_schedule) is not 0:
            thread = self.buffer_schedule.pop()
            # thread.start()
            self.start_task(thread)
        if self.execute_num==0 and len(self.buffer_schedule) is 0:
            self._finish()


    def start_task(self, thread):
        thread.start()
        self.execute_num = self.execute_num + 1

    def clear(self):
        self.execute_num = 0
        self.buffer_schedule = []

    @staticmethod
    def run(task, args, schedule):
        task.run(args)
        schedule.schedule_end()

    def append_task(self, task, args=None):
        thread = threading.Thread(target=Schedule.run, args=(task, args, self))
        if self._is_full():
            self.buffer_schedule.append(thread)
        else:
            self.start_task(thread)

    def _is_full(self):
        if self.thread_num is None:
            return False
        return True if self.execute_num >= self.thread_num else False
