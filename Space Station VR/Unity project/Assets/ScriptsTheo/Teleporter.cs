using System.Collections;
using System.Collections.Generic;
using UnityEngine;
using Valve.VR;
using Valve.VR.InteractionSystem;

public class Teleporter : MonoBehaviour
{
    public GameObject pointer;
    public SteamVR_Action_Boolean TeleportAction;

    private SteamVR_Behaviour_Pose Pose = null;
    private bool hasPosition = false;
    private bool isTeleporting = false;
    private float fadeTime = 0.5f;


    // Start is called before the first frame update
    void Awake()
    {
        Pose = GetComponent<SteamVR_Behaviour_Pose>();
    }

    // Update is called once per frame
    void Update()
    {
        //Pointer
        hasPosition = UpdatePointer();
        pointer.SetActive(hasPosition);



        //Teleport
        if (TeleportAction.GetStateUp(Pose.inputSource))
        {
            TryTeleport();
        }
    }

    private void TryTeleport()
    {
        //Check for valid position
        if (!hasPosition || isTeleporting)
        {
            return;
        }


        //Get Camera Rig
        Transform player = SteamVR_Render.Top().origin;

        Vector3 headPos = SteamVR_Render.Top().head.position;

        //Translation

        Vector3 groundPos = new Vector3(headPos.x, player.position.y, player.position.z);
        Vector3 translation = pointer.transform.position - groundPos;


        //Move
        StartCoroutine(MoveRig(player, translation));
    }

    private IEnumerator MoveRig(Transform player, Vector3 translation)
    {
        //Flag
        isTeleporting = true;

        //Fade to black
        SteamVR_Fade.Start(Color.black, fadeTime, true);

        //Apply translation
        yield return new WaitForSeconds(fadeTime);
        player.position += translation;

        //Fade black to clear
        SteamVR_Fade.Start(Color.clear, fadeTime, true);

        //Deflag
        isTeleporting = false;
    }
    
    private bool UpdatePointer()
    {
        //Ray from the controller
        Ray ray = new Ray(transform.position, transform.forward);
        RaycastHit hit;

        if(Physics.Raycast(ray, out hit))
        {
            pointer.transform.position = hit.point;
            return true;
        }


        return false;
    }
}
