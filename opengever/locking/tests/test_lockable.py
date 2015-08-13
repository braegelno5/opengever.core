from datetime import datetime
from datetime import timedelta
from ftw.builder import Builder
from ftw.builder import create
from ftw.testing import freeze
from opengever.base.model import create_session
from opengever.locking.model import Lock
from opengever.locking.model.locks import utcnow_tz_aware
from opengever.meeting.meeting_wrapper import MeetingWrapper
from opengever.testing import FunctionalTestCase
from plone.app.testing import TEST_USER_ID
from plone.locking.interfaces import ILockable
import pytz


class TestSQLLockable(FunctionalTestCase):

    def setUp(self):
        super(TestSQLLockable, self).setUp()
        self.session = create_session()
        self.committee = create(Builder('committee_model'))
        self.meeting = create(Builder('meeting').having(
            committee=self.committee,
            start=datetime(2010, 1, 1)))

        self.wrapper = MeetingWrapper(self.meeting)

    def test_lock_use_model_class_name_as_object_type(self):
        lockable = ILockable(self.wrapper)
        lockable.lock()

        lock = Lock.query.first()
        self.assertEqual(u'Meeting', lock.object_type)

    def test_lock_token_contains_object_type_and_is_separated_with_a_colon(self):
        lockable = ILockable(self.wrapper)
        lockable.lock()

        lock = Lock.query.first()
        self.assertEqual(u'Meeting:1', lock.token)

    def test_locked(self):
        lockable = ILockable(self.wrapper)
        lockable.lock()
        self.assertTrue(lockable.locked())

    def test_refresh_locks_update_locks_to_current_time(self):
        lockable = ILockable(self.wrapper)
        lockable.lock()

        with freeze(datetime(2015, 03, 10, 12, 05, tzinfo=pytz.utc)):
            lockable.refresh_lock()

        lock = Lock.query.one()
        self.assertEqual(
            datetime(2015, 03, 10, 12, 05, tzinfo=pytz.utc), lock.time)

    def test_unlock_does_nothing_for_not_locked_items(self):
        lockable = ILockable(self.wrapper)
        lockable.unlock()

    def test_unlock_delete_lock_if_a_lock_existsts(self):
        lockable = ILockable(self.wrapper)
        lockable.lock()
        lockable.unlock()
        self.assertFalse(lockable.locked())
        self.assertEquals(0, Lock.query.count())

    def test_unlock_does_not_check_if_lock_is_stealable_when_stealable_only_is_false(self):
        lockable = ILockable(self.wrapper)
        lockable.lock()

        # manually change lock creator
        lock = Lock.query.first()
        lock.creator = 'other-user'

        lockable.unlock()
        self.assertFalse(lockable.locked())

    def test_clear_locks_remove_all_locks_on_the_object(self):
        lockable = ILockable(self.wrapper)
        lockable.lock()
        self.assertTrue(lockable.locked())

        lockable.clear_locks()
        self.assertFalse(lockable.locked())

    def test_locked_is_true_if_a_valid_lock_exists(self):
        lock = Lock(object_type='Meeting',
                     object_id=1,
                     creator=TEST_USER_ID,
                     time=utcnow_tz_aware() - timedelta(seconds=100))
        self.session.add(lock)

        lockable = ILockable(self.wrapper)
        self.assertTrue(lockable.locked())

    def test_locked_is_false_if_lock_is_invalid(self):
        lock = Lock(object_type='Meeting',
                     object_id=1,
                     creator=TEST_USER_ID,
                     time=utcnow_tz_aware() - timedelta(seconds=800))
        self.session.add(lock)

        lockable = ILockable(self.wrapper)
        self.assertFalse(lockable.locked())

    def test_locked_is_false_if_no_lock_exists(self):
        lockable = ILockable(self.wrapper)
        self.assertFalse(lockable.locked())

    def test_can_safely_unlock_is_true_if_no_lock_exists(self):
        lockable = ILockable(self.wrapper)
        self.assertTrue(lockable.can_safely_unlock())

    def test_can_safely_unlock_is_true_if_a_lock_of_the_current_user_exists(self):
        lock = Lock(object_type='Meeting',
                    object_id=1,
                    creator=TEST_USER_ID,
                    lock_type=u'plone.locking.stealable',
                    time=utcnow_tz_aware())
        self.session.add(lock)

        self.assertTrue(ILockable(self.wrapper).can_safely_unlock())

    def test_can_safely_unlock_is_false_if_item_is_locked_by_an_other_user(self):
        lock = Lock(object_type='Meeting',
                    object_id=1,
                    creator=u'hugo.boss',
                    lock_type=u'plone.locking.stealable',
                    time=utcnow_tz_aware())
        self.session.add(lock)

        self.assertFalse(ILockable(self.wrapper).can_safely_unlock())

    def test_lock_info_returns_an_list_of_dicts_of_all_valid_locks(self):
        # valid
        lock1 = Lock(object_type='Meeting',
                     object_id=1,
                     creator=TEST_USER_ID,
                     lock_type=u'plone.locking.stealable',
                     time=utcnow_tz_aware() - timedelta(seconds=100))
        self.session.add(lock1)
        self.assertEquals(
            [{'creator': TEST_USER_ID,
              'time': lock1.time,
              'token': 'Meeting:1',
              'type': u'plone.locking.stealable'}],
            ILockable(self.wrapper).lock_info())

        # invalid
        lock1.time = utcnow_tz_aware() - timedelta(seconds=800)
        self.assertEquals([], ILockable(self.wrapper).lock_info())

    def test_during_lock_creation_the_expired_locks_gets_cleared(self):
        lock_1 = Lock(object_type='Meeting',
                      object_id=12345,
                      creator=TEST_USER_ID,
                      lock_type=u'plone.locking.stealable',
                      time=utcnow_tz_aware() - timedelta(seconds=1000))
        self.session.add(lock_1)

        lock_2 = Lock(object_type='Meeting',
                      object_id=56789,
                      creator=TEST_USER_ID,
                      lock_type=u'plone.locking.stealable',
                      time=utcnow_tz_aware() - timedelta(seconds=800))
        self.session.add(lock_2)

        ILockable(self.wrapper).lock()

        locks = Lock.query.all()

        self.assertEquals(1, len(locks))
        self.assertNotIn(lock_1, locks)
        self.assertNotIn(lock_2, locks)
