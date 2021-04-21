from typing import Dict, List, Optional

from .person import Person
from .tournament_map import TournamentMap


class TournamentState:
    instance = None  # type: TournamentState

    def __init__(self):
        self.pros = {}  # type: Dict[int: Person]
        self.amateurs = {}  # type: Dict[int: Person]
        self.tournamentmaps = {}  # type: Dict[int: TournamentMap]
        TournamentState.instance = self

    def is_running(self) -> bool:
        return len(self.tournamentmaps) > 0

    async def update_ranks(self) -> None:
        people = self.get_all_people()
        self.pros = {}
        self.amateurs = {}
        for person in people:
            await person.player.update()
            self.register(person)

    def register(self, person: Person) -> None:
        if person.player.rank < 50000:
            self.pros[person.player.player_id] = person
        else:
            self.amateurs[person.player.player_id] = person

    def unregister(self, player_id: int) -> None:
        if player_id in self.pros:
            self.pros.pop(player_id)
        elif player_id in self.amateurs:
            self.amateurs.pop(player_id)

    def get_all_people(self) -> List[Person]:
        output = []  # type: List[Person]
        output.extend(self.pros.values())
        output.extend(self.amateurs.values())
        return output

    def get_pros(self) -> List[Person]:
        return list(self.pros)

    def get_amateurs(self) -> List[Person]:
        return list(self.amateurs)

    def get_person_by_player_id(self, player_id: int) -> Optional[Person]:
        if player_id in self.pros:
            return self.pros[player_id]
        elif player_id in self.amateurs:
            return self.amateurs[player_id]
        return None

    def get_person_by_discord_id(self, discord_id: int) -> Optional[Person]:
        for person in self.get_all_people():
            if person.discord_id == discord_id:
                return person
        return None

    def get_person_by_player_name(self, player_name: str) -> Optional[Person]:
        for person in self.get_all_people():
            if person.player.username == player_name:
                return person
        return None

    def get_tournamentmaps(self) -> List[TournamentMap]:
        return list(self.tournamentmaps.values())

    def get_tournamentmap_by_beatmapset_id(self, beatmapset_id: int) -> Optional[TournamentMap]:
        if beatmapset_id in self.tournamentmaps:
            return self.tournamentmaps[beatmapset_id]
        return None


TournamentState()
