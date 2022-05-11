using System.Collections;
using System.Collections.Generic;
using UnityEngine;
using Valve.VR;
using Valve.VR.InteractionSystem;

public class InteractableFunctionality : MonoBehaviour
{
    [SerializeField]
    private List<string> riddlesNames;
    [SerializeField]
    private List<bool> riddlesBool;

    [SerializeField]
    private GameObject RemoteControl;
    [SerializeField]
    private List<GameObject> TVs;



    private RaycastHit hitInfo;
    private GameObject child;
    //TouchPad listener
    public SteamVR_Action_Boolean TouchpadAction = SteamVR_Input.GetAction<SteamVR_Action_Boolean>("TouchpadPressed");



    private void Start()
    {
        if (RemoteControl.transform.childCount > 1)
        {
            child = RemoteControl.transform.GetChild(1).gameObject;
        }
    }

    public void DeactivateRigidbodyConstraints(GameObject obj)
    {
        obj.GetComponent<Rigidbody>().constraints = RigidbodyConstraints.None;
    }

    public void DeactivateGravity(GameObject obj)
    {
        obj.GetComponent<Rigidbody>().useGravity = false;
    }

    public void UpdateRemoteControl()
    {
        //if TouchPad is pressed
        if (TouchpadAction.stateDown)
        {
            foreach (var tv in TVs)
            {
                if (Physics.Raycast(RemoteControl.transform.position, (child.transform.position - RemoteControl.transform.position).normalized, out hitInfo))
                {
                    //if remote control points to a tv
                    if (hitInfo.collider.name == tv.name)
                    {
                        Debug.Log(hitInfo.collider.name);
                        tv.GetComponent<ChangeColorScreen>().Change();
                        break;
                    }

                }
            }

            riddlesBool[1] = CheckTVRiddle();

        }
    }

    public void PickedUpPoster()
    {
        riddlesBool[0] = true;
    }

    public void PickedUpFridgeHandle()
    {
        Debug.Log("Fridge opened!");
    }

    private bool CheckTVRiddle()
    {
        if (TVs[0].GetComponent<ChangeColorScreen>().currentColor == Color.green && TVs[0].name == "TVLeft")
        {
            if (TVs[1].GetComponent<ChangeColorScreen>().currentColor == Color.red && TVs[1].name == "TVCenter")
            {
                if (TVs[2].GetComponent<ChangeColorScreen>().currentColor == Color.blue && TVs[2].name == "TVRight")
                {
                    ActivateNumberTVs();
                    return true;
                    
                }
            }
        }
        return false;
    }

    private void ActivateNumberTVs()
    {
        var tvs = FindObjectsOfType<TVText>();
        foreach(var tv in tvs)
        {
            tv.setStart(true);
        }
    }
}
