from typing import TypedDict

match_v4_TYPE_1 = TypedDict("match_v4_TYPE_1", {
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
_2,
})
test_TYPE_4 = TypedDict("test_TYPE_4", {
   "freeChampionIds" : list[int],
   "freeChampionIdsForNewPlayers" : list[int | test_TYPE_1],
   "maxNewPlayerLevel" : int,
   "foo" : str,
   "bar" : int,
   "details" : test_TYPE_2,
   "list_of_details" : list[test_TYPE_2 | test_TYPE_3],
   "list_of_any" : list[int | str | test_TYPE_3],
})
