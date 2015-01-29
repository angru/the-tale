# coding: utf-8

import random
import datetime

from the_tale.game.balance.power import Power

from the_tale.game import relations as game_relations

from the_tale.game.heroes import relations

from the_tale.game.artifacts.storage import artifacts_storage
from the_tale.game.cards import objects as cards_objects


class ShopAccessorsMixin(object):

    def purchase_energy_bonus(self, energy):
        self.add_energy_bonus(energy)

    def purchase_reset_preference(self, preference_type):
        if preference_type.is_ENERGY_REGENERATION_TYPE:
            self.preferences.set_energy_regeneration_type(self.race.energy_regeneration, change_time=datetime.datetime.fromtimestamp(0))
        elif preference_type.is_RISK_LEVEL:
            self.preferences.set_risk_level(relations.RISK_LEVEL.NORMAL, change_time=datetime.datetime.fromtimestamp(0))
        elif preference_type.is_ARCHETYPE:
            self.preferences.set_archetype(game_relations.ARCHETYPE.NEUTRAL, change_time=datetime.datetime.fromtimestamp(0))
        elif preference_type.is_COMPANION_DEDICATION:
            self.preferences.set_companion_dedication(relations.COMPANION_DEDICATION.NORMAL, change_time=datetime.datetime.fromtimestamp(0))
        else:
            self.preferences._reset(preference_type)

    def purchase_change_habits(self, habit_type, habit_value):
        self.change_habits(habit_type=habit_type, habit_value=habit_value)

    def purchase_reset_abilities(self):
        self.abilities.reset()

    def purchase_rechooce_abilities_choices(self):
        self.abilities.rechooce_choices()

    def purchase_experience(self, experience):
        self.add_experience(experience)

    def purchase_artifact(self, rarity, better):
        distribution = self.preferences.archetype.power_distribution

        power = Power.better_artifact_power_randomized(distribution, self.level) if better else Power.artifact_power_randomized(distribution, self.level)

        artifacts_storage.sync()

        artifact = random.choice(artifacts_storage.artifacts).create_artifact(level=self.level,
                                                                              power=power,
                                                                              rarity=rarity)
        self.put_loot(artifact, force=True)

        self.actions.request_replane()

        return artifact

    def purchase_card(self, card_type, count):
        for i in xrange(count):
            self.cards.add_card(cards_objects.Card(card_type, available_for_auction=True))
