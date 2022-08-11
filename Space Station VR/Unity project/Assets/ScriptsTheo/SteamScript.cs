using System.Collections;
using System.Collections.Generic;
using UnityEngine;
using Steamworks;

public class SteamScript : MonoBehaviour
{
    // Start is called before the first frame update
    void Start()
    {
        if (!SteamManager.Initialized) { return; }

        string name = SteamFriends.GetPersonaName();
        Debug.Log("steam name: " + name);
    }

    // Update is called once per frame
    void Update()
    {
        
    }

    public bool TryGetAchievement(string achievementName, bool condition)
    {
        if (SteamManager.Initialized && condition)
        {
            SteamUserStats.GetAchievement(achievementName, out bool achievementAlreadyCompleted);

            if (!achievementAlreadyCompleted)
            {
                SteamUserStats.SetAchievement(achievementName);
                SteamUserStats.StoreStats();
                return true;
            }
        }
        return false;

    }
}
