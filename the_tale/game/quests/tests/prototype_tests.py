# coding: utf-8
import mock

from django.test import TestCase

from dext.settings import settings

from common.utils.fake import FakeWorkerCommand

from accounts.logic import register_user
from game.heroes.prototypes import HeroPrototype
from game.logic_storage import LogicStorage


from game.logic import create_test_map
from game.actions.prototypes import ActionQuestPrototype
from game.quests.logic import create_random_quest_for_hero
from game.prototypes import TimePrototype


class QuestPrototypeTest(TestCase):

    def setUp(self):

        settings.refresh()
        current_time = TimePrototype.get_current_time()
        current_time.increment_turn()

        create_test_map()

        result, account_id, bundle_id = register_user('test_user')

        self.hero = HeroPrototype.get_by_account_id(account_id)
        self.storage = LogicStorage()
        self.storage.add_hero(self.hero)
        self.action_idl = self.storage.heroes_to_actions[self.hero.id][-1]

        self.quest = create_random_quest_for_hero(self.hero)
        self.action_quest = ActionQuestPrototype.create(self.action_idl, quest=self.quest)

    def tearDown(self):
        pass

    def complete_quest(self):
        current_time = TimePrototype.get_current_time()

        while not self.action_idl.leader:
            self.storage.process_turn()
            current_time.increment_turn()

    def test_initialization(self):
        self.assertEqual(TimePrototype.get_current_turn_number(), self.hero.quests_history[self.quest.env.root_quest.type()])


    def test_power_on_end_quest_for_fast_account_hero(self):
        fake_cmd = FakeWorkerCommand()

        with mock.patch('game.workers.environment.workers_environment.highlevel.cmd_change_person_power', fake_cmd):
            self.complete_quest()

        self.assertFalse(fake_cmd.commands)

    def test_power_on_end_quest_for_normal_account_hero(self):

        self.hero.is_fast = False

        fake_cmd = FakeWorkerCommand()

        with mock.patch('game.workers.environment.workers_environment.highlevel.cmd_change_person_power', fake_cmd):
            self.complete_quest()

        self.assertTrue(fake_cmd.commands)
