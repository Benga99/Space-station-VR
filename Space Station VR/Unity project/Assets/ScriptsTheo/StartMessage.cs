using System;
using System.Collections;
using System.Collections.Generic;
using UnityEngine;
using Valve.VR;
using UnityEngine.UI;

public class StartMessage : MonoBehaviour
{
    public Canvas MessageCanvas;
    //public string UserName = "";

    public SteamVR_Action_Boolean grabPinch; //Grab Pinch is the trigger, select from inspecter
    public SteamVR_Input_Sources inputSource = SteamVR_Input_Sources.Any;//which controller
                                                                         // Use this for initialization


    private void Start()
    {
        MessageCanvas.GetComponent<Text>().text = $"Hello Captain! You just woke up and realized your crew left you behind. The aliens will take over the ship shortly and you are the only one left on the ship. Find your way out! Press SELECT to continue!";
    }

    void OnEnable()
    {
        if (grabPinch != null)
        {
            grabPinch.AddOnChangeListener(OnTriggerPressedOrReleased, inputSource);
        }
    }


    private void OnDisable()
    {
        if (grabPinch != null)
        {
            grabPinch.RemoveOnChangeListener(OnTriggerPressedOrReleased, inputSource);
        }
    }

    private void OnTriggerPressedOrReleased(SteamVR_Action_Boolean fromAction, SteamVR_Input_Sources fromSource, bool newState)
    {
        Destroy(MessageCanvas.gameObject);
        Destroy(this);
    }
}