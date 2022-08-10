using System.Collections;
using System.Collections.Generic;
using UnityEngine;
using System;

public class Player : MonoBehaviour
{
    [SerializeField]
    public bool howToPlayButtonPressed;

    private MainMenuManager MM;

    private void Awake()
    {
        DontDestroyOnLoad(this);
        var list = FindObjectsOfType<Player>();
        //instance = this;
        if (list.Length > 1)
        {
            for (int i = 1; i < list.Length; i++)
            {
                Destroy(list[i].gameObject);
            }
        }
        DontDestroyOnLoad(this);

        MM = FindObjectOfType<MainMenuManager>();
    }

    public void ResetPlayer()
    {
        howToPlayButtonPressed = false;

        SavePlayer();
    }

    public void SavePlayer()
    {
        Debug.Log("Player Save!");
        SaveSystem.SavePlayer(this);
    }

    public void LoadPlayer()
    {
        MM = FindObjectOfType<MainMenuManager>();

        PlayerData data = SaveSystem.LoadPlayer();
        if (data != null)
        {
            howToPlayButtonPressed = data.howToPlayButtonPressed;
            
            if(MM != null)
            {
                MM.howToPlayButtonPressedFromSave = howToPlayButtonPressed;
            }
        }
        else
        {
            ResetPlayer();
        }

    }
}
