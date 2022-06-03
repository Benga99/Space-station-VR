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
    public List<bool> riddlesBool;

    [SerializeField]
    private GameObject RemoteControl;
    [SerializeField]
    private List<GameObject> TVs;
    [SerializeField]
    private GameObject key;
    [SerializeField]
    private GameObject dartsBoard;

    private List<bool> switchButtonsList = new List<bool>() { false, false, false, false};

    private bool switchButtonsTouched = false;
    
    private bool switchButtonsTouchedLevel2 = false;

    private RaycastHit hitInfo;
    private GameObject child = null;
    //TouchPad listener
    public SteamVR_Action_Boolean TouchpadAction = SteamVR_Input.GetAction<SteamVR_Action_Boolean>("TouchpadPressed");

    RiddleManager1 riddleManager;

    private void Start()
    {
        if (RemoteControl.transform.childCount > 1)
        {
            child = RemoteControl.transform.GetChild(1).gameObject;
        }
        riddleManager = FindObjectOfType<RiddleManager1>();
    }

    private void Update()
    {
        if (switchButtonsTouched)
        {
            if(switchButtonsList[0] == true && switchButtonsList[1] == false && switchButtonsList[2] == true && switchButtonsList[3] == true)
            {
                key.SetActive(true);
                //play some sound
            }
        }

        if (switchButtonsTouchedLevel2)
        {
            if (switchButtonsList[0] == true && switchButtonsList[1] == false && switchButtonsList[2] == false && switchButtonsList[3] == true)
            {
                //do smth
                dartsBoard.SetActive(true);
            }
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

            riddlesBool[2] = CheckRGB_TVRiddle();
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

    private bool CheckRGB_TVRiddle()
    {
        if (TVs[0].GetComponent<ChangeColorScreen>().currentColor == Color.green && TVs[0].name == "TVLeft")
        {
            if (TVs[1].GetComponent<ChangeColorScreen>().currentColor == Color.red && TVs[1].name == "TVCenter")
            {
                if (TVs[2].GetComponent<ChangeColorScreen>().currentColor == Color.blue && TVs[2].name == "TVRight")
                {
                    ActivateNumberTVs();
                    riddleManager.setRiddleDone(1);
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
            //tv.setStart(true);
            StartCoroutine(tv.displayingNumbers());
        }
    }

    public void SetSwitch(int index)
    {
        switchButtonsTouched = true;
        switchButtonsList[index] = !switchButtonsList[index];
    }

    public void SetSwitchLevel2(int index)
    {
        switchButtonsTouchedLevel2 = true;
        switchButtonsList[index] = !switchButtonsList[index];
    }
}
