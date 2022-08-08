using System.Collections;
using System.Collections.Generic;
using UnityEngine;
using Valve.VR.Extras;

public class HintsManagerCanvas : MonoBehaviour
{
    [Header("Lasers")]
    public SteamVR_LaserPointer laserPointerRight;
    public SteamVR_LaserPointer laserPointerLeft;


    void Awake()
    {
        laserPointerRight.PointerIn += PointerInside;
        laserPointerRight.PointerOut += PointerOutside;
        laserPointerRight.PointerClick += PointerClick;

        laserPointerLeft.PointerIn += PointerInside;
        laserPointerLeft.PointerOut += PointerOutside;
        laserPointerLeft.PointerClick += PointerClick;

        laserPointerLeft.active = false;
        laserPointerRight.active = false;
    }

    public void PointerClick(object sender, PointerEventArgs e)
    {
        if (!e.target.CompareTag("UI")) { return; }
        
        if(e.target.name == "CanvasHints")
        {
            Debug.Log("hint!");
        }

    }

    public void PointerInside(object sender, PointerEventArgs e)
    {
        if (!e.target.CompareTag("UI")) { return; }

        if (e.target.name == "CanvasHints")
        {
            laserPointerLeft.active = true;
            laserPointerRight.active = true;
        }

    }

    public void PointerOutside(object sender, PointerEventArgs e)
    {
        if (!e.target.CompareTag("UI")) { return; }

        if (e.target.name == "CanvasHints")
        {
            laserPointerLeft.active = false;
            laserPointerRight.active = false;
        }

    }
}
