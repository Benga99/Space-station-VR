using System.Collections;
using System.Collections.Generic;
using UnityEngine;
using Valve.VR;
using Valve.VR.InteractionSystem;

public class OperateSwitchButton : MonoBehaviour
{
    [SerializeField]
    private GameObject thisSwitchButton;
    [SerializeField]
    private GameObject leftHand;
    [SerializeField]
    private GameObject rightHand;
    [SerializeField]
    private Vector3 positionDown;
    [SerializeField]
    private Vector3 positionUp;
    [SerializeField]
    private SteamVR_Action_Boolean grabPinch;
    [SerializeField]
    private SteamVR_Input_Sources inputSource = SteamVR_Input_Sources.Any;

    private bool canMoveUp = true, canMoveDown = false;
    public bool isUp = false;

    private void Start()
    {
        rightHand.GetComponent<Hand>().grabPinchAction.AddOnStateDownListener(onPinchDown, inputSource);
        leftHand.GetComponent<Hand>().grabPinchAction.AddOnStateDownListener(onPinchDown, inputSource);
    }

    private IEnumerator moveSwitchDown()
    {
        float i = 0;
        this.gameObject.transform.rotation.eulerAngles.Set(0, -135, 0);
        while (i<=1)
        {
            this.gameObject.transform.position = Vector3.Lerp(positionUp, positionDown, i);
            i += Time.deltaTime;
            yield return new WaitForEndOfFrame();
        }
        canMoveUp = true;
        isUp = false;
    }

    private IEnumerator moveSwitchUp()
    {
        float i = 0;
        this.gameObject.transform.rotation.eulerAngles.Set(0, -135, 0);
        while (i <= 1)
        {
            this.gameObject.transform.position = Vector3.Lerp(positionDown, positionUp, i);
            i += Time.deltaTime;
            yield return new WaitForEndOfFrame();
        }
        canMoveDown = true;
        isUp = true;
    }


    private void onPinchDown(SteamVR_Action_Boolean action, SteamVR_Input_Sources input)
    {
        if ((rightHand.GetComponent<Hand>().hoveringInteractable != null && rightHand.GetComponent<Hand>().hoveringInteractable.gameObject == thisSwitchButton) ||
                (leftHand.GetComponent<Hand>().hoveringInteractable != null && leftHand.GetComponent<Hand>().hoveringInteractable.gameObject == thisSwitchButton))
        {
            if (canMoveUp)
            {
                canMoveUp = false;
                StartCoroutine(moveSwitchUp());
            }
            if(canMoveDown)
            {
                canMoveDown = false;
                StartCoroutine(moveSwitchDown());
            }
        }   
    }
}
