# coding: utf-8
from ..quest_line import Quest, Line
from ..writer import Writer
from .. import commands as cmd

class EVENTS:
    QUEST_DESCRIPTION = 'quest_description'
    MOVE_TO_QUEST = 'move_to_quest'
    START_QUEST = 'start_quest'
    GIVE_POWER = 'give_power'

class HelpLine(Quest):

    def initialize(self, identifier, env, **kwargs):
        super(HelpLine, self).initialize(identifier, env, **kwargs)

        self.env_local.register('quest_help', env.new_quest(place_start=self.env_local.place_end,
                                                            person_start=self.env_local.person_end) )

    def create_line(self, env):
        self.line =  Line(sequence= [ cmd.Move(place=self.env_local.place_end, event=EVENTS.MOVE_TO_QUEST),
                                      cmd.Quest(quest=self.env_local.quest_help, event=EVENTS.START_QUEST),
                                      cmd.GivePower(person=self.env_local.person_start, 
                                                    depends_on=self.env_local.person_end, multiply=0.25,
                                                    event=EVENTS.GIVE_POWER)])
        env.quests[self.env_local.quest_help].create_line(env)

class HelpWriter(Writer):

    QUEST_TYPE = HelpLine.type()

    ACTIONS = { EVENTS.QUEST_DESCRIPTION: u'%(person_start)s попросил героя помочь %(person_end)s из %(place_end)s',
                EVENTS.MOVE_TO_QUEST: u'Герой направился к %(person_end)s'}

    LOG = { EVENTS.QUEST_DESCRIPTION: u'%(person_start)s попросил героя помочь %(person_end)s из %(place_end)s',
            EVENTS.MOVE_TO_QUEST: u'Путь до %(place_end)s нелёгкий, о чём же попросит меня %(person_end)s?'}
