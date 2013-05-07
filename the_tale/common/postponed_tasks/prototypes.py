# coding: utf-8

import sys
import datetime

from django.core.urlresolvers import reverse

from dext.utils import s11n

from common.utils import discovering
from common.utils.prototypes import BasePrototype
from common.utils.discovering import discover_classes

from common.postponed_tasks.models import PostponedTask, POSTPONED_TASK_STATE, POSTPONED_TASK_LOGIC_RESULT
from common.postponed_tasks.exceptions import PostponedTaskException
from common.postponed_tasks.conf import postponed_tasks_settings


_INTERNAL_LOGICS = {}


class PostponedLogic(object):

    TYPE = None

    def __init__(self): pass

    def process(self, main_task):
        raise NotImplemented

    def serialize(self): return {}

    @classmethod
    def deserialize(cls, data):
        return cls(**data)

    @property
    def processed_data(self): return {}

    def processed_view(self, resource): pass

    @property
    def error_message(self):
        raise NotImplemented

    @property
    def uuid(self): return None


def _register_postponed_tasks(container, objects):

    for obj in discover_classes(objects, PostponedLogic):
        if obj.TYPE in container:
            raise PostponedTaskException(u'interanl logic "%s" for postponed task has being registered already' % obj.TYPE)
        if obj.TYPE is None:
            raise PostponedTaskException(u'interanl logic "%r" for postponed task does not define TYPE' % obj)
        container[obj.TYPE] = obj


@discovering.automatic_discover(_INTERNAL_LOGICS, 'postponed_tasks')
def autodiscover(container, module):
    _register_postponed_tasks(container, [getattr(module, name) for name in dir(module)])


class PostponedTaskPrototype(BasePrototype):
    _model_class = PostponedTask
    _readonly = ('id', 'internal_type', 'created_at', 'updated_at', 'live_time')
    _bidirectional = ('internal_state', 'internal_result', 'comment')
    _get_by = ('id', )

    def __init__(self, **kwargs):
        super(PostponedTaskPrototype, self).__init__(**kwargs)
        self._postsave_actions = []

    @property
    def type(self): return self.internal_type

    @property
    def status_url(self): return reverse('postponed-tasks:status', args=[self.id])

    @property
    def wait_url(self): return reverse('postponed-tasks:wait', args=[self.id])

    def get_state(self):
        if not hasattr(self, '_state'):
            self._state = POSTPONED_TASK_STATE(self._model.state)
        return self._state
    def set_state(self, value):
        self.state.update(value)
        self._model.state = self.state.value
    state = property(get_state, set_state)

    @property
    def internal_logic(self):
        if not hasattr(self, '_internal_logic'):
            self._internal_logic = _INTERNAL_LOGICS[self.type].deserialize(s11n.from_json(self._model.internal_data))
        return self._internal_logic

    def save(self):
        self._model.internal_data = s11n.to_json(self.internal_logic.serialize())
        self._model.internal_state = self._model.internal_state if isinstance(self._model.internal_state, int) else self._model.internal_state.value
        self._model.save()

    def remove(self):
        self._model.delete()

    @classmethod
    def reset_all(cls):
        PostponedTask.objects.filter(state=POSTPONED_TASK_STATE.WAITING).update(state=POSTPONED_TASK_STATE.RESETED)

    @classmethod
    def check_if_used(cls, internal_type, internal_uuid):
        return PostponedTask.objects.filter(internal_type=internal_type,
                                            internal_uuid=internal_uuid,
                                            state=POSTPONED_TASK_STATE.WAITING).exists()

    @classmethod
    def get_processed_tasks_query(cls):
        return PostponedTask.objects.exclude(state=POSTPONED_TASK_STATE.WAITING)

    @classmethod
    def remove_old_tasks(cls):
        cls.get_processed_tasks_query().filter(updated_at__lt=datetime.datetime.now() - datetime.timedelta(seconds=postponed_tasks_settings.TASK_LIVE_TIME)).delete()

    @classmethod
    def create(cls, task_logic, live_time=None):
        model = PostponedTask.objects.create(internal_type=task_logic.TYPE,
                                             internal_uuid=task_logic.uuid,
                                             internal_state=task_logic.state if isinstance(task_logic.state, int) else task_logic.state.value,
                                             internal_data=s11n.to_json(task_logic.serialize()),
                                             live_time=live_time)

        return cls(model=model)

    def add_postsave_action(self, action):
        self._postsave_actions.append(action)

    def extend_postsave_actions(self, actions):
        self._postsave_actions.extend(actions)

    def do_postsave_actions(self):
        if self.state.is_waiting or self.state.is_processed:
            for action in self._postsave_actions:
                action()

    def cmd_wait(self):
        from common.postponed_tasks.workers.environment import workers_environment
        workers_environment.refrigerator.cmd_wait_task(self.id)

    def process(self, logger, **kwargs):

        if not self.state.is_waiting:
            return

        if self.live_time is not None and datetime.datetime.now() > self.created_at + datetime.timedelta(seconds=self.live_time):
            self.state = POSTPONED_TASK_STATE.TIMEOUT
            self.save()
            return

        try:

            old_internal_result = self.internal_result

            self.internal_result = self.internal_logic.process(self, **kwargs)

            if self.internal_result == POSTPONED_TASK_LOGIC_RESULT.SUCCESS:
                self.state = POSTPONED_TASK_STATE.PROCESSED
            elif self.internal_result == POSTPONED_TASK_LOGIC_RESULT.ERROR:
                self.state = POSTPONED_TASK_STATE.ERROR
            elif self.internal_result == POSTPONED_TASK_LOGIC_RESULT.CONTINUE:
                pass
            elif self.internal_result == POSTPONED_TASK_LOGIC_RESULT.WAIT:
                if old_internal_result != POSTPONED_TASK_LOGIC_RESULT.WAIT:
                    self.extend_postsave_actions([lambda: self.cmd_wait()])
            else:
                raise PostponedTaskException(u'unknown process result %r' % (self.process_result, ))

            self.internal_state = self.internal_logic.state
            self.save()

        except Exception, e:

            logger.error('EXCEPTION: %s' % e)

            exception_info = sys.exc_info()

            logger.error('Worker exception: %r' % self,
                         exc_info=exception_info,
                         extra={} )

            self.state = POSTPONED_TASK_STATE.EXCEPTION
            self.comment = u'%s\n\n%s\n\n %s' % exception_info
            self.save()
