using System.Collections;
using System.Collections.Generic;
using UnityEngine;

[System.Serializable]
public class PlayerData
{
    public bool howToPlayButtonPressed;
    public PlayerData(Playerr player)
    {
        howToPlayButtonPressed = player.howToPlayButtonPressed;
    }
}
