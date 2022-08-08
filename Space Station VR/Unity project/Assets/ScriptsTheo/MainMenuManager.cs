using System.Collections;
using System.Collections.Generic;
using UnityEngine;
using Valve.VR.Extras;

public class MainMenuManager : MonoBehaviour
{
    public SteamVR_LaserPointer laserPointer;

    // Start is called before the first frame update
    void Start()
    {
        
    }

    // Update is called once per frame
    void Update()
    {
        
    }


    public void ExitGame()
    {
        Application.Quit();
    }

    

    void Awake()
    {
        laserPointer.PointerIn += PointerInside;
        laserPointer.PointerOut += PointerOutside;
        laserPointer.PointerClick += PointerClick;
    }

    public void PointerClick(object sender, PointerEventArgs e)
    {
        if (!e.target.CompareTag("UI")) { return; }
        switch (e.target.name)
        {
            case "StartButton":

                break;
            case "HowToPlayButton":

                break;
            case "SettingsButton":

                break;
            case "ExitButton":

                break;
            default:
                break;

        }
    }

    public void PointerInside(object sender, PointerEventArgs e)
    {
        Debug.Log("inside: " + e.target.name);
    }

    public void PointerOutside(object sender, PointerEventArgs e)
    {
        Debug.Log("outside: " + e.target.name);
    }
}
