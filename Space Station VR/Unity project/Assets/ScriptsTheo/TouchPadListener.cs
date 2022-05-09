using System.Collections;
using System.Collections.Generic;
using UnityEngine;
using Valve.VR;
using Valve.VR.InteractionSystem;

public class TouchPadListener : MonoBehaviour
{
    public SteamVR_Action_Boolean uiInteractAction = SteamVR_Input.GetAction<SteamVR_Action_Boolean>("TouchpadPressed");
    // Start is called before the first frame update
    void Start()
    {
        var array = SteamVR_Input.actionsIn;
        foreach (var v in array)
        {
            Debug.Log(v);
        }
        Hand hand = FindObjectOfType<Hand>();
       
    } 



    // Update is called once per frame
    void Update()
    {
        //if (uiInteractAction.changed)
        //{
        //    Debug.Log("ACTIVE");
        //}
    }
}
