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
