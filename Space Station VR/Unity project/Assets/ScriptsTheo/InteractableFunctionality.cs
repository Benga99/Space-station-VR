using System.Collections;
using System.Collections.Generic;
using UnityEngine;
using Valve.VR;
using Valve.VR.InteractionSystem;

public class InteractableFunctionality : MonoBehaviour
{
    [SerializeField]
    private List<GameObject> TVs;

    private RaycastHit hitInfo;

    private GameObject child;


    //TouchPad listener
    public SteamVR_Action_Boolean TouchpadAction = SteamVR_Input.GetAction<SteamVR_Action_Boolean>("TouchpadPressed");

    private void Start()
    {
        if (this.transform.childCount > 1)
        {
            child = this.transform.GetChild(1).gameObject;
        }
        
    }

    public void DeactivateRigidbodyConstraints()
    {
        this.gameObject.GetComponent<Rigidbody>().constraints = RigidbodyConstraints.None;
    }

    public void UpdateRemoteControl()
    {
        //if TouchPad is pressed
        if (TouchpadAction.stateDown)
        {
            foreach (var tv in TVs)
            {
                if (Physics.Raycast(this.transform.position, (child.transform.position - this.transform.position).normalized, out hitInfo))
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
        }
        
        
    }
}
