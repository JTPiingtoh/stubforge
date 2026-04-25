from typing import TypedDict

freeChampionIdsForNewPlayers_dto = TypedDict("freeChampionIdsForNewPlayers_dto", {
   "name" : str,
   "age" : int,
   "job" : str,
   "life" : str,
})

details_dto = TypedDict("details_dto", {
   "name" : str,
   "age" : int,
   "job" : str,
})

listOfDetails_dto = TypedDict("listOfDetails_dto", {
   "name" : str,
   "age" : int,
   "date" : details_dto,
})

test_dto = TypedDict("test_dto", {
   "freeChampionIds" : list[int],
   "freeChampionIdsForNewPlayers" : list[freeChampionIdsForNewPlayers_dto | int],
   "maxNewPlayerLevel" : int,
   "foo" : str,
   "bar" : int,
   "details" : details_dto,
   "list_of_details" : list[listOfDetails_dto | details_dto],
   "list_of_any" : list[listOfDetails_dto | int | str],
})

matchV4_dto = TypedDict("matchV4_dto", {
   "leagueId" : str,
   "queueType" : str,
   "tier" : str,
   "rank" : str,
   "puuid" : str,
   "leaguePoints" : int,
   "wins" : int,
   "losses" : int,
   "veteran" : bool,
   "inactive" : bool,
   "freshBlood" : bool,
   "hotStreak" : bool,
})

